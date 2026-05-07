"""
Phase 4: apply ko.po translations onto the per-asset JSONs.

Reads:
  translation/ko.po       (LQA-edited)
  translation/manifest.json
  work/dt_json/*.json     (originals from extract step)

Writes:
  work/dt_json_ko/*.json  (only files with at least one translated entry)

The .json delta strategy is byte-level inside Exports[i].Data (base64 of .uexp body):
  - Locate every translated string by (file, export_idx, byte_offset).
  - Build a new bytes by stitching original bytes around each replacement,
    so size deltas naturally accumulate.
  - UAssetGUI fromjson rewrites the .uasset / .uexp with corrected SerialSize/Offsets.
"""
from __future__ import annotations
import argparse, base64, json, re, sys, io
from pathlib import Path

# ---------- PO reader (minimal, no external dependency) ----------------------
PO_ESC = {"\\\\": "\\", '\\"': '"', "\\n": "\n", "\\r": "\r", "\\t": "\t"}

def po_unescape(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            esc = s[i:i+2]
            out.append(PO_ESC.get(esc, esc))
            i += 2
        else:
            out.append(s[i]); i += 1
    return "".join(out)

def parse_po(path: Path) -> dict[str, str]:
    """Return {msgctxt: msgstr} for every entry that has a non-empty msgstr."""
    entries: dict[str, str] = {}
    cur_ctx = cur_id = cur_str = None
    state = None  # 'ctx' | 'id' | 'str'
    def flush():
        if cur_ctx is not None and cur_str:
            entries[cur_ctx] = cur_str
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith('msgctxt "'):
            flush()
            cur_ctx = po_unescape(line[len('msgctxt "'):-1])
            cur_id = cur_str = ""; state = "ctx"
        elif line.startswith('msgid "'):
            cur_id = po_unescape(line[len('msgid "'):-1]); state = "id"
        elif line.startswith('msgstr "'):
            cur_str = po_unescape(line[len('msgstr "'):-1]); state = "str"
        elif line.startswith('"') and line.endswith('"'):
            chunk = po_unescape(line[1:-1])
            if state == "id": cur_id += chunk
            elif state == "str": cur_str += chunk
            elif state == "ctx": cur_ctx += chunk
    flush()
    return entries

# ---------- FString byte writer ---------------------------------------------
def make_fstring(s: str) -> bytes:
    """Serialise a Python string into a UE FString (length prefix + bytes incl NUL)."""
    if s == "":
        return b"\x00\x00\x00\x00"
    if any(ord(c) > 0x7e for c in s):
        body = s.encode("utf-16-le") + b"\x00\x00"
        n = len(body) // 2  # code units incl NUL
        return (-n).to_bytes(4, "little", signed=True) + body
    else:
        body = s.encode("ascii") + b"\x00"
        return len(body).to_bytes(4, "little", signed=True) + body

def orig_total_size(length_field: int) -> int:
    """Return the total byte size of the original FString record."""
    if length_field >= 0:
        return 4 + length_field
    return 4 + (-length_field) * 2

# ---------- per-export byte stitching ---------------------------------------
def apply_replacements(orig: bytes, repls: list[tuple[int, int, bytes]]) -> bytes:
    """`repls` = list of (offset, orig_total_size, new_bytes) sorted by offset."""
    out = bytearray()
    cursor = 0
    for off, orig_len, new_bytes in sorted(repls):
        if off < cursor:
            raise ValueError(f"overlapping replacements at offset {off}")
        out.extend(orig[cursor:off])
        out.extend(new_bytes)
        cursor = off + orig_len
    out.extend(orig[cursor:])
    return bytes(out)

_ROOT = Path(__file__).resolve().parent.parent

# ---------- main -------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ko-po",   default=str(_ROOT / "translation" / "ko.po"))
    ap.add_argument("--manifest", default=str(_ROOT / "translation" / "manifest.json"))
    ap.add_argument("--in-jsons", nargs="+",
                    default=[str(_ROOT / "work" / d) for d in
                             ("dt_json", "menu_json", "ui_json", "modules_json", "misc_json")],
                    help="one or more input directories of per-asset JSONs")
    ap.add_argument("--out-json", default=str(_ROOT / "work" / "dt_json_ko"))
    args = ap.parse_args()

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    in_dirs = [Path(p) for p in args.in_jsons]
    out_dir = Path(args.out_json); out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load translations + manifest
    translations = parse_po(Path(args.ko_po))
    print(f"loaded {len(translations)} translated entries from ko.po")
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    entries = manifest["entries"]
    print(f"manifest: {len(entries)} total string locations")

    # 2. Build per-(file, export_idx) replacement plan from translations
    plan: dict[tuple[str, int], list[tuple[int, int, bytes]]] = {}
    matched = 0; skipped_no_loc = 0
    for ctx, kor in translations.items():
        # Find the manifest entry whose msgctxt matches
        # ctx format: "{file}@e{export}@{hex_offset}"
        m = re.fullmatch(r"(.+)@e(\d+)@([0-9a-fA-F]+)", ctx)
        if not m:
            skipped_no_loc += 1; continue
        file, ie, off_hex = m.group(1), int(m.group(2)), int(m.group(3), 16)
        # Find original entry for length_field
        match = None
        for e in entries:
            if e["file"] == file and e["export_idx"] == ie and e["byte_offset"] == off_hex:
                match = e; break
        if match is None:
            skipped_no_loc += 1; continue
        orig_len = orig_total_size(match["length_field"])
        new_bytes = make_fstring(kor)
        plan.setdefault((file, ie), []).append((off_hex, orig_len, new_bytes))
        matched += 1
    print(f"matched {matched} entries, skipped {skipped_no_loc} with no manifest match")

    # 3. Rewrite affected JSONs
    affected_files = {f for (f, _) in plan.keys()}
    print(f"\nrewriting {len(affected_files)} JSON file(s):")
    for stem in sorted(affected_files):
        in_path = None
        for d in in_dirs:
            cand = d / f"{stem}.json"
            if cand.exists():
                in_path = cand; break
        if in_path is None:
            print(f"  skip {stem}: no JSON found in any input dir")
            continue
        out_path = out_dir / f"{stem}.json"
        j = json.loads(in_path.read_text(encoding="utf-8"))
        n_replacements_in_file = 0
        for ie, exp in enumerate(j.get("Exports", []) or []):
            repls = plan.get((stem, ie))
            if not repls: continue
            data_b64 = exp["Data"]
            buf = base64.b64decode(data_b64)
            new_buf = apply_replacements(buf, repls)
            exp["Data"] = base64.b64encode(new_buf).decode("ascii")
            n_replacements_in_file += len(repls)
            # Optional consistency: SerialSize will be rewritten by UAssetGUI on fromjson.
        out_path.write_text(json.dumps(j, indent=2, ensure_ascii=False), encoding="utf-8")
        delta = sum(len(b) - ol for _, ol, b in
                    [r for k, rs in plan.items() if k[0] == stem for r in rs])
        print(f"  {stem:30s} replacements={n_replacements_in_file:3d}  size_delta={delta:+d} bytes")

    print(f"\noutput JSONs in: {out_dir}")
    print("Next: run UAssetGUI fromjson on each modified JSON, then retoc to-zen.")

if __name__ == "__main__":
    main()
