"""
UE5 .locres reader/writer (v3, "Optimized_CityHash64_UTF16").

Format:
  [Magic: 16 bytes 0x0E14148174967428A0E4BFD8AAE5C0BD]  (v2+)
  [Version: u8]                                          (3 or 4)
  [StringTable Offset: i64]
  [Namespaces Count: u32]
  For each namespace:
    [Namespace hash: u32]
    [Namespace string: FString]
    [Keys Count: u32]
    For each key:
      [Key hash: u32]
      [Key string: FString]
      [Source string hash: u32]
      [Index in StringTable: i32]
  At StringTable Offset:
    [Count: i32]
    For each string:
      [String: FString]
      [RefCount: i32]

FString:
  [Length: i32]   positive = ASCII (length includes null), negative = UTF-16 (-length includes null)
  [bytes]
  [null terminator(s)]
"""
import struct, sys, io
from pathlib import Path

LOCRES_MAGIC = bytes.fromhex("0E147475674A03FC4A15909DC3377F1B")

def read_fstring(buf, pos):
    (length,) = struct.unpack_from("<i", buf, pos); pos += 4
    if length == 0:
        return "", pos
    if length > 0:
        data = buf[pos:pos+length-1]
        pos += length  # includes null
        return data.decode("utf-8"), pos
    else:
        n = -length
        data = buf[pos:pos+(n-1)*2]
        pos += n * 2  # 2 bytes per char incl wide null
        return data.decode("utf-16-le"), pos

def write_fstring(s):
    if s == "":
        return struct.pack("<i", 0)
    try:
        s.encode("ascii")
        b = s.encode("ascii") + b"\x00"
        return struct.pack("<i", len(b)) + b
    except UnicodeEncodeError:
        b = s.encode("utf-16-le") + b"\x00\x00"
        n_chars = len(b) // 2
        return struct.pack("<i", -n_chars) + b

# CityHash64 — UE5 uses CityHash64 truncated to u32 for namespace/key hash.
# We don't strictly need to compute it correctly because the runtime re-hashes on lookup;
# but to be safe we'll mimic UE: hash(string.ToUpper()).Lower32() — actually it's
# FTextLocalizationResource::HashString which uses StrCrc32 for v3 (legacy) or CityHash64 for v4.
# For v3 it's HashStringWithCRC. For UE5 v4 cookies use CityHash64.
# To stay portable, write the same hash the original file used: capture the hashes from input
# and reuse them. For new entries, we'll use the same algorithm as input.
#
# Empirically UE 5.5 produces v3 locres files using HashString -> StrCrc32 of UPPERCASE name.

# CRC32 polynomial = StrCrc32 used by UE = standard CRC-32 with reversed polynomial.
# UE FCrc::StrCrc32 implementation: takes string, hashes uppercase code units as little-endian
# uint16. Easier: capture original hashes from input file, write same hashes back if name
# unchanged. For Korean translations we keep namespace/key identical so hashes carry over.

class LocResEntry:
    __slots__ = ("ns_hash","ns","key_hash","key","src_hash","value")
    def __init__(self, ns_hash, ns, key_hash, key, src_hash, value):
        self.ns_hash, self.ns, self.key_hash, self.key, self.src_hash, self.value = \
            ns_hash, ns, key_hash, key, src_hash, value

def read_locres(path):
    buf = Path(path).read_bytes()
    pos = 0
    if buf[:16] == LOCRES_MAGIC:
        pos = 16
    else:
        raise ValueError("missing locres magic — not a v2+ locres or unsupported format")
    (version,) = struct.unpack_from("<B", buf, pos); pos += 1
    if version not in (3, 4):
        raise ValueError(f"unsupported locres version: {version}")
    (string_table_offset,) = struct.unpack_from("<q", buf, pos); pos += 8

    # Read string table first
    sp = string_table_offset
    (str_count,) = struct.unpack_from("<i", buf, sp); sp += 4
    string_table = []
    for _ in range(str_count):
        s, sp = read_fstring(buf, sp)
        (refc,) = struct.unpack_from("<i", buf, sp); sp += 4
        string_table.append((s, refc))

    # v3+: total entry count (used by runtime to size hash tables)
    if version >= 3:
        (entries_total,) = struct.unpack_from("<I", buf, pos); pos += 4
    # Read namespaces
    (ns_count,) = struct.unpack_from("<I", buf, pos); pos += 4
    entries = []
    for _ in range(ns_count):
        (ns_hash,) = struct.unpack_from("<I", buf, pos); pos += 4
        ns, pos = read_fstring(buf, pos)
        (key_count,) = struct.unpack_from("<I", buf, pos); pos += 4
        for _ in range(key_count):
            (key_hash,) = struct.unpack_from("<I", buf, pos); pos += 4
            key, pos = read_fstring(buf, pos)
            (src_hash,) = struct.unpack_from("<I", buf, pos); pos += 4
            (idx,)      = struct.unpack_from("<i", buf, pos); pos += 4
            value, _ = string_table[idx]
            entries.append(LocResEntry(ns_hash, ns, key_hash, key, src_hash, value))
    return version, entries

