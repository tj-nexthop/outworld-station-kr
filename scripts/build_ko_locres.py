"""
Build the full ko/Game.locres + ko-registered Game.locmeta for the Korean patch.

Strategy:
  1. Read en/Game.locres (2911 entries, 1 namespace "")
  2. For each entry, look up its SourceString in translation/ko.po
  3. If translated → add to ko/Game.locres with same ns/key/src_hash, value=Korean
  4. If not translated → omit (game falls back to en at runtime)
  5. Update Game.locmeta to register ko culture
  6. Layout files for repak: work/ko_pak_root/OutworldStation/Content/Localization/Game/...

Also includes hardcoded translations for the 8 mode-bar tooltips that aren't in
ko.po yet (those came from poc_bp_opcode.py's ENTRIES list).
"""
import sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from locres import read_locres, write_locres, LocResEntry, read_locmeta, write_locmeta
from match_locres_to_po import parse_po
from build_ko_po import TR  # full master translation dict
from ko_locres_extra import LOCRES_EXTRA  # supplementary .locres-only mappings

ROOT = Path(__file__).resolve().parent.parent
EN_LOCRES = ROOT / "work/locres_extract/OutworldStation/Content/Localization/Game/en/Game.locres"
EN_LOCMETA = ROOT / "work/locres_extract/OutworldStation/Content/Localization/Game/Game.locmeta"
KO_PO = ROOT / "translation/ko.po"
PAK_ROOT = ROOT / "work/ko_pak_root"

# 8 mode-bar tooltips not in ko.po (because they were originally targets of BP patching)
MODEBAR_KO = {
    "<Bold>Combat Mode</>\r\nEnters Combat Mode which lets you deploy your Drone's weapons.":
        "<Bold>전투 모드</>\r\n드론의 무기를 사용할 수 있는 전투 모드에 진입합니다.",
    "<Bold>Link Mode</>\r\nEnters Link Mode which lets you automate supply chains by linking source and destination modules together.":
        "<Bold>연결 모드</>\r\n공급원 모듈과 대상 모듈을 연결하여 공급망을 자동화하는 연결 모드에 진입합니다.",
    "<Bold>Repair Mode</>\r\nEnters Repair Mode which lets you repair damaged and disabled station modules with your Drone.":
        "<Bold>수리 모드</>\r\n드론으로 손상되거나 비활성화된 스테이션 모듈을 수리하는 수리 모드에 진입합니다.",
    "<Bold>Add Custom To-Do Task</>\r\nLets you add a custom task to your To-Do List which is also shared with all multiplayer players.":
        "<Bold>사용자 작업 추가</>\r\n모든 멀티플레이어와 공유되는 할 일 목록에 사용자 작업을 추가합니다.",
    "<Bold>Calculator</>\r\nOpens a calculator tool which lets you enter any maths expression and see the result.":
        "<Bold>계산기</>\r\n수식을 입력하고 결과를 볼 수 있는 계산기 도구를 엽니다.",
    "<Bold>Show Labels</>\r\nChoose whether to show a module's label when in the status view.":
        "<Bold>라벨 표시</>\r\n상태 뷰에서 모듈의 라벨 표시 여부를 선택합니다.",
    "<Bold>Show Pipe Flow</>\r\nChoose whether to show all pipe's flow displays in the status view.":
        "<Bold>파이프 흐름 표시</>\r\n상태 뷰에서 모든 파이프의 흐름 표시 여부를 선택합니다.",
    "<Bold>Show Tug Links</>\r\nChoose whether to show a module's tug links and destination in the status view.":
        "<Bold>예인선 연결 표시</>\r\n상태 뷰에서 모듈의 예인선 연결과 목적지 표시 여부를 선택합니다.",
    # Also the 9 odd-length ones — so we can revert BP patches and let .locres handle them too
    "<Bold>Build Mode</>\r\nOpens the Build Menu which lets you construct new station modules.":
        "<Bold>건설 모드</>\r\n새 스테이션 모듈을 건설할 수 있는 건설 메뉴를 엽니다.",
    "<Bold>Sell Mode</>\r\nEnters Sell Mode which lets you deconstruct station modules with your Drone and recoup all materials.":
        "<Bold>판매 모드</>\r\n드론으로 스테이션 모듈을 해체하고 모든 재료를 회수하는 판매 모드에 진입합니다.",
    "<Bold>Codex</>\r\nOpens the Codex which contains a great deal of useful information about the game.":
        "<Bold>코덱스</>\r\n게임에 관한 유용한 정보가 많이 담긴 코덱스를 엽니다.",
    "<Bold>Multi-Select Mode</>\r\nSelect multiple modules and easily apply functions to all of them at the same time.":
        "<Bold>다중 선택 모드</>\r\n여러 모듈을 선택하고 동시에 모든 모듈에 기능을 쉽게 적용합니다.",
    "<Bold>Select Connected</>\r\nExpand selection to all modules connected to the current selection":
        "<Bold>연결된 모듈 선택</>\r\n현재 선택에 연결된 모든 모듈로 선택을 확장합니다",
    "<Bold>Production Overview</>\r\nOpens the <Bold>Production Overview Panel</> which gives you a summary of all items, parts and materials your station is using and producing.":
        "<Bold>생산 개요</>\r\n스테이션이 사용 및 생산 중인 모든 아이템, 부품, 재료의 요약을 보여주는 <Bold>생산 개요 패널</>을 엽니다.",
    "<Bold>Show Item Send Rates</>\r\nChoose whether to show a module's item send rates when in the status view.":
        "<Bold>아이템 전송 속도 표시</>\r\n상태 뷰에서 모듈의 아이템 전송 속도 표시 여부를 선택합니다.",
    "<Bold>Show Links</>\r\nChoose whether to show all module links when in the status view.":
        "<Bold>연결 표시</>\r\n상태 뷰에서 모든 모듈 연결 표시 여부를 선택합니다.",
    "<Bold>Build Upgraded Modules</>\r\nSelect to build the highest available upgrade for each module directly":
        "<Bold>업그레이드 모듈 건설</>\r\n각 모듈에서 사용 가능한 최고 업그레이드를 직접 건설하도록 선택합니다",
}

