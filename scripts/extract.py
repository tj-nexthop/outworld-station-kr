"""
Phase 3: extract translatable English text from DataTable JSONs into a single
source.po that LQA edits, plus a manifest.json that records every byte position
needed to round-trip back into the .uasset/.uexp files.

Pipeline:
  legacy .uasset/.uexp  --tojson-->  *.json
                                       │
                                       ▼ extract.py
                                source.po + manifest.json
                                       │
                                       ▼ ko.po (LQA edits)
                                       │
                                       ▼ apply.py
                              modified *.json  --fromjson--> *.uasset/.uexp

The JSON has Exports[i].Data = base64 of the .uexp body (RawExport because the
package is unversioned cooked and we have no .usmap mappings). FStrings live
inline in those bytes:
  - ASCII   FString:  int32 length>0   + length bytes (last byte is NUL)
  - UTF-16  FString:  int32 length<0   + (|length|*2) bytes (last 2 bytes are NUL)
"""
from __future__ import annotations
import argparse, base64, json, re, struct, sys, io, hashlib
from dataclasses import dataclass, asdict
from pathlib import Path

# -------------------------------------------------------------- FString walker
def walk_fstrings(buf: bytes):
    """Yield (offset, length_field, raw_bytes_excl_null, decoded_str, is_utf16)."""
    p, n = 0, len(buf)
    while p + 4 <= n:
        ln = struct.unpack_from("<i", buf, p)[0]
        # Positive: ASCII string of `ln` bytes including NUL terminator
        if 1 < ln <= 512:
            end = p + 4 + ln
            if end <= n and buf[end - 1] == 0:
                raw = buf[p + 4:end - 1]
                if all(0x20 <= b <= 0x7e or b in (9, 10, 13) for b in raw):
                    yield (p, ln, raw, raw.decode("ascii"), False)
                    p = end
                    continue
        # Negative: UTF-16LE string of |ln| code units including NUL
        elif -2048 < ln < -1:
            m = -ln
            end = p + 4 + m * 2
            if end <= n and buf[end - 2] == 0 and buf[end - 1] == 0:
                raw = buf[p + 4:end - 2]
                if all(raw[i + 1] == 0 and (0x20 <= raw[i] <= 0x7e or raw[i] in (9, 10, 13))
                       for i in range(0, len(raw), 2)):
                    yield (p, ln, raw, raw.decode("utf-16le"), True)
                    p = end
                    continue
        p += 1

# -------------------------------------------------------------- classification
GUID32_RE = re.compile(r"^[A-F0-9]{32}$")
GUID36_RE = re.compile(r"^[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$")
IDENT_RE  = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PATH_RE   = re.compile(r"^/(Game|Engine|Script)/")

def classify(s: str) -> str:
    """Return one of: 'translatable', 'guid', 'identifier', 'path', 'empty', 'other'."""
    if not s: return "empty"
    if GUID32_RE.match(s) or GUID36_RE.match(s.upper()): return "guid"
    if PATH_RE.match(s): return "path"
    if IDENT_RE.match(s) and not " " in s and "_" in s and any(c.isupper() for c in s):
        return "identifier"  # snake_Case or PascalCase
    if not any(c.isalpha() for c in s): return "other"
    if len(s) < 2: return "other"
    return "translatable"

# -------------------------------------------------------------- per-file scan
@dataclass
class StringHit:
    file: str               # asset stem, e.g. "DT_Build_Categories"
    source_path: str        # extracted/legacy-relative .uasset path; tells build.ps1 where to put fromjson output
    export_idx: int         # which Exports[i] inside the JSON
    byte_offset: int        # offset within RawExport.Data
    length_field: int       # original int32 length prefix (signed)
    is_utf16: bool
    text: str
    kind: str               # classify() result

def scan_json(json_path: Path, source_path: str) -> list[StringHit]:
    j = json.loads(json_path.read_text(encoding="utf-8"))
    hits: list[StringHit] = []
    stem = json_path.stem
    for ie, exp in enumerate(j.get("Exports", []) or []):
        data_b64 = exp.get("Data")
        if not isinstance(data_b64, str): continue
        try:
            buf = base64.b64decode(data_b64)
        except Exception:
            continue
        for off, ln, raw, s, u16 in walk_fstrings(buf):
            hits.append(StringHit(
                file=stem, source_path=source_path,
                export_idx=ie, byte_offset=off,
                length_field=ln, is_utf16=u16, text=s,
                kind=classify(s),
            ))
    return hits

# -------------------------------------------------------------- PO writer
def po_escape(s: str) -> str:
    return (s.replace("\\", "\\\\").replace('"', '\\"')
             .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))