def write_locres(entries, version=3):
    """Reverse of read_locres. Reuses ns_hash/key_hash/src_hash from original entries."""
    # Group entries by namespace, preserving original ns_hash per namespace
    ns_groups = {}  # ns -> (ns_hash, [entry])
    for e in entries:
        g = ns_groups.setdefault(e.ns, (e.ns_hash, []))
        g[1].append(e)

    # Build string table: dedup values, count refs
    string_table = []
    str_index = {}  # value -> idx
    for e in entries:
        if e.value not in str_index:
            str_index[e.value] = len(string_table)
            string_table.append([e.value, 0])
        string_table[str_index[e.value]][1] += 1

    # Compute body (everything before string table) — we need the offset, so build body first
    body = io.BytesIO()
    if version >= 3:
        body.write(struct.pack("<I", len(entries)))  # total entries count
    body.write(struct.pack("<I", len(ns_groups)))
    for ns, (ns_hash, ns_entries) in ns_groups.items():
        body.write(struct.pack("<I", ns_hash))
        body.write(write_fstring(ns))
        body.write(struct.pack("<I", len(ns_entries)))
        for e in ns_entries:
            body.write(struct.pack("<I", e.key_hash))
            body.write(write_fstring(e.key))
            body.write(struct.pack("<I", e.src_hash))
            body.write(struct.pack("<i", str_index[e.value]))

    body_bytes = body.getvalue()

    # Header: magic(16) + version(1) + offset(8)
    header_size = 16 + 1 + 8
    string_table_offset = header_size + len(body_bytes)

    out = io.BytesIO()
    out.write(LOCRES_MAGIC)
    out.write(struct.pack("<B", version))
    out.write(struct.pack("<q", string_table_offset))
    out.write(body_bytes)
    # String table
    out.write(struct.pack("<i", len(string_table)))
    for value, refc in string_table:
        out.write(write_fstring(value))
        out.write(struct.pack("<i", refc))
    return out.getvalue()


# ---------------- LocMeta (Game.locmeta) reader/writer --------------------
LOCMETA_MAGIC = bytes.fromhex("4FEE4CA168485583 6C4C46BD70DA507C".replace(" ",""))

def read_locmeta(path):
    buf = Path(path).read_bytes()
    if buf[:16] != LOCMETA_MAGIC:
        raise ValueError("missing locmeta magic")
    pos = 16
    (version,) = struct.unpack_from("<B", buf, pos); pos += 1
    native_culture, pos = read_fstring(buf, pos)
    native_locres_path, pos = read_fstring(buf, pos)
    (count,) = struct.unpack_from("<I", buf, pos); pos += 4
    cultures = []
    for _ in range(count):
        c, pos = read_fstring(buf, pos)
        cultures.append(c)
    return version, native_culture, native_locres_path, cultures

def write_locmeta(version, native_culture, native_locres_path, cultures):
    out = io.BytesIO()
    out.write(LOCMETA_MAGIC)
    out.write(struct.pack("<B", version))
    out.write(write_fstring(native_culture))
    out.write(write_fstring(native_locres_path))
    out.write(struct.pack("<I", len(cultures)))
    for c in cultures:
        out.write(write_fstring(c))
    return out.getvalue()


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    if len(sys.argv) < 2:
        print("usage: python locres.py <path/to/Game.locres> [search_substr]"); sys.exit(1)
    version, entries = read_locres(sys.argv[1])
    needle = sys.argv[2] if len(sys.argv) > 2 else None
    print(f"version: {version}, entries: {len(entries)}, namespaces: {len(set(e.ns for e in entries))}")
    if needle:
        for e in entries:
            if needle in e.value or needle in e.key:
                print(f"  ns={e.ns!r} key={e.key!r}\n    value={e.value[:80]!r}{'...' if len(e.value)>80 else ''}")
    else:
        for e in entries[:10]:
            print(f"  ns={e.ns!r:30s} key={e.key!r:34s} -> {e.value[:60]!r}{'...' if len(e.value)>60 else ''}")
        if len(entries) > 10:
            print(f"  ... ({len(entries)-10} more)")