# ---- Build ko/Game.locres ----
ver, en_entries = read_locres(EN_LOCRES)
po_dict = parse_po(KO_PO)

# Combine sources: TR (master dict) → MODEBAR_KO (mode-bar specifics) → po_dict (current ko.po edits win)
# TR contains every translation including .locres-only entries (hover labels, codex articles, UI labels).
# po_dict is the subset that survived through manifest matching for DataTable byte-patching.
combined = dict(TR)
combined.update(LOCRES_EXTRA)
combined.update(MODEBAR_KO)
combined.update(po_dict)

ko_entries = []
mode_bar_count = po_count = 0
for e in en_entries:
    if e.value in combined:
        ko_value = combined[e.value]
        ko_entries.append(LocResEntry(
            ns_hash=e.ns_hash, ns=e.ns,
            key_hash=e.key_hash, key=e.key,
            src_hash=e.src_hash,
            value=ko_value,
        ))
        if e.value in MODEBAR_KO and e.value not in po_dict:
            mode_bar_count += 1
        else:
            po_count += 1

ko_dir = PAK_ROOT / "OutworldStation/Content/Localization/Game/ko"
ko_dir.mkdir(parents=True, exist_ok=True)
out = ko_dir / "Game.locres"
out.write_bytes(write_locres(ko_entries, version=ver))
print(f"ko/Game.locres: {len(ko_entries)} entries  ({po_count} from ko.po + {mode_bar_count} from MODEBAR_KO)  size={out.stat().st_size}")

# ---- Update Game.locmeta to register ko culture ----
mver, native, native_path, cultures = read_locmeta(EN_LOCMETA)
if "ko" not in cultures:
    cultures.append("ko")
loc_dir = PAK_ROOT / "OutworldStation/Content/Localization/Game"
locmeta_out = loc_dir / "Game.locmeta"
locmeta_out.write_bytes(write_locmeta(mver, native, native_path, cultures))
print(f"Game.locmeta: cultures={cultures}  size={locmeta_out.stat().st_size}")

# ---- Round-trip check ----
v2, e2 = read_locres(out)
v3, n3, p3, c3 = read_locmeta(locmeta_out)
assert len(e2) == len(ko_entries), "round-trip entry count mismatch"
assert "ko" in c3, "ko not in cultures after write"
print(f"\nround-trip OK: locres v{v2}/{len(e2)}, locmeta v{v3} cultures={c3}")