def write_po(po_path: Path, hits: list[StringHit]):
    """Write source.po with every translatable hit as msgctxt-keyed entry."""
    lines = [
        '# Outworld Station Korean translation — source extracted from DataTables',
        '# Edit msgstr lines only. msgctxt is the join key with manifest.json.',
        'msgid ""',
        'msgstr ""',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '"Content-Transfer-Encoding: 8bit\\n"',
        '"X-Generator: outworldstation_kr/extract.py\\n"',
        '',
    ]
    seen_keys = set()
    for h in hits:
        if h.kind != "translatable": continue
        key = f"{h.file}@e{h.export_idx}@{h.byte_offset:x}"
        if key in seen_keys: continue
        seen_keys.add(key)
        lines.append(f"#: {h.file} export[{h.export_idx}] offset=0x{h.byte_offset:x}")
        lines.append(f"#. encoding={'UTF-16LE' if h.is_utf16 else 'ASCII'} len_field={h.length_field}")
        lines.append(f'msgctxt "{po_escape(key)}"')
        lines.append(f'msgid "{po_escape(h.text)}"')
        lines.append('msgstr ""')
        lines.append('')
    po_path.write_text("\n".join(lines), encoding="utf-8")
    return len([1 for h in hits if h.kind == "translatable"])

# -------------------------------------------------------------- manifest writer
def write_manifest(manifest_path: Path, hits: list[StringHit]):
    """All hits (incl non-translatable) so apply.py can verify integrity."""
    payload = {
        "version": 1,
        "entries": [asdict(h) for h in hits],
    }
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

# -------------------------------------------------------------- CLI
_ROOT = Path(__file__).resolve().parent.parent

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-dirs", nargs="+",
                    default=[str(_ROOT / "work" / d) for d in
                             ("dt_json", "menu_json", "ui_json", "modules_json", "misc_json")],
                    help="directories containing per-asset JSONs (can specify multiple)")
    ap.add_argument("--source-paths", nargs="+",
                    default=[r"OutworldStation\Content\Data",
                             r"OutworldStation\Content\MainMenu",
                             r"OutworldStation\Content\UI",
                             r"OutworldStation\Content\Station\Modules",
                             r"__per_asset_path_map__"],  # special sentinel: read _path_map.json
                    help="for each JSON dir (in order), the relative source path under source/. "
                         "Use '__per_asset_path_map__' to read _path_map.json from that dir.")
    ap.add_argument("--out-dir", default=str(_ROOT / "translation"),
                    help="output directory for source.po + manifest.json")
    args = ap.parse_args()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if len(args.json_dirs) != len(args.source_paths):
        raise SystemExit("--json-dirs and --source-paths must be paired 1:1")
    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)

    all_hits: list[StringHit] = []
    for json_dir, src_rel in zip(args.json_dirs, args.source_paths):
        jd = Path(json_dir)
        if not jd.exists():
            print(f"skip (missing): {jd}")
            continue
        # Per-asset path map (sentinel mode for misc_json folder)
        per_asset_paths = {}
        if src_rel == "__per_asset_path_map__":
            pmap_path = jd / "_path_map.json"
            if pmap_path.exists():
                per_asset_paths = json.loads(pmap_path.read_text(encoding="utf-8"))
                print(f"scanning JSONs in {jd}  (per-asset paths from _path_map.json: {len(per_asset_paths)})")
            else:
                print(f"skip (missing _path_map.json): {jd}")
                continue
        else:
            print(f"scanning JSONs in {jd}  (source rel = {src_rel})")
        for jp in sorted(jd.glob("*.json")):
            if jp.name == "_path_map.json":
                continue
            if per_asset_paths:
                asset_source_path = per_asset_paths.get(jp.stem)
                if not asset_source_path:
                    continue  # asset not in map
            else:
                asset_source_path = f"{src_rel}\\{jp.stem}.uasset".replace("\\\\", "\\")
            hits = scan_json(jp, asset_source_path)
            kind_counts = {}
            for h in hits: kind_counts[h.kind] = kind_counts.get(h.kind, 0) + 1
            print(f"  {jp.stem:38s}  total={len(hits):4d}  translatable={kind_counts.get('translatable', 0):4d}  "
                  f"guid={kind_counts.get('guid', 0):3d}  ident={kind_counts.get('identifier', 0):3d}  "
                  f"path={kind_counts.get('path', 0):2d}  other={kind_counts.get('other', 0):3d}")
            all_hits.extend(hits)

    po_path = out_dir / "source.po"
    mf_path = out_dir / "manifest.json"
    n_translatable = write_po(po_path, all_hits)
    write_manifest(mf_path, all_hits)
    print(f"\nwrote {po_path}  ({n_translatable} translatable entries)")
    print(f"wrote {mf_path}  ({len(all_hits)} total entries across all kinds)")

    # Word-count summary for the LQA estimate
    words = sum(len(re.findall(r"[A-Za-z][A-Za-z'-]*", h.text))
                for h in all_hits if h.kind == "translatable")
    print(f"approx word count: {words:,}")

if __name__ == "__main__":
    main()
