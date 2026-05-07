"""
Generates translation/ko.po from a single English->Korean dict.
Reads manifest.json and emits one PO entry per translatable string we have a mapping for.

This is the Phase 7 'bulk' generator: same English string is mapped once and applied
everywhere it appears (across all DataTables). Strings without a mapping are skipped
(they remain English in-game until added).

Run:  python scripts/build_ko_po.py
Then: scripts\build.ps1
"""
from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "translation" / "manifest.json"
KOPO     = ROOT / "translation" / "ko.po"

# DataTables / assets we never translate (engine identifiers / version tags / enum keys)
SKIP_FILES = {
    "DT_Languages", "DT_ReleaseNotes",
    # MainMenu enums and pure-code BPs — these strings are internal identifiers
    "E_MainMenu_Page", "E_MainMenu_Settings_Page", "E_SessionType",
    "BP_GameMode_MainMenu", "BP_GameState_MainMenu", "BP_PlayerController_MainMenu",
    # Developer menu — internal-only, never shipped to players
    "UI_DeveloperMenu",
    # Base BP_Module — string is interface declaration, not user-facing
    "BP_Module",
}

# Tutorial video filename references — game uses these as lookup keys, do not touch
SKIP_TEXT_RE = [
    re.compile(r"^\d+_[A-Z_]+$"),                 # 02_ARTIFACT_SCANNING etc.
    re.compile(r"^Num[A-Z][A-Za-z]+$"),           # NumAntimatterReactors etc — BP variables
    re.compile(r"^\(\(Interface="),               # ((Interface= class declarations
    re.compile(r"^\./Movies/.+\.mp4$"),           # ./Movies/MV_Tutorial_*.mp4
    re.compile(r"^F[A-Z][A-Za-z]+$"),             # FShaderResource etc — UE C++ class names
    re.compile(r"^TBasePass[A-Za-z]+$"),
    re.compile(r"^TSlateMaterial[A-Za-z]+$"),
]

# Profanity filter words — game uses these for chat filtering. Do not touch.
PROFANITY = {"fuck","shit","cunt","nigger","twat","nazi","pedo","gay","lesbian",
             "nigga","dick","pussy"}

# Boolean / engine sentinel values that appear inside DataTables but aren't UI text
SKIP_VALUES = {"False", "True"}

