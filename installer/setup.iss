; Outworld Station Korean Patch -- Inno Setup script
; Compiles to a single .exe that:
;   1. auto-detects the Outworld Station install across all Steam libraries
;   2. installs mod files into %LOCALAPPDATA%\OutworldStation_KR\mods (backup)
;   3. installs wrapper.bat for auto-recovery
;   4. creates a directory junction at <game>\Content\Paks\~mods -> backup
;   5. uses Korean.isl so the install wizard itself is Hangul
; Uninstall removes the junction and backup folder cleanly.
;
; Note: this file is intentionally ASCII-only so it builds regardless of the
; editor's encoding. Korean wizard text comes from Korean.isl.

#define AppName    "Outworld Station Korean Patch"
#define AppVersion "1.0.4"
#define RepoURL    "https://github.com/tj-nexthop/outworld-station-kr"

[Setup]
AppId={{A4F9C2E8-3D5B-4C7A-9E1F-2B6D8A0F4C3E}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=tj-nexthop (Unofficial Fan Patch)
AppPublisherURL={#RepoURL}
AppSupportURL={#RepoURL}/issues
AppUpdatesURL={#RepoURL}/releases
AppContact={#RepoURL}
DefaultDirName={localappdata}\OutworldStation_KR
DisableDirPage=yes
DefaultGroupName=Outworld Station Korean Patch
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename=KoreanPatch_OutworldStation_v{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#AppName} v{#AppVersion}
UninstallDisplayIcon={app}\wrapper.bat

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Messages]
; Override welcome page to expose the GitHub source loud and clear
WelcomeLabel2=%n%n%1 v{#AppVersion}%n%n%n[ 비공식 한글 패치 ]%n%n제작 / 최신 버전 / 이슈 리포트:%n{#RepoURL}%n%n본 패치는 Trickjump Games Ltd와 무관한 팬 메이드 비공식 패치이며,%n무료로 배포됩니다. 게임 본체는 사용자가 별도로 보유해야 합니다.%n%n사용 폰트: Pretendard, Noto Sans KR (SIL Open Font License 1.1)%n자세한 라이선스 정보는 설치 후 NOTICE.txt 참고.%n%n[ 다음 ] 을 누르면 설치 위치 자동 탐색 후 설치를 시작합니다.

[Files]
Source: "..\mod\KoreanPatch_P.pak";        DestDir: "{app}\mods"; Flags: ignoreversion
Source: "..\mod\KoreanPatch_P.ucas";       DestDir: "{app}\mods"; Flags: ignoreversion
Source: "..\mod\KoreanPatch_P.utoc";       DestDir: "{app}\mods"; Flags: ignoreversion
Source: "..\mod\KoreanPatch_LocRes_P.pak"; DestDir: "{app}\mods"; Flags: ignoreversion
Source: "..\mod\KoreanPatch_Fonts_P.pak";  DestDir: "{app}\mods"; Flags: ignoreversion
Source: "wrapper.bat";                     DestDir: "{app}";      Flags: ignoreversion
Source: "NOTICE.txt";                      DestDir: "{app}";      Flags: ignoreversion

; Ensure config dir exists even if the game has never been launched yet
[Dirs]
Name: "{localappdata}\OutworldStation\Saved\Config\Windows"; Flags: uninsneveruninstall

; Force Culture=ko in GameUserSettings.ini so the game picks up our locres on first launch
; Without this, default Culture=en means the user must manually pick language in-game.
[INI]
Filename: "{localappdata}\OutworldStation\Saved\Config\Windows\GameUserSettings.ini"; \
  Section: "Internationalization"; Key: "Culture"; String: "ko"

[Icons]
Name: "{group}\Uninstall Outworld Station Korean Patch"; Filename: "{uninstallexe}"

[Run]
Filename: "{cmd}"; Parameters: "/c echo OK"; Flags: runhidden; StatusMsg: "Installing Korean patch"

[UninstallDelete]
; Remove the backup folder including any user-added files
Type: filesandordirs; Name: "{app}\mods"

[Code]
const
  GameRelPaks   = '\OutworldStation\Content\Paks';
  GameModsName  = '\~mods';

var
  GFoundGameDir: String;

// ---------- Steam library detection ---------------------------------------
function GetSteamPath(var Path: String): Boolean;
begin
  Result := RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Valve\Steam', 'InstallPath', Path);
  if not Result then
    Result := RegQueryStringValue(HKLM, 'SOFTWARE\Valve\Steam', 'InstallPath', Path);
  if not Result then
    Result := RegQueryStringValue(HKCU, 'SOFTWARE\Valve\Steam', 'SteamPath', Path);
end;

procedure CollectLibraryRoots(SteamPath: String; var Lines: TArrayOfString);
var
  Vdf: String;
  Content: AnsiString;
  i, n, p, q: Integer;
  s, val: String;
begin
  // Always include the main Steam install
  SetArrayLength(Lines, 1);
  Lines[0] := SteamPath;

  Vdf := SteamPath + '\steamapps\libraryfolders.vdf';
  if not FileExists(Vdf) then Exit;
  if not LoadStringFromFile(Vdf, Content) then Exit;
  s := String(Content);

  // Naive scan for `"path"  "X:\\some\\dir"` lines.
  n := Length(s);
  i := 1;
  while i <= n do begin
    p := Pos('"path"', Copy(s, i, n - i + 1));
    if p = 0 then Break;
    p := i + p - 1 + Length('"path"');
    // find the next quoted value
    q := p;
    while (q <= n) and (s[q] <> '"') do Inc(q);
    if q > n then Break;
    Inc(q);
    p := q;
    while (p <= n) and (s[p] <> '"') do Inc(p);
    if p > n then Break;
    val := Copy(s, q, p - q);
    StringChangeEx(val, '\\', '\', True);
    SetArrayLength(Lines, GetArrayLength(Lines) + 1);
    Lines[GetArrayLength(Lines) - 1] := val;
    i := p + 1;
  end;
end;

function FindOutworldStation(): String;
var
  SteamPath, Candidate: String;
  Roots: TArrayOfString;
  i: Integer;
begin
  Result := '';
  if not GetSteamPath(SteamPath) then Exit;
  CollectLibraryRoots(SteamPath, Roots);
  for i := 0 to GetArrayLength(Roots) - 1 do begin
    Candidate := Roots[i] + '\steamapps\common\OutworldStation';
    if DirExists(Candidate) then begin
      Result := Candidate;
      Exit;
    end;
  end;
end;

// ---------- junction handling --------------------------------------------
// We detect reparse points indirectly: `rmdir` on a junction or empty folder
// succeeds, but on a real folder with content it fails (errorlevel <> 0).

function TryRemoveDirOrJunction(JuncPath: String): Boolean;
var
  ResultCode: Integer;
begin
  if not DirExists(JuncPath) then begin
    Result := True;
    Exit;
  end;
  Exec(ExpandConstant('{cmd}'),
       '/c rmdir "' + JuncPath + '"',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := (ResultCode = 0) and (not DirExists(JuncPath));
end;

function MakeJunction(JuncPath, TargetPath: String): Boolean;
var
  ResultCode: Integer;
  Backup: String;
begin
  // If a non-empty real folder is in the way, move it aside (don't lose user data)
  if DirExists(JuncPath) and (not TryRemoveDirOrJunction(JuncPath)) then begin
    Backup := JuncPath + '_backup_' + GetDateTimeString('yyyymmdd_hhnnss', '-', '-');
    if not RenameFile(JuncPath, Backup) then begin
      Result := False;
      Exit;
    end;
  end;
  Result := Exec(ExpandConstant('{cmd}'),
    '/c mklink /J "' + JuncPath + '" "' + TargetPath + '"',
    '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := Result and (ResultCode = 0) and DirExists(JuncPath);
end;

// ---------- pre-install: locate game --------------------------------------
function InitializeSetup(): Boolean;
var
  Manual: String;
begin
  GFoundGameDir := FindOutworldStation();
  if GFoundGameDir = '' then begin
    if MsgBox('Outworld Station install folder was not found automatically.'
              + Chr(13) + Chr(10) + 'Pick the folder manually?',
              mbConfirmation, MB_YESNO) = IDYES then begin
      if not BrowseForFolder('Select the folder where Outworld Station is installed',
                             Manual, False) then begin
        Result := False; Exit;
      end;
      GFoundGameDir := Manual;
    end else begin
      Result := False; Exit;
    end;
  end;
  Log('detected game dir: ' + GFoundGameDir);
  Result := True;
end;

// ---------- after files copied: create junction ---------------------------
procedure CurStepChanged(CurStep: TSetupStep);
var
  ModsTarget, GameMods: String;
begin
  if CurStep = ssPostInstall then begin
    ModsTarget := ExpandConstant('{app}\mods');
    GameMods := GFoundGameDir + GameRelPaks + GameModsName;
    if not MakeJunction(GameMods, ModsTarget) then begin
      MsgBox('Failed to create junction.' + Chr(13) + Chr(10)
        + 'Game folder: ' + GFoundGameDir + Chr(13) + Chr(10)
        + 'Target: ' + ModsTarget,
        mbError, MB_OK);
    end;
  end;
end;

// ---------- finalize: friendly completion message --------------------------
procedure DeinitializeSetup();
var
  Hint: String;
begin
  if GFoundGameDir <> '' then begin
    Hint := '설치 완료!' + Chr(13) + Chr(10) + Chr(13) + Chr(10)
          + 'Steam에서 게임을 실행하시면 한국어로 표시됩니다.' + Chr(13) + Chr(10) + Chr(13) + Chr(10)
          + '제작 / 최신 버전:' + Chr(13) + Chr(10)
          + '{#RepoURL}' + Chr(13) + Chr(10) + Chr(13) + Chr(10)
          + '※ Steam이 게임을 업데이트한 후 한국어가 영어로 돌아가면,' + Chr(13) + Chr(10)
          + '   위 GitHub에서 최신 .exe를 받거나 이 .exe를 다시 실행하세요.';
    if not WizardSilent then
      MsgBox(Hint, mbInformation, MB_OK);
  end;
end;

// ---------- uninstall: remove the junction --------------------------------
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  GameDir, GameMods: String;
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then begin
    GameDir := FindOutworldStation();
    if GameDir <> '' then begin
      GameMods := GameDir + GameRelPaks + GameModsName;
      // rmdir succeeds for junctions and empty folders, fails for real folders.
      // That's exactly what we want: remove our junction, leave user data alone.
      if DirExists(GameMods) then
        Exec(ExpandConstant('{cmd}'), '/c rmdir "' + GameMods + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;

