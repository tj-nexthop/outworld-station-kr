# Outworld Station 한글 패치

[Outworld Station](https://store.steampowered.com/app/2607960/Outworld_Station/)
(UE5 / IoStore) 한국어 번역 모드. 단일 .exe 인스톨러로 배포되며, Steam 게임 폴더를 자동 탐지해 한 번의 클릭으로 한글화를 적용합니다.

| 항목 (Item) | 값 (Value) |
|---|---|
| 한글 패치 버전 (Patch version) | **v1.0.5** |
| 패치 빌드 날짜 (Patch build date) | **2026-05-26** |
| 대상 게임 빌드 (Target game build) | **Outworld Station 1.0.0.4 [REL]** (정식 출시 / Official release, 2026-05-05) |
| 테스트 OS (Tested OS) | **Windows 11** |

> ⚠️ **Steam이 게임을 업데이트하면 (예: 1.0.0.5, 1.0.1.0 등) 본 패치는 호환되지 않을 수 있습니다.** 새 게임 빌드가 나오면 새 한글 패치 버전이 올라올 때까지 기다려 주세요. 이슈는 [Issues](https://github.com/tj-nexthop/outworld-station-kr/issues)에 알려주시면 우선순위 보고 처리합니다 (보장은 어려움).
>
> ⚠️ *Patch may break when Steam updates the game (e.g., to 1.0.0.5). Wait for a new patch release in that case. Open an Issue if you encounter problems — fixes are best-effort.*

## 📌 알려드립니다 (Heads-up)

> [!IMPORTANT]
> **본인이 한국어로 플레이하려고 만든 취미 프로젝트입니다.** 게임을 완전히 클리어하지 못한 상태라 후반부 어디서 에러가 터질지 모르고, 버그/오역 수정은 보장하기 어렵습니다. 수정 PR은 언제든 환영합니다.
>
> *Hobby project made primarily to play the game in Korean myself. Game not fully cleared yet, so late-game errors are possible. Bug fixes are best-effort. PRs welcome.*

본 패치는 [**Claude Code**](https://claude.com/claude-code) (Anthropic)를 사용하여 제작되었습니다. UE5 리버스 엔지니어링, BP 바이트코드 분석, `.locres` 파이프라인 설계, 번역 작업 대부분이 AI 에이전트를 통해 이루어졌습니다.

*Built using [**Claude Code**](https://claude.com/claude-code) (Anthropic). UE5 reverse engineering, BP bytecode analysis, .locres pipeline design, and most translation work were done with the AI agent.*

## 설치 (사용자용)

> **테스트 환경 (Tested on)**: Windows 11. 그 외 환경(Windows 10 등)에서는 동작 보장이 어렵습니다.

1. Steam에서 Outworld Station을 설치합니다.
2. [v1.0.5 릴리즈 페이지](https://github.com/tj-nexthop/outworld-station-kr/releases/tag/v1.0.5)로 이동 → 페이지 하단 **Assets** 항목에서 `KoreanPatch_OutworldStation_v1.0.5.exe` 다운로드.
   (또는 항상 최신 버전으로 가려면 [/releases/latest](https://github.com/tj-nexthop/outworld-station-kr/releases/latest))
3. 더블클릭 → 설치.
4. Steam에서 게임 실행 → 한국어로 표시됩니다.

설치 후 Steam이 게임을 업데이트해서 한국어가 영어로 돌아간다면, 같은 .exe를 다시 실행하면 복구됩니다.

### "이 파일은 위험합니다" / SmartScreen 경고가 뜬다면

코드 서명 인증서가 없는 모든 인디 .exe에 동일하게 뜨는 경고입니다 (사기 아님, 작동 무관).

**다운로드 시** 브라우저에서 차단되면:
- Chrome/Edge: 다운로드 항목 옆 [⋯] → **"보관(Keep)"** 클릭

**실행 시** "Windows에서 PC를 보호했습니다" 창이 뜨면:
- **"추가 정보(More info)"** 클릭 → 나타나는 **"실행(Run anyway)"** 버튼 클릭

> 정식 코드 서명 인증서는 연 $100 이상이라 취미 프로젝트에는 적용하지 않았습니다. 다운로드 수가 누적되면 SmartScreen이 자동으로 신뢰하게 되어 경고가 사라집니다.

### 삭제 방법 (Uninstall)

1. **Windows 시작 메뉴 → 설정 → 앱 → 설치된 앱**
   (또는 **제어판 → 프로그램 → 프로그램 및 기능**)
2. 목록에서 **"Outworld Station Korean Patch"** 검색.
3. 우측 [⋯] 또는 [제거] → 제거 확인.
4. 게임은 자동으로 영어로 돌아옵니다 (Steam 게임 본체는 영향 없음).

> ⚠️ `~mods` 폴더를 직접 삭제하지 마세요. 위 방법으로 제거해야 정크션·백업 파일이 깨끗이 정리됩니다.

## 빌드 (개발자용)

### 요구 환경
- Windows 10/11 x64
- Python 3.10+
- .NET 8 데스크톱 + 런타임 (`C:\Users\<you>\dotnet8`에 설치 가정)
- 외부 도구 (`tools/` 폴더에 배치):
  - [UAssetGUI](https://github.com/atenfyr/UAssetGUI) — `.uasset` ↔ JSON
  - [retoc](https://github.com/trumank/retoc) — IoStore Zen ↔ Legacy
  - [repak](https://github.com/trumank/repak) — `.pak` v11
  - [Inno Setup 6](https://jrsoftware.org/isdl.php) — `ISCC.exe` (인스톨러)
- 폰트 (`fonts/` 폴더에 배치) — 자세한 다운로드 경로는 [`fonts/README.md`](fonts/README.md):
  - [Pretendard-Variable.ttf](https://github.com/orioncactus/pretendard/releases/latest)
  - [NotoSansKR-Regular.ttf](https://fonts.google.com/noto/specimen/Noto+Sans+KR)

### 한 줄 빌드
```powershell
scripts\build.ps1 -Init        # 최초 1회: 게임에서 에셋 추출 + manifest 생성
scripts\build.ps1 -Installer   # 번역 적용 → 모드 패키징 → .exe 빌드까지
```

### 파이프라인 흐름
```
TR dict (build_ko_po.py)
    ↓ build_ko_po.py
ko.po
    ↓ apply.py            # DataTable / Widget RawExport byte-stitching
work/dt_json_ko/
    ↓ UAssetGUI fromjson
source/.../*.uasset+.uexp
    ↓ retoc to-zen
mod/KoreanPatch_P.{utoc,ucas,pak}

ko.po + LOCRES_EXTRA
    ↓ build_ko_locres.py    # FText 로컬라이제이션
work/ko_pak_root/.../ko/Game.locres + Game.locmeta
    ↓ repak pack
mod/KoreanPatch_LocRes_P.pak

font_pak/
    ↓ repak pack
mod/KoreanPatch_Fonts_P.pak

mod/* + installer/setup.iss
    ↓ ISCC
installer/KoreanPatch_OutworldStation_vX.Y.Z.exe
```

## 기술적 발견

이 프로젝트에서 마주한 어려웟던 UE5 IoStore 모딩 이슈들:

- **BP bytecode parity invariant** — `EX_StringConst`(0x1F) → `EX_UnicodeStringConst`(0x34) 인코딩 변환은 ASCII 길이가 홀수일 때만 byte-size 보존 가능. (제일 큰 함정: `0x33`은 `EX_PropertyConst`이고 `0x34`가 `EX_UnicodeStringConst`)
- **FText vs FString**: `EX_TextConst[0x29] LocalizedText[0x01]` 패턴은 `.locres` lookup 가능. 게임에 `ko/Game.locres` + `Game.locmeta`만 추가하면 BP 패치 없이 모든 FText 한국어화. parity 문제 없음.
- **Localization meta format** — UE5 .locres v3 포맷 (Optimized_CityHash64_UTF16): 매직 GUID `0E147475 674A03FC 4A15909D C3377F1B`, v3+는 entries count u32가 namespace count 앞에 추가됨.

자세한 내용은 `scripts/locres.py` 헤더 주석 참고.

## 라이선스

- **빌드 스크립트, 인스톨러, 문서**: MIT
- **번역 텍스트** (`translation/ko.po`, `translation/glossary.csv`): CC-BY 4.0
- **사용된 폰트** (본 레포에 미포함, 빌드 시 별도 다운로드 — [`fonts/README.md`](fonts/README.md) 참고):
  - Pretendard: SIL Open Font License 1.1
  - Noto Sans KR: SIL Open Font License 1.1

게임 본체 자산은 본 레포에 포함되지 않으며, 사용자가 합법적으로 소유한 Steam 사본에서 빌드 시 추출됩니다.

---

## ⚠️ 면책 조항 (Disclaimer)

본 프로젝트는 **팬이 만든 비공식 한글 패치**이며, **Outworld Station** 및 그
개발/배급사인 **Trickjump Games Ltd**와 어떠한 관련도 없고 공식적으로
승인되지 않았습니다.

- 본 레포지토리에는 게임의 저작권 자산(텍스트, 이미지, 코드 등)이 포함되어
  있지 않습니다. 본 패치는 사용자가 합법적으로 소유한 Steam 사본 위에서만
  동작하며, 게임 본체를 재배포하지 않습니다.
- 패치는 **무료, 비상업적**으로 배포됩니다.
- 사용으로 인한 모든 결과(저장 게임 손상, 게임 충돌 등)는 사용자 본인의
  책임입니다.
- "Outworld Station" 및 관련 상표/저작권은 Trickjump Games Ltd의 소유입니다.
- Trickjump Games Ltd 또는 권리자가 본 패치의 배포 중단을 요청하는 경우,
  본 레포지토리와 모든 배포물을 즉시 제거합니다. 연락은 GitHub Issues로 부탁드립니다.

*This is an unofficial fan-made Korean translation patch, not affiliated with
or endorsed by Trickjump Games Ltd. No copyrighted game assets are
redistributed. Will be taken down upon request from rights holders.*
