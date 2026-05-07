"""Measure how much of en/Game.locres is covered by ko.po (via SourceString match).

Also exposes parse_po() for reuse by build_ko_locres.py.
"""
import sys, io
from pathlib import Path

PO_ESC = {'\\\\': '\\', '\\"': '"', '\\n': '\n', '\\r': '\r', '\\t': '\t'}

def po_unescape(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        if s[i] == '\\' and i + 1 < len(s):
            esc = s[i:i+2]
            out.append(PO_ESC.get(esc, esc))
            i += 2
        else:
            out.append(s[i]); i += 1
    return "".join(out)

def parse_po(path: Path) -> dict[str, str]:
    """{msgid: msgstr} for entries with a non-empty msgstr."""
    out = {}
    cur_id = cur_str = None
    state = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith('msgid "'):
            cur_id = po_unescape(line[7:-1]); state = "id"
        elif line.startswith('msgstr "'):
            cur_str = po_unescape(line[8:-1]); state = "str"
            if cur_str: out[cur_id] = cur_str
        elif state and line.startswith('"') and line.endswith('"'):
            v = po_unescape(line[1:-1])
            if state == "id": cur_id += v
            else:              cur_str += v
            if state == "str" and cur_str: out[cur_id] = cur_str
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.path.insert(0, str(Path(__file__).parent))
    from locres import read_locres

    _ROOT = Path(__file__).resolve().parent.parent
    ver, entries = read_locres(str(_ROOT / "work/locres_extract/OutworldStation/Content/Localization/Game/en/Game.locres"))
    ko = parse_po(_ROOT / "translation" / "ko.po")

    matched = unmatched = 0
    ex_match, ex_miss = [], []
    for e in entries:
        if e.value in ko:
            matched += 1
            if len(ex_match) < 5: ex_match.append((e.value, ko[e.value]))
        else:
            unmatched += 1
            if len(ex_miss) < 10: ex_miss.append(e.value)

    print(f"en/Game.locres entries: {len(entries)}")
    print(f"ko.po unique translations: {len(ko)}")
    print(f"matched: {matched}  ({100*matched/len(entries):.1f}%)")
    print(f"unmatched: {unmatched}")
    print()
    print("Sample MATCHED:")
    for en, kr in ex_match:
        print(f"  EN: {en[:80]!r}")
        print(f"  KO: {kr[:80]!r}")
    print()
    print("Sample UNMATCHED:")
    for s in ex_miss:
        print(f"  {s[:100]!r}")