# ---------------------------------------------------------------- TRANSLATIONS
# All mappings live here. Same source -> same target everywhere.
TR: dict[str, str] = {

    # ---- DT_Build_Categories ----
    "General": "일반",
    "Resources": "자원",
    "Production": "생산",
    "Power": "동력",
    "Transport": "운송",
    "Defence": "방어",
    "Science": "과학",

    # ---- DT_ArkshipTerminalStages ----
    "Terminal": "터미널",
    "Dock": "도크",
    "Arkship": "방주선",
    "Fuel": "연료",

    # ---- DT_DroneEquipment + drone-prefixed in Materials/TechUpgrades ----
    "Afterburner": "애프터버너",
    "Jet Booster that dramatically increases your drone's speed for a short time":
        "드론 속도를 짧은 시간 동안 크게 증가시키는 제트 부스터",
    "Missile Launcher": "미사일 발사기",
    "Launches explosive rockets that can home in on a target":
        "목표를 추적하는 폭발성 로켓을 발사합니다",
    "Neutron Lazer": "중성자 레이저",
    "Powerful beam lazer than can destroy enemies and incoming meteors":
        "적과 다가오는 운석을 파괴할 수 있는 강력한 빔 레이저",
    "Sensors": "센서",
    "Scans the local area for items, resources and threats":
        "주변 지역에서 아이템, 자원, 위협을 탐지합니다",
    "Radiation Filter": "방사선 필터",
    "Consumable that protects your drone from radioactive damage for a limited time":
        "제한된 시간 동안 드론을 방사능 피해로부터 보호하는 소모품",
    "Nano Repair": "나노 수리",
    "Single-use consumable that instantly restores Drone hitpoints":
        "드론의 체력을 즉시 회복시키는 일회용 소모품",
    "Energy Shield": "에너지 방어막",
    "Absorbs a certain amount of incoming damage and regenerates over time":
        "받는 피해를 일정량 흡수하며 시간이 지나면 재생됩니다",
    "Generates a <Bold>shield</> around your drone which <Bold>absorbs damage</> and <Bold>recharges</> over time":
        "드론 주변에 <Bold>방어막</>을 생성하여 <Bold>피해를 흡수</>하고 시간이 지나면 <Bold>재충전</>됩니다",
    "Micro Drone": "마이크로 드론",
    "Deploys a defence micro-drone that can shoot down incoming projectiles":
        "다가오는 발사체를 격추할 수 있는 방어용 마이크로 드론을 전개합니다",
    "Antimatter Lazer": "반물질 레이저",
    "Advanced and extremely powerful energy beam than can destroy enemies and meteors":
        "적과 운석을 파괴할 수 있는 고도로 강력한 에너지 빔",

    # ---- DT_LoadingScreenTips ----
    "You can hide the upper level of your station by holding <ACTION=HideUpperLevel_B> or <ACTION=HideUpperLevel_B_Alt>":
        "<ACTION=HideUpperLevel_B> 또는 <ACTION=HideUpperLevel_B_Alt>를 누르고 있으면 스테이션 상층부를 숨길 수 있습니다",
    "You can collect multiple asteroids easily by holding <Bold>SHIFT</> and dragging with <Bold>LMB</>":
        "<Bold>SHIFT</>를 누른 채 <Bold>좌클릭</>으로 드래그하면 여러 소행성을 한 번에 수집할 수 있습니다",
    "Use the <Bold>Sensor View</> to locate nearby resources or enemies by holding <ACTION=Sensors> or <ACTION=Sensors ALT>":
        "<ACTION=Sensors> 또는 <ACTION=Sensors ALT>를 누르고 있으면 <Bold>센서 뷰</>로 주변 자원이나 적을 찾을 수 있습니다",
    "Pressing <ACTION=Stop> while in <Bold>Connect Mode</> will clear all connections from the selected module":
        "<Bold>연결 모드</>에서 <ACTION=Stop>을 누르면 선택한 모듈의 모든 연결이 해제됩니다",
    "You can move items from a hovered object into your drone's inventory using <ACTION=Transfer_To_Drone>":
        "<ACTION=Transfer_To_Drone>로 마우스를 올린 오브젝트의 아이템을 드론 인벤토리로 옮길 수 있습니다",
    "You can teleport back to the Hub at any time by holding <ACTION=Home>":
        "<ACTION=Home>을 누르고 있으면 언제든 허브로 순간이동 할 수 있습니다",
    "Use the <ACTION=Transfer_From_Drone> and <ACTION=Transfer_To_Drone> hotkeys to quickly move items to and from your drone and the currently hovered or selected object":
        "<ACTION=Transfer_From_Drone>와 <ACTION=Transfer_To_Drone> 단축키로 드론과 마우스를 올리거나 선택한 오브젝트 사이에서 아이템을 빠르게 옮길 수 있습니다",
    "The <Bold>Station Overview</> lets you quickly see how your station is performing (Hold <ACTION=Show Status>)":
        "<Bold>스테이션 개요</>(<ACTION=Show Status> 길게 누름)에서 스테이션 상태를 빠르게 확인할 수 있습니다",
    "Quickly switch hovered or selected modules on and off using <ACTION=Toggle Power>":
        "<ACTION=Toggle Power>로 마우스를 올리거나 선택한 모듈의 전원을 빠르게 켜고 끌 수 있습니다",
    "Add a waypoint using <ACTION=Create Waypoint> while in the <Bold>Map View</>":
        "<Bold>지도 뷰</>에서 <ACTION=Create Waypoint>로 경유점을 추가할 수 있습니다",
    "Rotate the currently placing module using <ACTION=Rotate Left>":
        "<ACTION=Rotate Left>로 배치 중인 모듈을 회전시킬 수 있습니다",
    "The <Bold>Codex</> contains a lot of useful information including all previously seen tutorial videos":
        "<Bold>코덱스</>에는 이전에 본 튜토리얼 영상을 포함한 다양한 유용한 정보가 담겨 있습니다",
    "Most recipes can be <Bold>synthesized</> directly from your drone's inventory (hotkey: <ACTION=Inventory>)":
        "대부분의 제작법은 드론 인벤토리(<ACTION=Inventory>)에서 직접 <Bold>합성</>할 수 있습니다",
    "You can create a custom task by clicking the '+' button on the main toolbar":
        "메인 툴바의 '+' 버튼을 눌러 사용자 지정 작업을 만들 수 있습니다",
    "You can align multiple <Bold>solar generators</> by using <Bold>Shift + LMB</>":
        "<Bold>Shift + 좌클릭</>으로 여러 <Bold>태양광 발전기</>를 정렬할 수 있습니다",

    # ---- DT_Credits (labels only — names stay) ----
    "LOCALISATION VOLUNTEERS": "현지화 자원봉사자",
    "GERMAN": "독일어",
    "RUSSIAN": "러시아어",
    "FRENCH": "프랑스어",
    "POLISH": "폴란드어",
    "SPANISH": "스페인어",
    "VIETNAMESE": "베트남어",
    "THAI": "태국어",
    "PORTUGUESE (BRAZIL)": "포르투갈어 (브라질)",
    "CHINESE": "중국어",
    "TURKISH": "터키어",

    # ---- DT_Cutscenes ----
    "Intro": "인트로",
    "Our galaxy is <Red>doomed</>": "우리 은하는 <Red>운명을 다했다</>",
    "Destined to be <Red>consumed</>\nby the insatiable appetite":
        "탐욕스러운 식욕에\n<Red>삼켜질 운명</>이다",
    "Of the <Red>monster</>\nthat lies at its centre...":
        "그 중심에 도사린\n<Red>괴물</>의 식욕에...",
    "<Red_Large>The Void</>": "<Red_Large>공허</>",
    "Our only hope:\nTo build a <Yellow>vessel</> capable of leaving this galaxy":
        "우리의 유일한 희망:\n이 은하를 떠날 수 있는 <Yellow>함선</>을 건조하는 것",
    "BUT WE'VE RUN OUT OF TIME": "하지만 시간이 다 됐다",
    "The Void has reached <Yellow>Terra System</>\nand soon our home will be destroyed":
        "공허가 <Yellow>테라 성계</>에 도달했고\n곧 우리 고향은 파괴될 것이다",
    "So we've mined all our remaining resources":
        "그래서 남은 자원을 모두 채굴했고",
    "to construct <Yellow>The Gate</>": "<Yellow>게이트</>를 건설했다",
    "A <Yellow>stargate</> that can take us\nto the edge of the Galaxy":
        "은하 끝자락으로 우리를 데려갈\n<Yellow>스타게이트</>",
    "There we can hide - and build": "그곳에서 숨고 — 다시 건설할 수 있다",
    "And hopefully escape <Red>The Void</> forever":
        "그리고 <Red>공허</>로부터 영원히 탈출할 수 있기를",
    "Arkship... Launching...": "방주선... 발진...",
    "Hyperdrive... Initialised...": "하이퍼드라이브... 초기화...",
    "Dock is clear...": "도크 이상 없음...",
    "We are away...": "출발...",
    "Entering Void Event Horizon in 3...": "공허 사건 지평선 진입까지 3...",
    "Entering Void...": "공허 진입...",
    "Destination... Andromeda Galaxy... Locked...": "목적지... 안드로메다 은하... 설정 완료...",
    "Hyperdrive Engaging...": "하이퍼드라이브 작동...",

    # ---- DT_StationLevel ----
    "<Bold>Matter Printers</> can convert raw materials into more complex items ready to be used in further production chains.\n\nUse the <Bold>connect</> function to automatically feed the output of your <Bold>smelters</> into matter printers to speed up production.":
        "<Bold>물질 프린터</>는 원자재를 더 복잡한 아이템으로 변환하여 다음 생산 단계에서 사용할 수 있게 합니다.\n\n<Bold>제련소</>의 산출물을 물질 프린터로 자동 공급하려면 <Bold>연결</> 기능을 사용해 생산을 가속하세요.",
    "The <Bold>Artifact Analyzer</> is now available.\n\nFeed any <Bold>Alien Artifacts</> you may find into this unit to unlock important new technologies and upgrades.":
        "<Bold>유물 분석기</>를 사용할 수 있습니다.\n\n발견한 <Bold>외계 유물</>을 이 장치에 투입하여 새로운 기술과 업그레이드를 잠금 해제하세요.",
    "You can now construct <Bold>Fabricators</> in order to produce more complex items and simple starship parts.":
        "이제 <Bold>가공기</>를 건설하여 더 복잡한 아이템과 단순한 우주선 부품을 생산할 수 있습니다.",
    "<Bold>Energy Storage</> modules will store excess energy produced by your station ready to restore energy if you lose power.":
        "<Bold>에너지 저장소</> 모듈은 스테이션이 생산한 잉여 에너지를 저장하여 정전 시 에너지를 복구할 수 있게 합니다.",
    "You can now automate raw material extraction by constructing <Bold>Miners</> onto <Bold>Ore Nodes</> located on some larger asteroids.\n\nMiners have <Bold>connection points</> which can be <Bold>built on</> to create mining sub-stations that serve your main station.":
        "이제 더 큰 소행성에 위치한 <Bold>광맥</>에 <Bold>채굴기</>를 건설하여 원자재 추출을 자동화할 수 있습니다.\n\n채굴기에는 <Bold>연결점</>이 있어 그 위에 <Bold>건설</>하여 메인 스테이션을 보조하는 채굴 서브 스테이션을 만들 수 있습니다.",
    "The <Bold>Small Shipyard</> has now been unlocked.\n\nSmaller starships can be constructed here to satisfy orders for <Bold>starships</>.":
        "<Bold>소형 조선소</>가 잠금 해제되었습니다.\n\n여기서 작은 우주선을 건조하여 <Bold>우주선</> 주문을 처리할 수 있습니다.",
    "Construct <Bold>Freighter Docks</> to connect remote parts of your station such as miners and further automate resource processing.\n\n<Bold>Freighters</> can be built from any freighter dock and can then be ordered to pick up and drop off from any docks in the current zone.":
        "<Bold>화물선 도크</>를 건설하여 채굴기 같은 원격 스테이션 부품을 연결하고 자원 처리를 더욱 자동화하세요.\n\n<Bold>화물선</>은 어떤 화물선 도크에서든 건조할 수 있으며, 현재 구역의 어떤 도크에서든 픽업 및 배달 명령을 내릴 수 있습니다.",
    "<Bold>Defence Turrets</> can be constructed around your station (and remote sub-stations) to automatically defend from incoming <Bold>meteors</>, <Bold>enemy drones</> and <Bold>creatures</>.":
        "<Bold>방어 포탑</>을 스테이션(및 원격 서브 스테이션) 주변에 건설하여 다가오는 <Bold>운석</>, <Bold>적 드론</>, <Bold>생명체</>로부터 자동으로 방어하세요.",
    "You now have access to <Bold>Hydrogen production</> which is used in fusion reactors and starship fuel.\n\n<Bold>Refineries</> can convert <Bold>water</> from <Bold>ice asteroids</> into <Bold>hydrogen gas</>, which can then be piped around your station and either stored or used in <Bold>Fusion Reactors</> to produce large amounts of power.":
        "이제 <Bold>수소 생산</>이 가능합니다. 융합로와 우주선 연료에 사용됩니다.\n\n<Bold>정제소</>는 <Bold>얼음 소행성</>의 <Bold>물</>을 <Bold>수소 가스</>로 변환할 수 있으며, 이를 스테이션 곳곳으로 파이프 운반하여 저장하거나 <Bold>융합로</>에서 대량의 전력을 생산할 수 있습니다.",
    "<Bold>Power Linkers</> can be built to link the power grids of remote parts of your station - such as Miners - to your main station and centralize power generation.":
        "<Bold>전력 연결기</>를 건설하여 채굴기 같은 원격 스테이션 부품의 전력망을 메인 스테이션과 연결해 전력 생산을 중앙화할 수 있습니다.",
    "Additional <Bold>locations</> are now available to you to found new stations at. These can be accessed from the <Bold>System Map</>.\n\nMore locations will become available as your station grows, allowing access to new resource types.":
        "이제 새로운 스테이션을 설립할 수 있는 추가 <Bold>장소</>가 열렸습니다. <Bold>시스템 맵</>에서 접근할 수 있습니다.\n\n스테이션이 성장함에 따라 더 많은 장소가 열려 새로운 자원 유형에 접근할 수 있게 됩니다.",
    "Stations in other locations can be connected together via <Bold>Womhole Terminus</>, which allows movement of items, parts and volatiles between zones to be automated.":
        "다른 장소의 스테이션은 <Bold>웜홀 터미너스</>로 연결되어 구역 간 아이템, 부품, 휘발성 물질의 이동을 자동화할 수 있습니다.",
    "You may now receive orders for starships that have been <Fuelled>Fuelled</>.\n\nYou can <Fuelled>fuel</> a starship by dragging it into a <Bold>Fuel Depot</> that has been supplied with <Bold>Hydrogen Gas</>.":
        "이제 <Fuelled>연료가 주입된</> 우주선의 주문을 받을 수 있습니다.\n\n<Bold>수소 가스</>가 공급된 <Bold>연료 저장고</>에 우주선을 끌어 넣어 <Fuelled>연료를 주입</>할 수 있습니다.",
    "<Bold>Tug Bays</> will automatically move starships between station modules - such as from a <Bold>Shipyard</> into a <Bold>Fuel Depot</> - or into a <Bold>clear space</> next to your station ready to be shipped.\n\nUse the <Bold>Connect</> function to assign a Shipyard to a Fuel Depot or a space near your station and the nearest free tug will automatically be assigned.":
        "<Bold>예인선 도크</>는 스테이션 모듈 사이에서 우주선을 자동으로 이동시킵니다. 예를 들어 <Bold>조선소</>에서 <Bold>연료 저장고</>로, 또는 출하 준비된 스테이션 옆 <Bold>빈 공간</>으로 이동시킵니다.\n\n<Bold>연결</> 기능으로 조선소를 연료 저장고나 스테이션 근처 공간에 할당하면 가장 가까운 사용 가능한 예인선이 자동 배정됩니다.",
    "<Bold>Cloud Mining Stations</> let you deploy <Bold>Cloud Miners</> into the atmosphere of a gas giant and automate the collection of large amounts of hydrogen gas.\n\nConstruct <Bold>Vortex generators</> inside the atmosphere of <Bold>Gas giants</> to produce large amounts of power at very little cost.":
        "<Bold>구름 채굴 스테이션</>은 <Bold>구름 채굴기</>를 가스 거성의 대기 중에 배치하여 대량의 수소 가스 수집을 자동화합니다.\n\n<Bold>가스 거성</>의 대기 안에 <Bold>볼텍스 발전기</>를 건설하면 매우 적은 비용으로 대량의 전력을 생산할 수 있습니다.",
    "You can now synthesize the highly explosive bio-compound <Bold>Nitrox</>, which can be produced by refining the <Bold>Nitratium</> recovered from gas-giant flora and fauna and combining it in a <Bold>Refinery</> with <Bold>Oxygen</> extracted from <Bold>Water</>.":
        "이제 강력한 폭발성 생물 화합물 <Bold>나이트록스</>를 합성할 수 있습니다. 가스 거성의 동식물에서 회수한 <Bold>니트라튬</>을 정제하고 <Bold>물</>에서 추출한 <Bold>산소</>와 <Bold>정제소</>에서 결합하여 생산할 수 있습니다.",
    "Additional mining locations are now available, which give access to new resources - such as the rare metal <Bold>Tungsten</> which is used to create <Bold>Superalloy</>.":
        "추가 채굴 장소가 열렸으며, <Bold>초합금</> 제작에 사용되는 희귀 금속 <Bold>텅스텐</> 같은 새로운 자원에 접근할 수 있습니다.",
    "The <Bold>Plasma Forge</> has now been unlocked. Use this to combine elements together to form advanced <Bold>alloys</>.":
        "<Bold>플라즈마 용광로</>가 잠금 해제되었습니다. 이를 사용하여 원소를 결합해 고급 <Bold>합금</>을 제작하세요.",
    "The <Bold>Bio Extractor</> can be used to automate the extraction of <Bold>Nitratium</> from large gas-giant flora in order to automate large-scale <Bold>Nitrox</> production.":
        "<Bold>바이오 추출기</>를 사용하여 가스 거성의 거대 식물에서 <Bold>니트라튬</> 추출을 자동화하고, 대규모 <Bold>나이트록스</> 생산을 자동화할 수 있습니다.",
    "<Bold>Manufactories</> can now be constructed, allowing the most complex parts to be assembled.":
        "<Bold>제조소</>를 건설하여 가장 복잡한 부품을 조립할 수 있습니다.",
    "<Bold>Medium Shipyards</> are now available for you to fulfil ever-larger and more complex starship orders.\n\nNote: Larger ships may require <Bold>Micro Fusion Reactors</> to be installed. These ships must be fuelled quickly after completion to avoid catasptrophic reactor meltdown.":
        "<Bold>중형 조선소</>를 사용할 수 있어 점점 더 크고 복잡한 우주선 주문을 처리할 수 있습니다.\n\n참고: 더 큰 우주선은 <Bold>마이크로 융합로</>를 설치해야 할 수 있습니다. 이러한 우주선은 완성 후 빠르게 연료를 주입해야 원자로 멜트다운을 방지할 수 있습니다.",
    "The <Bold>Glacialis Ice Ring</> is the ideal location to automate the mining of larger <Bold>Ice Asteroids</> used in <Bold>Oxygen</> production.":
        "<Bold>글라시알리스 얼음 고리</>는 <Bold>산소</> 생산에 사용되는 더 큰 <Bold>얼음 소행성</> 채굴을 자동화하기에 이상적인 장소입니다.",
    "We also recommend building enhanced <Bold>Missile Defence Turrets</> on your most vulnerable stations to safely defend against larger groups of enemies.":
        "또한 가장 취약한 스테이션에 강화된 <Bold>미사일 방어 포탑</>을 건설하여 더 큰 적 무리로부터 안전하게 방어할 것을 권장합니다.",
    "You may now receive orders for <Armed>Military Starships</> which need to be supplied with <Armed>ammunition</>.\n\n<Armed>Ship Ammo</> is produced in the <Bold>Ammo Factory</> and loaded into a ship from the <Bold>Ammo Depot</>.":
        "이제 <Armed>탄약</>을 공급받아야 하는 <Armed>군용 우주선</> 주문을 받을 수 있습니다.\n\n<Armed>함선 탄약</>은 <Bold>탄약 공장</>에서 생산되며 <Bold>탄약 저장고</>에서 함선에 장전됩니다.",
    "The <Bold>Junkyard</> zone has been unlocked. \n\nThis is a very dangerous sector of space swept by frequent firestorms, so you may want to construct <Bold>Force-Field Generators</> to protect your stations in this area.":
        "<Bold>고철장</> 구역이 잠금 해제되었습니다. \n\n이곳은 잦은 화염 폭풍이 휩쓸고 지나가는 매우 위험한 우주 구역이므로, 이 지역의 스테이션을 보호하기 위해 <Bold>역장 발생기</>를 건설하는 것이 좋습니다.",
    "You now have access to <Bold>antimatter</> production - an incredibly powerful force which can be used to generate huge amounts of energy - or to create weapons of mass destruction.\n\nAntimatter is extremely unstable and must be stored in a powered <Bold>Containment Chamber</> - or it will <bold>explode</> after a short time.":
        "이제 <Bold>반물질</> 생산이 가능합니다 — 막대한 에너지를 생성하거나 대량 살상 무기를 만들 수 있는 엄청나게 강력한 힘입니다.\n\n반물질은 극도로 불안정하므로 전원이 공급되는 <Bold>격납 체임버</>에 보관해야 합니다 — 그렇지 않으면 짧은 시간 후 <bold>폭발</>합니다.",
    "Antimatter is generated inside the <Bold>Particle Accelerator</>. This is formed from a <Bold>Control Centre</> and a ring of <Bold>Conduit</> running through one or more <Bold>Towers</>.\n\nThe <Bold>larger</> the particle accelerator loop you build, the <Bold>faster</> you can generate antimatter - but the <Bold>more power</> is required.":
        "반물질은 <Bold>입자 가속기</> 안에서 생성됩니다. 이는 <Bold>제어 센터</>와 하나 이상의 <Bold>타워</>를 통과하는 <Bold>도관</> 고리로 구성됩니다.\n\n입자 가속기 루프를 <Bold>크게</> 건설할수록 반물질을 <Bold>더 빠르게</> 생성할 수 있지만 <Bold>더 많은 전력</>이 필요합니다.",
    "The <Bold>Servitor Station</> deploys a helpful <Bold>AI-powered robot</> that can be set to automatically perform tasks around your station such as <Bold>repairing damaged modules</>, aligning <Bold>solar panels</> and <Bold>collecting resources</> when <Bold>linked</> to a suitable destination module.":
        "<Bold>서비터 스테이션</>은 유용한 <Bold>AI 로봇</>을 배치하며, 적절한 대상 모듈에 <Bold>연결</>하면 <Bold>손상된 모듈 수리</>, <Bold>태양광 패널</> 정렬, <Bold>자원 수집</> 같은 작업을 스테이션 주변에서 자동으로 수행하도록 설정할 수 있습니다.",

    # ---- DT_Materials (155) ----
    "Titanium": "티타늄",
    "Light and strong general-purpose building material used in station and starship construction":
        "스테이션과 우주선 건조에 쓰이는 가볍고 튼튼한 범용 건축재",
    "Composite": "복합재",
    "Flexible carbon nano-material which can be used as a basis for many other materials":
        "다양한 재료의 기반이 되는 유연한 탄소 나노 소재",
    "Gold": "금",
    "Rare metal used in all forms of electronics and circuitry":
        "모든 종류의 전자 회로에 쓰이는 희귀 금속",
    "Titanium Ore": "티타늄 광석",
    "Raw ore that can be smelted into titanium metal used in construction":
        "제련하여 건설용 티타늄 금속으로 만들 수 있는 원광석",
    "Gold Ore": "금 광석",
    "Raw ore that can be smelted into usable metal":
        "제련하여 사용 가능한 금속으로 만들 수 있는 원광석",
    "Silica": "규소",
    "Raw material used to produce glass-fibre and other materials":
        "유리섬유 및 기타 재료 생산에 쓰이는 원자재",
    "Computers": "컴퓨터",
    "Quantum-based computing matrix used for advanced station modules and starships":
        "고급 스테이션 모듈과 우주선에 쓰이는 양자 기반 컴퓨팅 매트릭스",
    "Hull Plating": "선체 장갑",
    "General-purpose outer-hull plates used in both station modules and starship construction":
        "스테이션 모듈과 우주선 건조 모두에 쓰이는 범용 외부 장갑판",
    "Reinforced Frames": "강화 프레임",
    "Ultra-high-tensile framework used in more advanced construction projects and starships":
        "고급 건설 프로젝트와 우주선에 쓰이는 초고강도 골조",
    "Circuit Boards": "회로 기판",
    "Basic nano-wafer circuitry used to build advanced computational matrixes":
        "고급 연산 매트릭스를 구성하는 데 쓰이는 기본 나노 웨이퍼 회로",
    "Carbon Ore": "탄소 광석",
    "Carbon-based ore that can be smelted into stable carbon compounds":
        "제련하여 안정적인 탄소 화합물로 만들 수 있는 탄소 기반 광석",
    "Carbon": "탄소",
    "Carbon lattice material that can be further processed into useful composites":
        "유용한 복합재로 추가 가공할 수 있는 탄소 격자 소재",
    "Glass Fibre": "유리섬유",
    "Basic fibrous polymer material used to create more advanced products":
        "더 고급 제품을 만드는 데 쓰이는 기본 섬유성 폴리머 소재",
    "Fibre Optics": "광섬유",
    "High-capacity optical cabling used in computing and many other applications":
        "컴퓨터 및 여러 응용 분야에 쓰이는 고용량 광 케이블",
    "Small Engine": "소형 엔진",
    "Small but powerful booster engine used in simpler starship construction":
        "단순한 우주선 건조에 쓰이는 작지만 강력한 부스터 엔진",
    "Large Engine": "대형 엔진",
    "Extremely powerful engine used in the largest and most advanced starships":
        "최대형이자 가장 진보한 우주선에 쓰이는 극도로 강력한 엔진",
    "Small Fuel Tank": "소형 연료 탱크",
    "Small fuel tank generally fitted on simpler starships":
        "단순한 우주선에 주로 장착되는 소형 연료 탱크",
    "Small Cargo Pod": "소형 화물 포드",
    "Small cargo pod generally fitted on simpler starships":
        "단순한 우주선에 주로 장착되는 소형 화물 포드",
    "Water Ice": "얼음",
    "Impure water ice crystals that can be refined into pure water":
        "정제하여 순수한 물로 만들 수 있는 불순물 섞인 얼음 결정",
    "Hydrogen": "수소",
    "Base element used in fusion reactors and starship fuel":
        "융합로와 우주선 연료에 쓰이는 기본 원소",
    "Oxygen": "산소",
    "Reactive gaseous element used in explosive compounds":
        "폭발성 화합물에 쓰이는 반응성 기체 원소",
    "Nano Plating": "나노 장갑",
    "An advanced hull plating which is both incredibly strong and flexible when required":
        "매우 튼튼하면서도 필요시 유연한 고급 선체 장갑",
    "Basic Frames": "기본 프레임",
    "High-tensile framework used in more basic construction projects and simple starships":
        "기본 건설 프로젝트와 단순한 우주선에 쓰이는 고강도 골조",
    "Artificial Diamond": "인공 다이아몬드",
    "Crystalline matrix used in superconductors and high-tensile structures":
        "초전도체와 고강도 구조물에 쓰이는 결정 매트릭스",
    "Superconductor": "초전도체",
    "Ultra-high-capacity conductor used for advanced station modules and product manufacturing":
        "고급 스테이션 모듈과 제품 생산에 쓰이는 초고용량 도체",
    "Molecular Bonding": "분자 접착제",
    "This super-strong epoxy is used to bond many materials and products together":
        "다양한 재료와 제품을 단단히 접합하는 초강력 에폭시",
    "Nitratium": "니트라튬",
    "Bio-compound that can be harvested from gas-giant fauna and processed into explosives":
        "가스 거성 동식물에서 채취해 폭발물로 가공할 수 있는 생물 화합물",
    "Micro-Fusion Reactor": "마이크로 융합로",
    "Powerful mini reactor capable of powering larger starships":
        "더 큰 우주선에 동력을 공급할 수 있는 강력한 소형 원자로",
    "Supercomputer": "슈퍼컴퓨터",
    "AI-Powered advanced computing substrate": "AI 기반의 고급 컴퓨팅 기판",
    "Medium Engine": "중형 엔진",
    "Powerful engine used by larger starships": "더 큰 우주선이 사용하는 강력한 엔진",
    "Nitrox": "나이트록스",
    "Highly concentrated explosive used in weapons production":
        "무기 생산에 쓰이는 고농도 폭발물",
    "Carbon Nanotube": "탄소 나노튜브",
    "Ultra-strong carbon-based nano material used in pipes and cables":
        "파이프와 케이블에 쓰이는 초강력 탄소 기반 나노 소재",
    "Advanced Plating": "고급 장갑",
    "Ultra-high-tech plating used in starship and station module construction":
        "우주선과 스테이션 모듈 건조에 쓰이는 초첨단 장갑",
    "Heavy Frames": "중량 프레임",
    "Heavy high-tensile framework used in larger starships":
        "더 큰 우주선에 쓰이는 무거운 고강도 골조",
    "Exotic Matter": "이그조틱 물질",
    "Highly radioactive and unstable quasi-matter": "방사능이 매우 강하고 불안정한 준물질",
    "Warheads": "탄두",
    "Explosive module used in weapons production": "무기 생산에 쓰이는 폭발 모듈",
    "Light Missile Ammo": "경미사일 탄약",
    "General purpose missile used by military starships": "군용 우주선이 사용하는 범용 미사일",
    "Long-range missile launcher for military ships": "군용 우주선용 장거리 미사일 발사기",
    "Shield Generator": "방어막 발생기",
    "Protective forcefield generator for advanced starships": "고급 우주선용 보호 역장 발생기",
    "Antimatter": "반물질",
    "This pinnacle of our engineering technology can be used to generate incredible amounts of power... or destruction.":
        "우리 공학 기술의 정점. 막대한 에너지를 생성할 수 있고... 파괴 또한 가능합니다.",
    "Depleted Uranium": "열화 우라늄",
    "Incredibly hard nuclear byproduct used in the production of railgun slugs":
        "레일건 슬러그 생산에 쓰이는 매우 단단한 핵 부산물",
    "Nuclear Waste": "핵 폐기물",
    "Extremely radioactive nuclear by-product of certain products and reactions":
        "특정 제품과 반응에서 생성되는 강한 방사능 핵 부산물",
    "Railgun Ammo": "레일건 탄약",
    "Depleted uranium slugs fired at relativistic speeds from a ship-mounted railgun launcher":
        "함선 레일건에서 상대론적 속도로 발사되는 열화 우라늄 슬러그",
    "Railgun Turret": "레일건 포탑",
    "Fires depleted uranium slugs at near-relativistic speeds":
        "거의 상대론적 속도로 열화 우라늄 슬러그를 발사",
    "Nitronic Acid": "니트론산",
    "Highly corrosive substance used for scrubbing radioactive materials":
        "방사성 물질 세척에 쓰이는 강한 부식성 물질",
    "Pure Water": "순수한 물",
    "Pure water that can be converted into various gases": "다양한 기체로 변환할 수 있는 순수한 물",
    "Small Aero-Wing": "소형 공력 날개",
    "Super-strong aerodynamic wing that allows ships to manoeuvre in a planet's atmosphere":
        "행성 대기에서 함선이 기동할 수 있게 하는 초강력 공력 날개",
    "Small Scramjet": "소형 스크램제트",
    "Small but advanced engine which allows a spacecraft to function in space and in a planet's atmosphere":
        "우주와 행성 대기 모두에서 작동할 수 있는 작지만 첨단의 엔진",
    "Tungsten Ore": "텅스텐 광석",
    "Raw ore that can be smelted into tungsten metal":
        "제련하여 텅스텐 금속으로 만들 수 있는 원광석",
    "Tungsten": "텅스텐",
    "Dense metal that can be used to form alloys": "합금을 만들 수 있는 고밀도 금속",
    "Uranium Ore": "우라늄 광석",
    "Raw radioactive ore that can be refined into pure Uranium":
        "정제하여 순수 우라늄으로 만들 수 있는 방사성 원광석",
    "Uranium": "우라늄",
    "Highly radioactive metal used in the production of Antimatter":
        "반물질 생산에 쓰이는 강한 방사성 금속",
    "Superalloy": "초합금",
    "Incredibly tough alloy of titanium and tungsten": "티타늄과 텅스텐의 매우 강력한 합금",
    "Neutron Initiator": "중성자 점화기",
    "Radioactive consumable used in the Particle Accelerator to generate Antimatter":
        "입자 가속기에서 반물질을 생성하는 데 쓰이는 방사성 소모품",
    "Drone Afterburner": "드론 애프터버너",
    "AFTERBURNER": "애프터버너",
    "Drone Missile Launcher": "드론 미사일 발사기",
    "Drone Neutron Lazer": "드론 중성자 레이저",
    "Drone Energy Shield": "드론 에너지 방어막",
    "Drone Radiation Filter": "드론 방사선 필터",
    "Drone Nano Repair": "드론 나노 수리",
    "Drone Micro Drone": "드론 마이크로 드론",
    "Quantum Crystals": "양자 결정",
    "Exotic crystalline substrate used in quantum devices":
        "양자 장치에 쓰이는 이그조틱 결정 기판",
    "Quantum Computer": "양자 컴퓨터",
    "Incredibly powerful fuzzy-logic based computer": "매우 강력한 퍼지 논리 기반 컴퓨터",
    "Stargate Parts": "스타게이트 부품",
    "Essential stargate components": "필수 스타게이트 구성 요소",
    "Micro Antimatter Reactor": "마이크로 반물질 원자로",
    "Small but extremely powerful reactor used in the largest and most advanced starships.":
        "최대형이자 가장 진보한 우주선에 쓰이는 작지만 극도로 강력한 원자로.",
    "Arkship Dock Parts": "방주선 도크 부품",
    "Arkship Dock Part": "방주선 도크 부품",
    "Components to complete the Dock stage of the Arkship Terminal":
        "방주선 터미널의 도크 단계를 완성하는 구성 요소",
    "Science Module": "과학 모듈",
    "Advanced sensor array used by research vessels":
        "연구 함선이 사용하는 고급 센서 어레이",
    "Medium Fuel Tank": "중형 연료 탱크",
    "Medium fuel tank for larger starships": "더 큰 우주선용 중형 연료 탱크",
    "Small Probe": "소형 탐사기",
    "Disposable hypersonic probe used to collect scientific data":
        "과학 데이터 수집에 쓰이는 일회용 극초음속 탐사기",
    "Sensor Array": "센서 어레이",
    "Advanced sensor cluster that can detect quantum instabilities and other phenomena":
        "양자 불안정성과 기타 현상을 감지할 수 있는 고급 센서 클러스터",
    "Tungsten Carbide": "탄화 텅스텐",
    "Super dense alloy of tungsten and carbon used in high-pressure systems":
        "고압 시스템에 쓰이는 초고밀도 텅스텐-탄소 합금",
    "Armour Plating": "강화 장갑",
    "Damage-resistant plating designed to resist extreme environments and high pressure systems.":
        "극한 환경과 고압 시스템을 견디도록 설계된 피해 저항 장갑.",
    "Quantum Warheads": "양자 탄두",
    "Exotic matter-based warhead used in quantum ammunition":
        "양자 탄약에 쓰이는 이그조틱 물질 기반 탄두",
    "Quantum Implosion Ammo": "양자 내파 탄약",
    "Quantum Imploder Ammo": "양자 내파 탄약",
    "Exotic-matter based ammunition with the potential to destabilize quantum structures":
        "양자 구조를 불안정하게 만들 수 있는 이그조틱 물질 기반 탄약",
    "Quantum Destabilizer": "양자 안정화 파괴기",
    "Powerful weapon that can introduce instabilities in quantum structures such as singularities":
        "특이점 같은 양자 구조에 불안정성을 유발할 수 있는 강력한 무기",
    "Antimatter Fuel Tank": "반물질 연료 탱크",
    "Containment vessel for supplying large antimatter-fuelled starships":
        "대형 반물질 연료 우주선에 공급하기 위한 격납 용기",
    "Nano-Tube Cable": "나노튜브 케이블",
    "Incredibly strong carbon-nanotube-based cable used in mega-structures":
        "거대 구조물에 쓰이는 매우 강력한 탄소 나노튜브 기반 케이블",
    "Overdrive Core": "오버드라이브 코어",
    "Can be inserted into compatible factories to provide a large increase in efficiency":
        "호환 공장에 삽입하여 효율을 크게 향상시킬 수 있음",
    "Neutronium": "중성자물질",
    "Ultra-dense and highly radioactive stellar matter formed in black holes and the cores of stars.":
        "블랙홀과 항성 핵에서 형성되는 초고밀도 강방사성 항성 물질.",
    "Hyperdrive Fuel": "하이퍼드라이브 연료",
    "Neutronium-based fuel for intergalactic star-drives.":
        "은하 간 항성 추진 장치용 중성자물질 기반 연료.",
    "Drone Antimatter Lazer": "드론 반물질 레이저",

    # ---- DT_ProcessRecipes — extra short recipe names ----
    "Carbotanium": "카보타늄",
    "Pure Gold": "순금",
    "Nanonic Optics": "나노닉 광학",
    "Composite Hull Plate": "복합재 선체 장갑판",
    "Alloy Nano Plate": "합금 나노 판",
    "Composite Frames": "복합재 프레임",
    "Alloy Frames": "합금 프레임",
    "Etched Diamond": "에칭 다이아몬드",
    "Integrated Circuits": "집적 회로",
    "Small Alloy Engine": "소형 합금 엔진",
    "Small Alloy Fuel Tank": "소형 합금 연료 탱크",
    "Small Alloy Cargo Pod": "소형 합금 화물 포드",
    "Small Alloy Aero-Wing": "소형 합금 공력 날개",
    "Enriched Warheads": "농축 탄두",
    "Reclaimed Uranium": "회수 우라늄",

    # ---- DT_TechUpgrades + DT_TechUpgrades_OLD ----
    "Advanced Solar Cells": "고급 태양 전지",
    "High capacity solar power cells <Bold>increase energy</> generated from all <Bold>solar sources</>":
        "고용량 태양 전지가 모든 <Bold>태양 광원</>에서 생성되는 <Bold>에너지를 증가</>시킵니다",
    "<Bold><XXX>%</> extra solar power generated": "추가 태양 전력 생성 <Bold><XXX>%</>",
    "Shield Overcharge": "방어막 과충전",
    "Overcharges your energy shield allowing more incoming damage to be absorbed.":
        "에너지 방어막을 과충전하여 들어오는 피해를 더 많이 흡수할 수 있게 합니다.",
    "<Bold>+<XXX>%</> shield hitpoints": "방어막 체력 <Bold>+<XXX>%</>",
    "<Bold><XXX></> shield hitpoints": "방어막 체력 <Bold><XXX></>",
    "Heavy Thrusters": "강력 추진기",
    "Increases the <Bold>maximum weight</> your drone can <Bold>carry</>":
        "드론이 <Bold>운반</>할 수 있는 <Bold>최대 중량</>을 증가시킵니다",
    "Increases the <Bold>maximum weight</> your drone can <Bold>drag</>":
        "드론이 <Bold>견인</>할 수 있는 <Bold>최대 중량</>을 증가시킵니다",
    "<Bold>+<XXX>%</> max carry weight": "최대 운반 중량 <Bold>+<XXX>%</>",
    "Hardened Casing": "강화 외피",
    "Adds a layer of <Bold>ultra-hard diamond film</> to your drone's outer casement, increasing <Bold>overall survivability</>":
        "드론 외피에 <Bold>초경도 다이아몬드 필름</> 층을 추가하여 <Bold>전반적인 생존력</>을 향상시킵니다",
    "<Bold>+<XXX>%</> drone <Bold>hitpoints</>": "드론 <Bold>체력</> <Bold>+<XXX>%</>",
    "Expanded Storage": "확장 저장소",
    "Increases the available <Bold>inventory size</> of your drone, letting you <Bold>store more items</>":
        "드론의 <Bold>인벤토리 크기</>를 늘려 <Bold>더 많은 아이템을 보관</>할 수 있게 합니다",
    "<Bold>+<XXX></> inventory slots": "인벤토리 슬롯 <Bold>+<XXX></>",
    "Fuel Injection": "연료 분사",
    "Increases the top speed of your Drone when using the <Bold>Afterburner</>":
        "<Bold>애프터버너</> 사용 시 드론의 최고 속도를 증가시킵니다",
    "Adds an <Bold>Ion Booster</> to your drone, allowing you to cover <Bold>large distances</> more <Bold>quickly</>":
        "드론에 <Bold>이온 부스터</>를 추가하여 <Bold>먼 거리</>를 <Bold>더 빠르게</> 이동할 수 있게 합니다",
    "<Bold>+<XXX>%</> boost speed": "부스트 속도 <Bold>+<XXX>%</>",
    "Insulated Coating": "절연 코팅",
    "Adds an extra layer of <Bold>insulation</> under your drone's hull, dramatically <Bold>reducing electrical damage</> and stun time":
        "드론 선체 아래 추가 <Bold>절연</> 층을 더해 <Bold>전기 피해</>와 기절 시간을 크게 <Bold>감소</>시킵니다",
    "Adds an extra layer of <Bold>insulation</> under your drone's hull, dramatically <Bold>reducing electrical damage</>.":
        "드론 선체 아래 추가 <Bold>절연</> 층을 더해 <Bold>전기 피해</>를 크게 <Bold>감소</>시킵니다.",
    "<Bold><XXX>%</> less electrical damage and <Bold><YYY>%</> less stun time":
        "전기 피해 <Bold><XXX>%</> 감소, 기절 시간 <Bold><YYY>%</> 감소",
    "<Bold><XXX>%</> less damage from electrical sources":
        "전기 피해 <Bold><XXX>%</> 감소",
    "<Bold>-<XXX>%</> damage from electrical sources":
        "전기 피해 <Bold>-<XXX>%</>",
    "Focussed Lazer Optics": "집속 레이저 광학",
    "Increases the <Bold>power</> of your <Bold>Neutron Lazer</>, making it easier to destroy <Bold>enemy robots</>, aggressive <Bold>space fauna</> & <Bold>meteors</>":
        "<Bold>중성자 레이저</>의 <Bold>위력</>을 증가시켜 <Bold>적 로봇</>, 공격적인 <Bold>우주 생물</>, <Bold>운석</>을 더 쉽게 파괴할 수 있게 합니다",
    "<Bold>+<XXX>%</> lazer power": "레이저 위력 <Bold>+<XXX>%</>",
    "Defence Micro-Drone": "방어 마이크로 드론",
    "Deploys a <Bold>defensive drone</> that shoots down <Bold>incoming projectiles</>":
        "다가오는 <Bold>발사체</>를 격추하는 <Bold>방어용 드론</>을 전개합니다",
    "Deploys a <Bold>defensive drone</> that can shoot down <Bold>incoming projectiles</>":
        "다가오는 <Bold>발사체</>를 격추할 수 있는 <Bold>방어용 드론</>을 전개합니다",
    "Deploy <Bold><XXX></> drones that can fire once every <Bold><YYY></> seconds":
        "<Bold><YYY></>초마다 한 번 발사하는 드론 <Bold><XXX></>대 전개",
    "Missile Autoloader": "미사일 자동 장전기",
    "Decreases the reloading time between launches when you have the Missile Launcher equipped.":
        "미사일 발사기 장착 시 발사 간 재장전 시간을 감소시킵니다.",
    "Missiles reload <Bold><YYY>%</> faster": "미사일 재장전 속도 <Bold><YYY>%</> 향상",
    "Adds an unguided <Bold>missile launcher</> to your drone which fires <Bold>explosive projectiles</> that deal large amounts of damage to enemies":
        "드론에 무유도 <Bold>미사일 발사기</>를 추가하여 적에게 큰 피해를 주는 <Bold>폭발성 발사체</>를 발사합니다",
    "Launch <Bold><XXX></> missiles once every <Bold><YYY></> seconds":
        "<Bold><YYY></>초마다 미사일 <Bold><XXX></>발 발사",
    "Fusion Core": "융합 코어",
    "Increased <Bold>maximum energy</> reserves and energy <Bold>recharge speed</>":
        "<Bold>최대 에너지</> 비축량과 <Bold>충전 속도</> 증가",
    "<Bold>+<XXX>%</> energy storage and <Bold>+<YYY>%</> recharge speed":
        "에너지 저장 <Bold>+<XXX>%</>, 충전 속도 <Bold>+<YYY>%</>",
    "Curved Reflectors": "곡면 반사판",
    "Advanced optics <Bold>reduce power loss</> when mis-aligned, reducing the need to <Bold>manually align panels</>":
        "고급 광학이 정렬이 어긋났을 때 <Bold>전력 손실을 감소</>시켜 <Bold>수동 패널 정렬</> 필요성을 줄입니다",
    "<Bold><XXX>%</> less power reduction": "전력 손실 <Bold><XXX>%</> 감소",
    "Enhanced Atomizer": "강화 분해기",
    "AI control routines <Bold>reduce waste</> and <Bold>increase yield</> when feeding asteroids and other items into <Bold>Atomizers</>":
        "AI 제어 루틴이 <Bold>분해기</>에 소행성과 기타 아이템을 투입할 때 <Bold>낭비를 줄이고</> <Bold>산출량을 증가</>시킵니다",
    "<Bold>+<XXX>%</> yield from all atomizers": "모든 분해기 산출량 <Bold>+<XXX>%</>",
    "Enhanced Production": "강화 생산",
    "AI control routines increase the <Bold>production speed</> of all <Bold>factory</> modules":
        "AI 제어 루틴이 모든 <Bold>공장</> 모듈의 <Bold>생산 속도</>를 증가시킵니다",
    "<Bold>+<XXX>%</> production speed": "생산 속도 <Bold>+<XXX>%</>",
    "High-Speed Connectors": "고속 연결기",
    "Install <Bold>high-capacity connectors</> to <Bold>convey items</> around your station <Bold>faster</>":
        "<Bold>고용량 연결기</>를 설치하여 스테이션 곳곳으로 <Bold>아이템을 더 빠르게 운반</>합니다",
    "Items will move <Bold>+<XXX>%</> faster between station modules":
        "스테이션 모듈 간 아이템 이동 속도 <Bold>+<XXX>%</>",
    "Armoured Modules": "장갑 모듈",
    "A layer of <Bold>diamond-film</> composite increases the <Bold>hitpoints</> of all station modules":
        "<Bold>다이아몬드 필름</> 복합재 층이 모든 스테이션 모듈의 <Bold>체력</>을 증가시킵니다",
    "<Bold>+<XXX>%</> station module hitpoints": "스테이션 모듈 체력 <Bold>+<XXX>%</>",
    "Ship Production": "함선 생산",
    "AI control routines increase efficiency of all ship production":
        "AI 제어 루틴이 모든 함선 생산 효율을 증가시킵니다",
    "<Bold>+<XXX>%</> ship production speed": "함선 생산 속도 <Bold>+<XXX>%</>",
    "Energy Storage": "에너지 저장소",
    "More compact <Bold>energy lattices</> increase energy <Bold>storage capacity</> and <Bold>charge/discharge</> rates":
        "더 컴팩트한 <Bold>에너지 격자</>가 에너지 <Bold>저장 용량</>과 <Bold>충전/방전</> 속도를 증가시킵니다",
    "<Bold>+<XXX>%</> energy storage and <Bold>+<YYY>%</> charge/discharge rate":
        "에너지 저장 <Bold>+<XXX>%</>, 충전/방전 속도 <Bold>+<YYY>%</>",
    "Freighter Engines": "화물선 엔진",
    "Installing <Bold>Ion-based engines</> onto your <Bold>freighters</> increases top speed, reducing <Bold>transit times</> between parts of your station":
        "<Bold>이온 기반 엔진</>을 <Bold>화물선</>에 장착하여 최고 속도를 증가시키고 스테이션 부품 간 <Bold>이동 시간</>을 단축합니다",
    "<Bold>+<XXX>%</> max freighter speed": "최대 화물선 속도 <Bold>+<XXX>%</>",
    "Miner Output": "채굴기 산출",
    "High-powered <Bold>neutron lazers</> increase <Bold>output yield</> from miners":
        "고출력 <Bold>중성자 레이저</>가 채굴기의 <Bold>산출량</>을 증가시킵니다",
    "<Bold>+<XXX>%</> resource output from miners": "채굴기 자원 산출량 <Bold>+<XXX>%</>",
    "Auto-Repair Systems": "자동 수리 시스템",
    "Nanonic <Bold>micro-bots</> will automatically <Bold>repair damage</> taken by your station modules":
        "나노 <Bold>마이크로 봇</>이 스테이션 모듈이 받은 <Bold>피해를 자동으로 수리</>합니다",
    "Modules will self-repair <Bold><XXX></> hitpoints per second":
        "모듈이 초당 <Bold><XXX></> 체력 자가 수리",
    "Carbon Filters": "탄소 필터",
    "Improves the efficiency of Radiation Filters so that they last longer before wearing out":
        "방사선 필터의 효율을 개선하여 마모되기 전 더 오래 지속되도록 합니다",
    "Filters last <Bold><XXX>%</> longer": "필터 지속시간 <Bold><XXX>%</> 증가",
    "Advanced Fusion": "고급 융합",
    "Further breakthroughs in fusion technology lead to higher power output in fusion generators.":
        "융합 기술의 추가 돌파구로 융합 발전기의 출력이 향상됩니다.",
    "<Bold><XXX>%</> extra fusion power generated": "추가 융합 전력 생성 <Bold><XXX>%</>",
    "Insulated Modules": "절연 모듈",
    "Adds a layer of <Bold>insulation</> under your module's hulls, drastically reducing stun time":
        "모듈 선체 아래 <Bold>절연</> 층을 추가하여 기절 시간을 크게 감소시킵니다",
    "<Bold><XXX>%</> less stun time": "기절 시간 <Bold><XXX>%</> 감소",
    "Charged Nanites": "충전 나노로봇",
    "Increases the amount of hitpoints regenerated by the Nano Repair equipment.":
        "나노 수리 장비가 회복하는 체력량을 증가시킵니다.",
    "<Bold>+<XXX></> hitpoint regeneration": "체력 회복량 <Bold>+<XXX></>",
    "Quantum Attunement": "양자 동조",
    "Increases the rate items are uploaded from Quantum Storage devices.":
        "양자 저장 장치에서 아이템이 업로드되는 속도를 증가시킵니다.",
    "<Bold>+<XXX>%</> upload rate": "업로드 속도 <Bold>+<XXX>%</>",
    "Radiation Shielding": "방사선 차폐",
    "Depleted-uranium nano-particles integrated into your drone's casing decreases <Bold>radiation damage</>":
        "드론 외피에 통합된 열화 우라늄 나노 입자가 <Bold>방사능 피해</>를 감소시킵니다",
    "<Bold><XXX>%</> less damage from radioactive sources":
        "방사능 피해 <Bold><XXX>%</> 감소",

    # ---- DT_Tutorials ----
    "Building": "건설",
    "To build new modules on your station, enter <Bold>Build Mode</> using the Build option on the <Bold>Mode Bar</> at the bottom of the screen or press the <Bold>Build hotkey</>.\n\nChoose a <Bold>Build Category</> to see all available modules in that section, and then choose an option from the list to enter <Bold>Placing Mode</>.\n\nIf you have the required <Bold>parts</> in your <Bold>Drone's inventory</>, you can click to build, or <Bold>drag</> to automatically add <Bold>connectors</>.":
        "스테이션에 새 모듈을 건설하려면 화면 하단의 <Bold>모드 바</>에 있는 건설 옵션을 사용하거나 <Bold>건설 단축키</>를 눌러 <Bold>건설 모드</>로 진입하세요.\n\n<Bold>건설 카테고리</>를 선택하여 해당 섹션의 사용 가능한 모듈을 모두 확인한 다음, 목록에서 옵션을 선택해 <Bold>배치 모드</>로 진입하세요.\n\n<Bold>드론 인벤토리</>에 필요한 <Bold>부품</>이 있다면 클릭으로 건설하거나 <Bold>드래그</>하여 <Bold>연결기</>를 자동으로 추가할 수 있습니다.",
    "Atomizing": "분해",
    "When starting out, the main way to <Bold>gather resources</> is to feed <Bold>asteroids</> and other objects into an <Bold>Atomizer module.</>\n\nUse <Bold>left-drag</> to drag a single object to your <Bold>Atomizer</> and drop into the opening.\n\nYou can also <Bold>Shift-Left-Click</> to drag <Bold>multiple objects</> up to the <Bold>maximum carry weight</> of your drone.":
        "초반에는 <Bold>자원을 모으는</> 주된 방법은 <Bold>분해기 모듈</>에 <Bold>소행성</>과 기타 오브젝트를 투입하는 것입니다.\n\n<Bold>좌클릭 드래그</>로 단일 오브젝트를 <Bold>분해기</>로 끌어 투입구에 떨어뜨리세요.\n\n드론의 <Bold>최대 운반 중량</>까지 <Bold>여러 오브젝트</>를 끌려면 <Bold>Shift+좌클릭</>을 사용할 수 있습니다.",
    "Linking Modules": "모듈 연결",
    "Moving Items": "아이템 이동",
    "Most <Bold>production modules</> such as <Bold>Smelters</> need to have a <Bold>Recipe</> selected to start functioning.\n\nTo do this, select the module and click on the production section, then choose the required recipe from the list.\n\nWhen the module has the required Input items or materials it will begin production, and completed items will appear in the <Bold>Output section</>.":
        "<Bold>제련소</>와 같은 대부분의 <Bold>생산 모듈</>은 작동하려면 <Bold>제작법</>을 선택해야 합니다.\n\n모듈을 선택하고 생산 섹션을 클릭한 다음 목록에서 필요한 제작법을 선택하세요.\n\n모듈에 필요한 입력 아이템이나 재료가 들어오면 생산이 시작되며, 완성된 아이템은 <Bold>출력 섹션</>에 나타납니다.",
    "Objectives": "목표",
    "Pipes 1/3": "파이프 1/3",
    "Station modules that require, store or output <Bold>volatiles</> such as Hydrogen Gas will have one or more <Bold>Pipe Connections</>.\n\nYou can connect these to other modules using the <Bold>Pipe</> tool in the <Bold>Build > General</> menu.":
        "수소 가스 같은 <Bold>휘발성 물질</>이 필요하거나 저장 또는 출력하는 스테이션 모듈에는 하나 이상의 <Bold>파이프 연결점</>이 있습니다.\n\n<Bold>건설 > 일반</> 메뉴의 <Bold>파이프</> 도구로 다른 모듈에 연결할 수 있습니다.",
    "Pipe 2/3": "파이프 2/3",
    "Pipes will only <Bold>flow</> in <Bold>one direction</>, which can be easily seen using the <Bold>Station Status</> View (Left CTRL).\n\nYou can change the flow direction of any pipe by clicking the <Bold>flip pipe direction</> button on the pipe's popup menu, or quickly using the <Bold>H hotkey</> with any hovered or selected pipe.":
        "파이프는 <Bold>한 방향</>으로만 <Bold>흐릅니다</>. <Bold>스테이션 상태</> 뷰(왼쪽 CTRL)에서 쉽게 확인할 수 있습니다.\n\n파이프 팝업 메뉴의 <Bold>파이프 방향 전환</> 버튼을 클릭하거나, 마우스를 올리거나 선택한 파이프에 <Bold>H 단축키</>를 사용하여 어느 파이프든 흐름 방향을 바꿀 수 있습니다.",
    "Pipe 3/3": "파이프 3/3",
    "You can use <Bold>Pipe Junctions</> to create pipe <Bold>networks</> that feed multiple modules.\n\nPipe Junctions can also be <Bold>stacked</> on top of each other to direct pipes over the top of each other.":
        "<Bold>파이프 분기점</>을 사용하여 여러 모듈에 공급하는 파이프 <Bold>네트워크</>를 만들 수 있습니다.\n\n파이프 분기점은 서로 위에 <Bold>쌓을 수도</> 있어 파이프를 위로 지나가게 할 수 있습니다.",
    "Solar Generators": "태양광 발전기",
    "Upgrading Modules": "모듈 업그레이드",
    "You have unlocked a <Bold>Module Upgrade</>.\n\nSome station modules can be <Bold>upgraded</> to increase production efficiency and output if you have the required materials.\n\nClick the upgrade required from the module's properties window to upgrade the module to the new version.":
        "<Bold>모듈 업그레이드</>가 잠금 해제되었습니다.\n\n일부 스테이션 모듈은 필요한 재료가 있으면 생산 효율과 출력을 높이기 위해 <Bold>업그레이드</>할 수 있습니다.\n\n모듈 속성 창에서 필요한 업그레이드를 클릭하여 모듈을 새 버전으로 업그레이드하세요.",
    "Building Starships": "우주선 건조",
    "Miners": "채굴기",
    "To speed up resource collection you can now construct <Bold>Miners</> onto the <Bold>resource nodes</> you may find on larger asteroids.\n\nMiners can have other <Bold>station modules</> built onto them to create <Bold>sub-stations</> which can supply your main base with resources.\n\nLater in the game you will be able to automate moving resources between miners and your station using <Bold>Freighters</>.":
        "자원 수집 속도를 높이려면 더 큰 소행성에서 발견할 수 있는 <Bold>자원 노드</>에 <Bold>채굴기</>를 건설할 수 있습니다.\n\n채굴기 위에는 다른 <Bold>스테이션 모듈</>을 건설하여 메인 기지에 자원을 공급하는 <Bold>서브 스테이션</>을 만들 수 있습니다.\n\n게임 후반에는 <Bold>화물선</>을 사용하여 채굴기와 스테이션 간 자원 이동을 자동화할 수 있습니다.",
    "Multiple Locations": "다중 장소",
    "You have now unlocked a new <Bold>Location</> where you can found a <Bold>new station</>.\n\nNew locations can provide access to <Bold>new or rare resource types</>, and can be accessed by clicking the <Bold>New Station</> button in the <Bold>station toolbar</>, or from the <Bold>System View</>.\n\n<Bold>Be warned:</> These locations can also harbour more <Bold>deadly threats and events</> which will require you to protect your stations more carefully.":
        "<Bold>새 스테이션</>을 설립할 수 있는 새로운 <Bold>장소</>가 잠금 해제되었습니다.\n\n새 장소에서는 <Bold>새롭거나 희귀한 자원 유형</>에 접근할 수 있으며, <Bold>스테이션 툴바</>의 <Bold>새 스테이션</> 버튼이나 <Bold>시스템 뷰</>에서 접근할 수 있습니다.\n\n<Bold>주의:</> 이러한 장소에는 더 <Bold>치명적인 위협과 이벤트</>가 도사릴 수 있어 스테이션을 더 신중하게 보호해야 합니다.",
    "Freighters": "화물선",
    "Synthesizer": "합성기",
    "Most recipes can be <Bold>synthesized</> directly from your Inventory (Hotkey = <Bold>TAB</>).\n\nThis is done by opening the <Bold>drone inventory</> and clicking the <Bold>synthesizer</> tab.\n\nSelect the recipe from the list, and if you have the required materials you can click the button to start the process.\n\nYou can automatically repeat the process by toggling the <Bold>repeat</> button to the right.":
        "대부분의 제작법은 인벤토리에서 직접 <Bold>합성</>할 수 있습니다 (단축키 = <Bold>TAB</>).\n\n<Bold>드론 인벤토리</>를 열고 <Bold>합성기</> 탭을 클릭하면 됩니다.\n\n목록에서 제작법을 선택하고 필요한 재료가 있으면 버튼을 클릭하여 공정을 시작할 수 있습니다.\n\n오른쪽의 <Bold>반복</> 버튼을 켜면 공정을 자동 반복할 수 있습니다.",
    "Wormholes": "웜홀",
    "Tugs": "예인선",
    "<Bold>Tugs</> can be used to automate moving ships around your station.\n\nYou can use the <Bold>connect</> function to connect a <Bold>shipyard</> to another module such as a <Bold>fuel bay</> or <Bold>ammo depot</>, or to an <Bold>empty space</> near your station.\n\nIf a tug is in range of a completed ship in one of these connected modules it will automatically pick up and transfer the ship to the correct destination.":
        "<Bold>예인선</>을 사용하여 스테이션 주변에서 우주선 이동을 자동화할 수 있습니다.\n\n<Bold>연결</> 기능을 사용하여 <Bold>조선소</>를 <Bold>연료 저장고</>나 <Bold>탄약 저장고</> 같은 다른 모듈, 또는 스테이션 근처 <Bold>빈 공간</>에 연결할 수 있습니다.\n\n예인선이 이러한 연결된 모듈 중 하나에 있는 완성된 우주선의 사정거리 안에 있으면 자동으로 픽업하여 올바른 목적지로 운반합니다.",
    "Ship Reactors": "함선 원자로",
    "Larger ships can have one or more <Bold>micro fusion reactor</> components.\n\nOnce completed, these will begin to go <Bold>critical</>, and will <Bold>explode</> if allowed to fully melt down.\n\nTo avoid this the ship must be <Bold>fully fuelled</> in a <Bold>Fuel Bay</> before the timer runs out.":
        "더 큰 우주선은 하나 이상의 <Bold>마이크로 융합로</> 부품을 가질 수 있습니다.\n\n완성되면 <Bold>임계</> 상태로 진입하기 시작하며, 완전히 멜트다운되면 <Bold>폭발</>합니다.\n\n이를 방지하려면 타이머가 만료되기 전에 우주선을 <Bold>연료 저장고</>에서 <Bold>완전히 연료 주입</>해야 합니다.",
    "Artifacts": "유물",
    "Hotbar": "단축바",
    "Un-linking Modules": "모듈 연결 해제",
    "To remove a module link, enter <Bold>Link mode</> with <Bold>F</> or the toolbar, select a module that you have previously linked, and then select the destination module you want to unlink from it.\n\nHold <Bold>Shift</> to quickly un-link a module from multiple destinations.\n\nYou can also <Bold>remove all links</> by selecting a module in Link mode and pressing <Bold>X</>.":
        "모듈 연결을 제거하려면 <Bold>F</>나 툴바로 <Bold>연결 모드</>에 진입한 다음, 이전에 연결한 모듈을 선택하고 연결을 해제할 대상 모듈을 선택하세요.\n\n<Bold>Shift</>를 누르면 모듈을 여러 대상으로부터 빠르게 연결 해제할 수 있습니다.\n\n연결 모드에서 모듈을 선택하고 <Bold>X</>를 누르면 <Bold>모든 연결을 제거</>할 수도 있습니다.",
    "Advanced: Item Filters": "고급: 아이템 필터",
    "If you want more control over exactly what will be sent to Storage Units or Factories, you can use the <Bold>Item Filters</> panel.\n\nFrom here you can highlight any inventory slot and choose which items can be stored there, set a maximum limit for that item, or completely disable the slot.\n\nThere are also several functions for copying the current slot to all others, or from one slot to another.":
        "저장소나 공장으로 보낼 아이템을 더 정확히 제어하려면 <Bold>아이템 필터</> 패널을 사용할 수 있습니다.\n\n여기서 인벤토리 슬롯을 강조 표시하고 그 슬롯에 저장할 수 있는 아이템을 선택하거나, 그 아이템의 최대 한도를 설정하거나, 슬롯을 완전히 비활성화할 수 있습니다.\n\n현재 슬롯을 다른 모든 슬롯에 복사하거나, 한 슬롯에서 다른 슬롯으로 복사하는 기능도 있습니다.",
    "Advanced: Extra Functions": "고급: 추가 기능",
    "Clicking the <Bold>cog</> button opens the <Bold>Advanced Settings</> panel.\n\nFrom here you can <Bold>label</> any module with a custom tag which appears in the <Bold>Status View</> as well as several other functions.\n\nYou can also choose a module's <Bold>priority</> in this panel. Modules with a higher priority will <Bold>take more resources</> from sources than those with a lower priority - which is extremely useful for streamlining your station's manufacturing processes.":
        "<Bold>톱니바퀴</> 버튼을 클릭하면 <Bold>고급 설정</> 패널이 열립니다.\n\n여기서 모듈에 <Bold>라벨</>(커스텀 태그)을 붙여 <Bold>상태 뷰</>에 표시할 수 있고 여러 다른 기능을 사용할 수 있습니다.\n\n이 패널에서 모듈의 <Bold>우선순위</>도 선택할 수 있습니다. 우선순위가 높은 모듈은 우선순위가 낮은 모듈보다 공급원에서 <Bold>더 많은 자원</>을 가져오며, 스테이션의 제조 공정을 효율화하는 데 매우 유용합니다.",
    "Onboarding Complete": "온보딩 완료",
    "Congratulations Station Commander, you've completed the <Bold>Nova Corp Onboarding Process</>.\n\nYou're now ready to go forth and <Bold>build, explore and expand</> your industrial empire across the TAU system.\n\nWe see great things in your future, Commander - <Bold>good luck!</>":
        "축하합니다 스테이션 사령관님, <Bold>노바 코프 온보딩 절차</>를 완료하셨습니다.\n\n이제 TAU 성계 전역에서 산업 제국을 <Bold>건설하고, 탐험하고, 확장</>할 준비가 되셨습니다.\n\n사령관님의 미래에 큰 일이 있을 것이라 봅니다 — <Bold>행운을 빕니다!</>",
    "Particle Accelerator": "입자 가속기",
    "To generate <Bold>Antimatter</> you must construct a <Bold>Particle Accelerator Loop</>.\n\nThis is constructed from a <Bold>Control Station</>, one or more <Bold>Towers</>, all connected together via <Bold>Conduit</>.\n\nOnce you have a complete loop and have supplied your station with the required input items, you can start generating antimatter.\n\nThe <Bold>longer</> the loop you construct, the <Bold>faster</> you can generate antimatter, but the <Bold>more power</> your accelerator will require.":
        "<Bold>반물질</>을 생성하려면 <Bold>입자 가속기 루프</>를 건설해야 합니다.\n\n이는 <Bold>제어 스테이션</>, 하나 이상의 <Bold>타워</>로 구성되며, 모두 <Bold>도관</>으로 연결됩니다.\n\n완전한 루프가 만들어지고 스테이션에 필요한 입력 아이템이 공급되면 반물질 생성을 시작할 수 있습니다.\n\n루프를 <Bold>길게</> 만들수록 반물질을 <Bold>더 빠르게</> 생성할 수 있지만 가속기에 <Bold>더 많은 전력</>이 필요합니다.",
    "Station Status View": "스테이션 상태 뷰",
    "Equipment Station": "장비 정거장",
    "Multi-Select": "다중 선택",
    "You can use the <Bold>Multi-Select</> tool to select multiple station modules and perform operations on all of them at the same time.\n\nTo use the tool, click the Multi-Select button from the lower toolbar and <Bold>Left-Click</> or <Bold>Left-Drag</> station modules to select them.\n\nClick again or hold <Bold>Shift</> while dragging to <Bold>deselect</> modules.\n\nThe Multi-Select toolbar will appear and you can click one of the functions to apply it to all selected modules.":
        "<Bold>다중 선택</> 도구를 사용하여 여러 스테이션 모듈을 선택하고 동시에 작업을 수행할 수 있습니다.\n\n도구를 사용하려면 하단 툴바에서 다중 선택 버튼을 클릭하고 <Bold>좌클릭</> 또는 <Bold>좌클릭 드래그</>로 스테이션 모듈을 선택하세요.\n\n다시 클릭하거나 드래그 중 <Bold>Shift</>를 누르면 모듈을 <Bold>선택 해제</>합니다.\n\n다중 선택 툴바가 나타나며, 기능 중 하나를 클릭하여 선택된 모든 모듈에 적용할 수 있습니다.",
    "Blueprints": "청사진",
    "You can use <Bold>Blueprints</> to quickly and easily duplicate multiple station modules.\n\nTo create a blueprint, use the <Bold>Multi-Select</> tool to select multiple modules and click the <Bold>Create Blueprint</> button to open the blueprint creation menu.\n\nWhen you are satisfied, click the <Bold>Create</> button to form a new blueprint from the selected modules.\n\nYou can then access your previously created blueprints from the <Bold>Build > Blueprints</> category.":
        "<Bold>청사진</>을 사용하여 여러 스테이션 모듈을 빠르고 쉽게 복제할 수 있습니다.\n\n청사진을 만들려면 <Bold>다중 선택</> 도구로 여러 모듈을 선택하고 <Bold>청사진 만들기</> 버튼을 클릭하여 청사진 생성 메뉴를 여세요.\n\n만족스러우면 <Bold>만들기</> 버튼을 클릭하여 선택된 모듈로부터 새 청사진을 형성하세요.\n\n그 후 이전에 만든 청사진은 <Bold>건설 > 청사진</> 카테고리에서 접근할 수 있습니다.",
    "Component Factory": "부품 공장",
    "Exo Planet Ops": "외계행성 운영",
    "Some locations have <Bold>planet-based resources</> that you can collect, and this is accomplished by building an <Bold>Exo Planet Ops Centre</>.\n\nEach centre lets you deploy up to <Bold>4 planetary lifters</> to collect a specific resource, allowing you to fine-tune exactly which resources you want to gather.\n\nEach location only allowed a <Bold>maximum number of lifters</> in total however, so you will need to pick and choose which resources each centre will collect carefully.":
        "일부 장소에는 수집할 수 있는 <Bold>행성 기반 자원</>이 있으며, 이는 <Bold>외계행성 운영 센터</>를 건설하여 가능합니다.\n\n각 센터는 특정 자원을 수집하기 위해 최대 <Bold>4개의 행성 리프터</>를 배치할 수 있어 정확히 어떤 자원을 수집할지 세밀하게 조정할 수 있습니다.\n\n다만 각 장소에는 <Bold>총 리프터 최대 수</>가 정해져 있으므로 각 센터가 어떤 자원을 수집할지 신중하게 선택해야 합니다.",
    "Arkship Terminal": "방주선 터미널",
    "Production Overview Panel": "생산 개요 패널",
    "Space Elevator": "우주 엘리베이터",
    "Recycler": "재활용기",
    "Use the <Bold>Recycler</> to turn your unwanted items, materials and parts into <Bold>Tokens</>.\n\nTokens can then be spent on various <Bold>rewards</> such as Overdrive Cores, Tech Points and even to directly purchase completed ships.\n\nThe higher-value the resource you send into the Recycler, the more progress you will make towards the next Token.\n\nPlease note: each time you purchase a Token, the next Token will cost more resources to purchase.":
        "<Bold>재활용기</>를 사용하여 원치 않는 아이템, 재료, 부품을 <Bold>토큰</>으로 변환하세요.\n\n토큰은 오버드라이브 코어, 기술 포인트 등 다양한 <Bold>보상</>에 사용할 수 있고, 완성된 우주선을 직접 구매할 수도 있습니다.\n\n재활용기에 넣는 자원 가치가 높을수록 다음 토큰까지의 진행도가 더 많이 올라갑니다.\n\n참고: 토큰을 구매할 때마다 다음 토큰의 구매 비용이 증가합니다.",
    "Laboratory": "연구소",
    "The <Bold>Laboratory</> can be used to unlock <Bold>alternative and more efficient recipes</> for commonly used items, materials and parts.\n\nTo unlock an alternate recipe, feed in the <Bold>required resources</> as shown in the popup list and then select it.\n\nThe alternative recipe will then appear in the recipe list of the appropriate factory.":
        "<Bold>연구소</>는 자주 사용되는 아이템, 재료, 부품에 대한 <Bold>대체 및 더 효율적인 제작법</>을 잠금 해제하는 데 사용할 수 있습니다.\n\n대체 제작법을 잠금 해제하려면 팝업 목록에 표시된 <Bold>필요 자원</>을 투입한 다음 선택하세요.\n\n그러면 대체 제작법이 해당 공장의 제작법 목록에 나타납니다.",
    "Overdrive Cores": "오버드라이브 코어",
    "Overdrive Cores can be inserted into compatible modules to substantially increase their efficiency and output.\n\nMost factories and resource extractors can be overdriven by dragging an Overdrive Core into the slot located next to its Max Efficiency slider.\n\nOverdrive Cores can be purchased with Tokens in the Recycler, or found in the world.":
        "오버드라이브 코어는 호환 모듈에 삽입하여 효율과 출력을 크게 향상시킬 수 있습니다.\n\n대부분의 공장과 자원 추출기는 최대 효율 슬라이더 옆에 위치한 슬롯에 오버드라이브 코어를 끌어다 놓아 오버드라이브할 수 있습니다.\n\n오버드라이브 코어는 재활용기에서 토큰으로 구매하거나 게임 세계에서 발견할 수 있습니다.",

    # ---- DT_ContractText ----
    "<Bold>Mission Complete</>, Station Commander.": "<Bold>임무 완료</>, 스테이션 사령관님.",
    "<Bold>Congratulations</> Commander, Mission accomplished.":
        "<Bold>축하합니다</> 사령관님, 임무 달성.",
    "<Bold>Primary objective completed</>. well done, Station Commander.":
        "<Bold>주요 목표 완료</>. 잘하셨습니다, 스테이션 사령관님.",
    "New <bold>technologies, modules, items</> and <bold>parts</> are now available for you to unlock...":
        "이제 새로운 <bold>기술, 모듈, 아이템</> 및 <bold>부품</>을 잠금 해제할 수 있습니다...",
    "To continue, select a new objective from the <Bold>Objectives Panel</>...":
        "계속하려면 <Bold>목표 패널</>에서 새 목표를 선택하세요...",
    "When you're ready, open the <Bold>Objectives Panel</> to continue expanding your station...":
        "준비되시면 <Bold>목표 패널</>을 열어 스테이션 확장을 계속하세요...",
    "More objectives are available from the <Bold>Objectives Panel</>...":
        "<Bold>목표 패널</>에서 더 많은 목표를 사용할 수 있습니다...",
    "Choose another objective from the <Bold>Objectives Panel</>...":
        "<Bold>목표 패널</>에서 다른 목표를 선택하세요...",
    "The <Bold>Objectives Panel</> contains new objectives for you...":
        "<Bold>목표 패널</>에 새로운 목표가 준비되어 있습니다...",
    "Welcome to the <Bold>TAU</> system, <Bold>Station Commander</>...":
        "<Bold>TAU</> 성계에 오신 것을 환영합니다, <Bold>스테이션 사령관님</>...",
    "Located on the fringes of the known galaxy, <Bold>Nova Corp</> has singled out this system for <Bold>exploitation and expansion</>.\n\nAs one of our newest <Bold>Station Commanders</>, we expect <Bold>big things</> from you - but <Bold>don't worry</>, I'll be here to guide you along the way...":
        "알려진 은하 변두리에 위치한 이 성계를 <Bold>노바 코프</>가 <Bold>개발 및 확장</> 대상으로 선정했습니다.\n\n저희의 새로운 <Bold>스테이션 사령관</> 중 한 분으로서 <Bold>큰 성과</>를 기대합니다 — 그러나 <Bold>걱정 마세요</>, 제가 길을 안내해 드리겠습니다...",
    "Open the <Bold>Objectives Panel</> to select an objective and start developing your station.":
        "<Bold>목표 패널</>을 열어 목표를 선택하고 스테이션 개발을 시작하세요.",
    "To continue developing your station,": "스테이션 개발을 계속하려면,",
    "To reach the next Station Level,": "다음 스테이션 레벨에 도달하려면,",
    "To expand your station further,": "스테이션을 더 확장하려면,",
    "To fulfil your next objective,": "다음 목표를 달성하려면,",
    "Let us know when you have all of the required items.":
        "필요한 아이템을 모두 갖추시면 알려주세요.",
    "We'll be in contact when you've fulfilled all of the objectives.":
        "모든 목표를 달성하시면 연락드리겠습니다.",
    "Better get to work, Station Commander.": "작업에 착수하시는 게 좋겠습니다, 스테이션 사령관님.",
    "No time to waste, Commander.": "낭비할 시간이 없습니다, 사령관님.",
    "we'll need you to construct the following ships:\n\n<Ships>...":
        "다음 함선들을 건조해 주셔야 합니다:\n\n<Ships>...",
    "the following starships need to be constructed:\n\n<Ships>...":
        "다음 우주선들을 건조해야 합니다:\n\n<Ships>...",
    "please make sure you construct these ships:\n\n<Ships>...":
        "다음 함선들을 반드시 건조해 주세요:\n\n<Ships>...",
    "make sure you have the following starships:\n\n<Ships>...":
        "다음 우주선들을 갖추셔야 합니다:\n\n<Ships>...",
    "please build these ships:\n\n<Ships>...": "다음 함선들을 건조해 주세요:\n\n<Ships>...",
    "we'll need you to manufacture the following items:\n\n<Items>...":
        "다음 아이템들을 제조해 주셔야 합니다:\n\n<Items>...",
    "the following items need to be constructed:\n\n<Items>...":
        "다음 아이템들을 제작해야 합니다:\n\n<Items>...",
    "please fulfil these items:\n\n<Items>...": "다음 아이템들을 채워 주세요:\n\n<Items>...",
    "we need these items to be in your HUB:\n\n<Items>...":
        "이 아이템들이 허브에 있어야 합니다:\n\n<Items>...",
    "You've done some truly amazing work in this sector, Commander.\n\n<Bold>Station Command</> has taken notice, and have decided to <Bold>promote</> you to the rank of <Bold>Captain</>!\n\nYou should feel extremely proud of yourself...":
        "이 구역에서 정말 놀라운 일을 해내셨습니다, 사령관님.\n\n<Bold>스테이션 본부</>가 이를 주목했고, <Bold>대위</> 계급으로 <Bold>승진</>시키기로 결정했습니다!\n\n자부심을 느끼셔도 좋습니다...",
    "You've completed the <Bold>initial phase of development</> in this system.\n\nPlease continue to expand your station and we'll be in touch very soon with <Bold>new technologies</> and <Bold>further orders</>...":
        "이 성계에서 <Bold>개발 초기 단계</>를 완료하셨습니다.\n\n계속해서 스테이션을 확장하시면 곧 <Bold>새 기술</>과 <Bold>추가 명령</>으로 연락드리겠습니다...",
    "<Bold>My compliments</>, Station Commander.": "<Bold>축하 드립니다</>, 스테이션 사령관님.",
    "<Bold>Congratulations</> Commander.": "<Bold>축하합니다</> 사령관님.",
    "<Bold>Objective Completed</> Commander.": "<Bold>목표 완료</> 사령관님.",
    "<Bold>Objective completed</>. well done, Station Commander.":
        "<Bold>목표 완료</>. 잘하셨습니다, 스테이션 사령관님.",
    "You've completed an Objective - My Compliments.":
        "목표를 완료하셨습니다 — 축하 드립니다.",
    "<Bold>Drone Control Initiated...</>\n\nWelcome to <Bold>Stargate Control Alpha</>, Station Commander...":
        "<Bold>드론 제어 시작...</>\n\n<Bold>스타게이트 제어 알파</>에 오신 것을 환영합니다, 스테이션 사령관님...",
    "<Enemy>The Void</> is now only light-minutes away from Terra Prime and we're running out of time...":
        "<Enemy>공허</>가 이제 테라 프라임에서 광분 거리밖에 안 떨어져 있고 시간이 부족합니다...",
    "We need to get that <Bold>Jumpgate Buffer</> back online now, so we can re-initiate <Bold>The Gate</> and escape to the <Bold>TAU system</> before this system is destroyed.":
        "이 성계가 파괴되기 전에 <Bold>게이트</>를 재가동하고 <Bold>TAU 성계</>로 탈출할 수 있도록 그 <Bold>점프게이트 버퍼</>를 즉시 복구해야 합니다.",
    "We just need to run a few <Bold>tests</> on your Drone's <Bold>control routines</>...\n\nFollow the steps and then we can get to work.":
        "사령관님의 드론 <Bold>제어 루틴</>에 몇 가지 <Bold>테스트</>만 진행하면 됩니다...\n\n단계를 따라가시면 작업을 시작할 수 있습니다.",
    "OK, now we need to clear the <Enemy>wreckage</> from around the damaged jumpgate buffer before we can replace it.\n\nWe recommend using your <Bold>Neutron Lazer</> to accomplish this...":
        "좋습니다, 이제 손상된 점프게이트 버퍼 주변의 <Enemy>잔해</>를 교체 전에 제거해야 합니다.\n\n이를 위해 <Bold>중성자 레이저</>를 사용하실 것을 권장합니다...",
    "We can now <Bold>deconstruct</> the damaged buffer to clear space for the new buffer we'll need to produce...\n\nYou can use the <Bold>Sell mode</> to accomplish this.":
        "이제 새 버퍼를 생산할 공간을 확보하기 위해 손상된 버퍼를 <Bold>해체</>할 수 있습니다...\n\n이를 위해 <Bold>판매 모드</>를 사용할 수 있습니다.",
    "We need to get a new buffer up and running as soon as we can, but all our factories were <Bold>dismantled</> to build <Bold>The Gate</>...":
        "가능한 한 빨리 새 버퍼를 가동해야 하지만, 모든 공장은 <Bold>게이트</>를 건설하기 위해 <Bold>해체</>되었습니다...",
    "We'll need to get a small factory up and running to manufacture the <Bold>Stargate Parts</> we need...\n\nStart by collecting the items left in your <Bold>HUB</>.":
        "필요한 <Bold>스타게이트 부품</>을 제조하려면 작은 공장을 가동해야 합니다...\n\n<Bold>허브</>에 남아 있는 아이템부터 수집하세요.",
    "We'll need some basic materials before we can start building more complex parts...":
        "더 복잡한 부품을 만들기 전에 몇 가지 기본 재료가 필요합니다...",
    "Construct an <Bold>Atomizer</> to let us turn collected asteroids into raw materials, and a <Bold>Smelter</> to turn these into useable metals.":
        "수집한 소행성을 원자재로 변환하기 위해 <Bold>분해기</>를 건설하고, 이를 사용 가능한 금속으로 변환하기 위해 <Bold>제련소</>를 건설하세요.",
    "Now our <Bold>Atomizer</> is up and running we can collect asteroids floating around our station and drop them into the opening to process them.":
        "이제 <Bold>분해기</>가 가동되었으니 스테이션 주변에 떠 있는 소행성을 수집하고 투입구에 떨어뜨려 처리할 수 있습니다.",
    "All factories need to have a <Bold>recipe</> selected in order to function.\n\nChoose the <Bold>Titanium</> recipe now from your <Bold>Smelter's popup menu</>.":
        "모든 공장은 작동하려면 <Bold>제작법</>이 선택되어 있어야 합니다.\n\n지금 <Bold>제련소 팝업 메뉴</>에서 <Bold>티타늄</> 제작법을 선택하세요.",
    "Automate the movement of items and materials around your station by <Bold>linking</> modules together - they will intelligently <Bold>send required items</> to modules they are linked to.\n\nLink your <Bold>Atomizer</> to your <Bold>Smelter</> and your <Bold>Smelter</> to your <Bold>HUB</> to start sending items now.":
        "모듈을 <Bold>연결</>하여 스테이션 주변의 아이템과 재료 이동을 자동화하세요 — 모듈이 자신과 연결된 모듈로 <Bold>필요한 아이템을</> 지능적으로 <Bold>전송</>합니다.\n\n지금 <Bold>분해기</>를 <Bold>제련소</>에, <Bold>제련소</>를 <Bold>허브</>에 연결하여 아이템 전송을 시작하세요.",
    "If you have made a mistake linking modules together you can <Bold>unlink</> them by repeating the same link action.\n\nWe recommend unlinking your <Bold>Smelter</> from your <Bold>HUB</> now.":
        "모듈 연결에 실수가 있었다면 동일한 연결 동작을 반복하여 <Bold>연결을 해제</>할 수 있습니다.\n\n지금 <Bold>제련소</>를 <Bold>허브</>에서 연결 해제하시는 것을 권장합니다.",
    "We're going to need some <Bold>additional modules</> to create our mini factory.\n\nPlease build the required modules so we can continue.":
        "미니 공장을 만들려면 <Bold>추가 모듈</>이 필요합니다.\n\n계속 진행할 수 있도록 필요한 모듈을 건설해 주세요.",
    "Now <Bold>link</> all of your new modules together as directed to form <Bold>supply chains</>.":
        "이제 안내에 따라 새 모듈들을 모두 <Bold>연결</>하여 <Bold>공급망</>을 형성하세요.",
    "Our <Bold>power generation</> is getting dangerously low...\n\nBuild a <Bold>Solar Panel</> and <Bold>align</> it to the sun's direction to increase power levels.":
        "<Bold>전력 생산</>이 위험할 정도로 낮아지고 있습니다...\n\n<Bold>태양광 패널</>을 건설하고 태양 방향으로 <Bold>정렬</>하여 전력 수준을 높이세요.",
    "Before we continue, please check that these <Bold>advanced functions</> are working correctly as they will come in very useful as your station expands further.":
        "계속하기 전에 이 <Bold>고급 기능</>이 올바르게 작동하는지 확인해 주세요. 스테이션이 확장됨에 따라 매우 유용해질 것입니다.",
    "All modules have <Bold>advanced settings</> which give you more control over what they will process and store - please test these functions now.":
        "모든 모듈에는 처리하고 저장할 항목을 더 잘 제어할 수 있는 <Bold>고급 설정</>이 있습니다 — 지금 이 기능을 테스트해 주세요.",
    "Completing <Bold>Objectives</> allows us to unlock <Bold>new technologies, items, modules and ships</>.\n\nSelect the <Bold>Complete The Gate</> objective now from the <Bold>Objectives Panel</>.":
        "<Bold>목표</>를 완료하면 <Bold>새로운 기술, 아이템, 모듈 및 함선</>을 잠금 해제할 수 있습니다.\n\n지금 <Bold>목표 패널</>에서 <Bold>게이트 완성</> 목표를 선택하세요.",
    "To rebuild the damaged buffer unit we'll need to construct complex <Bold>Stargate Parts</>, using the materials our smelters have processed.\n\nWe can use our Drone's <Bold>Synthesizer</> function to produce these parts. This is accessed from the <Bold>Synthesizer Tab</> on your Drone's <Bold>inventory</> popup menu...":
        "손상된 버퍼 유닛을 재건하려면 제련소가 처리한 재료를 사용해 복잡한 <Bold>스타게이트 부품</>을 제작해야 합니다.\n\n드론의 <Bold>합성기</> 기능으로 이 부품을 생산할 수 있습니다. 드론 <Bold>인벤토리</> 팝업 메뉴의 <Bold>합성기 탭</>에서 접근할 수 있습니다...",
    "Now we've fabricated the required <Bold>Stargate Parts</>, we should place these in our <Bold>HUB</> in order to complete the current Objective.":
        "이제 필요한 <Bold>스타게이트 부품</>을 제작했으니, 현재 목표를 완료하기 위해 <Bold>허브</>에 배치해야 합니다.",
    "If you <Bold>run out of materials</> while synthesizing, don't forget to feed more asteroids into your <Bold>Atomizer</>, and collect more completed materials from your <Bold>HUB</>.":
        "합성 중에 <Bold>재료가 바닥나면</> <Bold>분해기</>에 더 많은 소행성을 투입하고 <Bold>허브</>에서 완성된 재료를 더 많이 수집하는 것을 잊지 마세요.",
    "Local <Bold>star constellations</> fixed and locked...\n\nConfirmed... We've arrived in the <Bold>TAU system</>, Station Commander...":
        "지역 <Bold>별자리</> 확정 및 고정...\n\n확인 완료... <Bold>TAU 성계</>에 도착했습니다, 스테이션 사령관님...",
    "<Bold>Long-range scans</> reveal that this <Bold>mysterious</> system contains all the raw resources we'll need to develop our <Bold>Intergalactic Arkship</> and escape this galaxy....":
        "<Bold>장거리 스캔</> 결과 이 <Bold>신비로운</> 성계에는 우리의 <Bold>은하 간 방주선</>을 개발하고 이 은하를 탈출하는 데 필요한 모든 원자재가 있는 것으로 나타났습니다....",
    "However, it appears that <Bold>The Void's</> expansion is <Bold>accelerating</>, and we may not have as long here as we hoped before it reaches us again...\n\n<Bold>So we better get to work, Station Commander!</>":
        "그러나 <Bold>공허</>의 팽창이 <Bold>가속화</>되고 있어, 다시 우리에게 닿기 전까지 우리가 바랐던 만큼의 시간이 없을 수도 있습니다...\n\n<Bold>그러니 작업에 착수하는 게 좋겠습니다, 스테이션 사령관님!</>",
    "Select an <Bold>Objective</> from the <Bold>Objectives Panel</> to start.":
        "시작하려면 <Bold>목표 패널</>에서 <Bold>목표</>를 선택하세요.",

    # ---- DT_Upgrades — short numeric perks ----
    "<Bold>+14</> storage slots": "저장 슬롯 <Bold>+14</>",
    "<Bold>+50%</> item send speed": "아이템 전송 속도 <Bold>+50%</>",
    "<Bold>+100%</> output": "출력 <Bold>+100%</>",
    "<Bold>+100%</> production speed": "생산 속도 <Bold>+100%</>",
    "<Bold>+6</> storage slots": "저장 슬롯 <Bold>+6</>",
    "Loads and unloads <Bold>gases & liquids</>": "<Bold>기체 및 액체</> 적재/하역",
    "<Bold>+120/min</> item send speed": "아이템 전송 속도 <Bold>+120/분</>",
    "Transports <Bold>gases & liquids</>": "<Bold>기체 및 액체</> 운송",
    "<Bold>+50%</> movement speed": "이동 속도 <Bold>+50%</>",
    "<Bold>+200%</> transfer speed": "전송 속도 <Bold>+200%</>",
    "<Bold>+100%</> storage capacity": "저장 용량 <Bold>+100%</>",
    "<Bold>+9</> storage slots": "저장 슬롯 <Bold>+9</>",
    "<Bold>+60/min</> item send speed": "아이템 전송 속도 <Bold>+60/분</>",
    "<Bold>+100%</> liquid/gas capacity": "액체/기체 용량 <Bold>+100%</>",
    "<Bold>Beam Weapon</> Turret": "<Bold>빔 무기</> 포탑",
    "<Bold>+4</> storage slots": "저장 슬롯 <Bold>+4</>",
    "<Bold>+100%</> liquid/gas storage capacity": "액체/기체 저장 용량 <Bold>+100%</>",
    "<Bold>+60%</> movement speed": "이동 속도 <Bold>+60%</>",
    "<Bold>+100%</> Hitpoints": "체력 <Bold>+100%</>",
    "<Bold>+200%</> storage capacity": "저장 용량 <Bold>+200%</>",
    "<Bold>+6</> item slots": "아이템 슬롯 <Bold>+6</>",
    "<Bold>+2</> pipe connections": "파이프 연결 <Bold>+2</>",
    "Can store and supply <Bold>Antimatter</>": "<Bold>반물질</>을 저장하고 공급할 수 있음",
    "<Bold>+100%</> transfer speed": "전송 속도 <Bold>+100%</>",
    "<Bold>+100%</> hydrogen storage capacity": "수소 저장 용량 <Bold>+100%</>",
    "<Bold>+100%</> transfer rate": "전송률 <Bold>+100%</>",

    # ---- DT_Levels — short titles & unlock labels (103 entries) ----
    "Advanced AI Robotics": "고급 AI 로봇공학",
    "Advanced Computing": "고급 컴퓨팅",
    "Advanced Fluid Transport": "고급 유체 운송",
    "Advanced Fuelling": "고급 연료 주입",
    "Advanced Logistics": "고급 물류",
    "Advanced Manufacturing": "고급 제조",
    "Advanced Ore Extraction": "고급 광석 추출",
    "Advanced Portals": "고급 포털",
    "Advanced Ship Construction": "고급 함선 건조",
    "Advanced Storage": "고급 저장소",
    "Alloy Production": "합금 생산",
    "Alternate Recipe Research": "대체 제작법 연구",
    "Antimatter Fuelling": "반물질 연료 주입",
    "Antimatter Power Generation": "반물질 전력 생산",
    "Arkship Dock": "방주선 도크",
    "Armoured Materials": "장갑 재료",
    "Artifact Scanning": "유물 스캔",
    "Automated Logistics": "자동화 물류",
    "Automated Ore Extraction": "자동 광석 추출",
    "Base Defence": "기지 방어",
    "Basic Ammunition Production": "기본 탄약 생산",
    "Basic Computing": "기본 컴퓨팅",
    "Basic Manufacturing": "기본 제조",
    "Basic Ship Construction": "기본 함선 건조",
    "Battlecruisers": "전투순양함",
    "Bio-Extractor": "바이오 추출기",
    "Building The Arkship": "방주선 건조",
    "Centrifuge Technology": "원심분리 기술",
    "Cerberus Beach-head": "케르베로스 교두보",
    "Commander, the Arkship is fuelled, powered and ready to launch!":
        "사령관님, 방주선의 연료 주입과 동력 공급이 완료되어 발진 준비가 끝났습니다!",
    "Complete The Arkship": "방주선 완성",
    "Complete the Gate": "게이트 완성",
    "Deep Space Scanning": "심우주 스캔",
    "Destination: Glacialis": "목적지: 글라시알리스",
    "Destination: Titania": "목적지: 티타니아",
    "Enhanced Base Defence": "강화 기지 방어",
    "Enhanced Logistics": "강화 물류",
    "Enhanced Manufacturing": "강화 제조",
    "Enhanced Military Starships": "강화 군용 우주선",
    "Enhanced Ore Extraction": "강화 광석 추출",
    "Enhanced Ship Construction": "강화 함선 건조",
    "Enhanced Smelting": "강화 제련",
    "Enhanced Storage": "강화 저장소",
    "Exoplanet Ops": "외계행성 운영",
    "Expanded Blueprints": "확장 청사진",
    "Expansion Protocol": "확장 프로토콜",
    "Factory Evaluation": "공장 평가",
    "Fast Travel": "빠른 이동",
    "Force-Field Technology": "역장 기술",
    "Fusion Technology": "융합 기술",
    "Gas Giant Operations": "가스 거성 운영",
    "Going Further": "더 멀리",
    "Heavy Ship Construction": "중형 함선 건조",
    "High Energy Physics": "고에너지 물리학",
    "High Explosives": "고폭약",
    "Hydrogen Processing": "수소 가공",
    "Large Ship Construction": "대형 함선 건조",
    "Large Starship Transportation": "대형 우주선 운송",
    "Launch The Arkship": "방주선 발진",
    "Magnetic Accelerator": "자기 가속기",
    "Military Grade Starships": "군용 우주선",
    "Neutronium Processing": "중성자물질 가공",
    "Nuclear Waste Processing": "핵 폐기물 처리",
    "Operation: Junkyard": "작전: 고철장",
    "Portal Technology": "포털 기술",
    "Power Transmission": "전력 전송",
    "Prologue: Escape Terra System": "프롤로그: 테라 성계 탈출",
    "Quantum Destabilization": "양자 안정화 파괴",
    "Quantum Physics": "양자 물리학",
    "Quantum Rift Extraction": "양자 균열 추출",
    "Quantum Storage": "양자 저장소",
    "Radiation Protection": "방사능 방호",
    "Scouting Surroundings": "주변 정찰",
    "Starship Fuelling": "우주선 연료 주입",
    "Starship Transportation": "우주선 운송",
    "Superconductors": "초전도체",
    "Test Ship Construction": "시험 함선 건조",
    "The Arkship": "방주선",
    "Unlocks <Bold>Quantum-based technologies</>":
        "<Bold>양자 기반 기술</>을 잠금 해제합니다",
    "Unlocks additional <Bold>military-grade</> starship parts and ship classes.":
        "추가 <Bold>군용</> 우주선 부품과 함급을 잠금 해제합니다.",
    "Unlocks more advanced starship parts and ship classes.":
        "더 고급의 우주선 부품과 함급을 잠금 해제합니다.",
    "Unlocks more powerful automated base defences.":
        "더 강력한 자동 기지 방어를 잠금 해제합니다.",
    "Unlocks superconductors - an essential component for advanced manufacturing.":
        "고급 제조에 필수적인 초전도체를 잠금 해제합니다.",
    "Unlocks the ability to construct larger ship classes.":
        "더 큰 함급을 건조할 수 있게 합니다.",
    "Unlocks the ability to construct military starships.":
        "군용 우주선을 건조할 수 있게 합니다.",
    "Unstable Element Containment": "불안정 원소 격납",
    "Uranium Processing": "우라늄 가공",
    "Welcome to the TAU system": "TAU 성계에 오신 것을 환영합니다",
    "Welcome to the Tau System": "타우 성계에 오신 것을 환영합니다",
    "Production Overview": "생산 개요",

    # ---- DT_Levels — long descriptions (207 unique) ----
    "The ultramassive cosmic entity known only as <Bold>The Void</> has reached <Bold>Terra System</>, and its only a matter of time before your home planet is consumed.\n\nYou've mined all your home system's remaining resources to construct <Bold>The Gate</> - an intersteller stargate that can take you to the edge of the galaxy - and buy you some time.\n\nBut <Bold>The Gate is damaged</> and it must be <Bold>repaired</> so you can use it to escape Terra System before The Void arrives and all is lost.":
        "<Bold>공허</>로만 알려진 초대질량 우주 존재가 <Bold>테라 성계</>에 도달했고, 고향 행성이 삼켜지는 것은 시간 문제일 뿐입니다.\n\n당신은 고향 성계의 남은 자원을 모두 채굴하여 <Bold>게이트</>를 건설했습니다 — 은하 끝자락으로 데려갈 수 있는 항성 간 스타게이트로 시간을 벌어줍니다.\n\n하지만 <Bold>게이트가 손상</>되었고 <Bold>수리</>해야 합니다. 그래야 공허가 도달해 모든 것이 끝나기 전에 테라 성계를 탈출할 수 있습니다.",
    "Unlocks <Bold>basic production buildings, items</> and <Bold>materials</> essential for turning simple materials into useable items and parts.":
        "단순 재료를 사용 가능한 아이템과 부품으로 만드는 데 필수적인 <Bold>기본 생산 건물, 아이템</> 및 <Bold>재료</>를 잠금 해제합니다.",
    "<Bold>Matter Printers</> can convert raw materials into more complex items ready to be used in further production chains.\n\nUse the <Bold>Link</> function to automatically feed the output of your <Bold>smelters</> into matter printers to speed up production.":
        "<Bold>물질 프린터</>는 원자재를 더 복잡한 아이템으로 변환하여 다음 생산 단계에서 사용할 수 있게 합니다.\n\n<Bold>제련소</>의 산출물을 물질 프린터로 자동 공급하려면 <Bold>연결</> 기능을 사용해 생산을 가속하세요.",
    "Our <Bold>first priority</> should be making sure our systems survived the journey here, so we'll need to run some <Bold>tests</> on our <Bold>robotic manufacturing facilities</>...":
        "<Bold>최우선 순위</>는 시스템이 여기까지의 여정을 견뎠는지 확인하는 것입니다. 따라서 <Bold>로봇 제조 시설</>에 몇 가지 <Bold>테스트</>를 실행해야 합니다...",
    "Please produce the <Bold>following items</> and place them in your <Bold>HUB</> to continue:\n\n{REQUIRED_ITEMS}":
        "계속하려면 <Bold>다음 아이템</>을 생산해 <Bold>허브</>에 배치하세요:\n\n{REQUIRED_ITEMS}",
    "<Bold>Good job, Station Commander</> - all systems appear operating at <Bold>100% efficiency</>.\n\nWe are now free to proceed with the <Bold>next phase</> of our operations here.":
        "<Bold>잘하셨습니다, 스테이션 사령관님</> — 모든 시스템이 <Bold>100% 효율</>로 작동하는 것으로 보입니다.\n\n이제 여기에서의 운영의 <Bold>다음 단계</>로 자유롭게 진행할 수 있습니다.",
    "You've escaped to the mysterious <Bold>Tau System</> after your home planet is destroyed by <Bold>The Void</>: An ultramassive cosmic entity that is gradually consuming your galaxy.\n\nYour HUB contains the <Bold>genetic material</> and <Bold>uploaded personalities</> of your entire homeworld, ready to be reconstituted once you've reached a safe haven.\n\n<Bold>Your mission:</> To develop and construct an <Bold>Inter-Galactic Arkship</> you can use to escape this doomed galaxy - and The Void - forever.":
        "당신의 은하를 점차 삼키고 있는 초대질량 우주 존재 <Bold>공허</>에 의해 고향 행성이 파괴된 후, 당신은 신비로운 <Bold>타우 성계</>로 탈출했습니다.\n\n당신의 허브에는 고향 행성 전체의 <Bold>유전 물질</>과 <Bold>업로드된 인격체</>가 담겨 있어, 안전한 피난처에 도달하면 복원될 준비가 되어 있습니다.\n\n<Bold>임무:</> 운명 지어진 이 은하 — 그리고 공허 — 로부터 영원히 탈출하기 위한 <Bold>은하 간 방주선</>을 개발하고 건조하는 것.",
    "Unlocks new <Bold>items, materials</> and the <Bold>Fabricator</> which can take simple items and materials and combine them to produce more complex items and simple starship parts.":
        "단순 아이템과 재료를 결합하여 더 복잡한 아이템과 단순한 우주선 부품을 생산할 수 있는 <Bold>가공기</>와 새로운 <Bold>아이템, 재료</>를 잠금 해제합니다.",
    "You can now construct <Bold>Fabricators</> which can take simple items and materials and combine them to produce more complex items and simple starship parts.":
        "이제 단순 아이템과 재료를 결합하여 더 복잡한 아이템과 단순한 우주선 부품을 생산할 수 있는 <Bold>가공기</>를 건설할 수 있습니다.",
    "Advanced <Bold>scanning technologies</> let you extract powerful technological breakthroughs from any <Bold>alien artifacts</> you may find.":
        "고급 <Bold>스캔 기술</>로 발견한 <Bold>외계 유물</>에서 강력한 기술 돌파구를 추출할 수 있습니다.",
    "The <Bold>Artifact Analyzer</> is now available from the build menu.\n\nFeed any <Bold>Alien Artifacts</> you may find into this unit to earn <Bold>Tech Points</> which can be spent on powerful upgrades and abilities.":
        "건설 메뉴에서 <Bold>유물 분석기</>를 사용할 수 있습니다.\n\n발견한 <Bold>외계 유물</>을 이 장치에 투입하여 <Bold>기술 포인트</>를 획득하고, 강력한 업그레이드와 능력에 사용하세요.",
    "Unlocks high-capacity laminar batteries for storing any excess power your station may generate.":
        "스테이션이 생산하는 잉여 전력을 저장하기 위한 고용량 라미나 배터리를 잠금 해제합니다.",
    "You have now unlocked the <Bold>Energy Storage</> module.\n\nYou can use <Bold>Energy Storage</> to store excess energy produced by your station ready to restore power levels if you lose power in your station.":
        "이제 <Bold>에너지 저장소</> 모듈이 잠금 해제되었습니다.\n\n<Bold>에너지 저장소</>를 사용하여 스테이션이 생산한 잉여 에너지를 저장해두고, 스테이션 전력이 손실될 경우 전력 수준을 복구할 수 있습니다.",
    "Our initial surveys hinted at <Bold>vast amounts of resources</> scattered throughout this system - but now we have to <Bold>find them, and mine them</>...":
        "초기 조사는 이 성계 곳곳에 흩어진 <Bold>막대한 자원</>의 존재를 시사했습니다 — 이제 우리는 <Bold>그것들을 찾아 채굴</>해야 합니다...",
    "We should upgrade our HUB with a <Bold>Deep Space Scanner</>. This will unlock the <Bold>System View</> and give us a clearer picture of what is around us...":
        "허브를 <Bold>심우주 스캐너</>로 업그레이드해야 합니다. 그러면 <Bold>시스템 뷰</>가 잠금 해제되어 주변 상황을 더 명확하게 볼 수 있게 됩니다...",
    "<Bold>Deep Space Scanner... Deploying...</>\n\n<Bold>Great job Station Commander</>, the <Bold>System View</> can now be accessed from the <Bold>Map Screen</>....":
        "<Bold>심우주 스캐너... 전개 중...</>\n\n<Bold>잘하셨습니다 스테이션 사령관님</>, 이제 <Bold>지도 화면</>에서 <Bold>시스템 뷰</>에 접근할 수 있습니다....",
    "We're already getting data back from our initial scans, but charting the <Bold>entire system</> will take some time, and there's plenty to do in the meantime.":
        "초기 스캔에서 이미 데이터가 들어오고 있지만, <Bold>성계 전체</>를 차트화하는 데는 시간이 걸리며, 그 동안에도 할 일이 많습니다.",
    "Unlocks circuit boards and basic computers which are essential components widely used in advanced modules and smaller starships.":
        "고급 모듈과 소형 우주선에 널리 사용되는 필수 부품인 회로 기판과 기본 컴퓨터를 잠금 해제합니다.",
    "Circuit boards and basic computers are now available to manufacture from the Fabricator.\n\nThese essential components are widely used in advanced modules and smaller starships.":
        "이제 가공기에서 회로 기판과 기본 컴퓨터를 제조할 수 있습니다.\n\n이 필수 부품들은 고급 모듈과 소형 우주선에 널리 사용됩니다.",
    "Unlocks technologies which let you automate raw material extraction by constructing <Bold>Miners</> onto <Bold>Ore Nodes</> that can be found on larger asteroids.":
        "더 큰 소행성에서 발견할 수 있는 <Bold>광맥</>에 <Bold>채굴기</>를 건설하여 원자재 추출을 자동화하는 기술을 잠금 해제합니다.",
    "You can now automate raw material extraction by constructing <Bold>Miners</> onto <Bold>Ore Nodes</> that can be found on larger asteroids.\n\nMiners can also be <Bold>built on</> to create mining sub-stations that serve your main station.":
        "이제 더 큰 소행성에서 발견할 수 있는 <Bold>광맥</>에 <Bold>채굴기</>를 건설하여 원자재 추출을 자동화할 수 있습니다.\n\n채굴기 위에 <Bold>건설</>하여 메인 스테이션을 보조하는 채굴 서브 스테이션을 만들 수도 있습니다.",
    "Unlocks the Small Shipyard which lets you construct smaller starships to satisfy more complex objectives.":
        "더 복잡한 목표를 달성하기 위해 작은 우주선을 건조할 수 있는 소형 조선소를 잠금 해제합니다.",
    "The <Bold>Small Shipyard</> has now been unlocked.\n\nSmaller starships can be constructed here to satisfy orders for <Bold>starships</> and complete later objectives.":
        "<Bold>소형 조선소</>가 잠금 해제되었습니다.\n\n여기서 작은 우주선을 건조하여 <Bold>우주선</> 주문을 처리하고 후속 목표를 완료할 수 있습니다.",
    "Unlocks the <Bold>Production Overview Panel</> which gives you a summary of how many of each <Bold>item, material and part</> in each location your station is <Bold>producing and using</>.":
        "각 장소에서 스테이션이 <Bold>생산하고 사용하는</> 각 <Bold>아이템, 재료, 부품</>의 수량 요약을 제공하는 <Bold>생산 개요 패널</>을 잠금 해제합니다.",
    "The <Bold>Production Overview Panel</> is a useful tool for optimising your stations.\n\nThis screen gives you a summary of how many of each <Bold>item, material and part</> in each location your station is <Bold>producing and using</>, making it easier to locate shortfalls in your production lines.":
        "<Bold>생산 개요 패널</>은 스테이션 최적화에 유용한 도구입니다.\n\n이 화면은 각 장소에서 스테이션이 <Bold>생산하고 사용하는</> 각 <Bold>아이템, 재료, 부품</>의 수량 요약을 제공해 생산 라인의 부족분을 쉽게 찾을 수 있게 합니다.",
    "To perform tasks around the TAU system, we'll need <Bold>ships</> - and lots of them.\n\nWithout them we cannot <Bold>explore</> or <Bold>visit other planets</> and <Bold>locations</> - or <Bold>defend ourselves</> from hostile threats...":
        "TAU 성계 곳곳에서 작업을 수행하려면 <Bold>함선</>이 필요합니다 — 그것도 많이.\n\n함선이 없으면 <Bold>탐험</>하거나 <Bold>다른 행성과 장소를 방문</>할 수 없고, 적대적 위협으로부터 <Bold>방어</>할 수도 없습니다...",
    "We need to <Bold>test our ship-building capabilities</> - let's start by producing the following <Bold>basic ships</>:\n\n{REQUIRED_SHIPS}":
        "<Bold>함선 건조 능력을 테스트</>해야 합니다 — 다음 <Bold>기본 함선</>들을 생산하는 것으로 시작합시다:\n\n{REQUIRED_SHIPS}",
    "Ship telemetry is all in the green Station Commander, I think we're ready to move on with more <Bold>advanced technologies and ships now</>.":
        "함선 원격측정이 모두 양호합니다 스테이션 사령관님, 이제 <Bold>더 고급의 기술과 함선</>으로 넘어갈 준비가 됐다고 생각합니다.",
    "We have made a major breakthrough in the development of superconducting materials.\n\nThis will allow us to fabricate even more complex and high-technology items.":
        "초전도 재료 개발에 큰 돌파구를 마련했습니다.\n\n이로써 훨씬 더 복잡하고 첨단의 아이템을 제작할 수 있게 됩니다.",
    "Unlocks robotic freighters and docks, letting you automate the movement of materials between remote parts of your station.":
        "스테이션의 원격 부분 간 재료 이동을 자동화할 수 있는 로봇 화물선과 도크를 잠금 해제합니다.",
    "You have now unlocked the <Bold>Freighter Dock</> and robotic <Bold>Freighter</>, which can be used to automate the transport of items, parts and materials between remote parts of your station - such as between Miners and your main base.\n\nConstruct one or more Docks on your station, and then build at least one Freighter from the Dock's popup menu.\n\nYou can then assign any combination of Docks for the selected Freighter to pick up and drop off items.":
        "이제 <Bold>화물선 도크</>와 로봇 <Bold>화물선</>이 잠금 해제되었습니다. 채굴기와 메인 기지 사이 같은 스테이션의 원격 부분 간 아이템, 부품, 재료 운송을 자동화하는 데 사용할 수 있습니다.\n\n스테이션에 도크를 하나 이상 건설한 다음, 도크 팝업 메뉴에서 화물선을 적어도 한 척 건조하세요.\n\n그런 다음 선택한 화물선이 픽업하고 배달할 도크 조합을 자유롭게 할당할 수 있습니다.",
    "Unlocks the Equipment Station which lets you manufacture equipment that can installed on your drone to enhance its capabilities":
        "드론에 장착하여 능력을 향상시킬 수 있는 장비를 제조할 수 있는 장비 정거장을 잠금 해제합니다",
    "The <Bold>Equipment Station</> is now available to construct from the Build menu.\n\nThe Equipment Station lets you craft equipment that can installed on your drone to enhance its capabilities.":
        "이제 건설 메뉴에서 <Bold>장비 정거장</>을 건설할 수 있습니다.\n\n장비 정거장은 드론에 장착해 능력을 향상시킬 수 있는 장비를 제작할 수 있게 합니다.",
    "Unlocks the ability to a Blueprint from modules selected using the Multi-Select tool which can then be easily placed onto your station.":
        "다중 선택 도구로 선택한 모듈로부터 청사진을 만들고, 이를 스테이션에 쉽게 배치할 수 있는 능력을 잠금 해제합니다.",
    "<Bold>Blueprints</> are now available from the Multi-Select tool popup menu.\n\nOnce you have selected multiple modules using the Multi-Select tool you can create a blueprint which can then be placed from the Build menu.":
        "이제 다중 선택 도구 팝업 메뉴에서 <Bold>청사진</>을 사용할 수 있습니다.\n\n다중 선택 도구로 여러 모듈을 선택한 후 청사진을 만들 수 있으며, 이는 건설 메뉴에서 배치할 수 있습니다.",
    "Unlocks the Beam Turret which automates station defence against incoming meteors or enemies.":
        "다가오는 운석이나 적에 대한 스테이션 방어를 자동화하는 빔 포탑을 잠금 해제합니다.",
    "You have now unlocked the <Bold>Beam Defence Turret</> which can be constructed around your stations and sub-stations in order to automatically defend from incoming <Bold>meteors</>, <Bold>enemy drones</> and <Bold>creatures</>.":
        "이제 <Bold>빔 방어 포탑</>이 잠금 해제되었습니다. 스테이션과 서브 스테이션 주변에 건설하여 다가오는 <Bold>운석</>, <Bold>적 드론</>, <Bold>생명체</>로부터 자동으로 방어할 수 있습니다.",
    "Unlocks Mk 2 Storage Units which can store considerably more items, materials and parts as well as supply more linked modules due to their faster max item send speed.":
        "더 많은 아이템, 재료, 부품을 저장할 수 있고 최대 아이템 전송 속도가 빨라 더 많은 연결 모듈에 공급할 수 있는 Mk 2 저장 유닛을 잠금 해제합니다.",
    "<Bold>Mk 2 Storage Units</> have now been unlocked. \n\nThese can store considerably more items, materials and parts as well as supply more linked modules due to their faster max item send speed.":
        "<Bold>Mk 2 저장 유닛</>이 잠금 해제되었습니다.\n\n더 많은 아이템, 재료, 부품을 저장할 수 있고, 최대 아이템 전송 속도가 빨라 더 많은 연결 모듈에 공급할 수 있습니다.",
    "Unlocks the Nano Repair consumable which restores your Drone's hitpoints and can be crafted in the Equipment Station":
        "드론의 체력을 회복시키며 장비 정거장에서 제작할 수 있는 나노 수리 소모품을 잠금 해제합니다",
    "The <Bold>Nano Repair</> equipment has now been unlocked. \n\nCraft this consumable in the Equipment Station and equip it in an equipment slot on your drone to restore hitpoints instantly when your drone is damaged.":
        "<Bold>나노 수리</> 장비가 잠금 해제되었습니다.\n\n장비 정거장에서 이 소모품을 제작하여 드론의 장비 슬롯에 장착하면, 드론이 피해를 입었을 때 체력을 즉시 회복할 수 있습니다.",
    "Our <Bold>Deep Space Scans</> have revealed potentially resource-rich locations spread throughout the system - However we'll need to <Bold>scout these locations</> before we can decide where we should expand our facilities to next...":
        "우리의 <Bold>심우주 스캔</>으로 성계 전역에 자원이 풍부할 가능성이 있는 장소들이 드러났습니다 — 그러나 시설을 다음에 확장할 곳을 결정하기 전에 <Bold>이 장소들을 정찰</>해야 합니다...",
    "To do this, we'll need to <Bold>construct</> the following <Bold>scout-ships</>:\n\n{REQUIRED_SHIPS}":
        "이를 위해 다음 <Bold>정찰선</>들을 <Bold>건조</>해야 합니다:\n\n{REQUIRED_SHIPS}",
    "Our scouting mission has identified the presence of a <Bold>nearby Gas Giant</> that we've named <Bold>Titania...</>":
        "정찰 임무는 우리가 <Bold>티타니아</>라고 명명한 <Bold>인근 가스 거성</>의 존재를 확인했습니다...",
    "Gas Giants are the ideal place to deploy <Bold>cloud-miners</> and automate the production of <Bold>hydrogen gas</> used in our fusion reactors and starships - so this should be our <Bold>primary objective</> for further expansion.":
        "가스 거성은 <Bold>구름 채굴기</>를 배치하고 융합로와 우주선에 사용되는 <Bold>수소 가스</> 생산을 자동화하기에 이상적인 장소입니다 — 따라서 이것이 추가 확장의 <Bold>주요 목표</>가 되어야 합니다.",
    "Unlocks modules and processes required for the production of Hydrogen gas used in Fusion Reactors and starship fuel.":
        "융합로와 우주선 연료에 사용되는 수소 가스 생산에 필요한 모듈과 공정을 잠금 해제합니다.",
    "You now have access to <Bold>Hydrogen production</> which is used in fusion reactors and for fuelling starships.\n\n<Bold>Refineries</> can convert <Bold>water</> from <Bold>ice asteroids</> into <Bold>hydrogen gas</>, which can then be piped around your station and either stored or used in <Bold>Fusion Reactors</> to produce large amounts of power.":
        "이제 융합로와 우주선 연료 주입에 사용되는 <Bold>수소 생산</>이 가능합니다.\n\n<Bold>정제소</>는 <Bold>얼음 소행성</>의 <Bold>물</>을 <Bold>수소 가스</>로 변환할 수 있으며, 이를 스테이션 곳곳으로 파이프 운반하여 저장하거나 <Bold>융합로</>에서 대량의 전력을 생산할 수 있습니다.",
    "You have unlocked a higher tier of starship construction, including additional starship parts and more advanced ship classes ready to be built from the Shipyard.":
        "조선소에서 건조할 수 있는 추가 우주선 부품과 더 고급의 함급을 포함한 더 높은 등급의 우주선 건조를 잠금 해제했습니다.",
    "Unlocks breakthroughs in Fusion Energy production, giving you access to advanced power generation options.":
        "융합 에너지 생산의 돌파구를 잠금 해제하여 고급 전력 생산 옵션에 접근할 수 있게 합니다.",
    "You have now unlocked the <Bold>Fusion Reactor</> which utilises Hydrogen Gas to sustain a fusion reaction and generate large amounts of clean energy.\n\nWe highly recommend moving from more primitive energy generation systems onto Fusion as soon as possible to secure your power needs.":
        "이제 수소 가스를 사용해 융합 반응을 유지하고 대량의 청정 에너지를 생성하는 <Bold>융합로</>가 잠금 해제되었습니다.\n\n전력 수요를 확보하기 위해 가능한 한 빨리 더 원시적인 에너지 생산 시스템에서 융합으로 이전할 것을 강력히 권장합니다.",
    "Unlocks the Tug Bay and Ship Tugs which will automatically move starships around your station  - such as from a <Bold>Shipyard</> into a <Bold>Fuel Depot</> - or into a <Bold>clear space</> next to your station ready to be shipped.":
        "스테이션 주변에서 우주선을 자동으로 이동시키는 예인선 도크와 함선 예인선을 잠금 해제합니다 — 예를 들어 <Bold>조선소</>에서 <Bold>연료 저장고</>로, 또는 출하 준비된 스테이션 옆 <Bold>빈 공간</>으로 이동시킵니다.",
    "<Bold>Tug Bays</> will automatically move starships between station modules - such as from a <Bold>Shipyard</> into a <Bold>Fuel Depot</> - or into a <Bold>clear space</> next to your station ready to be shipped.\n\nUse the <Bold>Link</> function to assign a Shipyard to a Fuel Depot or a space near your station and the nearest free tug will automatically be assigned.\n\nPlease note that Tugs have a maximum range that they will pick ships up inside - hold Shift to see this.":
        "<Bold>예인선 도크</>는 스테이션 모듈 사이에서 우주선을 자동으로 이동시킵니다. 예를 들어 <Bold>조선소</>에서 <Bold>연료 저장고</>로, 또는 출하 준비된 스테이션 옆 <Bold>빈 공간</>으로.\n\n<Bold>연결</> 기능으로 조선소를 연료 저장고나 스테이션 근처 공간에 할당하면 가장 가까운 사용 가능한 예인선이 자동 배정됩니다.\n\n참고: 예인선은 함선을 픽업할 수 있는 최대 사정거리가 있습니다 — Shift를 눌러 확인하세요.",
    "Unlocks the Power Linker which can be used to connect the power networks of remote parts of your station.":
        "스테이션의 원격 부분의 전력망을 연결할 수 있는 전력 연결기를 잠금 해제합니다.",
    "<Bold>Power Linkers</> can be built to link the power grids of remote parts of your station - such as Miners - to your main station and centralize power generation.":
        "<Bold>전력 연결기</>를 건설하여 채굴기 같은 원격 스테이션 부품의 전력망을 메인 스테이션과 연결해 전력 생산을 중앙화할 수 있습니다.",
    "Unlocks an equippable Energy Shield that can be crafted in the Equipment Station and assigned to a slot on your Drone.":
        "장비 정거장에서 제작하여 드론 슬롯에 할당할 수 있는 장착형 에너지 방어막을 잠금 해제합니다.",
    "You've unlocked the Energy Shield.\n\nThis can be crafted in the Machine Shop and assigned to a slot on your Drone to project a personal force-field which absorbs incoming damage and is regenerated over time.":
        "에너지 방어막을 잠금 해제했습니다.\n\n기계 공방에서 제작하여 드론 슬롯에 할당하면, 들어오는 피해를 흡수하고 시간이 지나면 재생되는 개인 역장을 투사할 수 있습니다.",
    "Unlocks the <Bold>Drone Teleporter</> which can be constructed at your remote bases - such as mines - and used to instantly travel between them.":
        "광산 같은 원격 기지에 건설하여 그 사이를 즉시 이동할 수 있는 <Bold>드론 텔레포터</>를 잠금 해제합니다.",
    "You have unlocked the <Bold>Drone Teleporter</>.\n\nConstruct teleporters on remote areas of your stations to instantly travel between them, and speed up time taken to traverse your factories.":
        "<Bold>드론 텔레포터</>가 잠금 해제되었습니다.\n\n스테이션의 원격 지역에 텔레포터를 건설하여 그 사이를 즉시 이동하고 공장을 가로지르는 시간을 단축하세요.",
    "The nearby Gas Giant - Titania - will be the perfect location to <Bold>cloud-mine</> for Hydrogen Gas.\n\nWe can use this in our <Bold>Fusion Reactors</> and to <Bold>fuel our ships</> so we can launch much longer-range missions around the system...":
        "인근 가스 거성 — 티타니아 — 는 수소 가스를 <Bold>구름 채굴</>하기에 완벽한 장소가 될 것입니다.\n\n이를 <Bold>융합로</>에 사용하고 <Bold>함선의 연료</>로 사용하면 성계 곳곳에서 훨씬 더 장거리 임무를 시작할 수 있습니다...",
    "We've prepared a number of <Bold>Sensor Packages</> we'd like you to drop into low-orbit around Titania, so we'll need you to build the <Bold>following ships</> to accomplish this:\n\n{REQUIRED_SHIPS}":
        "티타니아 저궤도에 투하할 <Bold>센서 패키지</>를 여러 개 준비했습니다. 이를 위해 <Bold>다음 함선</>들을 건조해 주셔야 합니다:\n\n{REQUIRED_SHIPS}",
    "The sensor network we deployed has determined what appears to be the <Bold>perfect location</> for us to establish a <Bold>cloud-mining station</> in the upper layers of Titania's atmosphere.\n\nThis location has been added to the <Bold>System View</> and you can now establish a <Bold>new station</> there as soon as you have the required resources.":
        "전개한 센서 네트워크가 티타니아 대기 상층부에 <Bold>구름 채굴 스테이션</>을 설립할 <Bold>완벽한 장소</>로 보이는 곳을 확인했습니다.\n\n이 장소가 <Bold>시스템 뷰</>에 추가되었으며, 필요한 자원이 있으면 그곳에 <Bold>새 스테이션</>을 설립할 수 있습니다.",
    "After establishing ourselves in the <Bold>Tau System</>, we conducted tests on our manufacturing capabilities to make sure they survived the journey here.\n\nWe then produced several exploration ships and sent them out to scout the local surroundings, discovering a nearby <Bold>Gas Giant</> that we can mine for <Bold>Hydrogen Gas</> for use in our Fusion Reactors and Starship fuel.":
        "<Bold>타우 성계</>에 자리 잡은 후, 제조 능력이 여기까지의 여정을 견뎠는지 확인하기 위해 테스트를 수행했습니다.\n\n그런 다음 여러 탐사선을 생산해 주변을 정찰하기 위해 보냈고, 융합로와 우주선 연료에 사용할 <Bold>수소 가스</>를 채굴할 수 있는 인근 <Bold>가스 거성</>을 발견했습니다.",
    "Unlocks the Wormhole Terminus module which can be used to link stations in different Zones together.":
        "서로 다른 구역의 스테이션을 연결하는 데 사용할 수 있는 웜홀 터미너스 모듈을 잠금 해제합니다.",
    "You have now unlocked the <Bold>Wormhole Terminus</> which can be connected to a Terminus in a distant location to form a quantum gateway.\n\nItems, materials and parts can be fed into a Terminus and will appear in the Output of the gateway on the other side.\n\nYou can also connect multiple pipes to the input pipe-connectors on one Terminus and they will arrive in the same-numbered output pipe-connectors on the other side - ready to be piped elsewhere in your station.":
        "이제 먼 장소의 터미너스와 연결되어 양자 게이트웨이를 형성할 수 있는 <Bold>웜홀 터미너스</>가 잠금 해제되었습니다.\n\n아이템, 재료, 부품을 터미너스에 투입하면 반대편 게이트웨이의 출력으로 나타납니다.\n\n또한 한 터미너스의 입력 파이프 연결기에 여러 파이프를 연결할 수 있으며, 이는 반대편의 같은 번호 출력 파이프 연결기로 도착해 스테이션 다른 곳으로 운반될 준비가 됩니다.",
    "Unlocks new modules for taking advantage of being in the lower atmosphere of a Gas Giant.":
        "가스 거성 하층 대기에 있는 이점을 활용하기 위한 새 모듈들을 잠금 해제합니다.",
    "<Bold>Cloud Mining Stations</> let you deploy <Bold>Cloud Miners</> into the atmosphere of a gas giant and automate the collection of large amounts of hydrogen gas.\n\nConstruct <Bold>Vortex generators</> inside the atmosphere of <Bold>Gas giants</> to produce large amounts of power at very little cost.":
        "<Bold>구름 채굴 스테이션</>은 <Bold>구름 채굴기</>를 가스 거성의 대기 중에 배치하여 대량의 수소 가스 수집을 자동화합니다.\n\n<Bold>가스 거성</>의 대기 안에 <Bold>볼텍스 발전기</>를 건설하면 매우 적은 비용으로 대량의 전력을 생산할 수 있습니다.",
    "Unlocks new processes for converting Nitratium into explosive compounds ready to be used in military applications.":
        "니트라튬을 군사용으로 사용 가능한 폭발성 화합물로 변환하는 새 공정을 잠금 해제합니다.",
    "You can now synthesize the highly explosive bio-compound <Bold>Nitrox</>, which can be produced by refining the <Bold>Nitratium</> recovered from gas-giant flora and fauna and combining it in a <Bold>Refinery</> with <Bold>Oxygen</> extracted from <Bold>Water</>.":
        "이제 강력한 폭발성 생물 화합물 <Bold>나이트록스</>를 합성할 수 있습니다. 가스 거성의 동식물에서 회수한 <Bold>니트라튬</>을 정제하고 <Bold>물</>에서 추출한 <Bold>산소</>와 <Bold>정제소</>에서 결합하여 생산할 수 있습니다.",
    "Unlocks the Fuel Depot which can be used to fuel starships with Hydrogen and complete higher-level objectives.":
        "수소로 우주선에 연료를 주입하고 더 높은 단계의 목표를 완료할 수 있는 연료 저장고를 잠금 해제합니다.",
    "You have unlocked the <Bold>Fuel Depot</> which can be supplied with Hydrogen Gas and fuel waiting starships.\n\nYou can <Fuelled>fuel</> a starship by dragging it into an empty <Bold>Fuel Depot</> and fuelling will begin automatically.\n\nYou can also link a Shipyard to a Fuel Depot to have a free tug automatically move ships into the depot.":
        "수소 가스를 공급받아 대기 중인 우주선에 연료를 주입할 수 있는 <Bold>연료 저장고</>가 잠금 해제되었습니다.\n\n빈 <Bold>연료 저장고</>에 우주선을 끌어 넣으면 <Fuelled>연료 주입</>이 자동으로 시작됩니다.\n\n조선소를 연료 저장고에 연결하면 사용 가능한 예인선이 자동으로 함선을 저장고로 이동시킵니다.",
    "Unlocks the Mk 2 Smelter which can process raw materials at a faster rate and increase production.":
        "원자재를 더 빠른 속도로 처리하고 생산을 증가시키는 Mk 2 제련소를 잠금 해제합니다.",
    "<Bold>Mk 2 Smelters</> have now been unlocked. \n\nThese can process raw materials into usable metals and other materials at a higher rate and increase the output of your factory immensely.":
        "<Bold>Mk 2 제련소</>가 잠금 해제되었습니다.\n\n원자재를 사용 가능한 금속과 기타 재료로 더 빠른 속도로 처리하여 공장의 출력을 크게 증가시킵니다.",
    "Unlocks the Mk 2 Miner which can extract ores at a faster rate and increase factory output.":
        "광석을 더 빠른 속도로 추출하고 공장 출력을 증가시키는 Mk 2 채굴기를 잠금 해제합니다.",
    "<Bold>Mk 2 Miners</> have now been unlocked. \n\nThese can extract raw materials at a higher rate and increase the output of your factory immensely.":
        "<Bold>Mk 2 채굴기</>가 잠금 해제되었습니다.\n\n원자재를 더 빠른 속도로 추출하여 공장의 출력을 크게 증가시킵니다.",
    "Unlocks an equippable <Bold>Missile Launcher</> that can be crafted in the <Bold>Equipment Station</> and assigned to a slot on your Drone.":
        "<Bold>장비 정거장</>에서 제작하여 드론 슬롯에 할당할 수 있는 장착형 <Bold>미사일 발사기</>를 잠금 해제합니다.",
    "You've unlocked the <Bold>Missile Launcher</>.\n\nThis can be crafted in the <Bold>Equipment Station</> and assigned to a slot on your Drone to fire <Bold>explosive-tipped missiles</> at enemies.":
        "<Bold>미사일 발사기</>를 잠금 해제했습니다.\n\n<Bold>장비 정거장</>에서 제작하여 드론 슬롯에 할당하면 적에게 <Bold>폭발성 탄두 미사일</>을 발사할 수 있습니다.",
    "Things are progressing well here, but we're running low on <Bold>raw resources</> so we need to find <Bold>additional mining locations</> we can exploit...":
        "여기는 잘 진행되고 있지만, <Bold>원자재</>가 부족해지고 있어 활용할 수 있는 <Bold>추가 채굴 장소</>를 찾아야 합니다...",
    "To explore further afield we'll need to dispatch scout-ships which have been <Bold>fuelled</>, as well as <Bold>tanker-ships</> which can refuel them on their journey...":
        "더 먼 곳을 탐사하려면 <Bold>연료가 주입된</> 정찰선과 함께 그것들을 여정 중에 재급유할 수 있는 <Bold>유조선</>도 파견해야 합니다...",
    "Let us know when you've produced the <Bold>following ships</>:\n\n{REQUIRED_SHIPS}":
        "<Bold>다음 함선</>들을 생산하시면 알려주세요:\n\n{REQUIRED_SHIPS}",
    "Our expedition has discovered a <Bold>resource-rich mining location</> in the secondary Asteroid Belt which will greatly increase our supply of raw materials and enable us to expand even further.\n\nThis location has been added to the <Bold>System View</> and you can now establish a <Bold>new station</> there as soon as you have the required resources.":
        "우리 탐사대는 2차 소행성대에서 <Bold>자원이 풍부한 채굴 장소</>를 발견했습니다. 이는 원자재 공급을 크게 증가시키고 더 확장할 수 있게 해줍니다.\n\n이 장소가 <Bold>시스템 뷰</>에 추가되었으며, 필요한 자원이 있으면 그곳에 <Bold>새 스테이션</>을 설립할 수 있습니다.",
    "Unlocks the Plasma Forge which can be used to fuse metallic elements together into superstrong alloys.":
        "금속 원소를 융합해 초강력 합금으로 만들 수 있는 플라즈마 용광로를 잠금 해제합니다.",
    "Unlocks the Bio-Extractor which can automate the extraction of biological compounds from larger flora and fauna.":
        "더 큰 동식물에서 생물학적 화합물 추출을 자동화할 수 있는 바이오 추출기를 잠금 해제합니다.",
    "Unlocks the Mk 2 Freighter Dock and Mk 2 Freighter which can transport more items as well as liquids and gases around your station.":
        "스테이션 주변에서 더 많은 아이템뿐만 아니라 액체와 기체까지 운송할 수 있는 Mk 2 화물선 도크와 Mk 2 화물선을 잠금 해제합니다.",
    "<Bold>Mk 2 Freighter Docks</> can store considerably more items ready for transport, as well as gases and liquids. They can also output items at a faster rate, letting you link more modules to them and avoid bottlenecks.\n\n<Bold>Mk 2 Freighters</> can be constructed from Mk 2 Docks, and these can also transport more items at higher speeds, as well as gases and liquids too.":
        "<Bold>Mk 2 화물선 도크</>는 운송 준비가 된 아이템과 함께 기체와 액체도 훨씬 더 많이 저장할 수 있습니다. 또한 아이템을 더 빠른 속도로 출력할 수 있어 더 많은 모듈을 연결하고 병목 현상을 피할 수 있습니다.\n\n<Bold>Mk 2 화물선</>은 Mk 2 도크에서 건조할 수 있으며, 더 많은 아이템을 더 빠른 속도로 운송할 수 있고 기체와 액체도 운송할 수 있습니다.",
    "Enables larger blueprint area and a higher maximum number of modules inside a blueprint":
        "더 큰 청사진 영역과 청사진 안의 더 많은 최대 모듈 수를 가능하게 합니다",
    "You have unlocked expanded blueprints, which lets you select and add <Bold>more modules</> to a blueprint, as well as an expanded blueprint <Bold>area</>.":
        "확장 청사진을 잠금 해제했습니다. 청사진에 <Bold>더 많은 모듈</>을 선택해 추가할 수 있고, 확장된 청사진 <Bold>영역</>도 사용할 수 있습니다.",
    "Unlocks the <Bold>Recycler</> which you can feed unwanted resources into in exhange for <Bold>Tokens</> that you can spend on various rewards.":
        "원치 않는 자원을 투입해 다양한 보상에 사용할 수 있는 <Bold>토큰</>으로 교환할 수 있는 <Bold>재활용기</>를 잠금 해제합니다.",
    "The <Bold>Recycler</> has been unlocked.\n\nFeed unwanted resources into this module in exchange for <Bold>Tokens</> that you can spend on various rewards.":
        "<Bold>재활용기</>가 잠금 해제되었습니다.\n\n원치 않는 자원을 이 모듈에 투입하여 다양한 보상에 사용할 수 있는 <Bold>토큰</>으로 교환하세요.",
    "Unlocks the <Bold>Laboratory</> and the ability to research <Bold>alternative recipes</> for producing various items, materials and parts":
        "<Bold>연구소</>와 다양한 아이템, 재료, 부품을 생산하기 위한 <Bold>대체 제작법</> 연구 능력을 잠금 해제합니다",
    "The <Bold>Laboratory</> has been unlocked.\n\nFeed items, parts and materials into this module for analysis and you can unlock <Bold>alternative</> and <Bold>more efficient</> recipes for producing them.":
        "<Bold>연구소</>가 잠금 해제되었습니다.\n\n분석을 위해 아이템, 부품, 재료를 이 모듈에 투입하면 그것들을 생산하기 위한 <Bold>대체</> 및 <Bold>더 효율적인</> 제작법을 잠금 해제할 수 있습니다.",
    "The <Bold>Ice Planet Glacialis</> is the perfect location to automate the harvesting of <Bold>water ice</> for use in oxygen production and other industries...":
        "<Bold>얼음 행성 글라시알리스</>는 산소 생산과 기타 산업에 사용할 <Bold>얼음</> 채집을 자동화하기에 완벽한 장소입니다...",
    "However, the rings of this planet are highly <Bold>unstable</>, so we'll need to deploy more <Bold>advanced ships and sensors</> to locate a stable zone we can establish a station within...":
        "하지만 이 행성의 고리는 매우 <Bold>불안정</>하므로, 스테이션을 설립할 수 있는 안정 구역을 찾기 위해 더 <Bold>고급 함선과 센서</>를 배치해야 합니다...",
    "<Bold>Neutron Explorers</> are perfect for this task, and we can use the new <Bold>Stratos Prospecters</> to retrieve samples from deep within the ring. Please produce the following:\n\n{REQUIRED_SHIPS}":
        "<Bold>중성자 탐사선</>이 이 작업에 적합하며, 새 <Bold>스트라토스 탐사선</>을 사용해 고리 깊숙한 곳에서 샘플을 회수할 수 있습니다. 다음을 생산해 주세요:\n\n{REQUIRED_SHIPS}",
    "We believe that we've identified a stable zone deep within the rings of <Bold>Glacialis</> that will enable us to automate the mining of Water Ice to be used in our production chains.\n\nThis location has been added to the <Bold>System View</> and you can now establish a <Bold>new station</> there as soon as you have the required resources.":
        "<Bold>글라시알리스</>의 고리 깊숙한 곳에서 안정 구역을 확인한 것으로 보이며, 이를 통해 생산 체인에 사용할 얼음 채굴을 자동화할 수 있습니다.\n\n이 장소가 <Bold>시스템 뷰</>에 추가되었으며, 필요한 자원이 있으면 그곳에 <Bold>새 스테이션</>을 설립할 수 있습니다.",
    "Unlocks highly advanced manufacturing processes providing access to new items, materials and parts.":
        "새로운 아이템, 재료, 부품에 접근할 수 있는 고도로 진보한 제조 공정을 잠금 해제합니다.",
    "<Bold>Manufactories</> can now be constructed from the Build menu.\n\nThese giant production machines can produce some of the largest and most complex parts and items you'll need for more advanced modules and starships.":
        "이제 건설 메뉴에서 <Bold>제조소</>를 건설할 수 있습니다.\n\n이 거대한 생산 기계는 더 고급 모듈과 우주선에 필요한 가장 크고 복잡한 부품과 아이템 일부를 생산할 수 있습니다.",
    "Unlocks ultra-high-speed supercomputing technologies which power larger starships and advanced station modules.":
        "더 큰 우주선과 고급 스테이션 모듈을 구동하는 초고속 슈퍼컴퓨팅 기술을 잠금 해제합니다.",
    "You've now unlocked Supercomputers which are an essential component in the most advanced module and starship production.":
        "이제 가장 고급의 모듈과 우주선 생산에 필수적인 슈퍼컴퓨터를 잠금 해제했습니다.",
    "<Bold>Medium Shipyards</> are now available for you to fulfil ever-larger and more complex starship orders.\n\nNote: Larger ships may require <Bold>Micro Fusion Reactors</> to be installed. These ships must be fuelled quickly after completion to avoid catastrophic reactor meltdown.":
        "<Bold>중형 조선소</>를 사용할 수 있어 점점 더 크고 복잡한 우주선 주문을 처리할 수 있습니다.\n\n참고: 더 큰 우주선은 <Bold>마이크로 융합로</>를 설치해야 할 수 있습니다. 이러한 우주선은 완성 후 빠르게 연료를 주입해야 원자로 멜트다운을 방지할 수 있습니다.",
    "Enhanced Base Defences are now available for construction.\n\nWe recommend building enhanced <Bold>Missile Defence Turrets</> on your most vulnerable stations to safely defend against larger groups of enemies.":
        "강화 기지 방어 시설을 건설할 수 있습니다.\n\n가장 취약한 스테이션에 강화된 <Bold>미사일 방어 포탑</>을 건설하여 더 큰 적 무리로부터 안전하게 방어할 것을 권장합니다.",
    "Unlocks the <Bold>Mk 3 Storage Unit</> and <Bold>Mk 2 Storage Tank</> which can store even more items and outputs items at a faster rate.":
        "더 많은 아이템을 저장하고 더 빠른 속도로 출력할 수 있는 <Bold>Mk 3 저장 유닛</>과 <Bold>Mk 2 저장 탱크</>를 잠금 해제합니다.",
    "<Bold>Mk 3 Storage Units</> and <Bold>Mk 2 Storage Tanks</> have now been unlocked. \n\nThese can store considerably more items, materials and parts as well as supply more linked modules due to their faster max item send speed.":
        "<Bold>Mk 3 저장 유닛</>과 <Bold>Mk 2 저장 탱크</>가 잠금 해제되었습니다.\n\n더 많은 아이템, 재료, 부품을 저장할 수 있고, 최대 아이템 전송 속도가 빨라 더 많은 연결 모듈에 공급할 수 있습니다.",
    "Unlocks the Micro Drone which when equipped will shoot down incoming projectiles.":
        "장착하면 다가오는 발사체를 격추하는 마이크로 드론을 잠금 해제합니다.",
    "The <Bold>Defence Micro Drone</> has now been unlocked. \n\nThis can be crafted in the Equipment Station and when equipped can shoot down incoming projectiles.":
        "<Bold>방어 마이크로 드론</>이 잠금 해제되었습니다.\n\n장비 정거장에서 제작할 수 있으며, 장착하면 다가오는 발사체를 격추할 수 있습니다.",
    "Its time to <Bold>expand our operations</> here once again, Station Commander, and for that we'll need more <Bold>raw materials...</>":
        "다시 한 번 <Bold>운영을 확장</>할 시간입니다, 스테이션 사령관님. 이를 위해 더 많은 <Bold>원자재</>가 필요합니다...",
    "We propose to dispatch <Bold>additional scouting missions</> to the following locations:\n\nOne mission will explore the far distant, <Bold>third Asteroid Belt</>, while the other mission will investigate some <Bold>strange energy readings</> we've detected from the <Bold>Lava Planet</> we've named <Bold>Cerberus...</>":
        "다음 장소들에 <Bold>추가 정찰 임무</>를 파견할 것을 제안합니다:\n\n한 임무는 멀리 떨어진 <Bold>3차 소행성대</>를 탐사하고, 다른 임무는 우리가 <Bold>케르베로스</>라고 명명한 <Bold>용암 행성</>에서 감지한 <Bold>이상한 에너지 신호</>를 조사할 것입니다...",
    "These are <Bold>hazardous, long-distance missions</>, so we we'll need additional <Bold>heavy ships</> to successfully carry them out. Please construct the <Bold>following ships:</>\n\n{REQUIRED_SHIPS}":
        "이는 <Bold>위험하고 장거리인 임무</>이므로, 성공적으로 수행하려면 추가 <Bold>중형 함선</>이 필요합니다. <Bold>다음 함선들을 건조</>해 주세요:\n\n{REQUIRED_SHIPS}",
    "We have <Bold>good news</> and <Bold>bad news</> Commander: The expedition to the most distant Asteroid Belt was a success, and this location has been added to your <Bold>System View</> for immediate expansion...":
        "<Bold>좋은 소식</>과 <Bold>나쁜 소식</>이 있습니다 사령관님: 가장 먼 소행성대로의 탐사는 성공했고, 이 장소가 즉각 확장을 위해 <Bold>시스템 뷰</>에 추가되었습니다...",
    "However, we have <Bold>lost all contact</> with the ships sent to the <Bold>Lava Planet Cerberus</>, and we fear that they have all been <Bold>destroyed</> by an <Bold>unknown hostile force</>. \n\nThe <Bold>energy readings</> coming from this location cannot be ignored however, so we will have to <Bold>mount another mission</> to this location in the future.":
        "그러나 <Bold>용암 행성 케르베로스</>로 보낸 함선들과 <Bold>모든 통신이 끊겼고</>, <Bold>알 수 없는 적대 세력</>에 의해 모두 <Bold>파괴</>된 것이 우려됩니다.\n\n그러나 이 장소에서 오는 <Bold>에너지 신호</>는 무시할 수 없으므로, 향후 이 장소에 <Bold>또 다른 임무를 시행</>해야 할 것입니다.",
    "After expanding into the Gas Giant Titania, we discovered that the rings of a nearby Ice Planet contain everything we need to expand and automate our water-to-oxygen pipeline.\n\nIf we hope to mass-produce explosives and weapons, this is going to have to be our next destination.":
        "가스 거성 티타니아로 확장한 후, 인근 얼음 행성의 고리에 물-산소 파이프라인을 확장하고 자동화하는 데 필요한 모든 것이 있다는 사실을 발견했습니다.\n\n폭발물과 무기를 대량 생산하려면, 이곳이 다음 목적지가 되어야 합니다.",
    "Unlocks the ability to produce warheads, missiles and the Ammo Depot to install them into military-grade starships.":
        "탄두, 미사일과 그것들을 군용 우주선에 설치할 수 있는 탄약 저장고 생산 능력을 잠금 해제합니다.",
    "You have now unlocked the <Bold>Ammo Factory</> and <Bold>Ammo Depot</>.\n\n<Armed>Ship Ammo</> is produced in the <Bold>Ammo Factory</> and loaded into a ship from the <Bold>Ammo Depot</>.\n\nAs with Fuel Depots, you can link a module to an Ammo Depot and nearby tugs will automatically transport ships between them.":
        "이제 <Bold>탄약 공장</>과 <Bold>탄약 저장고</>가 잠금 해제되었습니다.\n\n<Armed>함선 탄약</>은 <Bold>탄약 공장</>에서 생산되며 <Bold>탄약 저장고</>에서 함선에 장전됩니다.\n\n연료 저장고와 마찬가지로, 모듈을 탄약 저장고에 연결하면 인근 예인선이 자동으로 함선을 그 사이로 운송합니다.",
    "You have now unlocked Military Starships which must be provided with the required Ammo.\n\nAmmo is produced in the Ammo Factory, and can be deployed from the Ammo Depot.":
        "이제 필요한 탄약을 공급받아야 하는 군용 우주선을 잠금 해제했습니다.\n\n탄약은 탄약 공장에서 생산되며, 탄약 저장고에서 배치할 수 있습니다.",
    "Unlocks the <Bold>Mk 3 Miner</> and <Bold>Mk 2 Bio-Extractor</> to further increase maximum raw material extraction rate.":
        "최대 원자재 추출 속도를 더 증가시키는 <Bold>Mk 3 채굴기</>와 <Bold>Mk 2 바이오 추출기</>를 잠금 해제합니다.",
    "<Bold>Mk 3 Miners</> and <Bold>Mk 2 Bio-Extractors</> have now been unlocked. \n\nThese can extract raw materials at a higher rate and increase the output of your factory immensely.":
        "<Bold>Mk 3 채굴기</>와 <Bold>Mk 2 바이오 추출기</>가 잠금 해제되었습니다.\n\n원자재를 더 빠른 속도로 추출하여 공장의 출력을 크게 증가시킵니다.",
    "Unlocks the Mk 2 Fuel Depot which has a faster fuel transfer rate and fuel larger starships more efficiently.":
        "더 빠른 연료 전달 속도를 가지고 더 큰 우주선에 더 효율적으로 연료를 주입할 수 있는 Mk 2 연료 저장고를 잠금 해제합니다.",
    "The <Bold>Mk 2 Fuel Depot</> has now been unlocked.\n\nThis module has a faster fuel transfer rate and can fuel larger starships more efficiently.":
        "<Bold>Mk 2 연료 저장고</>가 잠금 해제되었습니다.\n\n이 모듈은 연료 전달 속도가 더 빠르고 더 큰 우주선에 더 효율적으로 연료를 주입할 수 있습니다.",
    "Unlocks the Mk 3 Freighter Dock and Mk 3 Freighter which can transport items even faster around your stations.":
        "스테이션 주변에서 아이템을 훨씬 더 빠르게 운송할 수 있는 Mk 3 화물선 도크와 Mk 3 화물선을 잠금 해제합니다.",
    "<Bold>Mk 3 Freighter Docks</> can store considerably more items ready for transport. They can also output items at a faster rate, letting you link more modules to them and avoid bottlenecks.\n\n<Bold>Mk 3 Freighters</> can be constructed from Mk 3 Docks, and these can also transport more items at higher speeds, as well as having a mounted Beam Turret for defence against nearby enemies.":
        "<Bold>Mk 3 화물선 도크</>는 운송 준비가 된 아이템을 훨씬 더 많이 저장할 수 있습니다. 또한 아이템을 더 빠른 속도로 출력할 수 있어 더 많은 모듈을 연결하고 병목 현상을 피할 수 있습니다.\n\n<Bold>Mk 3 화물선</>은 Mk 3 도크에서 건조할 수 있으며, 더 많은 아이템을 더 빠른 속도로 운송할 수 있고 인근 적에 대한 방어를 위해 빔 포탑이 장착되어 있습니다.",
    "We've still had <Bold>no contact</> from the mission sent to the <Bold>Lava Planet Cerberus</>, so we have no choice but to make sure that any future operations sent to this area can defend themselves against <Bold>hostile threats...</>":
        "<Bold>용암 행성 케르베로스</>로 보낸 임무로부터 여전히 <Bold>통신이 없으므로</>, 이 지역으로 보내는 미래의 모든 작전이 <Bold>적대적 위협</>에 맞서 스스로를 방어할 수 있도록 보장하는 것 외에 선택의 여지가 없습니다...",
    "Energy readings point to this area being a potential source of <Bold>Exotic Matter</> however, so we must mount <Bold>another expedition</> to investigate this further...":
        "그러나 에너지 신호는 이 지역이 <Bold>이그조틱 물질</>의 잠재적 공급원임을 시사하므로, 이를 더 조사하기 위해 <Bold>또 다른 탐사대</>를 시행해야 합니다...",
    "With this in mind we recommend that we assemble a <Bold>military force</> to explore this area and find the source of the exotic readings emanating from the region. Please build the following ships:\n\n{REQUIRED_SHIPS}":
        "이를 염두에 두고, 이 지역을 탐사하고 그 지역에서 발산되는 이그조틱 신호의 원천을 찾기 위해 <Bold>군사력</>을 결집할 것을 권장합니다. 다음 함선들을 건조해 주세요:\n\n{REQUIRED_SHIPS}",
    "Our assault mission to <Bold>Cerberus</> has been able to establish a <Bold>beach-head</> in orbit around the planet, and the source of the energy readings has been identified:\n\nA vast <Bold>debris field</> made from the <Bold>wrecks of countless starships</> orbits the planet - we believe these are the remnants of an ancient war between unknown forces.":
        "<Bold>케르베로스</>로의 공격 임무는 행성 궤도에 <Bold>교두보</>를 설립하는 데 성공했고, 에너지 신호의 원천이 확인되었습니다:\n\n행성 궤도에는 <Bold>수많은 우주선의 잔해</>로 이루어진 광대한 <Bold>잔해 지대</>가 있습니다 — 우리는 이것이 알 수 없는 세력 간의 고대 전쟁의 잔재라고 봅니다.",
    "Our forces have confirmed the presence of <Bold>Exotic Matter</> in and around these wrecks, which will be essential if we want to begin the production of <Bold>Antimatter</>.\n\nOur forces also discovered an ancient <Bold>robot production facility</> within this area, and we believe this is where most of the <Bold>hostile robots</> we've encountered in this system are coming from.":
        "우리 부대는 이 잔해 안과 주변에서 <Bold>이그조틱 물질</>의 존재를 확인했으며, 이는 <Bold>반물질</> 생산을 시작하려면 필수적입니다.\n\n또한 이 지역 안에서 고대 <Bold>로봇 생산 시설</>을 발견했으며, 이것이 이 성계에서 마주친 대부분의 <Bold>적대 로봇</>의 출처라고 봅니다.",
    "Unlocks processes for processing <Bold>radioactive raw materials</> into useable items.":
        "<Bold>방사성 원자재</>를 사용 가능한 아이템으로 처리하는 공정을 잠금 해제합니다.",
    "You have now unlocked the ability to process <Bold>Uranium</>.\n\nThis is a <Bold>highly radioactive</> substance that will <Bold>damage your drone</> unless you have <Bold>Radiation Filters</> installed.":
        "이제 <Bold>우라늄</> 처리 능력이 잠금 해제되었습니다.\n\n이는 <Bold>강한 방사능</> 물질로, <Bold>방사선 필터</>가 설치되어 있지 않으면 <Bold>드론에 피해</>를 입힙니다.",
    "Unlocks the <Bold>Particle Accelerator</> which lets you convert radioactive materials into <Bold>Antimatter</>.":
        "방사성 물질을 <Bold>반물질</>로 변환할 수 있는 <Bold>입자 가속기</>를 잠금 해제합니다.",
    "<Bold>Antimatter</> is generated inside the <Bold>Particle Accelerator</>. This is formed from a <Bold>Control Centre</> and a ring of <Bold>Conduit</> running through one or more <Bold>Towers</>.\n\nThe <Bold>larger</> the particle accelerator loop you build, the <Bold>faster</> you can generate antimatter - but the <Bold>more power</> is required.":
        "<Bold>반물질</>은 <Bold>입자 가속기</> 안에서 생성됩니다. 이는 <Bold>제어 센터</>와 하나 이상의 <Bold>타워</>를 통과하는 <Bold>도관</> 고리로 구성됩니다.\n\n입자 가속기 루프를 <Bold>크게</> 건설할수록 반물질을 <Bold>더 빠르게</> 생성할 수 있지만 <Bold>더 많은 전력</>이 필요합니다.",
    "Unlocks the <Bold>Antimatter Reactor</> which lets you generate huge amounts of <Bold>power</> from <Bold>antimatter</>.":
        "<Bold>반물질</>로부터 막대한 양의 <Bold>전력</>을 생성할 수 있는 <Bold>반물질 원자로</>를 잠금 해제합니다.",
    "You now have access to the <Bold>Antimatter Reactor</> which can consume <Bold>antimatter</> to produce <Bold>vast quantities of energy</>.\n\nThis process does produce a large amount of <Bold>nuclear waste</> however which you will need to remove and process to prevent radioactive build-ups.":
        "이제 <Bold>반물질</>을 소비해 <Bold>막대한 양의 에너지</>를 생산할 수 있는 <Bold>반물질 원자로</>에 접근할 수 있습니다.\n\n그러나 이 공정은 대량의 <Bold>핵 폐기물</>을 생산하므로, 방사능 축적을 방지하기 위해 제거하고 처리해야 합니다.",
    "Unlocks processes required for converting <Bold>nuclear waste</> into <Bold>usable materials and items</>.":
        "<Bold>핵 폐기물</>을 <Bold>사용 가능한 재료와 아이템</>으로 변환하는 데 필요한 공정을 잠금 해제합니다.",
    "You have now unlocked the ability to process <Bold>Nuclear Waste</> byproducts into <Bold>usable items and materials</>.":
        "이제 <Bold>핵 폐기물</> 부산물을 <Bold>사용 가능한 아이템과 재료</>로 처리하는 능력이 잠금 해제되었습니다.",
    "You have unlocked a higher tier of <Bold>military starship</> construction, including additional starship parts and more advanced ship classes ready to be built from the <Bold>Shipyard</>.":
        "<Bold>조선소</>에서 건조할 수 있는 추가 우주선 부품과 더 고급의 함급을 포함한 <Bold>군용 우주선</> 건조의 더 높은 등급을 잠금 해제했습니다.",
    "Unlocks technologies for <Bold>protecting</> your Drone and Station Modules from the harmful effects of <Bold>radiation</>.":
        "<Bold>방사능</>의 유해 영향으로부터 드론과 스테이션 모듈을 <Bold>보호</>하는 기술을 잠금 해제합니다.",
    "Various technologies for <Bold>protecting</> your Drone and Station Modules from the harmful effects of <Bold>radiation</> have been unlocked.\n\n<Bold>Radiation Filters</> will protect your Drone from external <Bold>radiation damage</>, but only last for a short time before needing to be <Bold>replaced</>.":
        "<Bold>방사능</>의 유해 영향으로부터 드론과 스테이션 모듈을 <Bold>보호</>하는 다양한 기술이 잠금 해제되었습니다.\n\n<Bold>방사선 필터</>는 외부 <Bold>방사능 피해</>로부터 드론을 보호하지만, 짧은 시간만 지속되며 <Bold>교체</>가 필요합니다.",
    "Unlocks the ability to safely store and contain unstable or radioactive elements.":
        "불안정하거나 방사성인 원소를 안전하게 저장하고 격납할 수 있는 능력을 잠금 해제합니다.",
    "You have now unlocked the <Bold>Containment Chamber</>.\n\nAs long as it is <Bold>powered</>, this device can be used to safely store <Bold>Antimatter and radioactive elements</> without losing containment or damaging nearby machines.":
        "이제 <Bold>격납 체임버</>가 잠금 해제되었습니다.\n\n<Bold>전원이 공급되는</> 한, 이 장치는 격납을 잃거나 인근 기계를 손상시키지 않고 <Bold>반물질과 방사성 원소</>를 안전하게 저장하는 데 사용할 수 있습니다.",
    "Unlocks <Bold>force-field-based technologies</> which can be used to protect your station from external threats.":
        "외부 위협으로부터 스테이션을 보호하는 데 사용할 수 있는 <Bold>역장 기반 기술</>을 잠금 해제합니다.",
    "You have now unlocked <Bold>Force-Field Generators</>, which can be used to <Bold>protect your stations</> from all forms of damage - including <Bold>firestorms and electrical storms</>.":
        "이제 <Bold>역장 발생기</>가 잠금 해제되었습니다. <Bold>화염 폭풍과 전기 폭풍</>을 포함한 모든 형태의 피해로부터 <Bold>스테이션을 보호</>하는 데 사용할 수 있습니다.",
    "If we are to survive in this system, its imperative that the <Bold>robot production facility</> our forces discovered in orbit around <Bold>Cerberus</> is <Bold>neutralized</>.\n\nHowever, this complex is heavily guarded by <Bold>hostile robot patrols</> left over from an ancient war...":
        "이 성계에서 살아남으려면, 우리 부대가 <Bold>케르베로스</> 궤도에서 발견한 <Bold>로봇 생산 시설</>을 <Bold>중립화</>하는 것이 필수적입니다.\n\n그러나 이 복합 시설은 고대 전쟁에서 남은 <Bold>적대 로봇 순찰대</>에 의해 강력히 방어되고 있습니다...",
    "Its time to take the gloves off, Station Commander, and perform a <Bold>surgical strike</> with a task-force of powerful <Bold>military capital ships</> - we think the following will be sufficient to get the job done:\n\n{REQUIRED_SHIPS}":
        "장갑을 벗을 때입니다, 스테이션 사령관님. 강력한 <Bold>군용 주력함</> 기동대로 <Bold>정밀 타격</>을 수행해야 합니다 — 다음이 임무를 완수하기에 충분할 것이라 봅니다:\n\n{REQUIRED_SHIPS}",
    "Mission Complete, Station Commander: <Bold>Target Destroyed.</>\n\nBecause of your success in this mission, we've decided to promote you to the rank of <Bold>Station Captain!</>":
        "임무 완료, 스테이션 사령관님: <Bold>목표 파괴.</>\n\n이 임무에서의 성공으로 인해 <Bold>스테이션 대위</> 계급으로 승진시키기로 결정했습니다!",
    "With the main source of hostiles neutralized in this system - and with the technologies you have unlocked so far - its time to move onto the <Bold>next phase</> of our operations in the TAU system: \n\nConstructing our <Bold>Intergalactic Arkship</> and escaping this galaxy before <Bold>The Void</> catches up with us again.":
        "이 성계에서 적대 세력의 주요 출처가 중립화되었고, 지금까지 잠금 해제한 기술로, 이제 TAU 성계에서 운영의 <Bold>다음 단계</>로 넘어갈 시간입니다:\n\n<Bold>은하 간 방주선</>을 건조하고 <Bold>공허</>가 우리를 다시 따라잡기 전에 이 은하를 탈출하는 것.",
    "After <Bold>losing contact</> with our long-range scouting mission, we discovered that an ancient <Bold>automated robot production facility</> is still operational near the <Bold>Lava Planet Cerberus</>.\n\nThis is likely the source of most of the <Bold>hostile robots</> we've encountered in the system, so our next course of action must be to mount a <Bold>military operation</> and eliminate it.":
        "우리의 장거리 정찰 임무와 <Bold>통신을 잃은</> 후, 고대 <Bold>자동화 로봇 생산 시설</>이 여전히 <Bold>용암 행성 케르베로스</> 인근에서 작동 중임을 발견했습니다.\n\n이는 성계에서 마주친 대부분의 <Bold>적대 로봇</>의 출처일 가능성이 높으므로, 다음 행동 방침은 <Bold>군사 작전</>을 시행하여 이를 제거하는 것입니다.",
    "We have made a significant scientific breakthrough in <Bold>Quantum Physics</>, and unlocked several <Bold>new parts and materials</> that can be used in further technologies.":
        "<Bold>양자 물리학</>에서 중요한 과학적 돌파구를 마련했고, 추가 기술에 사용할 수 있는 여러 <Bold>새 부품과 재료</>를 잠금 해제했습니다.",
    "Unlocks the <Bold>Servitor Station</> which deploys a programmable <Bold>robotic AI helper</>.":
        "프로그래밍 가능한 <Bold>로봇 AI 보조</>를 배치하는 <Bold>서비터 스테이션</>을 잠금 해제합니다.",
    "A particularly useful function for the Servitor is to automate the collection of <Bold>Exotic Matter</> from the <Bold>Junkyard Zone</>.":
        "서비터의 특히 유용한 기능은 <Bold>고철장 구역</>에서 <Bold>이그조틱 물질</> 수집을 자동화하는 것입니다.",
    "Unlocks the <Bold>Mk 2 Wormhole</> which can transport more items, gases and liquids at a <Bold>faster rate</>.":
        "더 많은 아이템, 기체, 액체를 <Bold>더 빠른 속도</>로 운송할 수 있는 <Bold>Mk 2 웜홀</>을 잠금 해제합니다.",
    "<Bold>Mk 2 Wormholes</> have now been unlocked. \n\nThese can transport more items, gases and liquids between remote parts of your stations at a faster rate.":
        "<Bold>Mk 2 웜홀</>이 잠금 해제되었습니다.\n\n스테이션의 원격 부분 간 더 많은 아이템, 기체, 액체를 더 빠른 속도로 운송할 수 있습니다.",
    "Unlocks the <Bold>Quantum Storage</> device which lets you feed in items and parts and then <Bold>access them from anywhere</> via your <Bold>Drone's inventory</>.":
        "아이템과 부품을 투입한 다음 <Bold>드론 인벤토리</>를 통해 <Bold>어디서든 접근</>할 수 있는 <Bold>양자 저장</> 장치를 잠금 해제합니다.",
    "<Bold>Quantum Storage</> units have now been unlocked. \n\nFeed items and materials into this device and <Bold>access them anywhere</> from your <Bold>Drone's inventory</>.":
        "<Bold>양자 저장</> 유닛이 잠금 해제되었습니다.\n\n아이템과 재료를 이 장치에 투입하고 <Bold>드론 인벤토리</>에서 <Bold>어디서든 접근</>하세요.",
    "Unlocks the <Bold>Centrifuge</> which can be used to enrich <Bold>waste products</> and convert them into <Bold>useable materials</>.":
        "<Bold>폐기물</>을 농축하여 <Bold>사용 가능한 재료</>로 변환하는 데 사용할 수 있는 <Bold>원심분리기</>를 잠금 해제합니다.",
    "The <Bold>Centrifuge</> has now been unlocked. \n\nThis device can be used to <Bold>enrich waste products</> and convert them into <Bold>usable materials</>.":
        "<Bold>원심분리기</>가 잠금 해제되었습니다.\n\n이 장치는 <Bold>폐기물을 농축</>하여 <Bold>사용 가능한 재료</>로 변환하는 데 사용할 수 있습니다.",
    "<Bold>The Arkship</> will be our race's <Bold>greatest achievement</> - and our salvation - but its construction will take everything we have.":
        "<Bold>방주선</>은 우리 종족의 <Bold>최고의 업적</> — 그리고 우리의 구원 — 이 될 것이지만, 그 건조에는 우리가 가진 모든 것을 쏟아부어야 할 것입니다.",
    "The first step will be constructing an <Bold>Arkship Terminal</>, which will serve as a nexus to channel items, parts and materials into the project. This is now available to construct from the <Bold>Build menu</>.":
        "첫 단계는 <Bold>방주선 터미널</>을 건조하는 것입니다. 이는 아이템, 부품, 재료를 프로젝트로 채널링하는 중심부 역할을 합니다. 이제 <Bold>건설 메뉴</>에서 건설할 수 있습니다.",
    "We've also picked up some <Bold>interesting readings</> from the orbit of the gas giant <Bold>Scylla</> - we recommend dispatching an <Bold>exploration mission</> there immediately with the following ships:\n\n{REQUIRED_SHIPS}":
        "또한 가스 거성 <Bold>스킬라</> 궤도에서 <Bold>흥미로운 신호</>를 포착했습니다 — 다음 함선들로 즉시 <Bold>탐사 임무</>를 그곳에 파견할 것을 권장합니다:\n\n{REQUIRED_SHIPS}",
    "Well done Station Commander, the Arkship Terminal is now <Bold>fully operational</>.\n\nWhen you're ready, you can start feeding in the required items, parts and materials and take us to the <Bold>next stage</> of operation.":
        "잘하셨습니다 스테이션 사령관님, 방주선 터미널이 이제 <Bold>완전 가동</>됩니다.\n\n준비되시면 필요한 아이템, 부품, 재료를 투입하기 시작하여 운영의 <Bold>다음 단계</>로 데려가실 수 있습니다.",
    "Our <Bold>exploration mission</> to the gas giant <Bold>Scylla</> has also discovered an extremely <Bold>mineral-rich moon</> orbiting the planet - <Bold>Helion</> - and this location has been added to the System Map ready for <Bold>immediate expansion</>.":
        "가스 거성 <Bold>스킬라</>로의 <Bold>탐사 임무</>는 행성을 공전하는 매우 <Bold>광물이 풍부한 위성</> — <Bold>헬리온</> — 도 발견했고, 이 장소가 <Bold>즉각 확장</>을 위해 시스템 지도에 추가되었습니다.",
    "After neutralising an <Bold>ancient robot production facility</> in orbit around the <Bold>Lava Planet Cerberus</> - and developing many new manufacturing technologies - we believe we are finally ready to start production on our <Bold>Intergalactic Arkship</> and escape this doomed galaxy forever.\n\nThis is not going to be easy, however, and <Bold>The Void</> has <Bold>accelerated its expansion</> - so we may not have as much time as we hoped...":
        "<Bold>용암 행성 케르베로스</> 궤도의 <Bold>고대 로봇 생산 시설</>을 중립화하고 — 많은 새 제조 기술을 개발한 후 — 마침내 <Bold>은하 간 방주선</> 생산을 시작하고 이 운명 지어진 은하를 영원히 탈출할 준비가 됐다고 봅니다.\n\n그러나 이는 쉽지 않을 것이며, <Bold>공허</>가 <Bold>팽창을 가속화</>하고 있어 — 바랐던 만큼의 시간이 없을 수 있습니다...",
    "Researches <Bold>Tungten Carbide</> and related materials for extreme damage resistance.":
        "극한의 피해 저항을 위한 <Bold>탄화 텅스텐</>과 관련 재료를 연구합니다.",
    "We've completed research into the material <Bold>Tungsten Carbide</>.\n\nThis very dense, tough material can be used in extreme environments and high pressure systems.":
        "<Bold>탄화 텅스텐</> 재료에 대한 연구를 완료했습니다.\n\n이 매우 밀도 높고 강한 재료는 극한 환경과 고압 시스템에 사용할 수 있습니다.",
    "Unlocks the <Bold>Component Factory</> module, which can produce large <Bold>Starship</> and <Bold>Arkship components</>.":
        "큰 <Bold>우주선</>과 <Bold>방주선 부품</>을 생산할 수 있는 <Bold>부품 공장</> 모듈을 잠금 해제합니다.",
    "The <Bold>Component Factory</> has been unlocked.\n\nThis module is used to produce larger <Bold>Starship</> and <Bold>Arkship components</> which will require a tug to install into their destination.":
        "<Bold>부품 공장</>이 잠금 해제되었습니다.\n\n이 모듈은 큰 <Bold>우주선</>과 <Bold>방주선 부품</>을 생산하는 데 사용되며, 목적지에 설치하려면 예인선이 필요합니다.",
    "Unlocks the <Bold>Large Shipyard</>, which can construct the largest classes of ships.":
        "가장 큰 함급을 건조할 수 있는 <Bold>대형 조선소</>를 잠금 해제합니다.",
    "The <Bold>Large Shipyard</> has been unlocked.\n\nThis can construct the very largest classes of starship, which will require a <Bold>large tug</> to move around your station.":
        "<Bold>대형 조선소</>가 잠금 해제되었습니다.\n\n가장 큰 함급의 우주선을 건조할 수 있으며, 스테이션 주변에서 이동시키려면 <Bold>대형 예인선</>이 필요합니다.",
    "Unlocks the <Bold>Large Tug Bay</> and <Bold>Large Ship Tugs</> which can transport the largest ships around your station.":
        "스테이션 주변에서 가장 큰 함선을 운송할 수 있는 <Bold>대형 예인선 도크</>와 <Bold>대형 함선 예인선</>을 잠금 해제합니다.",
    "You have unlocked the <Bold>Large Tug Bay</> and <Bold>Large Ship Tugs</> which can be used to transport even the largest ships around your station.":
        "스테이션 주변에서 가장 큰 함선까지도 운송하는 데 사용할 수 있는 <Bold>대형 예인선 도크</>와 <Bold>대형 함선 예인선</>이 잠금 해제되었습니다.",
    "Unlocks the <Bold>Exoplanet Ops Centre</> which can deploy <Bold>Planetary Lifters</> to fetch resources from the surface of compatible planets.":
        "호환 행성 표면에서 자원을 가져오는 <Bold>행성 리프터</>를 배치할 수 있는 <Bold>외계행성 운영 센터</>를 잠금 해제합니다.",
    "You have now unlocked the <Bold>Exoplanet Ops Centre</>.\n\nThis module can deploy multiple <Bold>Planetary Lifters</> which can be set to fetch resources from the surface of compatible planets.":
        "이제 <Bold>외계행성 운영 센터</>가 잠금 해제되었습니다.\n\n이 모듈은 호환 행성 표면에서 자원을 가져오도록 설정할 수 있는 여러 <Bold>행성 리프터</>를 배치할 수 있습니다.",
    "Unlocks <Bold>Mark 2 Pipes</> and an <Bold>increased gas/fluid output rate</> to speed up how fast you can transport gases and fluids around your station.":
        "스테이션 주변에서 기체와 유체를 운송하는 속도를 높이는 <Bold>Mark 2 파이프</>와 <Bold>증가된 기체/유체 출력 속도</>를 잠금 해제합니다.",
    "You have unlocked <Bold>Mark 2 Pipes</> and an <Bold>increased gas/fluid output rate</>.\n\nTogether these will vastly speed up how fast you can transport gases and fluids around your station.":
        "<Bold>Mark 2 파이프</>와 <Bold>증가된 기체/유체 출력 속도</>를 잠금 해제했습니다.\n\n이 둘은 함께 스테이션 주변에서 기체와 유체를 운송하는 속도를 크게 높입니다.",
    "Unlocks the <Bold>Mk 3 Fuel Depot</> which has a faster fuel transfer rate and can supply <Bold>Antimatter</> to larger ships, as well as the Crusader Auxilliary, a Capital-class resupply ship.":
        "더 빠른 연료 전달 속도를 가지고 더 큰 함선에 <Bold>반물질</>을 공급할 수 있는 <Bold>Mk 3 연료 저장고</>와 주력함급 재보급 함선인 크루세이더 보조함을 잠금 해제합니다.",
    "The <Bold>Mk 3 Fuel Depot</> has now been unlocked.\n\nThis module has a <Bold>faster fuel transfer rate</> and can both store and supply <Bold>Antimatter</> to the largest starships.\n\nYou can now also construct the Crusader Auxilliary, a Capital-class resupply ship which can refuel both fusion and antimatter-based starships.":
        "<Bold>Mk 3 연료 저장고</>가 잠금 해제되었습니다.\n\n이 모듈은 <Bold>더 빠른 연료 전달 속도</>를 가지고 가장 큰 우주선에 <Bold>반물질</>을 저장하고 공급할 수 있습니다.\n\n또한 융합과 반물질 기반 우주선 모두를 재급유할 수 있는 주력함급 재보급 함선인 크루세이더 보조함을 건조할 수 있습니다.",
    "Unlocks the <Bold>Quantum Extractor</> which can extract Exotic Matter directly from a Quantum Rift":
        "양자 균열에서 이그조틱 물질을 직접 추출할 수 있는 <Bold>양자 추출기</>를 잠금 해제합니다",
    "The <Bold>Quantum Extractor</> has now been unlocked.\n\nConstruct this advanced device onto <Bold>Quantum Rifts</> you can find in locations like the <Bold>Junkyard</> to automate large-scale extraction of <Bold>Exotic Matter</>.":
        "<Bold>양자 추출기</>가 잠금 해제되었습니다.\n\n<Bold>고철장</> 같은 장소에서 발견할 수 있는 <Bold>양자 균열</>에 이 고급 장치를 건설하여 <Bold>이그조틱 물질</>의 대규모 추출을 자동화하세요.",
    "Commander, all of our <Bold>deep-space scanning</> stations have just <Bold>gone dark</>, and we are completely blind to what is happening in this sector of space...":
        "사령관님, 우리의 모든 <Bold>심우주 스캔</> 스테이션이 방금 <Bold>무응답</>이 되었고, 이 우주 구역에서 무슨 일이 일어나는지 완전히 알 수 없게 되었습니다...",
    "We can patch this gap with a network of our most powerful <Bold>science and scanning ships</>, along with an appropriate escort of military and resupply ships:\n\n{REQUIRED_SHIPS}":
        "가장 강력한 <Bold>과학 및 스캔 함선</> 네트워크와 함께 적절한 군용 및 재보급 함선 호위로 이 공백을 메울 수 있습니다:\n\n{REQUIRED_SHIPS}",
    "While this mission is underway, it's also <Bold>vital</> that you continue construction of our Intergalactic Arkship Project.\n\nThe next phase of the project will be building the <Bold>Arkship Dock</>, ready to begin construction of the Arkship itself.":
        "이 임무가 진행되는 동안, 우리의 은하 간 방주선 프로젝트 건조를 계속하는 것도 <Bold>필수적</>입니다.\n\n프로젝트의 다음 단계는 방주선 자체의 건조를 시작할 준비가 된 <Bold>방주선 도크</>를 짓는 것입니다.",
    "<Bold>Bad news</>, Commander...\n\nWe've just heard back from the fleet we dispatched to the edge of the system, and it's official: <Bold>The Void has arrived...</>":
        "<Bold>나쁜 소식</>입니다, 사령관님...\n\n성계 끝자락으로 파견한 함대로부터 방금 보고를 받았고, 이는 공식입니다: <Bold>공허가 도달했습니다...</>",
    "The Void's last <Bold>Expansion Phase</> has halted at the edge of this system, but another Expansion could occur at any time... we need to get the Arkship completed as soon as we can, Commander!":
        "공허의 마지막 <Bold>팽창 단계</>는 이 성계 끝자락에서 멈췄지만, 또 다른 팽창이 언제든 일어날 수 있습니다... 가능한 한 빨리 방주선을 완성해야 합니다, 사령관님!",
    "Analysis has confirmed that a station could survive on the edge of The Void's event horizon, and could provide invaluable insight into the inner workings of this mysterious cosmic entity...\n\nThis location has been added to your <Bold>System Map</>.":
        "분석 결과 스테이션이 공허의 사건 지평선 가장자리에서 생존할 수 있고, 이 신비로운 우주 존재의 내부 작동에 대한 귀중한 통찰을 제공할 수 있다는 것이 확인되었습니다...\n\n이 장소가 <Bold>시스템 지도</>에 추가되었습니다.",
    "Unlocks the <Bold>Space Elevator</> - a massive structure that can lift valuable resources from the surface of a planet.":
        "행성 표면에서 귀중한 자원을 들어 올릴 수 있는 거대한 구조물인 <Bold>우주 엘리베이터</>를 잠금 해제합니다.",
    "You have unlocked the <Bold>Space Elevator</>.\n\nThis massive orbital structure is capable of lifting valuable items, materials and parts from the surface of a planet, ready to be used in your station.":
        "<Bold>우주 엘리베이터</>를 잠금 해제했습니다.\n\n이 거대한 궤도 구조물은 행성 표면에서 귀중한 아이템, 재료, 부품을 들어 올려 스테이션에서 사용할 수 있게 합니다.",
    "Unlocks materials, items and parts related to <Bold>Quantum Destabilization</> - a highly experimental technology which has the power to <Bold>disrupt cosmic phenomena</> such as black holes.":
        "블랙홀 같은 <Bold>우주 현상을 교란</>하는 힘을 가진 고도로 실험적인 기술인 <Bold>양자 안정화 파괴</>와 관련된 재료, 아이템, 부품을 잠금 해제합니다.",
    "We have completed research into the field of Quantum Destabilization.\n\nAccording to our scientists, this highly experimental technology has the power to disrupt quantum entities - such as singularities - and may help us in our fight against The Void.":
        "양자 안정화 파괴 분야의 연구를 완료했습니다.\n\n우리 과학자들에 따르면, 이 고도로 실험적인 기술은 특이점 같은 양자 존재를 교란할 힘을 가지고 있어 공허와의 싸움에서 우리에게 도움이 될 수 있습니다.",
    "Unlocks the <Bold>Battlecruiser class</> of starship - a massive capital-class ship that can mount the heaviest experimental weaponry.":
        "가장 무거운 실험 무기를 장착할 수 있는 거대한 주력함급 함선인 우주선의 <Bold>전투순양함급</>을 잠금 해제합니다.",
    "You have unlocked the Battlecruiser class of starship.\n\nThis massive capital-class ship can mount the heaviest experimental weaponry and will be invaluable in our fight against The Void.":
        "우주선의 전투순양함급을 잠금 해제했습니다.\n\n이 거대한 주력함급 함선은 가장 무거운 실험 무기를 장착할 수 있고 공허와의 싸움에서 매우 귀중할 것입니다.",
    "Unlocks the <Bold>Magnetic Accelerator</> which can target and destroy <Bold>Void Anomalies</> you may encounter at The Void's event horizon location.":
        "공허의 사건 지평선 장소에서 마주칠 수 있는 <Bold>공허 이상 현상</>을 표적으로 하여 파괴할 수 있는 <Bold>자기 가속기</>를 잠금 해제합니다.",
    "You have unlocked the <Bold>Magnetic Accelerator</>.\n\nThis massive cannon can fire <Bold>Quantum Implosion Ammo</> at the <Bold>Void Anomalies</> you may encounter at The Void's <Bold>Event Horizon location</>.\n\nWhen destroyed, these anomalies may leave behind the rare and valuable material <Bold>Neutronium</>.":
        "<Bold>자기 가속기</>를 잠금 해제했습니다.\n\n이 거대한 대포는 공허의 <Bold>사건 지평선 장소</>에서 마주칠 수 있는 <Bold>공허 이상 현상</>에 <Bold>양자 내파 탄약</>을 발사할 수 있습니다.\n\n파괴되면 이 이상 현상들은 희귀하고 귀중한 재료인 <Bold>중성자물질</>을 남길 수 있습니다.",
    "Unlocks the ability to process <Bold>Neutronium</> into powerful <Bold>hyperdrive fuel</> that can be used in intergalactic star-drives.":
        "은하 간 항성 추진 장치에 사용할 수 있는 강력한 <Bold>하이퍼드라이브 연료</>로 <Bold>중성자물질</>을 처리하는 능력을 잠금 해제합니다.",
    "You have unlocked the ability to process <Bold>Neutronium</>.\n\nThis rare and valuable stellar substance is found in the core of stars and black holes, and can be refined into <Bold>Hyperdrive Fuel</> which can power intergalactic star-drives.":
        "<Bold>중성자물질</> 처리 능력을 잠금 해제했습니다.\n\n이 희귀하고 귀중한 항성 물질은 항성과 블랙홀 핵에서 발견되며, 은하 간 항성 추진 장치를 구동할 수 있는 <Bold>하이퍼드라이브 연료</>로 정제할 수 있습니다.",
    "Unlocks the <Bold>Antimatter Lazer</> which is a powerful beam weapon that can be crafted from the <Bold>Equipment Station</>.":
        "<Bold>장비 정거장</>에서 제작할 수 있는 강력한 빔 무기인 <Bold>반물질 레이저</>를 잠금 해제합니다.",
    "You have now unlocked the <Bold>Antimatter Lazer</>.\n\nThis is an extremely powerful beam weapon that can be crafted from the <Bold>Equipment Station</> and can be used to defend yourself from even the most powerful enemies.":
        "이제 <Bold>반물질 레이저</>가 잠금 해제되었습니다.\n\n이는 <Bold>장비 정거장</>에서 제작할 수 있는 극도로 강력한 빔 무기로, 가장 강력한 적으로부터도 스스로를 방어하는 데 사용할 수 있습니다.",
    "With our recent advancements in <Bold>Quantum Destablization</> technology, it may actually be possible to temporarily delay The Void's next expansion phase - giving us enough time to complete the <Bold>Arkship</> and escape this galaxy...":
        "최근 <Bold>양자 안정화 파괴</> 기술의 발전으로, 실제로 공허의 다음 팽창 단계를 일시적으로 지연시켜 <Bold>방주선</>을 완성하고 이 은하를 탈출할 시간을 충분히 벌 수 있을지도 모릅니다...",
    "This will require a flotilla of our most <Bold>powerful battlecruisers</> - fitted with this devastating weapons technology - all working in unison:\n\n{REQUIRED_SHIPS}":
        "이를 위해서는 가장 <Bold>강력한 전투순양함</> 함대가 — 이 파괴적인 무기 기술을 장착하고 — 일사불란하게 작동해야 합니다:\n\n{REQUIRED_SHIPS}",
    "Now that the <Bold>Arkship Dock</> is complete, its time to put all of our efforts into building the <Bold>Arkship</> itself - use every means at your disposal Commander, <Bold>we may not have much time!</>":
        "이제 <Bold>방주선 도크</>가 완성되었으니, 모든 노력을 <Bold>방주선</> 자체를 짓는 데 쏟을 시간입니다 — 사령관님, 가능한 모든 수단을 동원하세요. <Bold>시간이 많지 않을 수 있습니다!</>",
    "<Bold>The Arkship is complete</>, Commander - truly an <Bold>amazing accomplishment!</>\n\nAll that remains is to power and fuel its <Bold>Intergalactic Stardrive</> - then we will be ready to <Bold>launch</>.":
        "<Bold>방주선이 완성되었습니다</>, 사령관님 — 정말 <Bold>놀라운 업적</>입니다!\n\n남은 것은 <Bold>은하 간 항성 추진 장치</>에 동력과 연료를 공급하는 것뿐입니다 — 그러면 <Bold>발진</> 준비가 됩니다.",
    "Fuel and power the Intergalactic Arkship's Hyper-drive and escape the galaxy - and The Void - forever...":
        "은하 간 방주선의 하이퍼드라이브에 연료와 동력을 공급하고 은하 — 그리고 공허 — 로부터 영원히 탈출하세요...",
    "With the Arkship complete, we now have everything we need to escape the galaxy - and The Void - forever.\n\nAll that remains is to <Bold>power and fuel</> the Arkship's Intergalactic <Bold>Hyperdrive</> with neutronium-based fuel.":
        "방주선이 완성되어 이제 은하 — 그리고 공허 — 로부터 영원히 탈출하는 데 필요한 모든 것을 가지게 되었습니다.\n\n남은 것은 방주선의 은하 간 <Bold>하이퍼드라이브</>에 중성자물질 기반 연료로 <Bold>동력과 연료를 공급</>하는 것입니다.",
    "This experimental drive will require <Bold>massive amounts of power</> to initialise - so you will need to use all of your engineering abilities to accomplish this.":
        "이 실험적 추진 장치는 초기화에 <Bold>막대한 양의 전력</>이 필요합니다 — 따라서 이를 달성하려면 모든 공학 능력을 사용해야 합니다.",
    "Although our Battlecruisers have bought us some time, The Void could start its next <Bold>Expansion Phase</> at any time, so we recommend moving with <Bold>all haste</>, Commander...":
        "우리 전투순양함이 시간을 벌어줬지만, 공허는 언제든 다음 <Bold>팽창 단계</>를 시작할 수 있으므로 <Bold>최대한 서두를</> 것을 권장합니다, 사령관님...",
    "But there's something you should know - we've been receiving communications from inside The Void, and its been confirmed: The people from our home system are still alive somehow - inside The Void - transcribed into a quantum state...":
        "하지만 알아두셔야 할 것이 있습니다 — 우리는 공허 안에서 통신을 받아오고 있었고, 확인되었습니다: 우리 고향 성계의 사람들은 어떻게든 아직 살아있습니다 — 공허 안에서 — 양자 상태로 전사되어...",
    "According to them, The Void is NOT the great destroyer that we believed...\n\nInstead, it seems to be a vast machine created aeons ago to achieve Singularity for everyone in this galaxy... and its almost ready to activate...":
        "그들에 따르면, 공허는 우리가 믿었던 위대한 파괴자가 아닙니다...\n\n그 대신, 이 은하의 모든 이를 위한 특이점을 달성하기 위해 영겁 전에 만들어진 거대한 기계로 보이며... 활성화 준비가 거의 됐습니다...",
    "Its up to you now, Commander...\n\nDo we use the Arkship to join our lost kin inside The Void - or to escape this galaxy forever...?":
        "이제 사령관님께 달렸습니다...\n\n방주선을 사용해 공허 안의 잃어버린 동족과 합류할까요 — 아니면 이 은하를 영원히 탈출할까요...?",

    # ====================================================================
    # MainMenu folder — main menu, in-game pause menu, settings (Options)
    # ====================================================================

    # ---- common buttons / actions ----
    "NEW GAME": "새 게임",
    "CONTINUE": "계속하기",
    "LOAD GAME": "게임 불러오기",
    "SAVE GAME": "게임 저장",
    "SAVED GAMES": "저장된 게임",
    "DELETE GAME": "게임 삭제",
    "DELETE SESSION": "세션 삭제",
    "NEW SAVE FILE": "새 저장 파일",
    "NEW SAVE GAME": "새 저장 게임",
    "NEW SESSION": "새 세션",
    "JOIN GAME": "게임 참가",
    "JOIN SESSION": "세션 참가",
    "START GAME": "게임 시작",
    "SETTINGS": "설정",
    "SESSIONS": "세션",
    "SESSIONS FOUND": "세션 찾음",
    "SESSION": "세션",
    "SESSION NAME": "세션 이름",
    "SESSION TYPE": "세션 유형",
    "EXIT": "나가기",
    "QUIT": "종료",
    "RESUME": "재개",
    "BACK": "뒤로",
    "ACCEPT": "확인",
    "CANCEL": "취소",
    "OK": "확인",
    "YES": "예",
    "NO": "아니오",
    "CREDITS": "크레딧",
    "RELEASE NOTES": "패치 노트",
    "REPORT A BUG": "버그 신고",
    "MAIN MENU": "메인 메뉴",
    "VERSION": "버전",
    "RESPAWN AT HUB": "허브에서 부활",
    "UNDERSTOOD": "알겠습니다",

    # ---- early access / demo banners ----
    "BETA": "베타",
    "DEMO": "데모",
    "EARLY ACCESS": "얼리 액세스",
    "EARLY ACCESS RELEASE": "얼리 액세스 출시",
    "EARLY ACCESS RELEASE - DOES NOT REPRESENT FINAL QUALITY":
        "얼리 액세스 출시 - 최종 품질을 반영하지 않습니다",
    "END OF DEMO": "데모 종료",
    "WISHLIST NOW!": "지금 위시리스트에 추가!",

    # ---- session / online options ----
    "GAME NAME:": "게임 이름:",
    "GAME OPTIONS:": "게임 옵션:",
    "CURRENT SESSION NAME": "현재 세션 이름",
    "CURRENT SESSION:": "현재 세션:",
    "SESSION TIME:": "세션 시간:",
    "GAME TIME:": "게임 시간:",
    "STATION LEVEL:": "스테이션 레벨:",
    "Station Level:": "스테이션 레벨:",
    "Players:": "플레이어:",
    "SAVE GAME NAME": "저장 게임 이름",
    "SINGLEPLAYER": "싱글플레이어",
    "PUBLIC": "공개",
    "FRIENDS ONLY": "친구만",
    "All players can join your game": "모든 플레이어가 게임에 참가할 수 있습니다",
    "Only players who you are friends with will be able to join your game":
        "친구로 등록된 플레이어만 게임에 참가할 수 있습니다",
    "No other players will be able to join your game": "다른 플레이어는 게임에 참가할 수 없습니다",
    "Choose how your game can be joined by other players online":
        "다른 플레이어가 온라인으로 게임에 참가하는 방식을 선택하세요",
    "Friends": "친구",
    "Offline": "오프라인",
    "Public": "공개",

    # ---- gameplay options ----
    "ENVIRONMENTAL HAZARDS": "환경 위험 요소",
    "Environmental Hazards": "환경 위험 요소",
    "Choose whether to spawn environmental hazards such as Electrical Clouds":
        "전기 구름 같은 환경 위험 요소를 생성할지 선택하세요",
    "GLOBAL EVENTS": "전역 이벤트",
    "Choose whether to spawn global events such as Meteor Storms":
        "운석 폭풍 같은 전역 이벤트를 생성할지 선택하세요",
    "NPC BEHAVIOUR": "NPC 행동",
    "Defines how NPCs will react to your presence and actions":
        "NPC가 플레이어의 존재와 행동에 어떻게 반응할지 정의합니다",
    "FRIENDLY": "우호적",
    "REACTIVE": "반응적",
    "NPCs will never attack you": "NPC가 절대 공격하지 않습니다",
    "Unfriendly NPCs will retaliate if attacked by you": "적대적인 NPC는 공격받으면 반격합니다",
    "Unfriendly NPCs will attack you (and each other) on sight":
        "적대적인 NPC는 보이는 즉시 (서로도) 공격합니다",
    "Ship Reactor Meltdowns": "함선 원자로 멜트다운",
    "SHIP REACTOR MELTDOWNS": "함선 원자로 멜트다운",
    "Choose whether ships with reactors will melt down if they are not fuelled after construction":
        "건조 후 연료를 주입하지 않은 원자로 함선이 멜트다운할지 선택하세요",
    "STATION COLOUR": "스테이션 색상",
    "SESSION COLOUR": "세션 색상",
    "Set the colour scheme of your station": "스테이션의 색상 테마를 설정합니다",
    # Color names — kept English to be safe (may be lookup keys in some places)

    # ---- main menu specific ----
    "Please choose your language:": "언어를 선택해 주세요:",
    "Asteroid Belt": "소행성대",
    "GAS GIANT TITANIA": "가스 거성 티타니아",
    "Escape Terra": "테라 탈출",
    "TAU SYSTEM:": "TAU 성계:",
    "Tau System:": "타우 성계:",
    "Prologue:": "프롤로그:",
    "SELECT A STARTING LOCATION:": "시작 장소를 선택하세요:",
    "SHOW TUTORIALS (RECOMMENDED)": "튜토리얼 표시 (권장)",
    "BUILD LOCKED": "건설 잠김",
    "Starting Location": "시작 장소",
    "PREFIX:": "접두어:",
    "Prefix": "접두어",
    "This is the <Bold>Description</> for this <Bold>Starting Location</>":
        "이 <Bold>시작 장소</>의 <Bold>설명</>입니다",
    "UNLOCKS AT <Yellow>STATION LEVEL 6</>": "<Yellow>스테이션 레벨 6</>에서 잠금 해제",

    # ---- Settings: top-level categories (Options screen tabs) ----
    "AUDIO": "오디오",
    "GRAPHICS": "그래픽",
    "CONTROLS": "조작",
    "GAMEPLAY": "게임플레이",
    "INTERFACE": "인터페이스",
    "USER-INTERFACE": "사용자 인터페이스",
    "User Interface": "사용자 인터페이스",
    "MISC": "기타",
    "MOVEMENT": "이동",
    "STATION": "스테이션",
    "STATION MODULES": "스테이션 모듈",
    "DRONE": "드론",
    "ADVANCED OPTIONS": "고급 옵션",
    "BASIC OPTIONS": "기본 옵션",
    "DEFAULTS": "기본값",
    "DEFAULT": "기본",
    "APPLY": "적용",
    "Default": "기본",
    "Disabled": "사용 안 함",
    "Enabled": "사용",
    "DISABLED": "사용 안 함",
    "ENABLED": "사용",
    "NEVER": "사용 안 함",
    "EXPANDED": "확장",
    "MINIMAL": "최소",
    "Custom": "사용자 정의",
    "None": "없음",
    "UNLIMITED": "무제한",
    "Language": "언어",
    "Language Name": "언어 이름",
    "Choose which language you want the game to use": "게임에서 사용할 언어를 선택하세요",

    # ---- Audio settings ----
    "Audio Output Device": "오디오 출력 장치",
    "Effects": "효과음",
    "Music": "음악",
    "Voice": "음성",
    "Ambient": "환경음",
    "Warnings": "경고",
    "Cutscenes": "컷씬",
    "Multiplayer Chat": "멀티플레이어 채팅",
    "Global": "전체",

    # ---- Graphics settings ----
    "Anti-Aliasing Mode": "안티에일리어싱 모드",
    "Anti-Aliasing Quality": "안티에일리어싱 품질",
    "Enable VSYNC": "VSYNC 사용",
    "Fullscreen": "전체 화면",
    "Fullscreen Mode": "전체 화면 모드",
    "Fullscreen Resolution": "전체 화면 해상도",
    "Fullscreen Window": "전체 화면 창",
    "Windowed": "창 모드",
    "Resolution Scale": "해상도 배율",
    "View Distance": "시야 거리",
    "Shadows": "그림자",
    "Textures": "텍스처",
    "Post Processing": "후처리 효과",
    "Graphics Quality": "그래픽 품질",
    "FXAA": "FXAA",
    "Temporal AA": "Temporal AA",
    "High": "높음",
    "Medium": "중간",
    "Low": "낮음",
    "Ultra": "최상",
    "LIMIT FPS": "FPS 제한",
    "30 FPS": "30 FPS",
    "60 FPS": "60 FPS",
    "120 FPS": "120 FPS",
    "240 FPS": "240 FPS",

    # ---- Auto-save settings ----
    "AUTO-SAVE INTERVAL": "자동 저장 주기",
    "MAX AUTO-SAVE FILES": "최대 자동 저장 파일 수",
    "The maximum number of concurrent auto-save files to create before deleting older saves":
        "오래된 저장본을 삭제하기 전에 동시에 유지할 자동 저장 파일의 최대 개수",
    "5 MINS": "5분",
    "15 MINS": "15분",
    "30 MINS": "30분",
    "1 HOUR": "1시간",
    "MINUTES x 1": "1분",
    "MINUTES x 5": "5분",
    "MINUTES x 10": "10분",
    "MINUTES x 30": "30분",
    "RECIPE x 1": "제작법 x 1",
    "RECIPE x 5": "제작법 x 5",
    "RECIPE x 10": "제작법 x 10",
    "RECIPE x 25": "제작법 x 25",
    "RECIPE x 100": "제작법 x 100",
    "SHIPS x 1": "함선 x 1",
    "SHIPS x 5": "함선 x 5",
    "SHIPS x 10": "함선 x 10",
    "SHIPS x 50": "함선 x 50",

    # ---- Gameplay/UI options ----
    "AUTO-SORT DRONE INVENTORY ON OPEN": "열 때 드론 인벤토리 자동 정렬",
    "AUTO-SORT MODULE INVENTORY ON OPEN": "열 때 모듈 인벤토리 자동 정렬",
    "Enable this open to automatically sort station module inventories when you open them":
        "열 때 스테이션 모듈 인벤토리가 자동 정렬되게 합니다",
    "Enable this open to automatically sort your drone's inventory when you open it":
        "열 때 드론 인벤토리가 자동 정렬되게 합니다",
    "ENABLE GLITCH EFFECTS": "글리치 효과 사용",
    "Enable or disable glitch effects when near radiation sources":
        "방사능 원천 근처에서 글리치 효과를 사용/사용 안 함",
    "ENABLE SCREEN-EDGE SCROLLING": "화면 가장자리 스크롤 사용",
    "Enable or disable panning/scrolling the camera when the mouse cursor is near the edge of the screen":
        "마우스 커서가 화면 가장자리에 있을 때 카메라 패닝/스크롤을 사용/사용 안 함",
    "ENABLE SCREEN-SHAKES": "화면 흔들림 사용",
    "Enable or disable camera screen-shaking when near explosions or damage is taken":
        "폭발 근처이거나 피해를 받을 때 카메라 흔들림을 사용/사용 안 함",
    "LOCK CURSOR WHEN MIDDLE-CLICK-DRAGGING": "휠클릭 드래그 시 커서 잠금",
    "LOCK CURSOR WHEN RIGHT-CLICK-DRAGGING": "우클릭 드래그 시 커서 잠금",
    "Choose whether this warning message is enabled or disabled": "이 경고 메시지 사용/사용 안 함",
    "Default Popup Size": "기본 팝업 크기",
    "Expand Popups": "팝업 확장",
    "Hovered Popups Scale": "호버 팝업 배율",
    "Overall User Interface Scale": "전체 사용자 인터페이스 배율",
    "Scale": "배율",
    "Screen Edge Markers Scale": "화면 가장자리 마커 배율",
    "Status View Icons Scale": "상태 뷰 아이콘 배율",

    # ---- Default factory/shipyard limits ----
    "Max Factory Input": "최대 공장 입력",
    "Max Factory Output": "최대 공장 출력",
    "Max Power Generator Input": "최대 발전기 입력",
    "Max Shipyard Input": "최대 조선소 입력",
    "Set the default max amount of input items shipyards will take from source modules":
        "조선소가 공급원 모듈에서 받을 입력 아이템 기본 최대량 설정",
    "Set the default max amount of input items this factory will take from source modules":
        "공장이 공급원 모듈에서 받을 입력 아이템 기본 최대량 설정",
    "Set the default max amount of input resources this power generator will take from source modules":
        "발전기가 공급원 모듈에서 받을 입력 자원 기본 최대량 설정",
    "Set the default max amount of items this factory will store in its output inventory":
        "공장이 출력 인벤토리에 저장할 아이템 기본 최대량 설정",

    # ---- Notification/warnings ----
    "CLOUD MINERS WAITING": "구름 채굴기 대기 중",
    "CLOUD MINERS": "구름 채굴기",
    "FACTORY INPUT BLOCKED": "공장 입력 차단됨",
    "FREIGHTERS WAITING": "화물선 대기 중",
    "FREIGHTERS": "화물선",
    "GENERATOR LOW ON FUEL": "발전기 연료 부족",
    "GENERATOR WASTE IS FULL": "발전기 폐기물 가득 참",
    "MATTER PRINTERS": "물질 프린터",
    "MODULE CONTAINMENT FAILING": "모듈 격납 실패 중",
    "MODULES DAMAGED": "모듈 손상됨",
    "MODULES DISABLED": "모듈 비활성화됨",
    "MODULES STUNNED": "모듈 기절함",
    "MODULES UNDER ATTACK": "모듈 공격받는 중",
    "POWER IS LOW": "전력 부족",
    "REFINERIES": "정제소",
    "SCAVENGERS WAITING": "스캐빈저 대기 중",
    "SHIP REACTORS FAILING": "함선 원자로 실패 중",
    "SHIP WAITING IN AMMO BAY": "탄약고에서 함선 대기 중",
    "SHIP WAITING IN FUEL BAY": "연료고에서 함선 대기 중",
    "SHIP WAITING IN SHIPYARD": "조선소에서 함선 대기 중",
    "SMELTERS": "제련소",
    "SOLAR PANELS NEED ALIGNING": "태양광 패널 정렬 필요",
    "TUG CANNOT FIND CLEAR SPACE": "예인선이 빈 공간을 찾지 못함",
    "USING STORED POWER": "저장된 전력 사용 중",
    "ASTEROIDS": "소행성",
    "CONTAINERS / CRASHED SHIPS": "컨테이너 / 추락한 함선",

    # ---- Control bindings (action names) ----
    "Activate Utility": "유틸리티 활성화",
    "Activate utility": "유틸리티 활성화",
    "Add Custom TODO Task": "사용자 지정 TODO 작업 추가",
    "Add Link Stopover": "연결 경유점 추가",
    "Add Waypoint": "경유점 추가",
    "Afterburner": "애프터버너",
    "Alternate Modify Selection": "대체 선택 수정",
    "Build Mode": "건설 모드",
    "Calculator": "계산기",
    "Codex": "코덱스",
    "Combat Mode": "전투 모드",
    "Confirm / Click": "확인 / 클릭",
    "Drone Inventory": "드론 인벤토리",
    "Fire Primary Weapon": "주 무기 발사",
    "Fire Weapons": "무기 발사",
    "Flip Pipe Flow Direction": "파이프 흐름 방향 전환",
    "Hide Upper Station Level": "스테이션 상층부 숨기기",
    "Hotbar": "단축바",
    "Hotbar 1": "단축바 1",
    "Hotbar 2": "단축바 2",
    "Hotbar 3": "단축바 3",
    "Hotbar 4": "단축바 4",
    "Hotbar 5": "단축바 5",
    "Hotbar 6": "단축바 6",
    "Hotbar 7": "단축바 7",
    "Hotbar 8": "단축바 8",
    "Hotbar 9": "단축바 9",
    "Hotbar 10": "단축바 10",
    "Build Categories": "건설 카테고리",
    "Build Category 1": "건설 카테고리 1",
    "Build Category 2": "건설 카테고리 2",
    "Build Category 3": "건설 카테고리 3",
    "Build Category 4": "건설 카테고리 4",
    "Build Category 5": "건설 카테고리 5",
    "Build Category 6": "건설 카테고리 6",
    "Build Category 7": "건설 카테고리 7",
    "Build Category 8": "건설 카테고리 8",
    "Build Category 9": "건설 카테고리 9",
    "Build Category 10": "건설 카테고리 10",
    "Ingame Menu": "인게임 메뉴",
    "Inventory": "인벤토리",
    "Link Mode": "연결 모드",
    "Map View": "지도 뷰",
    "Modify (Shift)": "수정 (Shift)",
    "Modify Selection": "선택 수정",
    "Move Camera/Drone": "카메라/드론 이동",
    "Move Camera/Drone Down": "카메라/드론 아래로 이동",
    "Move Camera/Drone Left": "카메라/드론 왼쪽으로 이동",
    "Move Camera/Drone Right": "카메라/드론 오른쪽으로 이동",
    "Move Camera/Drone Up": "카메라/드론 위로 이동",
    "Move Cursor": "커서 이동",
    "Move all from drone inventory": "드론 인벤토리에서 전부 이동",
    "Move all to drone inventory": "드론 인벤토리로 전부 이동",
    "Multi-Select Mode": "다중 선택 모드",
    "Objectives": "목표",
    "Objectives Panel": "목표 패널",
    "Pan Camera / Move Drone": "카메라 패닝 / 드론 이동",
    "Pan Camera View": "카메라 뷰 패닝",
    "Pause": "일시정지",
    "Photo Mode": "사진 모드",
    "Production overview": "생산 개요",
    "Repair Mode": "수리 모드",
    "Rotate Camera": "카메라 회전",
    "Rotate Camera View": "카메라 뷰 회전",
    "Rotate Placing Module": "배치 모듈 회전",
    "Rotate build module": "건설 모듈 회전",
    "Sell Mode": "판매 모드",
    "Sensors": "센서",
    "Show/Hide Item Filters Panel": "아이템 필터 패널 표시/숨기기",
    "Sort Drone Inventory": "드론 인벤토리 정렬",
    "Sort Selected Object's Inventory": "선택 오브젝트 인벤토리 정렬",
    "Station Overview": "스테이션 개요",
    "Station Status View": "스테이션 상태 뷰",
    "Station overview": "스테이션 개요",
    "Stop/Clear": "정지/초기화",
    "Teleport To Home": "홈으로 순간이동",
    "Teleport to HUB": "허브로 순간이동",
    "Toggle power": "전원 켜기/끄기",
    "Transfer From Drone": "드론에서 전송",
    "Transfer To Drone": "드론으로 전송",
    "Zoom Camera": "카메라 줌",
    "Action Name": "동작 이름",

    # ---- Misc ----
    "BLANK": "빈",
    "CURRENT OPTION": "현재 옵션",

    # ====================================================================
    # Station/Modules — module names + tooltip descriptions
    # ====================================================================
    "Module": "모듈",
    "Station Module": "스테이션 모듈",
    "Ammo Factory": "탄약 공장",
    "Produces various ammunition types for military-grade starships":
        "군용 우주선용 다양한 탄약을 생산합니다",
    "Antimatter Reactor": "반물질 원자로",
    "Harnesses the awesome power of Antimatter to generate massive amounts of energy":
        "반물질의 막대한 힘을 이용해 대량의 에너지를 생성합니다",
    "Base station for constructing and launching the Intergalactic Arkship":
        "은하 간 방주선의 건조와 발진을 위한 기지 스테이션",
    "Artifact Analyzer": "유물 분석기",
    "Feed alien artifacts into this module to unlock new technologies":
        "이 모듈에 외계 유물을 투입해 새로운 기술을 잠금 해제하세요",
    "Assembler": "조립기",
    "Assembles components into more complex parts": "부품을 더 복잡한 파츠로 조립합니다",
    "Atomizer": "분해기",
    "Destructs captured asteroids into raw materials": "포획한 소행성을 원자재로 분해합니다",
    "Protects your station against enemies and meteor strikes":
        "스테이션을 적과 운석 충돌로부터 보호합니다",
    "Centrifuge": "원심분리기",
    "Enriches waste products to create useable materials":
        "폐기물을 농축해 사용 가능한 재료를 생성합니다",
    "Cloud Miner": "구름 채굴기",
    "Deploys a harvester which can mine hydrogen gas from the upper atmosphere of a gas giant":
        "가스 거성 상층 대기에서 수소 가스를 채굴하는 수확선을 배치합니다",
    "Manufactures large starship and arkship components ready to be installed via tug.":
        "예인선으로 설치할 수 있는 대형 우주선 및 방주선 부품을 제조합니다.",
    "Connector": "연결기",
    "Expands your station and transports items between buildings. Can transport an <Bold>unlimited</> amount of <Bold>items per minute</>.":
        "스테이션을 확장하고 건물 간 아이템을 운송합니다. <Bold>분당 무제한</>의 <Bold>아이템</>을 운송할 수 있습니다.",
    "Construct onto a standard connector to add an extra layer on top of your station":
        "표준 연결기 위에 건설하여 스테이션에 한 층을 추가합니다",
    "Vertical Connector": "수직 연결기",
    "Construction Bay": "건조 베이",
    "Enables starship construction": "우주선 건조를 가능하게 합니다",
    "Constructs the largest class of starships": "가장 큰 함급의 우주선을 건조합니다",
    "Large Shipyard": "대형 조선소",
    "Constructs medium-sized starships": "중형 우주선을 건조합니다",
    "Medium Shipyard": "중형 조선소",
    "Constructs small starships": "소형 우주선을 건조합니다",
    "Small Shipyard": "소형 조선소",
    "Collects and safely stores unstable elements": "불안정한 원소를 수집하고 안전하게 보관합니다",
    "Containment Chamber": "격납 체임버",
    "Automatically destroys incoming meteors and hostile robots":
        "다가오는 운석과 적대 로봇을 자동으로 파괴합니다",
    "Defence Turret": "방어 포탑",
    "Targets and destroys Void Anomalies found at the event horizon of The Void. Requires Quantum Implosion Ammo.":
        "공허의 사건 지평선에서 발견되는 공허 이상 현상을 표적으로 파괴합니다. 양자 내파 탄약이 필요합니다.",
    "Launches homing missiles that are good at taking out groups of enemies.":
        "적 무리를 처리하기에 좋은 추적 미사일을 발사합니다.",
    "Missile Turret": "미사일 포탑",
    "Charges when you have excess power": "잉여 전력이 있을 때 충전됩니다",
    "Constructs equipment that can be fitted to your drone to expand its capabilities":
        "드론의 능력을 확장하기 위해 장착할 수 있는 장비를 제작합니다",
    "Directs planetary operations such as surface mining": "표면 채굴 같은 행성 운영을 지휘합니다",
    "Exoplanet Ops Centre": "외계행성 운영 센터",
    "Assembles simple parts into more complex ones": "단순 부품을 더 복잡한 부품으로 조립합니다",
    "Fabricator": "가공기",
    "Force-field Generator": "역장 발생기",
    "Generates an energy shield around nearby station modules that absorbs incoming damage":
        "인근 스테이션 모듈 주변에 들어오는 피해를 흡수하는 에너지 방어막을 생성합니다",
    "Allows freighters to load and unload materials": "화물선이 재료를 적재/하역할 수 있게 합니다",
    "Freighter Dock": "화물선 도크",
    "Consumes hydrogen to generate large amounts of energy": "수소를 소비해 대량의 에너지를 생성합니다",
    "Fusion Reactor": "융합로",
    "HUB": "허브",
    "The core of your station. Stores resources and generates power.":
        "스테이션의 중심. 자원을 저장하고 전력을 생성합니다.",
    "Intersteller stargate capable of transporting objects vast distances":
        "물체를 광활한 거리로 운송할 수 있는 항성 간 스타게이트",
    "The Gate": "게이트",
    "Buffers energy overload from an intersteller jump-gate":
        "항성 간 점프게이트의 에너지 과부하를 완충합니다",
    "Jumpgate Buffer": "점프게이트 버퍼",
    "Destroyed Jumpgate Buffer": "파괴된 점프게이트 버퍼",
    "Analyses items, materials and parts to unlock alternate recipes":
        "아이템, 재료, 부품을 분석해 대체 제작법을 잠금 해제합니다",
    "Assembles large and complicated parts from smaller ones":
        "작은 부품들로부터 크고 복잡한 부품을 조립합니다",
    "Manufactory": "제조소",
    "Matter Printer": "물질 프린터",
    "Produces simple parts from raw materials": "원자재로부터 단순 부품을 생산합니다",
    "Main control station for a particle accelerator ring. Converts Coated Exotic Matter into Antimatter.":
        "입자 가속기 고리의 주 제어 스테이션. 코팅된 이그조틱 물질을 반물질로 변환합니다.",
    "Accelerator Tower": "가속기 타워",
    "Serves as a junction point for Particle Accelerator Conduit, allowing you to form a Particle Accelerator loop.":
        "입자 가속기 도관의 분기점 역할을 하여 입자 가속기 루프를 형성할 수 있게 합니다.",
    "Pipe": "파이프",
    "Transfers liquids and gases around your station": "스테이션 주변에서 액체와 기체를 운송합니다",
    "Connects multiple pipes": "여러 파이프를 연결합니다",
    "Pipe Junction": "파이프 분기점",
    "Accelerator Conduit": "가속기 도관",
    "Use along with a Control Station and Towers to create a Particle Accelerator loop to generate Antimatter.":
        "제어 스테이션 및 타워와 함께 사용해 반물질을 생성하는 입자 가속기 루프를 만드세요.",
    "Plasma Forge": "플라즈마 용광로",
    "Uses superheated plasma to fuse elements into alloys":
        "초고열 플라즈마를 사용해 원소들을 합금으로 융합시킵니다",
    "Increases power production": "전력 생산을 증가시킵니다",
    "Generates power from sunlight. Becomes less efficient the more are connected together and must be aligned to the sun's direction.":
        "햇빛으로 전력을 생성합니다. 연결된 패널이 많을수록 효율이 떨어지며 태양 방향으로 정렬해야 합니다.",
    "Solar Panel": "태양광 패널",
    "Connects remote parts of your station to your power grid":
        "스테이션의 원격 부분을 전력망에 연결합니다",
    "Power Link": "전력 연결기",
    "Cyclone Generator": "사이클론 발전기",
    "Utilizes the cyclonic forces found within the lower atmosphere of a Gas Giant to generate power":
        "가스 거성 하층 대기의 사이클론 힘을 이용해 전력을 생성합니다",
    "Feed items and parts into this device to access them from anywhere via your Drone's inventory":
        "이 장치에 아이템과 부품을 투입하면 드론 인벤토리를 통해 어디서든 접근할 수 있습니다",
    "Feed in unwanted resources and exchange for Tokens that can be spent on various rewards":
        "원치 않는 자원을 투입하고 다양한 보상에 사용할 수 있는 토큰으로 교환합니다",
    "Converts liquids into gases and other products": "액체를 기체와 기타 제품으로 변환합니다",
    "Refinery": "정제소",
    "Extracts resources from ore nodes": "광맥에서 자원을 추출합니다",
    "Miner": "채굴기",
    "Bio Extractor": "바이오 추출기",
    "Extracts bio-compounds from local flora and fauna":
        "지역 동식물에서 생물 화합물을 추출합니다",
    "Extracts Exotic Matter from a Quantum Rift": "양자 균열에서 이그조틱 물질을 추출합니다",
    "Quantum Extractor": "양자 추출기",
    "Deploys an AI-powered helper-bot that can automatically perform tasks around your station":
        "스테이션 주변에서 작업을 자동 수행할 수 있는 AI 보조 로봇을 배치합니다",
    "Servitor Station": "서비터 스테이션",
    "Ammo Depot": "탄약 저장고",
    "Resupply depot where starships can be armed with weapons and ammunition":
        "우주선을 무기와 탄약으로 무장시킬 수 있는 재보급 저장고",
    "Fuel Depot": "연료 저장고",
    "Uses hydrogen to refuel starships": "수소를 사용해 우주선에 연료를 재공급합니다",
    "Processes raw materials into usable metals": "원자재를 사용 가능한 금속으로 가공합니다",
    "Smelter": "제련소",
    "Processes raw matter into usable materials": "원자재를 사용 가능한 재료로 가공합니다",
    "Massive structure capable of lifting valuable items, materials and parts directly from a planet's surface":
        "행성 표면에서 귀중한 아이템, 재료, 부품을 직접 들어 올릴 수 있는 거대한 구조물",
    "Holds resources": "자원을 보관합니다",
    "Storage": "저장소",
    "Pressurized container for gases and liquids": "기체와 액체를 위한 가압 용기",
    "Storage Tank": "저장 탱크",
    "Holds resources ready to be used in your station":
        "스테이션에서 사용될 준비가 된 자원을 보관합니다",
    "Storage Unit": "저장 유닛",
    "Lets you travel between destinations instantly": "목적지 사이를 즉시 이동할 수 있게 합니다",
    "Teleporter": "텔레포터",
    "Deploys a Tug which can move ships around your station":
        "스테이션 주변에서 함선을 이동시킬 수 있는 예인선을 배치합니다",
    "Tug Bay": "예인선 도크",
    "Deploys a Large Tug which can move the largest ships around your station":
        "스테이션 주변에서 가장 큰 함선을 이동시킬 수 있는 대형 예인선을 배치합니다",
    "Large Tug Bay": "대형 예인선 도크",
    "Establish a quantum connection to a terminus in another location to instantly send resources between them":
        "다른 장소의 터미너스와 양자 연결을 설립해 즉시 자원을 주고받을 수 있게 합니다",
    "Wormhole Terminus": "웜홀 터미너스",

    # ====================================================================
    # UI_HUD — bottom mode bar + general HUD labels
    # ====================================================================
    "BUILD": "건설",
    "COMBAT": "전투",
    "LINK": "연결",
    "SELL": "판매",
    "REPAIR": "수리",
    "CODEX": "코덱스",
    "MULTI-SEL": "다중 선택",
    "MULTI-SELECT": "다중 선택",
    "MULTI-SELECT:": "다중 선택:",
    "ADD TODO": "할 일 추가",
    "CALC": "계산기",
    "BLUEPRINTS": "청사진",
    "TODO LIST": "할 일 목록",
    "CUSTOM TASKS": "사용자 작업",
    "OVERVIEW": "개요",
    "STATUS VIEW": "상태 뷰",
    "PHOTO MODE": "사진 모드",
    "EXIT PHOTO MODE": "사진 모드 종료",
    "TAKE PHOTO": "사진 찍기",
    "[RECORDING]": "[녹화 중]",
    "OPEN\r\nSCREENSHOTS\r\nFOLDER": "스크린샷\r\n폴더\r\n열기",
    "GAME PAUSED": "게임 일시정지됨",
    "100 FPS": "100 FPS",
    "ADD MULTIPLE": "여러 개 추가",
    "ADD STOPOVER": "경유지 추가",
    "AREA SELECT": "영역 선택",
    "CLEAR": "초기화",
    "CLEAR ALL": "전부 초기화",
    "CLEAR ALL LINKS": "모든 연결 초기화",
    "CLEAR LINKS": "연결 초기화",
    "DESELECT": "선택 해제",
    "DRAG": "드래그",
    "HOLD": "길게 누름",
    "LOCKED": "잠김",
    "MOVE CAMERA": "카메라 이동",
    "MOVE FASTER": "더 빠르게 이동",
    "PLACE WAYPOINT": "경유점 배치",
    "RAISE/LOWER CAMERA": "카메라 높낮이",
    "ROTATE CAMERA": "카메라 회전",
    "SELECT AN": "선택",
    "SELECT SOURCE MODULE": "공급원 모듈 선택",
    "SELL MULTIPLE": "여러 개 판매",
    "SWAP DIRECTION": "방향 전환",
    "DECOMMISSION STATION": "스테이션 폐기",
    "OBJECTIVE": "목표",
    "OPTIONAL": "선택 사항",
    "PRIMARY": "주요",
    "RADIATION WARNING": "방사능 경고",
    "WARNINGS": "경고",
    "ARTIFACTS FOUND: ": "발견한 유물: ",
    "CYCLONIC POWER:": "사이클론 전력:",
    "ENEMY STRENGTH:": "적 전력:",
    "RESOURCES:": "자원:",
    "SUNLIGHT LEVEL:": "햇빛 수준:",
    "ZONE": "구역",
    "SYSTEM": "성계",
    "TAU": "TAU",
    "TEXT CHAT": "텍스트 채팅",
    "UPPER LEVEL HIDDEN": "상층부 숨김",
    "NEUTRON BEAM LAZER": "중성자 빔 레이저",
    "CTRL": "CTRL",

    # ====================================================================
    # UI_Tooltip_BuildItem / BlueprintItem — building-card hover tooltip
    # ====================================================================
    "BUILD COST:": "건설 비용:",
    "ADD/REMOVE ON HOT-BAR": "단축바에 추가/제거",
    "ADD TO TODO-LIST": "할 일 목록에 추가",
    "ALREADY BUILT": "이미 건설됨",
    "ALREADY BUILT IN THIS LOCATION": "이 장소에 이미 건설됨",
    "CANNOT BUILD IN THIS ZONE": "이 구역에서 건설할 수 없음",
    "CTRL +": "CTRL +",
    "EXPLODES ON DAMAGE": "피해 시 폭발",
    "FUEL": "연료",
    "HOLDS ANTIMATTER": "반물질 보유",
    "INSULATED": "절연됨",
    "MK": "MK",
    "MW": "MW",
    "PARTICLE ACCELERATOR": "입자 가속기",
    "RADIATION PROOF": "방사능 차폐",
    "VOLATILE": "휘발성",
    "WASTE": "폐기물",
    "BLUEPRINT": "청사진",
    "BLUEPRINT NAME": "청사진 이름",
    "Blueprint Items": "청사진 아이템",
    "CONTAINMENT CHAMBER": "격납 체임버",

    # ====================================================================
    # UI_Hovered_Module / UI_Selected_Module — module info panel labels
    # ====================================================================
    "/MIN": "/분",
    "<Bold>Overdrive Core Slot</>: Drop an Overdrive Core into this slot to overcharge this module":
        "<Bold>오버드라이브 코어 슬롯</>: 이 슬롯에 오버드라이브 코어를 떨어뜨려 모듈을 과충전하세요",
    "EFFICIENCY: ": "효율: ",
    "FLOW RATE": "흐름 속도",
    "Flow Rate": "흐름 속도",
    "INPUT": "입력",
    "Input": "입력",
    "ITEM OUTPUT": "아이템 출력",
    "ITEM UPLOAD": "아이템 업로드",
    "ITEMS RECEIVED": "받은 아이템",
    "MAX": "최대",
    "MAX EFFICIENCY:": "최대 효율:",
    "MAX FLOW RATE": "최대 흐름 속도",
    "MAX: ": "최대: ",
    "MINUTES": "분",
    "MODULE DISABLED": "모듈 비활성화됨",
    "MODULE STUNNED": "모듈 기절함",
    "MODULE NAME": "모듈 이름",
    "MOVE ALL": "전부 이동",
    "NOT\r\nCONNECTED": "연결되지\r\n않음",
    "ON": "켜짐",
    "OFF": "꺼짐",
    "OUTPUT": "출력",
    "OUTPUT: ": "출력: ",
    "Output": "출력",
    "PRODUCED: ": "생산됨: ",
    "RECIPE": "제작법",
    "RECIPE:": "제작법:",
    "SHIPS": "함선",
    "SORT": "정렬",
    "STATION NAME": "스테이션 이름",
    "STATUS COLOUR": "상태 색상",
    "STATUS COLOUR:": "상태 색상:",
    "TERMINUS": "터미너스",
    "TERMINUS NAME": "터미너스 이름",
    "TRAVEL TO OTHER SIDE": "반대편으로 이동",
    "USAGE: ": "사용량: ",
    "USE REPAIR FUNCTION": "수리 기능 사용",
    "USER NAME": "사용자 이름",
    "USER NAME ALT": "사용자 이름 대체",
    "VENT": "배출",
    "VENT ALL": "전부 배출",
    "Waste": "폐기물",
    "[UPGRADES]": "[업그레이드]",
    "PRIORITY": "우선순위",
    "POWER PRIORITY": "전력 우선순위",
    "POWER PRIORITY:": "전력 우선순위:",
    "PRIORITY:": "우선순위:",
    "COPY\r\nSETUP": "설정\r\n복사",
    "PASTE\r\nSETUP": "설정\r\n붙여넣기",
    "RESET\r\nDEFAULTS": "기본값\r\n재설정",
    "FLIP PIPE FLOW DIRECTION": "파이프 흐름 방향 전환",
    "DETAILS": "세부 정보",
    "PRODUCING:": "생산 중:",

    # ====================================================================
    # UI_Tooltip_Item / Recipe / LaboratoryItem / ContractItem
    # ====================================================================
    "ALTERNATE RECIPE": "대체 제작법",
    "CHOOSE AMOUNT": "수량 선택",
    "COMPONENT": "부품",
    "DAMAGES NEARBY MACHINES": "인근 기계에 피해",
    "EQUIPMENT: ": "장비: ",
    "EXPLODES IF POWER IS LOST": "전원 손실 시 폭발",
    "LIQUID/GAS": "액체/기체",
    "NAME": "이름",
    "PRODUCED AT": "생산 위치",
    "PURCHASE RECIPE": "제작법 구매",
    "RADIOACTIVE": "방사능",
    "RECIPE NAME": "제작법 이름",
    "SMELTER": "제련소",
    "SPLIT": "나누기",
    "TRANSPORT VIA PIPES": "파이프로 운송",
    "TRANSPORT VIA TUG": "예인선으로 운송",
    "UNSTABLE": "불안정",
    "Used in": "사용처",
    "UNLOCKED": "잠금 해제됨",

    # ---- UI_Tooltip_ContractItem ----
    "ARMED": "무장됨",
    "FROM HUB": "허브에서",
    "FUELLED": "연료 주입됨",
    "MUST BE FULLY ARMED IN AN AMMO BAY": "탄약고에서 완전 무장되어야 함",
    "MUST BE FULLY FUELLED IN A FUEL BAY": "연료고에서 완전 연료 주입되어야 함",
    "PRESS": "누름",
    "TO LAUNCH": "발진",
    "TO SEND": "전송",
    "TRANSFER MATERIALS INTO": "재료 전송 대상",

    # ====================================================================
    # UI_Tooltip_TechUpgrade / ObjectUpgrade
    # ====================================================================
    "DESCRIPTION": "설명",
    "LEVEL": "레벨",
    "NOT ENOUGH TECH POINTS": "기술 포인트 부족",
    "PURCHASED": "구매됨",
    "REQUIRES": "필요 사항",
    "UPGRADE: ": "업그레이드: ",
    "UPGRADE COST": "업그레이드 비용",
    "YOU HAVE NOT UNLOCKED\r\nTHIS UPGRADE": "이 업그레이드는\r\n잠금 해제되지 않았습니다",
    "III": "III",

    # ====================================================================
    # UI_MultiSelect_Modules
    # ====================================================================
    "BLUEPRINT IS TOO LARGE": "청사진이 너무 큼",
    "CREATE": "만들기",
    "CREATE BLUEPRINT": "청사진 만들기",
    "LINK ALL": "전부 연결",
    "MAX INPUT ITEMS": "최대 입력 아이템",
    "MAX OUTPUT ITEMS": "최대 출력 아이템",
    "MAX POWER FUEL": "최대 전력 연료",
    "NEW BLUEPRINT": "새 청사진",
    "SELECT MODULE": "모듈 선택",
    "Selected Modules": "선택된 모듈",
    "Selected Ships": "선택된 함선",
    "Upgrades": "업그레이드",

    # ====================================================================
    # UI_Codex
    # ====================================================================
    "EXPLORATION": "탐사",
    "LOCATIONS": "장소",
    "MILITARY": "군사",
    "OPERATIONS": "운영",
    "RECIPES": "제작법",
    "SCIENCE": "과학",
    "STATION LEVELS": "스테이션 레벨",
    "STORY": "스토리",
    "SELECT A TUTORIAL FROM THE LIST": "목록에서 튜토리얼을 선택하세요",
    "TUTORIAL:": "튜토리얼:",
    "TUTORIALS": "튜토리얼",

    # ====================================================================
    # UI_Tutorial_Popup / UI_StoryPopup
    # ====================================================================
    "<Bold>NOTE:</> YOU CAN ACCESS ALL PREVIOUSLY VIEWED TUTORIAL VIDEOS FROM THE <Bold>CODEX</>":
        "<Bold>참고:</> 이전에 본 모든 튜토리얼 영상은 <Bold>코덱스</>에서 다시 볼 수 있습니다",
    "<Bold>NOTE:</> YOU CAN SEE ALL COMPLETED STORY CHAPTERS FROM THE <Bold>CODEX</>":
        "<Bold>참고:</> 완료한 모든 스토리 챕터는 <Bold>코덱스</>에서 볼 수 있습니다",
    "SHOW TUTORIAL POPUPS": "튜토리얼 팝업 표시",
    "TUTORIAL NAME": "튜토리얼 이름",
    "The Story So Far...": "지금까지의 이야기...",

    # ====================================================================
    # UI_ActiveContract / UI_Objectives
    # ====================================================================
    "CHANGE OBJECTIVE": "목표 변경",
    "COMPLETE": "완료",
    "COMPLETED": "완료됨",
    "FAILED": "실패",
    "MISSION": "임무",
    "NO SPACE IN HUB": "허브에 공간 없음",
    "REJECT": "거부",
    "STATION EXPANSION": "스테이션 확장",
    "ARKSHIP STAGE": "방주선 단계",
    "Continue expanding your industrial empire and \r\nStation Command will be in touch very soon...":
        "산업 제국 확장을 계속하세요. 스테이션 본부가\r\n곧 연락드리겠습니다...",
    "Locate and destroy the following in the <Bold>Asteroid Belt 2</> Zone:":
        "<Bold>소행성대 2</> 구역에서 다음을 찾아 파괴하세요:",
    "On completion you will receive:": "완료 시 다음을 받게 됩니다:",
    "Please construct the following ships:": "다음 함선들을 건조해 주세요:",
    "Please place the following items in your HUB:": "다음 아이템들을 허브에 배치해 주세요:",
    "No Objective Selected": "선택된 목표 없음",
    "Objectives <Bold>Panel</>": "목표 <Bold>패널</>",
    "Required Items": "필요한 아이템",
    "Required Ships": "필요한 함선",
    "Requires <Bold>Enhanced Manufacturing</> to be unlocked":
        "<Bold>강화 제조</> 잠금 해제 필요",
    "Rewards": "보상",
    "SELECT OBJECTIVE": "목표 선택",
    "SUB-OBJECTIVE": "하위 목표",
    "This is a description for this <Bold>sub-objective</>\r\nThis is a description for this <Bold>sub-objective</>":
        "이 <Bold>하위 목표</>의 설명입니다\r\n이 <Bold>하위 목표</>의 설명입니다",
    "CONTINUE EXPANDING YOUR INDUSTRIAL EMPIRE AND STATION COMMAND WILL BE IN TOUCH VERY SOON...":
        "산업 제국 확장을 계속하면 스테이션 본부가 곧 연락드리겠습니다...",

    # ====================================================================
    # UI_Message_ObjectiveCompleted
    # ====================================================================
    "ASTEROID BELT": "소행성대",
    "EQUIPMENT": "장비",
    "MODULES": "모듈",
    "NEW": "새로운",
    "NEW LOCATION UNLOCKED:": "새 장소 잠금 해제됨:",
    "PARTS": "부품",
    "PROMOTION RECEIVED": "승진 받음",
    "STATION LEVEL": "스테이션 레벨",
    "TECH UPGRADES": "기술 업그레이드",

    # ====================================================================
    # UI_Drone_Inventory
    # ====================================================================
    "QUANTUM\r\nSTORAGE": "양자\r\n저장소",
    "QUANTUM STORAGE": "양자 저장소",
    "SELECT A RECIPE": "제작법 선택",
    "SYNTHESIZE": "합성",
    "SYNTHESIZER": "합성기",
    "Advanced": "고급",

    # ====================================================================
    # UI_Hovered_Ship / UI_Tooltip_ShipBlueprint
    # ====================================================================
    "AMMO": "탄약",
    "CAPTURE": "포획",
    "CARRY TO": "운반 대상",
    "CLASS": "함급",
    "MEDIUM": "중형",
    "MUST BE FUELLED TO AVOID MELTDOWN": "멜트다운 방지를 위해 연료 주입 필수",
    "REACTOR": "원자로",
    "READY TO LAUNCH": "발진 준비 완료",
    "SHIP DESCRIPTION": "함선 설명",
    "SHIP NAME": "함선 이름",
    "TO": "에",
    "ADD TO QUEUE": "대기열에 추가",
    "ADD/REMOVE x 10": "추가/제거 x 10",
    "BUILD PARTS": "부품 건설",
    "REMOVE FROM QUEUE": "대기열에서 제거",

    # ====================================================================
    # UI_Hovered_Asteroid
    # ====================================================================
    "ASTEROID": "소행성",
    "CONTENTS": "내용",
    "EXPLODES ON IMPACT": "충돌 시 폭발",
    "Feed into an Atomizer to extract raw materials Feed into an Atomizer to extract raw materials":
        "분해기에 투입해 원자재를 추출하세요",
    "WILL EXPLODE AFTER A TIME": "일정 시간 후 폭발",

    # ====================================================================
    # UI_Hovered_Zone / UI_Dialog_CreateStation
    # ====================================================================
    "ARTIFACTS:": "유물:",
    "CREATE NEW <Bold>STATION</>": "새 <Bold>스테이션</> 만들기",
    "SIZE:": "크기:",
    "SUNLIGHT POWER:": "햇빛 전력:",
    "ZONE NAME": "구역 이름",
    "CANNOT AFFORD": "비용 부족",
    "CONFIRM NEW STATION": "새 스테이션 확인",
    "Parts required:": "필요한 부품:",

    # ====================================================================
    # UI_Panel_* — various panels
    # ====================================================================
    "EMPTY": "비어있음",
    "NEXT LEVEL": "다음 레벨",
    "NO SHIPS FOUND": "함선을 찾지 못함",
    "ORDER SHIP": "함선 주문",
    "POINTS": "포인트",
    "REDEEM": "교환",
    "TOKEN SHOP": "토큰 상점",
    "TOKENS": "토큰",
    "TECH POINTS": "기술 포인트",
    "TECH POINTS AVAILABLE": "기술 포인트 보유",
    "ALIEN ARTIFACT": "외계 유물",
    "NO SUBJECT FOR ANALYSIS": "분석할 대상 없음",
    "SCANNING:": "스캔 중:",
    "SELECT AN UPGRADE": "업그레이드 선택",
    "BAY EMPTY": "베이 비어있음",
    "CLEAR\r\nQUEUE": "대기열\r\n초기화",
    "CURRENT PROJECT": "현재 프로젝트",
    "SHIP IS BLOCKING BAY": "함선이 베이를 막고 있음",
    "SHIPYARD IDLE": "조선소 대기 중",
    "BUILD MORE CONDUIT TO FORM A CLOSED CIRCUIT": "닫힌 회로를 형성하려면 도관을 더 건설하세요",
    "LOOP NOT COMPLETE": "루프 미완성",
    "Loop length:": "루프 길이:",
    "OUTPUT:": "출력:",
    "POWER NEEDED:": "필요 전력:",
    "/ MIN": "/ 분",
    "mw": "mw",
    "CONNECTED": "연결됨",
    "CONNECTED TO": "연결 대상",
    "CURRENT ZONE": "현재 구역",
    "NEW WORMHOLE": "새 웜홀",
    "REMOTE ZONES": "원격 구역",
    "SEARCH FOR TERMINUS": "터미너스 검색",
    "WORMHOLES AVAILABLE": "사용 가능한 웜홀",
    "ZONE:": "구역:",
    "NO POWER": "전력 없음",
    "LINKS AVAILABLE": "사용 가능한 연결",
    "MAX LINKS:": "최대 연결:",
    "NEW POWER LINKER": "새 전력 연결기",
    "SEARCH FOR LINK": "연결 검색",
    "ALIGN SOLAR PANELS": "태양광 패널 정렬",
    "GATHER RESOURCES": "자원 수집",
    "REPAIR DAMAGED MODULES": "손상된 모듈 수리",
    "TASKS": "작업",
    "DESTINATIONS": "목적지",
    "NEW TELEPORTER": "새 텔레포터",
    "SEARCH FOR DESTINATION": "목적지 검색",

    # ====================================================================
    # UI_Selected_Freighter / UI_Hovered_Freighter
    # ====================================================================
    "Dropoff At": "하차 위치",
    "FREIGHTER NAME": "화물선 이름",
    "FREIGHTER PAUSED WHILE SELECTED": "선택 중 화물선 일시정지",
    "Freighter Description Freighter Description": "화물선 설명",
    "MAX WAIT TIME": "최대 대기 시간",
    "Pickup From": "픽업 위치",
    "SEARCH FOR DOCK": "도크 검색",
    "WAIT FOR ITEMS": "아이템 대기",
    "20s": "20초",
    "60s": "60초",
    "Transports materials and parts between stations": "스테이션 간 재료와 부품을 운송합니다",

    # ====================================================================
    # UI_CreateTodo / CustomTodoTask
    # ====================================================================
    "COLOUR:": "색상:",
    "CUSTOM TASK": "사용자 작업",
    "Create a custom todo task with 5 optional sub-tasks that is shared between all players:":
        "5개의 선택적 하위 작업을 가진 사용자 할 일 작업을 만듭니다 (모든 플레이어가 공유):",
    "IS SHARED:": "공유됨:",
    "NAME:": "이름:",
    "NEW TODO ITEM": "새 할 일 아이템",
    "SUB TASK 1": "하위 작업 1",
    "SUB TASK 2": "하위 작업 2",
    "SUB TASK 3": "하위 작업 3",
    "SUB TASK 4": "하위 작업 4",
    "SUB TASK 5": "하위 작업 5",
    "SUB TASKS": "하위 작업",
    "TUTORIAL TITLE": "튜토리얼 제목",

    # ====================================================================
    # UI_Selected_Module_PowerDetails / UI_Selected_Pod / UI_Hovered_Pod
    # ====================================================================
    "CHARGING:": "충전 중:",
    "DISCHARGING:": "방전 중:",
    "MAX CONSUMED": "최대 소비",
    "POWER DETAILS": "전력 세부 정보",
    "PRODUCED:": "생산됨:",
    "STORED": "저장됨",
    "TOTAL NETWORK": "전체 네트워크",
    "USAGE": "사용량",
    "USED:": "사용됨:",
    "POD NAME": "포드 이름",
    "Pod Description": "포드 설명",
    "SUPPLY THE FOLLOWING ITEMS TO UNLOCK:": "잠금 해제하려면 다음 아이템을 공급하세요:",
    "UNLOCK": "잠금 해제",

    # ====================================================================
    # Misc panels & dialogs
    # ====================================================================
    "Item filters": "아이템 필터",
    "COPY": "복사",
    "COPY TO ALL": "전체에 복사",
    "RESET\r\nALL": "전체\r\n재설정",
    "RESET\r\nSLOT": "슬롯\r\n재설정",
    "RESET ALL": "전체 재설정",
    "SET TO CURRENT": "현재로 설정",
    "PASTE": "붙여넣기",
    "ADD CONNECTORS": "연결기 추가",
    "BUILDING: ": "건설 중: ",
    "CHANGE HEIGHT": "높이 변경",
    "ROTATE": "회전",
    "ARKSHIP STAGE NAME": "방주선 단계 이름",
    "COMPLETE STAGE": "단계 완료",
    "ITEMS REQUIRED": "필요 아이템",
    "POWER REQUIRED": "필요 전력",
    "STAGE": "단계",
    "Location": "장소",
    "NO DATA TO SHOW": "표시할 데이터 없음",
    "PRODUCTION OVERVIEW": "생산 개요",
    "TUTORIAL TITLE TUTORIAL TITLE": "튜토리얼 제목",
    "UNLOCKS:": "잠금 해제 항목:",
    "OBJECTIVES:": "목표:",
    "OBJECTIVE NAME": "목표 이름",
    "TRANSMISSIONS:": "전송:",
    "Zone <Bold>Description</>": "구역 <Bold>설명</>",
    "RANK": "계급",
    "CAPTAIN": "대위",
    "Enter The Void": "공허로 들어가기",
    "Escape The Void": "공허에서 탈출",
    "Launch the Intergalactic Arkship and travel to another galaxy...":
        "은하 간 방주선을 발진해 다른 은하로 이동...",
    "MAKE YOUR CHOICE...": "선택하세요...",
    "Pilot the Arkship into the Void and achieve singularity...":
        "방주선을 공허로 조종해 특이점에 도달...",
    "(Early Access placeholder voice)": "(얼리 액세스 임시 음성)",
    "ESCAPE": "ESC",
    "Skip": "건너뛰기",
    "CURRENT TARGET:": "현재 대상:",
    "Description": "설명",
    "SCAVENGER NAME": "스캐빈저 이름",
    "TITANIUM": "티타늄",
    "TITANIUM ORE": "티타늄 광석",
    "FUEL INJECTION": "연료 분사",

    # ====================================================================
    # Asteroids / Containers / Pods (BP_Asteroid_*, BP_Container_*)
    # ====================================================================
    "Asteroid": "소행성",
    "Feed into an Atomizer to extract resources": "분해기에 투입해 자원을 추출하세요",
    "Feed into a Containment Chamber to extract resources": "격납 체임버에 투입해 자원을 추출하세요",
    "Gold Asteroid": "금 소행성",
    "Ice Asteroid": "얼음 소행성",
    "Titanium Asteroid": "티타늄 소행성",
    "Tungsten Asteroid": "텅스텐 소행성",
    "Uranium Asteroid": "우라늄 소행성",
    "Debris": "잔해",
    "Gasbag Plant": "가스주머니 식물",
    "Meteor Core": "운석 코어",
    "Wreckage": "잔해",
    "Lootable Container": "약탈 가능한 컨테이너",
    "Pod": "포드",
    "Crashed Ship": "추락한 함선",
    "Lootable Wreckage": "약탈 가능한 잔해",
    "Nitratium Pod": "니트라튬 포드",
    "Large Nitratium Pod": "대형 니트라튬 포드",
    "Scavengable remains": "약탈 가능한 잔해",
    "Derelict Ship": "버려진 함선",
    "Cargo Door Lock": "화물문 잠금장치",
    "Security Device": "보안 장치",
    "Shipping Container": "화물 컨테이너",
    "Ancient Cargo": "고대 화물",
    "Freighter Pod": "화물선 포드",
    "Player Pod": "플레이어 포드",
    "Station Pod": "스테이션 포드",
    "Place into an Artifact Analyzer to gain vital Tech Upgrades":
        "유물 분석기에 넣어 중요한 기술 업그레이드를 획득하세요",
    "Artifact": "유물",

    # ====================================================================
    # Robots (BP_Robot_*)
    # ====================================================================
    "Beamer": "비머",
    "Lazer defence drone": "레이저 방어 드론",
    "Beamer Turret": "비머 포탑",
    "Lazer defence turret": "레이저 방어 포탑",
    "Shielded Beamer Turret": "방어막 비머 포탑",
    "Promethean": "프로메테우스",
    "Exotic Matter Robot": "이그조틱 물질 로봇",
    "Stinger": "스팅어",
    "Pizo-electric gelatinous creature": "압전성 젤라틴 생물",
    "Seeker": "추적자",
    "Homing Missile Drone": "추적 미사일 드론",
    "Dactyl": "닥틸",
    "Winged reptilian creature": "날개 달린 파충류 생물",
    "Armadillo": "아르마딜로",
    "Shield Drone": "방어막 드론",
    "Slinger": "슬링어",
    "Defence Drone": "방어 드론",
    "Plasma Turret": "플라즈마 포탑",
    "Defence robot": "방어 로봇",
    "Trapdoor": "트랩도어",
    "Ancient Defence Turret": "고대 방어 포탑",
    "Mine": "지뢰",
    "Magnetic explosive device": "자기 폭발 장치",
    "Jumpgate buffer wreckage": "점프게이트 버퍼 잔해",

    # ====================================================================
    # Ships (BP_Ship_*)
    # ====================================================================
    "Aeon": "이언",
    "Aeon Scout": "이언 정찰선",
    "Short-range exploration ship": "단거리 탐사선",
    "Aeon Hopper": "이언 호퍼",
    "General-purpose utility ship": "범용 유틸리티 함선",
    "Colossus": "콜로서스",
    "Battlecruiser": "전투순양함",
    "Colossus Imperator": "콜로서스 임페라토르",
    "Colossus Prodigy": "콜로서스 프로디지",
    "Massive science and research vessel": "거대 과학 및 연구 함선",
    "Crusader Victor": "크루세이더 빅터",
    "Fleet Escort Destroyer": "함대 호위 구축함",
    "Crusader Auxilliary": "크루세이더 보조함",
    "Bulk refuelling and resupply ship": "대량 재급유 및 재보급 함선",
    "Crusader Explorer": "크루세이더 익스플로러",
    "Capital exploration and science vessel": "주력급 탐사 및 과학 함선",
    "Meson": "메슨",
    "Meson Archer": "메슨 아처",
    "Light Missile Frigate": "경미사일 호위함",
    "Meson Heavy Hauler": "메슨 헤비 해울러",
    "Heavy Cargo Ship": "중형 화물선",
    "Meson Lifter": "메슨 리프터",
    "Heavy Cargo Shuttle": "중형 화물 셔틀",
    "Neutron": "뉴트론",
    "Neutron Explorer": "뉴트론 익스플로러",
    "Advanced exploration ship": "고급 탐사선",
    "Photon": "포톤",
    "Photon Light Hauler": "포톤 라이트 해울러",
    "Light cargo transport ship": "경량 화물 운송선",
    "Photon Tanker": "포톤 탱커",
    "Light fuel transport ship": "경량 연료 운송선",
    "Stratos": "스트라토스",
    "Stratos Interceptor": "스트라토스 인터셉터",
    "Planetary Defence Fighter": "행성 방어 전투기",
    "Stratos Prospector": "스트라토스 프로스펙터",
    "Sensor and sampling ship": "센서 및 샘플링 함선",

    # ====================================================================
    # Zones (BP_Zone_*)
    # ====================================================================
    "Terra": "테라",
    "Our home system": "우리 고향 성계",
    "Located on the far edge of the system, the asteroid belt has abundant basic resources and few hostiles.":
        "성계 외곽에 위치한 소행성대는 풍부한 기본 자원과 적은 적대 세력이 있습니다.",
    "Titania - Low Orbit": "티타니아 - 저궤도",
    "The cloud-packed atmosphere of the gas-giant Titania provides easy access to Hydrogen, though aggressive local fauna may cause a problem to undefended stations.":
        "구름이 가득한 가스 거성 티타니아의 대기는 수소에 쉽게 접근할 수 있게 해 주지만, 공격적인 토착 동물군이 방어되지 않은 스테이션에 문제를 일으킬 수 있습니다.",
    "Helion": "헬리온",
    "This resource rich moon orbits the gas giant Scylla and may be the perfect site for surface-based mining facilities":
        "이 자원이 풍부한 위성은 가스 거성 스킬라를 공전하며 표면 기반 채굴 시설로 완벽한 장소가 될 수 있습니다",
    "Glacialis - Ice Ring": "글라시알리스 - 얼음 고리",
    "The frozen rings of the ice planet Glacialis are an ideal location to mine ice asteroids and automate water and oxygen production.":
        "얼음 행성 글라시알리스의 얼어붙은 고리는 얼음 소행성을 채굴하고 물과 산소 생산을 자동화하기에 이상적인 장소입니다.",
    "Junkyard": "고철장",
    "The shattered debris of an ancient war orbit the blasted planet Cerberus. Exotic matter can be found here, but beware the automated defences that remain active.":
        "고대 전쟁의 파편이 폭격된 행성 케르베로스를 공전합니다. 이그조틱 물질을 찾을 수 있지만, 여전히 활동하는 자동 방어 시설을 조심하세요.",
    "The Void - Event Horizon": "공허 - 사건 지평선",
    "Perched on the cusp of The Void's Event Horizon, this dangerous location may hold the key to our salvation.":
        "공허의 사건 지평선 끝자락에 자리 잡은 이 위험한 장소가 우리 구원의 열쇠를 가지고 있을지도 모릅니다.",

    # ====================================================================
    # Events (BP_Event_*)
    # ====================================================================
    "Particle Storm": "입자 폭풍",
    "Electromagnetic Storm": "전자기 폭풍",
    "Firestorm": "화염 폭풍",
    "Ice Comet": "얼음 혜성",
    "Ice Storm": "얼음 폭풍",
    "Meteor Storm": "운석 폭풍",
    "Meteor Strike": "운석 충돌",
    "Micro-Meteor Swarm": "마이크로 운석 무리",
    "Quantum Storm": "양자 폭풍",
    "Creature Swarm": "생명체 무리",

    # ====================================================================
    # UI_Dialog_Calculator
    # ====================================================================
    "CALCULATE": "계산",
    "RESULT": "결과",
    "EXECUTE": "실행",
    "CLOSE": "닫기",

    # ====================================================================
    # UI hover/popup widgets — labels in object descriptions
    # ====================================================================
    "CLOUD HARVESTER": "구름 수확기",
    "Harvests hydrogen gas from the upper atmosphere of gas giants":
        "가스 거성의 상층 대기에서 수소 가스를 수확합니다",
    "PLANETARY LIFTER": "행성 리프터",
    "Transports resources from a planet's surface into orbit":
        "행성 표면에서 궤도로 자원을 운송합니다",
    "MATERIAL": "재료",
    "NODE": "노드",
    "Mineable source of raw materials": "채굴 가능한 원자재 공급원",
    "ARKSHIP TERMINAL": "방주선 터미널",
    "ARKSHIP LAUNCHED": "방주선 발진됨",
    "LOW POWER": "전력 부족",
    "FREIGHTER": "화물선",
    "NEW FREIGHTER DOCK": "새 화물선 도크",
    "SELECT FREIGHTERS": "화물선 선택",
    "ENEMY NAME": "적 이름",
    "ROBOT NAME": "로봇 이름",
    "Robot Description": "로봇 설명",
    "WAYPOINT NAME": "경유점 이름",
    "WAYPOINT:": "경유점:",
    "WAYPOINT": "경유점",
    "OBJECT NAME": "오브젝트 이름",
    "SHIP TUG": "함선 예인선",
    "Moves completed ships around parts of your station":
        "완성된 함선을 스테이션 부품 사이로 이동시킵니다",
    "Sun Alignment": "태양 정렬",
    "Efficiency": "효율",
    "Panels in Network": "네트워크 내 패널",
    "SUN ALIGNMENT": "태양 정렬",
    "AVAILABLE BAYS": "사용 가능 베이",
    "AVAILABLE RESOURCES": "사용 가능 자원",
    "MAX LIFTERS IN LOCATION": "장소 내 최대 리프터",
    "MAX REACHED IN LOCATION": "장소 내 최대 도달",
    "EQUIPMENT NAME": "장비 이름",
    "Parts Required": "필요 부품",
    "SELECT AN ITEM TO CRAFT": "제작할 아이템 선택",
    "LOCATION": "장소",
    "BAY": "베이",
    "UNLOCK BAY FOR:": "베이 잠금 해제:",
    "ENTRY TITLE": "항목 제목",
    "EXTRA DATA:": "추가 데이터:",
    "HOTKEY:": "단축키:",
    "TIPS:": "팁:",
    "TIP: ": "팁: ",
    "LOADING": "로딩 중",
    "ENTERING ZONE": "구역 진입",
    "TUTORIAL": "튜토리얼",
    "TITLE": "제목",
    "ERROR REASON": "오류 사유",
    "ERROR MESSAGE": "오류 메시지",
    "STUNNED": "기절함",
    "Repairing...": "수리 중...",
    "Selling...": "판매 중...",
    "Teleporting to Hub...": "허브로 순간이동 중...",
    "BASIC SHIP CONSTRUCTION": "기본 함선 건조",
    "TRANSFER": "전송",
    "Choose amount to transfer:": "전송 수량 선택:",
    "ITEM NAME": "아이템 이름",
    "AVAILABLE RECIPES": "사용 가능한 제작법",
    "Available Recipes": "사용 가능한 제작법",
    "Available Items": "사용 가능한 아이템",
    "TECH POINT": "기술 포인트",
    "POWER LINKER NAME": "전력 연결기 이름",
    "PROLOGUE": "프롤로그",
    "PART": "파트",
    "THE TAU SYSTEM": "타우 성계",
    "WELCOME TO THE TAU SYSTEM": "타우 성계에 오신 것을 환영합니다",
    "Marker Label": "마커 라벨",
    "MARKER MESSAGE": "마커 메시지",
    "LABEL": "라벨",
    "LABEL TEXT": "라벨 텍스트",
    "MICRO DRONE": "마이크로 드론",
    "SUPERCONDUCTOR": "초전도체",
    "TYPE": "유형",
    "Title": "제목",
    "Name": "이름",
    "REWARDS": "보상",
    "MINUTE": "분",
    "UPGRADES": "업그레이드",
    "UNLOCKS:": "잠금 해제:",
    "NEW <Bold>PHASE</> STEP": "새 <Bold>단계</> 스텝",
    "<Bold>Current</> Phase Title": "<Bold>현재</> 단계 제목",
    "<Bold>Current</> Step Text": "<Bold>현재</> 스텝 텍스트",
    "<Bold>Player:</> This is a chat message": "<Bold>플레이어:</> 채팅 메시지입니다",
    "EQUIPMENT:": "장비:",
    "UNLOCK NAME": "잠금 해제 이름",
    "UNLOCKED:": "잠금 해제됨:",
    "MAX:": "최대:",
    "CURRENT:": "현재:",
    "Options": "옵션",
    "MODULE": "모듈",
    "TECH UPGRADES": "기술 업그레이드",
    "UPGRADE": "업그레이드",
    "II": "II",
    "Warning Text": "경고 텍스트",
    "ENEMY": "적",
    "Cutscenes": "컷씬",

    # ====================================================================
    # BP_Tutorial_Prologue — early tutorial step text
    # ====================================================================
    "Prologue": "프롤로그",
    "Camera Navigation": "카메라 조작",
    "Move around using <Bold>W,A,S,D</> / <Bold>Arrow keys</> or holding <Bold>MMB</>":
        "<Bold>W,A,S,D</> / <Bold>방향키</> 또는 <Bold>휠클릭</>을 누른 채 이동합니다",
    "Move around using <img id=\"Gamepad_Left_Thumbstick\"/>":
        "<img id=\"Gamepad_Left_Thumbstick\"/>로 이동합니다",
    "Pan camera by holding <Bold>Middle Mouse Button</>": "<Bold>휠클릭</>을 누른 채 카메라를 움직입니다",
    "Pan camera using <Bold>W,A,S,D</> or <Bold>Arrow keys</>":
        "<Bold>W,A,S,D</> 또는 <Bold>방향키</>로 카메라를 움직입니다",
    "Pan camera using <img id=\"Gamepad_Left_Thumbstick\"/>":
        "<img id=\"Gamepad_Left_Thumbstick\"/>로 카메라를 움직입니다",
    "Rotate camera by holding <Bold>Right Mouse Button</>":
        "<Bold>우클릭</>을 누른 채 카메라를 회전합니다",
    "Rotate camera using <img id=\"Gamepad_Right_Thumbstick\"/>":
        "<img id=\"Gamepad_Right_Thumbstick\"/>로 카메라를 회전합니다",
    "Zoom camera using <Bold>Mouse Wheel</> or <Bold>Page Up/Down</>":
        "<Bold>마우스 휠</> 또는 <Bold>Page Up/Down</>으로 카메라를 줌합니다",
    "Zoom camera with <img id=\"Gamepad_Left_Trackpad_Y\"/>":
        "<img id=\"Gamepad_Left_Trackpad_Y\"/>로 카메라를 줌합니다",
    "Gather <Bold>Resources</>": "<Bold>자원</> 수집",
    "Drag a <Bold>titanium asteroid</> into the <Bold>Atomizer</>":
        "<Bold>티타늄 소행성</>을 <Bold>분해기</>로 끌어 넣으세요",
    "Hold <Bold>SHIFT</> and click or hold <Bold>LMB</> to collect <Bold>multiple</> asteroids and feed into the <Bold>Atomizer</>":
        "<Bold>SHIFT</>를 누르고 클릭하거나 <Bold>좌클릭</>을 누른 채 <Bold>여러</> 소행성을 수집해 <Bold>분해기</>에 투입하세요",
    "Hold <img id=\"Gamepad_Left_Bumper\"/> and <img id=\"Gamepad_Left_Trigger\"/> to collect <Bold>multiple</> asteroids and feed into the <Bold>Atomizer</>":
        "<img id=\"Gamepad_Left_Bumper\"/>와 <img id=\"Gamepad_Left_Trigger\"/>를 누른 채 <Bold>여러</> 소행성을 수집해 <Bold>분해기</>에 투입하세요",
    "You can <bold>hold left-click</> to quickly gather asteroids":
        "<bold>좌클릭을 누른 채</> 소행성을 빠르게 수집할 수 있습니다",
    "You can hold <img id=\"Gamepad_Left_Trigger\"/> to quickly gather asteroids":
        "<img id=\"Gamepad_Left_Trigger\"/>를 눌러 소행성을 빠르게 수집할 수 있습니다",
    "Construct an <Bold>Atomizer</> and <Bold>Smelter</>": "<Bold>분해기</>와 <Bold>제련소</>를 건설하세요",
    "Construct a <Bold>Solar Generator</>": "<Bold>태양광 발전기</>를 건설하세요",
    "Construct a <Bold>Storage Module</>": "<Bold>저장 모듈</>을 건설하세요",
    "Construct <Bold>2 additional Smelters</>": "<Bold>제련소 2개를 추가로</> 건설하세요",
    "Build a <Bold>Smelter</> from the <Bold>Production</> category":
        "<Bold>생산</> 카테고리에서 <Bold>제련소</>를 건설하세요",
    "Build an <Bold>Atomizer</> from the <Bold>Resources</> category":
        "<Bold>자원</> 카테고리에서 <Bold>분해기</>를 건설하세요",
    "<bold>Drag</> when building to <Bold>auto-add connectors</>":
        "건설 시 <bold>드래그</>하면 <Bold>연결기가 자동 추가</>됩니다",
    "Set up <Bold>Smelter</>": "<Bold>제련소</> 설정",
    "Select one of your <Bold>Smelters</>": "<Bold>제련소</> 하나를 선택하세요",
    "Select the <Bold>Titanium recipe</> from the <Bold>Smelter</>":
        "<Bold>제련소</>에서 <Bold>티타늄 제작법</>을 선택하세요",
    "Set one new <Bold>Smelter</> to produce <Bold>Glass Fibre</> and the other <Bold>Gold</>":
        "새 <Bold>제련소</> 하나를 <Bold>유리섬유</> 생산으로, 다른 하나를 <Bold>금</> 생산으로 설정하세요",
    "<Bold>Linking</> modules": "<Bold>모듈 연결</>",
    "<Bold>Unlinking</> modules": "<Bold>모듈 연결 해제</>",
    "<Bold>Link</> the <Bold>Atomizer</> to the <Bold>Smelter</>":
        "<Bold>분해기</>를 <Bold>제련소</>에 <Bold>연결</>하세요",
    "<Bold>Link</> the <Bold>Atomizer</> to the new <Bold>Smelters</>":
        "<Bold>분해기</>를 새 <Bold>제련소</>에 <Bold>연결</>하세요",
    "<Bold>Link</> the <Bold>Smelter</> to the <Bold>HUB</>":
        "<Bold>제련소</>를 <Bold>허브</>에 <Bold>연결</>하세요",
    "<Bold>Link</> all of the <Bold>Smelters</> to the <Bold>Storage Module</>":
        "모든 <Bold>제련소</>를 <Bold>저장 모듈</>에 <Bold>연결</>하세요",
    "<Bold>Link</> the <Bold>Storage Module</> to the <Bold>HUB</>":
        "<Bold>저장 모듈</>을 <Bold>허브</>에 <Bold>연결</>하세요",
    "<Bold>Unlink</> the <Bold>Smelter</> from the <Bold>HUB</>":
        "<Bold>제련소</>를 <Bold>허브</>에서 <Bold>연결 해제</>하세요",
    "Open the <Bold>Codex</> with the <Bold>[ C ] Key</>":
        "<Bold>[ C ] 키</>로 <Bold>코덱스</>를 여세요",
    "Open the <Bold>Codex</> with <img id=\"Gamepad_D_pad_Right\"/>":
        "<img id=\"Gamepad_D_pad_Right\"/>로 <Bold>코덱스</>를 여세요",
    "Open the <Bold>Map View</> with the <Bold>[ M ] Key</>":
        "<Bold>[ M ] 키</>로 <Bold>지도 뷰</>를 여세요",
    "Open the <Bold>Map View</> with <img id=\"Gamepad_D_pad_Up\"/>":
        "<img id=\"Gamepad_D_pad_Up\"/>로 <Bold>지도 뷰</>를 여세요",
    "Open the <Bold>Objectives Panel</> (Hotkey <Bold>[ O ]</>)":
        "<Bold>목표 패널</>을 여세요 (단축키 <Bold>[ O ]</>)",
    "Open the <Bold>Objectives Panel</> with <img id=\"Gamepad_D_pad_Down\"/>":
        "<img id=\"Gamepad_D_pad_Down\"/>로 <Bold>목표 패널</>을 여세요",
    "Open your Drone's <Bold>inventory</> (Hotkey: TAB)":
        "드론의 <Bold>인벤토리</>를 여세요 (단축키: TAB)",
    "Open your Drone\'s <Bold>inventory</> (Hotkey: <img id=\"Gamepad_Special_Left\"/>)":
        "드론의 <Bold>인벤토리</>를 여세요 (단축키: <img id=\"Gamepad_Special_Left\"/>)",
    "Open the <Bold>Synthesizer tab</>": "<Bold>합성기 탭</>을 여세요",
    "Click <Bold>Synthesize</> to craft the item": "<Bold>합성</>을 클릭해 아이템을 제작하세요",
    "Select the <Bold>Stargate Parts</> recipe": "<Bold>스타게이트 부품</> 제작법을 선택하세요",
    "Pick up completed <Bold>materials</> from your HUB":
        "허브에서 완성된 <Bold>재료</>를 수거하세요",
    "Place completed <Bold>Stargate Parts</> into your <Bold>HUB</>":
        "완성된 <Bold>스타게이트 부품</>을 <Bold>허브</>에 배치하세요",
    "Craft <Bold>Stargate Parts</>": "<Bold>스타게이트 부품</> 제작",
    "<Bold>Repeat</> until you have the <Bold>required parts</>":
        "<Bold>필요한 부품</>을 갖출 때까지 <Bold>반복</>하세요",
    "Fetch additional materials from your HUB if you cannot craft enough Stargate Parts":
        "스타게이트 부품을 충분히 제작할 수 없으면 허브에서 추가 재료를 가져오세요",
    "Move all starting materials from your <Bold>HUB</> into your <Bold>Drone inventory</>":
        "<Bold>허브</>의 모든 시작 재료를 <Bold>드론 인벤토리</>로 옮기세요",
    "Collect <Bold>HUB items</>": "<Bold>허브 아이템</> 수집",
    "Clear <Bold>Jumpgate Wreckage</>": "<Bold>점프게이트 잔해</> 제거",
    "Destroy all <Bold>Wreckage</>": "모든 <Bold>잔해</> 파괴",
    "Destroy all <Enemy>Wreckage</>": "모든 <Enemy>잔해</> 파괴",
    "Hold <Bold>LMB</> on the damaged buffer": "손상된 버퍼에 <Bold>좌클릭</>을 누르세요",
    "Deconstruct <Bold>Damaged Buffer</>": "<Bold>손상된 버퍼</> 해체",
    "Continue <Bold>Station Expansion</> 1/2": "<Bold>스테이션 확장</> 계속 1/2",
    "Continue <Bold>Station Expansion</> 2/2": "<Bold>스테이션 확장</> 계속 2/2",
    "Expand <Bold>Power</> Generation": "<Bold>전력</> 생산 확장",
    "<Bold>Align</> the <Bold>Solar Generator</> by dragging with <Bold>[LMB]</>":
        "<Bold>좌클릭</>으로 드래그해 <Bold>태양광 발전기</>를 <Bold>정렬</>하세요",
    "<Bold>Align</> the <Bold>Solar Generator</> by dragging with <img id=\"Gamepad_Right_Trigger\"/>":
        "<img id=\"Gamepad_Right_Trigger\"/>로 드래그해 <Bold>태양광 발전기</>를 <Bold>정렬</>하세요",
    "Choose the <Bold>Complete The Gate</> objective": "<Bold>게이트 완성</> 목표를 선택하세요",
    "Click <Bold>Select Objective</> to set as the current objective":
        "<Bold>목표 선택</>을 클릭하여 현재 목표로 설정하세요",
    "Click the <Bold>Complete</> button on the active <Bold>objective window</>":
        "활성 <Bold>목표 창</>에서 <Bold>완료</> 버튼을 클릭하세요",
    "Complete Objective": "목표 완료",
    "Select an <Bold>Objective</>": "<Bold>목표</> 선택",
    "Activate extra functions": "추가 기능 활성화",
    "Activate the <Bold>Sensor View</> by holding <Bold>Backslash [ \\ ]</> or <Bold>T</>":
        "<Bold>백슬래시 [ \\ ]</> 또는 <Bold>T</>를 누른 채 <Bold>센서 뷰</>를 활성화합니다",
    "Activate the <Bold>Sensor View</> by holding <img id=\"Steam_Touch_0\"/>":
        "<img id=\"Steam_Touch_0\"/>를 누른 채 <Bold>센서 뷰</>를 활성화합니다",
    "Show the <Bold>Station Overview</> by holding <Bold>Left Control</>":
        "<Bold>왼쪽 Ctrl</>을 누른 채 <Bold>스테이션 개요</>를 표시합니다",
    "Show the <Bold>Station Overview</> by holding <img id=\"Gamepad_Right_Bumper\"/>":
        "<img id=\"Gamepad_Right_Bumper\"/>를 누른 채 <Bold>스테이션 개요</>를 표시합니다",
    "Open the <Bold>Item Filters Panel</> (grid icon button)":
        "<Bold>아이템 필터 패널</>을 여세요 (격자 아이콘 버튼)",
    "Close the Item Filters panel by right-clicking": "우클릭으로 아이템 필터 패널을 닫습니다",
    "Close the Item Filters panel with <img id=\"Gamepad_Special_Right\"/>":
        "<img id=\"Gamepad_Special_Right\"/>로 아이템 필터 패널을 닫습니다",
    "Open the <Bold>Advanced Panel</> (cog icon button)":
        "<Bold>고급 패널</>을 여세요 (톱니바퀴 아이콘 버튼)",
    "<Bold>Advanced</> Module Settings": "<Bold>고급</> 모듈 설정",
    "Enter <Bold>Combat</> mode with <Bold>E</> or the lower toolbar":
        "<Bold>E</> 또는 하단 툴바로 <Bold>전투</> 모드에 진입합니다",
    "Enter <Bold>Combat</> mode with <img id=\"Gamepad_Face_Button_Bottom\"/> or the lower toolbar":
        "<img id=\"Gamepad_Face_Button_Bottom\"/> 또는 하단 툴바로 <Bold>전투</> 모드에 진입합니다",
    "<Bold>Leave</> Combat mode with <Bold>Right-Click</> or <Bold>Escape</>":
        "<Bold>우클릭</> 또는 <Bold>Esc</>로 전투 모드를 <Bold>나갑니다</>",
    "<Bold>Leave</> Combat mode with <img id=\"Gamepad_Face_Button_Bottom\"/> or <img id=\"Gamepad_Special_Right\"/>":
        "<img id=\"Gamepad_Face_Button_Bottom\"/> 또는 <img id=\"Gamepad_Special_Right\"/>로 전투 모드를 <Bold>나갑니다</>",
    "Enter <Bold>Link</> mode with <Bold>F</> or the lower toolbar":
        "<Bold>F</> 또는 하단 툴바로 <Bold>연결</> 모드에 진입합니다",
    "Enter <Bold>Link</> mode with <img id=\"Gamepad_Face_Button_Left\"/> or the lower toolbar":
        "<img id=\"Gamepad_Face_Button_Left\"/> 또는 하단 툴바로 <Bold>연결</> 모드에 진입합니다",
    "<Bold>Leave</> Link mode with <Bold>Right-Click</> or <Bold>Escape</>":
        "<Bold>우클릭</> 또는 <Bold>Esc</>로 연결 모드를 <Bold>나갑니다</>",
    "<Bold>Leave</> Link mode with <img id=\"Gamepad_Face_Button_Left\"/> or <img id=\"Gamepad_Special_Right\"/>":
        "<img id=\"Gamepad_Face_Button_Left\"/> 또는 <img id=\"Gamepad_Special_Right\"/>로 연결 모드를 <Bold>나갑니다</>",
    "Enter <Bold>Sell</> mode with <Bold>R</> or the lower toolbar":
        "<Bold>R</> 또는 하단 툴바로 <Bold>판매</> 모드에 진입합니다",
    "Enter <Bold>Sell</> mode with <img id=\"Gamepad_Face_Button_Top\"/> or the lower toolbar":
        "<img id=\"Gamepad_Face_Button_Top\"/> 또는 하단 툴바로 <Bold>판매</> 모드에 진입합니다",
    "<Bold>Leave</> Sell mode with <Bold>Right-Click</> or <Bold>Escape</>":
        "<Bold>우클릭</> 또는 <Bold>Esc</>로 판매 모드를 <Bold>나갑니다</>",
    "<Bold>Leave</> Sell mode with <img id=\"Gamepad_Face_Button_Top\"/> or <img id=\"Gamepad_Special_Right\"/>":
        "<img id=\"Gamepad_Face_Button_Top\"/> 또는 <img id=\"Gamepad_Special_Right\"/>로 판매 모드를 <Bold>나갑니다</>",
    "<Bold>Close any popups</> and return to the game view with <Bold>Escape</>":
        "<Bold>Esc</>로 <Bold>모든 팝업을 닫고</> 게임 뷰로 돌아갑니다",
    "<Bold>Close any popups</> and return to the game view with <img id=\"Gamepad_Special_Right\"/>":
        "<img id=\"Gamepad_Special_Right\"/>로 <Bold>모든 팝업을 닫고</> 게임 뷰로 돌아갑니다",
    "You can <bold>hold shift</> to quickly link multiple modules":
        "<bold>Shift를 누른 채</> 여러 모듈을 빠르게 연결할 수 있습니다",
    "You can hold <img id=\"Gamepad_Left_Bumper\"/> to quickly link multiple modules":
        "<img id=\"Gamepad_Left_Bumper\"/>를 눌러 여러 모듈을 빠르게 연결할 수 있습니다",
    "You can <bold>hold shift</> to select and align multiple solar panels at the same time":
        "<bold>Shift를 누른 채</> 여러 태양광 패널을 동시에 선택하고 정렬할 수 있습니다",
    "You can hold <img id=\"Gamepad_Left_Bumper\"/> to select and align multiple solar panels at the same time":
        "<img id=\"Gamepad_Left_Bumper\"/>를 눌러 여러 태양광 패널을 동시에 선택하고 정렬할 수 있습니다",
    "You can <bold>press X</> to unlink all modules linked to the current module":
        "<bold>X를 누르면</> 현재 모듈에 연결된 모든 모듈의 연결을 해제할 수 있습니다",
    "You can change objectives at any time": "언제든 목표를 변경할 수 있습니다",
    "You can open your Drone's inventory at any time using the TAB hotkey":
        "TAB 단축키로 언제든 드론 인벤토리를 열 수 있습니다",
    "You can partially complete objectives by clicking them in the objectives panel":
        "목표 패널에서 목표를 클릭하여 부분적으로 완료할 수 있습니다",
    "You can use the <Bold>B Hotkey</> to easily move all items to your drone":
        "<Bold>B 단축키</>로 모든 아이템을 드론으로 쉽게 옮길 수 있습니다",

    # ---- HUD hover labels (right-bottom icons) ----
    "YOUR CURRENT <Bold>STATION LEVEL</>": "현재 <Bold>스테이션 레벨</>",
    "YOUR UNSPENT <Bold>TECH POINTS</>": "미사용 <Bold>기술 포인트</>",

    # ---- Codex tutorial article bodies (long-form) - exact SourceStrings from en/Game.locres ----
    "You can assign your most commonly constructed station modules to the <Bold>Hotbar</> for quick selection.\r\n\r\nTo assign a module to a hotbar slot, place your mouse cursor over an item from the <Bold>build menu</>, and while <Bold>holding SHIFT or CTRL</>, press a <Bold>number key 1-9</> to assign it to that hotbar slot.\r\n\r\nTo <Bold>remove</> an item from the hotbar, repeat the above process.\r\n\r\nYou can then either click on a hotbar entry or press the assigned number 1-9 to select that build item.\r\n\r\nThere are also up to <Bold>5 active hotbars</> available, and you can switch between them using <Bold>ALT + Mouse Wheel.</>":
        "가장 자주 건설하는 스테이션 모듈을 <Bold>단축바</>에 할당하여 빠르게 선택할 수 있습니다.\r\n\r\n단축바 슬롯에 모듈을 할당하려면 <Bold>건설 메뉴</>의 항목 위에 마우스 커서를 올린 상태에서 <Bold>SHIFT 또는 CTRL을 누른 채</> <Bold>숫자 키 1-9</>를 눌러 해당 단축바 슬롯에 할당합니다.\r\n\r\n단축바에서 항목을 <Bold>제거</>하려면 위 과정을 반복하세요.\r\n\r\n할당 후에는 단축바 항목을 클릭하거나 할당된 1-9 숫자를 눌러 해당 건설 항목을 선택할 수 있습니다.\r\n\r\n또한 최대 <Bold>5개의 활성 단축바</>가 있으며 <Bold>ALT + 마우스 휠</>로 단축바를 전환할 수 있습니다.",
    "Hold or tap <Bold>CTRL</> to display the Station Status View. The <Bold>Station Status View</> is a great way to see an overview of how your station is performing, and identify any production bottlenecks you may have.\r\n\r\nEach module will display an icon showing its overall state: \r\n\r\n• <Bold>Black</> = module is disabled\r\n• <Bold>Red</> = module is switched off\r\n• <Bold>Orange</> = factory is idle / full storage\r\n• <Bold>Yellow</> = medium efficiency\r\n• <Bold>Green</> = high efficiency\r\n\r\nFactories will also display an icon showing what they are currently producing, while storage will show the most common item stored. Shipyards will show which ship class they are currently constructing.":
        "<Bold>CTRL</>을 누르거나 탭하여 스테이션 상태 뷰를 표시합니다. <Bold>스테이션 상태 뷰</>는 스테이션의 전반적인 작동 상태를 한눈에 파악하고 생산 병목 지점을 식별하기 좋은 방법입니다.\r\n\r\n각 모듈은 전체 상태를 나타내는 아이콘을 표시합니다:\r\n\r\n• <Bold>검정</> = 모듈 비활성화\r\n• <Bold>빨강</> = 모듈 꺼짐\r\n• <Bold>주황</> = 공장 유휴 / 저장소 가득 참\r\n• <Bold>노랑</> = 중간 효율\r\n• <Bold>초록</> = 높은 효율\r\n\r\n공장은 현재 생산 중인 품목 아이콘을, 저장소는 가장 많이 저장된 품목을 표시합니다. 조선소는 현재 건조 중인 함선 등급을 표시합니다.",
    "You can <Bold>transfer items</> between any <Bold>station module, container</> or other object's inventory and your drone by <Bold>left-clicking</> it or <Bold>left-click-dragging</> it into an available slot.\r\n\r\nHolding <Bold>Shift</> when clicking an item will move <Bold>half</> of the item stack, while <Bold>Middle-Clicking</> will let you move a <Bold>specific amount.</>\r\n\r\nHolding <Bold>left CTRL</> while clicking will attempt to move <Bold>all stacks</> of that item.\r\n\r\nYou can open your <Bold>Drone Inventory</> at any time by pressing <Bold>TAB</>.":
        "<Bold>스테이션 모듈, 컨테이너</> 또는 다른 객체의 인벤토리와 드론 사이에서 아이템을 <Bold>좌클릭</>하거나 사용 가능한 슬롯으로 <Bold>좌클릭 드래그</>하여 <Bold>아이템을 이동</>할 수 있습니다.\r\n\r\n아이템을 클릭할 때 <Bold>Shift</>를 누르면 스택의 <Bold>절반</>이 이동하고, <Bold>휠 클릭</>은 <Bold>특정 수량</>을 이동할 수 있게 합니다.\r\n\r\n클릭할 때 <Bold>왼쪽 CTRL</>을 누르면 해당 아이템의 <Bold>모든 스택</>을 이동하려 시도합니다.\r\n\r\n언제든 <Bold>TAB</>을 눌러 <Bold>드론 인벤토리</>를 열 수 있습니다.",
    "<Bold>Solar Panels</> provide a decent amount of energy for relatively little cost, but become <Bold>less efficient</> the more panels you connect together in one <Bold>network</>.\r\n\r\nWhen first built, they must be <Bold>manually aligned</> to the sun by <Bold>Left-Dragging</> with your drone. You can use <Bold>Shift + LMB</> to align mutliple solar panels at the same time.\r\n\r\n<Bold>Note:</> Each location has a different level of <Bold>Solar Intensity</> and this also effects how much power solar panels will generate.":
        "<Bold>태양광 패널</>은 비교적 적은 비용으로 적당한 에너지를 제공하지만, 하나의 <Bold>네트워크</>에 더 많은 패널을 연결할수록 <Bold>효율이 떨어집니다</>.\r\n\r\n처음 건설된 직후에는 드론으로 <Bold>좌클릭 드래그</>하여 태양에 <Bold>수동으로 정렬</>해야 합니다. <Bold>Shift + 좌클릭</>으로 여러 태양광 패널을 동시에 정렬할 수도 있습니다.\r\n\r\n<Bold>참고:</> 각 지역마다 <Bold>태양광 강도</>가 다르며 이는 태양광 패널이 생성하는 전력량에도 영향을 미칩니다.",
    "Automate supply chains by <Bold>linking</> station modules together.\r\n\r\nModules will automatically <Bold>send any needed items</> to linked factories and other modules.\r\n\r\nAlthough <Bold>Connectors</> can transport an <Bold>unlimited</> number of items per minute - you are limited by how many items a module can <Bold>send</> (shown on its popup) - so avoid linking one module to many destinations.\r\n\r\nCreate a link by entering <Bold>Link mode</> and <Bold>Left-Clicking</> a source and destination module. Hold <Bold>Shift</> to quickly link a module to <Bold>multiple destinations</>.\r\n\r\nYou can also use <Bold>Middle-Click</> to add a <Bold>Stopover</> and create a custom route.":
        "스테이션 모듈을 <Bold>연결</>해 공급망을 자동화합니다.\r\n\r\n연결된 공장과 다른 모듈로 <Bold>필요한 아이템을 자동으로 전송</>합니다.\r\n\r\n<Bold>연결관(Connector)</>은 분당 <Bold>무제한</> 수의 아이템을 운송할 수 있지만, 모듈이 <Bold>전송</>할 수 있는 아이템 수에는 제한이 있습니다 (팝업에 표시) — 그래서 한 모듈을 너무 많은 대상에 연결하지 않는 것이 좋습니다.\r\n\r\n<Bold>연결 모드</>에 진입한 뒤 출발지와 목적지 모듈을 <Bold>좌클릭</>하여 연결을 만듭니다. <Bold>Shift</>를 누르면 한 모듈을 <Bold>여러 대상</>에 빠르게 연결할 수 있습니다.\r\n\r\n<Bold>휠 클릭</>으로 <Bold>중간 경유지(Stopover)</>를 추가하여 사용자 정의 경로를 만들 수도 있습니다.",
    "Select an objective by opening the <bold>Objectives Panel</> and choosing your next goal. Your currently selected objective will appear in the top-right of the screen.\r\n\r\nAny items, parts and materials in your <Bold>HUB's Storage</>, or completed ships within a certain range of your station will count towards these goals.\r\n\r\n<Bold>NOTE:</> You can send <Bold>any completed items or ships</> at any time by clicking on its item in the current objective panel - or wait until all goals have been met and click the <Bold>complete</> button which will appear.":
        "<bold>목표 패널</>을 열어 다음 목표를 선택합니다. 현재 선택된 목표는 화면 우측 상단에 표시됩니다.\r\n\r\n<Bold>HUB 저장소</>에 있는 아이템, 부품, 재료, 또는 스테이션 일정 범위 안에 완성된 함선들이 이러한 목표에 카운트됩니다.\r\n\r\n<Bold>참고:</> 현재 목표 패널의 항목을 클릭하여 언제든 <Bold>완성된 아이템이나 함선을 전송</>할 수 있습니다 — 또는 모든 목표가 충족될 때까지 기다렸다가 표시되는 <Bold>완료</> 버튼을 클릭할 수도 있습니다.",

    # ---- Common short labels (uppercase variants & UI states) ----
    "ALPHA": "알파", "BETA": "베타", "GAMMA": "감마",
    "RED": "빨강",
    "BLUE": "파랑", "GREEN": "초록", "YELLOW": "노랑", "ORANGE": "주황",
    "PURPLE": "보라", "RANDOM": "무작위", "MAGENTA": "자홍", "TURQUOISE": "청록",
    "NONE": "없음", "STORAGE": "저장소", "STORAGE UNIT": "저장 장치",
    "SHIPBUILDING": "함선 건조", "SHIP": "함선", "FREIGHTER": "화물선", "FREIGHTERS": "화물선",
    "FRIENDLY": "우호", "FUEL": "연료", "FUELLED": "연료 충전됨",
    "BLOCKED": "차단됨", "INVALID": "유효하지 않음", "INVALID SHAPE": "잘못된 모양",
    "MAGENTA": "자홍", "MASSIVE": "거대", "LARGE": "큰", "SMALL": "작은",
    "PRODUCTION": "생산", "ARTIFACTS": "유물",
    "HELION": "헬리온", "TITANIA": "티타니아", "GLACIALIS": "글라시알리스", "SCYLLA": "스킬라",
    "CERBERUS": "케르베로스", "NOVA": "노바", "VORTEX": "와류",
    "GAS GIANT": "가스 행성", "ICE PLANET": "얼음 행성", "LAVA PLANET": "용암 행성",
    "MOON": "위성", "QUANTUM RIFT": "양자 균열", "THE VOID": "공허",
    "ASTEROID: ": "소행성: ", "WRECKAGE": "잔해", "OVERDRIVE CORE": "오버드라이브 코어",
    "FUEL INJECTION FUEL INJECTION": "연료 주입 연료 주입",
    "G-CLASS": "G-등급", "SPACE": "우주", "SHIFT": "시프트", "SHIFT+": "시프트+",
    "CAPS-LOCK": "캡스락",
    "TOO FAR": "너무 멈", "TOO HIGH": "너무 높음", "TOO LONG": "너무 김", "TOO STEEP": "너무 가파름",
    "FAILED": "실패", "STARTED": "시작됨", "STORED:": "저장됨:", "MINING:": "채굴 중:",
    "OBJECT TOO FAR": "대상이 너무 멈", "NODE OCCUPIED": "노드 사용 중",
    "OUTSIDE ZONE BOUNDS": "구역 경계 밖", "MAX WEIGHT EXCEEDED": "최대 중량 초과",
    "NO WEAPONS EQUIPPED": "장비된 무기 없음", "ENERGY DEPLETED": "에너지 고갈",
    "EDIT": "편집", "EDIT TASK": "작업 편집", "QUIT GAME": "게임 종료",
    "QUIT TO MAIN MENU": "메인 메뉴로 종료", "EXIT TUTORIAL": "튜토리얼 종료",
    "DECOMISSION STATION?": "스테이션을 폐기하시겠습니까?",
    "OVERWRITE GAME": "게임 덮어쓰기", "SAVE EXISTS": "저장 존재함",
    "SESSION EXISTS": "세션이 이미 존재함", "GAME NAME EMPTY": "게임 이름이 비어있음",
    "SINGLE-PLAYER": "싱글플레이어", "ONLINE: PUBLIC": "온라인: 공개",
    "ONLINE: FRIENDS ONLY": "온라인: 친구만",
    "Cancel": "취소", "Quit": "종료", "Save + Quit": "저장 + 종료",
    "Accept": "수락", "Error": "오류", "False": "거짓",
    "Photo": "사진", "Module": "모듈", "Freighter": "화물선",
    "ARTIFACT ANALYSIS <Bold>COMPLETE</>": "유물 분석 <Bold>완료</>",
    "AVAILABLE <Bold>STATION POINTS</>": "사용 가능한 <Bold>스테이션 포인트</>",
    "ALT RECIPE": "대체 레시피", "ADMIRAL": "제독", "RAW MATERIALS": "원자재",
    "RESOURCES FOUND:": "발견된 자원:", "CONSTRUCTED AT:": "건설 위치:",
    "CUSTOM LABEL": "사용자 라벨", "POPUP TITLE": "팝업 제목",
    "COMING SOON": "출시 예정", "END OF BETA": "베타 종료",
    "End of BETA": "베타 종료", "End of demo": "데모 종료",
    "CARGO PODS": "화물 포드", "CAN'T AFFORD": "비용 부족",
    "DRAG HERE TO <Bold>DESTROY</> AN ITEM": "여기로 드래그해 아이템을 <Bold>파괴</>",
    "DRAG HERE TO <Bold>DROP</> AN ITEM": "여기로 드래그해 아이템을 <Bold>버리기</>",
    "<Bold>ADD</> TO <Bold>TO-DO</> LIST": "할 일 목록에 <Bold>추가</>",
    "<Bold>REMOVE</> FROM <Bold>TO-DO</> LIST": "할 일 목록에서 <Bold>제거</>",
    "<Bold>DELETE</> BLUEPRINT": "청사진 <Bold>삭제</>",
    "NEW <Bold>PRIMARY</> OBJECTIVE AVAILABLE": "새 <Bold>주요</> 목표가 사용 가능",
    "NEW <Bold>OPTIONAL</> OBJECTIVE AVAILABLE": "새 <Bold>선택</> 목표가 사용 가능",
    "UNLOCKS AT <Yellow>STATION LEVEL {Level}</>": "<Yellow>스테이션 레벨 {Level}</>에서 잠금 해제",
    "LEVEL\r\n{Level}": "레벨\r\n{Level}",
    "PLACE ONTO {Node} NODE": "{Node} 노드에 배치",
    "Reset Tech Points?": "기술 포인트 초기화?",
    "Resolution Changed": "해상도 변경됨", "Keep this screen resolution?": "이 해상도를 유지하시겠습니까?",
    "Delete Blueprint": "청사진 삭제", "Blueprint is too large": "청사진이 너무 큼",
    "Auto-saving game...": "게임 자동 저장 중...",
    "Connection timed out": "연결 시간 초과", "Server quit": "서버 종료",
    "Server travel failed": "서버 이동 실패", "Client travel failed": "클라이언트 이동 실패",
    "Travel failed": "이동 실패", "Level load failed": "레벨 로드 실패",
    "Level not found": "레벨을 찾을 수 없음", "Cannot join session": "세션에 참여할 수 없음",
    "Couldn't Start Game": "게임을 시작할 수 없음",
    "The server quit the session": "서버가 세션을 종료함",
    "The server closed the session": "서버가 세션을 닫음",
    "This session is <Bold>full</>": "이 세션은 <Bold>가득 참</>",
    "This session is set to <Bold>Friends only</>": "이 세션은 <Bold>친구만</> 으로 설정됨",
    "Cancel tutorial popups?": "튜토리얼 팝업을 취소하시겠습니까?",
}

