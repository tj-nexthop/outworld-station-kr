<#
.SYNOPSIS
  Phase 6 — install the Korean patch via the junction-and-wrapper pattern.
  One-time setup. Keeps the mod files outside the game folder so Steam updates,
  integrity verification, or full reinstalls can't wipe them.

.DESCRIPTION
  Layout this script establishes:

    %LOCALAPPDATA%\OutworldStation_KR\mods\          ← real mod files live here
    %LOCALAPPDATA%\OutworldStation_KR\wrapper.bat    ← what Steam launches
    <game>\Content\Paks\~mods\                       ← junction → backup folder

  After running once:
    - build.ps1 copies new mod files into the backup folder; the junction
      makes them visible to the game with no further action.
    - If Steam ever deletes ~mods (integrity check, game reinstall, etc.),
      wrapper.bat re-creates the junction the next time the game launches.

.PARAMETER Steam
  Print the exact "Set Launch Options" string to paste into Steam.

.PARAMETER Repair
  Force-recreate the junction even if it already exists.
#>
param(
  [switch]$Steam,
  [switch]$Repair
)

$ErrorActionPreference = 'Stop'

$ROOT      = (Resolve-Path "$PSScriptRoot\..").Path
$BACKUP    = "$env:LOCALAPPDATA\OutworldStation_KR\mods"
$WRAPPER   = "$env:LOCALAPPDATA\OutworldStation_KR\wrapper.bat"
$GAME_PAKS = 'C:\Program Files (x86)\Steam\steamapps\common\OutworldStation\OutworldStation\Content\Paks'
$GAME_MODS = "$GAME_PAKS\~mods"
$GAME_EXE  = 'C:\Program Files (x86)\Steam\steamapps\common\OutworldStation\OutworldStation.exe'

function Step($m) { Write-Host "[*] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "    $m" -ForegroundColor DarkGray }

# ---------- 1. Backup directory ----------
Step "Create backup directory: $BACKUP"
New-Item -ItemType Directory -Force -Path $BACKUP | Out-Null

# ---------- 2. Move existing mod files out of the game folder ----------
Step "Move any existing KoreanPatch* files from game ~mods to backup"
if (Test-Path $GAME_MODS) {
  $existing = Get-ChildItem $GAME_MODS -Filter "KoreanPatch*" -ErrorAction SilentlyContinue
  if ($existing) {
    foreach ($f in $existing) {
      $dst = Join-Path $BACKUP $f.Name
      Move-Item -Force $f.FullName $dst
      Ok "moved $($f.Name)"
    }
  } else { Ok "no existing KoreanPatch* files in game ~mods" }
}

# Also seed from build output if backup is empty
if (-not (Get-ChildItem $BACKUP -Filter "KoreanPatch*" -ErrorAction SilentlyContinue)) {
  if (Test-Path "$ROOT\mod\KoreanPatch_P.utoc") {
    Step "Seed backup from $ROOT\mod"
    Copy-Item "$ROOT\mod\KoreanPatch*" $BACKUP -Force
    Ok "seeded $((Get-ChildItem $BACKUP -Filter 'KoreanPatch*').Count) files"
  } else {
    Ok "no $ROOT\mod files yet — run build.ps1 once before launching the game"
  }
}

# ---------- 3. Set up the junction ----------
Step "Set up junction: $GAME_MODS  ->  $BACKUP"
$needCreate = $false
if (Test-Path $GAME_MODS) {
  $item = Get-Item $GAME_MODS -Force
  $isJunction = ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0
  if ($isJunction) {
    # Read its target via cmd
    $tgt = (cmd /c dir /AL "$GAME_PAKS" 2>$null | Select-String '~mods')
    if ($Repair) {
      Step "Repair: removing existing junction"
      cmd /c rmdir "$GAME_MODS" | Out-Null
      $needCreate = $true
    } else {
      Ok "junction already in place"
    }
  } else {
    # It's a real folder — that's the legacy install
    $contents = Get-ChildItem $GAME_MODS -ErrorAction SilentlyContinue
    if ($contents.Count -gt 0) {
      Ok "WARNING: $GAME_MODS is a real folder with $($contents.Count) item(s)."
      Ok "         Move/back them up before this script can replace it with a junction."
      throw "Refusing to overwrite real ~mods folder. Move its contents to $BACKUP first."
    }
    Step "Empty real folder — replacing with junction"
    Remove-Item $GAME_MODS -Force
    $needCreate = $true
  }
} else {
  $needCreate = $true
}

if ($needCreate) {
  cmd /c mklink /J `"$GAME_MODS`" `"$BACKUP`" | Out-Null
  if (-not (Test-Path $GAME_MODS)) { throw "junction creation failed" }
  Ok "junction created"
}

# ---------- 4. Write wrapper.bat ----------
Step "Write wrapper.bat -> $WRAPPER"
# %* receives the full Steam command incl. game exe + args.
# /D makes sure the working dir matches the launch.
$wrapperBody = @"
@echo off
rem Outworld Station Korean Patch — wrapper for Steam launch.
rem Re-creates the ~mods junction if Steam (or anything else) cleaned it.

set "BACKUP=%LOCALAPPDATA%\OutworldStation_KR\mods"
set "MODS=$GAME_MODS"

if not exist "%MODS%\KoreanPatch_P.utoc" (
  if exist "%MODS%" rmdir /Q "%MODS%" 2>nul
  mklink /J "%MODS%" "%BACKUP%" >nul
)

rem Pass through to whatever Steam wanted to run.
%*
"@
Set-Content -Encoding ascii -Path $WRAPPER -Value $wrapperBody
Ok "wrapper written ($((Get-Item $WRAPPER).Length) bytes)"

# ---------- 5. Print Steam instructions ----------
Step "Phase 6 install complete."
""
"Mod files are now at:        $BACKUP"
"Game folder ~mods is:        a junction → backup"
"wrapper.bat is at:           $WRAPPER"
""
"To make the patch self-healing across Steam updates, set the game's launch options:"
"  Steam → Library → Outworld Station → right-click → Properties → 일반 → 시작 옵션"
""
"  ""$WRAPPER"" %command%"
""
"After that, every time you launch the game from Steam:"
"  - wrapper.bat checks the junction"
"  - if missing, recreates it from $BACKUP"
"  - then runs the game as Steam intended"
""
if ($Steam) {
  "[copy this exactly into Steam Launch Options]"
  "`"$WRAPPER`" %command%"
}