# ---------- helpers ---------------------------------------------------------
def po_escape(s: str) -> str:
    return (s.replace("\\", "\\\\").replace('"', '\\"')
             .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"))

def should_skip(entry: dict) -> bool:
    if entry["file"] in SKIP_FILES: return True
    if any(p.match(entry["text"]) for p in SKIP_TEXT_RE): return True
    if entry["text"] in PROFANITY: return True
    if entry["text"] in SKIP_VALUES: return True
    return False

def normalize_newlines(s: str) -> str:
    """The game uses CRLF in multi-line strings; our dict keys use LF. Match both."""
    return s.replace("\r\n", "\n").replace("\r", "\n")

# ---------- main ------------------------------------------------------------
def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries  = [e for e in manifest["entries"] if e["kind"] == "translatable"]
    print(f"manifest entries (translatable): {len(entries)}")

    # We emit one PO entry per (file, export_idx, byte_offset) so apply.py can match.
    out = [
        '# Outworld Station 한글 패치 — auto-generated by build_ko_po.py',
        '# To extend: add the English source -> Korean target to the TR dict in build_ko_po.py.',
        'msgid ""',
        'msgstr ""',
        '"Content-Type: text/plain; charset=UTF-8\\n"',
        '',
    ]
    matched = unmatched = skipped = 0
    last_file = None
    unmatched_samples: dict[str, list[str]] = {}
    for e in entries:
        if should_skip(e):
            skipped += 1
            continue
        # Try exact first, then normalized newlines
        ko = TR.get(e["text"]) or TR.get(normalize_newlines(e["text"]))
        if ko is None:
            unmatched += 1
            samples = unmatched_samples.setdefault(e["file"], [])
            if len(samples) < 3 and e["text"] not in samples:
                samples.append(e["text"][:80])
            continue
        if e["file"] != last_file:
            out.append(f"# ---------------------------------------------------------- {e['file']}")
            last_file = e["file"]
        ctx = f"{e['file']}@e{e['export_idx']}@{e['byte_offset']:x}"
        out.append(f'msgctxt "{po_escape(ctx)}"')
        out.append(f'msgid "{po_escape(e["text"])}"')
        out.append(f'msgstr "{po_escape(ko)}"')
        out.append('')
        matched += 1

    KOPO.write_text("\n".join(out), encoding="utf-8")
    print(f"\nko.po written: {KOPO}")
    print(f"  matched   = {matched}")
    print(f"  skipped   = {skipped} (engine identifiers / profanity / video refs)")
    print(f"  unmatched = {unmatched} (still English in-game)")
    if unmatched:
        print(f"\nunmatched per file (first 3 samples):")
        for f, samples in sorted(unmatched_samples.items(), key=lambda x: -len(x[1])):
            print(f"  {f}:")
            for s in samples:
                print(f"    {s!r}")

if __name__ == "__main__":
    main()
