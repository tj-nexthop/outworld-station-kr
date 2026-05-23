<#
.SYNOPSIS
  Outworld Station Korean patch — single-command build pipeline.

.DESCRIPTION
  Reads translation\ko.po, runs the apply→fromjson→to-zen chain, and (by default)
  copies the resulting mod into the game's ~mods folder.

.PARAMETER Init
  One-time bootstrap: re-extract assets from the game container into extracted\ and
  produce per-DT JSONs in work\dt_json. Run this once after install or after a game
  patch.

.PARAMETER Clean
  Wipe source\ and rebuild it from extracted\ before applying translations. Use
  whenever ko.po removes a previously-set translation, since apply.py only edits;
  it does not undo.

.PARAMETER NoInstall
  Build the mod files but do not copy them into the game's ~mods folder.

.PARAMETER NoFonts
  Skip rebuilding the font mod (uses the existing KoreanPatch_Fonts_P.pak).

.PARAMETER Verify
  Run scripts\verify.py at the end (Phase 5 V5.* gates).
#>
param(
  [switch]$Init,
  [switch]$Clean,
  [switch]$NoInstall,
  [switch]$NoFonts,
  [switch]$Verify,
  [switch]$Installer    # also build distributable .exe via Inno Setup
)

$ErrorActionPreference = 'Stop'
$sw = [System.Diagnostics.Stopwatch]::StartNew()

# ---------- Paths ----------
$ROOT       = (Resolve-Path "$PSScriptRoot\..").Path
$DOTNET_DIR = if ($env:DOTNET_ROOT) { $env:DOTNET_ROOT } `
              elseif (Test-Path "$env:USERPROFILE\dotnet8\dotnet.exe") { "$env:USERPROFILE\dotnet8" } `
              else { Split-Path (Get-Command dotnet -ErrorAction SilentlyContinue).Source }
$RETOC      = "$ROOT\tools\retoc.exe"
$UASSETGUI  = "$ROOT\tools\UAssetGUI.exe"
$REPAK      = "$ROOT\tools\repak\repak.exe"
$ISCC       = "$ROOT\tools\innosetup\ISCC.exe"
$SOURCE_DIR = "$ROOT\source"
$EXTRACTED  = "$ROOT\extracted\legacy"
$DT_JSON    = "$ROOT\work\dt_json"
$DT_JSON_KO = "$ROOT\work\dt_json_ko"
$MOD_DIR    = "$ROOT\mod"
$KO_PO      = "$ROOT\translation\ko.po"
$MANIFEST   = "$ROOT\translation\manifest.json"
$FONT_PAK_ROOT = "$ROOT\work\font_pak"
$GAME_PAKS  = 'C:\Program Files (x86)\Steam\steamapps\common\OutworldStation\OutworldStation\Content\Paks'
$GAME_MODS  = "$GAME_PAKS\~mods"

# Make .NET 8 visible for UAssetGUI
$env:DOTNET_ROOT = $DOTNET_DIR
$env:PATH = "$DOTNET_DIR;$env:PATH"
$env:PYTHONIOENCODING = 'utf-8'

function Step($msg) { Write-Host ("[{0,5:F1}s] {1}" -f $sw.Elapsed.TotalSeconds, $msg) -ForegroundColor Cyan }
function Ok($msg)   { Write-Host ("        {0}" -f $msg) -ForegroundColor DarkGray }
function Die($msg)  { Write-Error $msg; exit 1 }

# ---------- Sanity ----------
foreach ($t in @($RETOC, $UASSETGUI, $REPAK)) {
  if (-not (Test-Path $t)) { Die "missing tool: $t" }
}
if (-not (Test-Path "$DOTNET_DIR\dotnet.exe")) {
  Die "missing .NET 8 host at $DOTNET_DIR — install .NET 8 desktop+runtime"
}
if (-not (Test-Path $KO_PO))    { Die "missing $KO_PO" }
if (-not (Test-Path $MANIFEST)) { Die "missing $MANIFEST — did you run -Init?" }

# ---------- (optional) Init: extract from game ----------
if ($Init) {
  Step "Init: re-extract from game container"
  if (-not (Test-Path $EXTRACTED)) { New-Item -ItemType Directory -Force -Path $EXTRACTED | Out-Null }
  & $RETOC to-legacy --no-shaders --version UE5_5 $GAME_PAKS $EXTRACTED 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { Die "retoc to-legacy failed" }

  Step "Init: tojson on every DT_*.uasset"
  if (-not (Test-Path $DT_JSON)) { New-Item -ItemType Directory -Force -Path $DT_JSON | Out-Null }
  $dtFiles = Get-ChildItem "$EXTRACTED\OutworldStation\Content\Data" -Filter "DT_*.uasset"
  $i = 0
  foreach ($f in $dtFiles) {
    $i++
    $out = "$DT_JSON\$($f.BaseName).json"
    $p = Start-Process -FilePath $UASSETGUI -ArgumentList @('tojson', $f.FullName, $out, 'VER_UE5_5') `
      -NoNewWindow -PassThru -Wait `
      -RedirectStandardOutput "$env:TEMP\ua_o.log" -RedirectStandardError "$env:TEMP\ua_e.log"
    if ($p.ExitCode -ne 0 -or -not (Test-Path $out)) { Die "tojson failed for $($f.Name)" }
    Write-Progress -Activity "tojson" -Status $f.Name -PercentComplete (100 * $i / $dtFiles.Count)
  }
  Write-Progress -Activity "tojson" -Completed
  Ok "  $($dtFiles.Count) DataTables converted to JSON"

  Step "Init: extract source.po + manifest.json"
  python "$ROOT\scripts\extract.py" 2>&1 | Out-Host
  if ($LASTEXITCODE -ne 0) { Die "extract.py failed" }

  Step "Init: extract en/Game.locres + Game.locmeta from game .pak"
  $LOCRES_EXTRACT = "$ROOT\work\locres_extract"
  $GAME_PAK = "$GAME_PAKS\OutworldStation-Windows.pak"
  if (-not (Test-Path $GAME_PAK)) { Die "missing game pak: $GAME_PAK" }
  if (Test-Path $LOCRES_EXTRACT) { Remove-Item $LOCRES_EXTRACT -Recurse -Force }
  New-Item -ItemType Directory -Force -Path $LOCRES_EXTRACT | Out-Null
  & $REPAK unpack -o $LOCRES_EXTRACT -i "OutworldStation/Content/Localization/Game" $GAME_PAK 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { Die "repak unpack locres failed" }
  $locresFile = "$LOCRES_EXTRACT\OutworldStation\Content\Localization\Game\en\Game.locres"
  if (-not (Test-Path $locresFile)) { Die "en/Game.locres not found after repak unpack" }
  Ok "  locres extracted: $(Split-Path $locresFile -Leaf) ($((Get-Item $locresFile).Length) bytes)"
}

# ---------- Step 0: regenerate ko.po from build_ko_po.py TR dict ----------
Step "Regenerate ko.po from build_ko_po.py master TR dict"
python "$ROOT\scripts\build_ko_po.py" 2>&1 | Select-Object -Last 4 | Out-Host
if ($LASTEXITCODE -ne 0) { Die "build_ko_po.py failed" }

# ---------- Step 1: clean source/ if requested, ensure populated ----------
Step "Apply translations from ko.po -> work\dt_json_ko"
python "$ROOT\scripts\apply.py" 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) { Die "apply.py failed" }

# ---------- Step 2: fromjson each modified JSON into source/ ----------
Step "fromjson: rebuild .uasset/.uexp from modified JSONs"

# Build a {asset stem -> source relative path} map from manifest so we can route
# DT_* into Content/Data and UI_*/BP_*/E_*/S_* into Content/MainMenu (or wherever
# extract.py recorded their original location).
$manifestRaw = Get-Content $MANIFEST -Raw -Encoding UTF8 | ConvertFrom-Json
$assetPathMap = @{}
foreach ($e in $manifestRaw.entries) {
  if ($e.source_path -and -not $assetPathMap.ContainsKey($e.file)) {
    $assetPathMap[$e.file] = $e.source_path
  }
}

if ($Clean) {
  Step "Clean: copy originals from extracted\ to source\"
  Get-ChildItem "$SOURCE_DIR" -Recurse -File -ErrorAction SilentlyContinue | Remove-Item -Force
  $copyMap = @{
    "OutworldStation\Content\Data"             = "DT_*"
    "OutworldStation\Content\MainMenu"         = "*"
    "OutworldStation\Content\UI"               = "*"
    "OutworldStation\Content\Station\Modules"  = "*"
  }
  foreach ($rel in $copyMap.Keys) {
    $srcPath = Join-Path $EXTRACTED $rel
    $dstPath = Join-Path $SOURCE_DIR $rel
    New-Item -ItemType Directory -Force -Path $dstPath | Out-Null
    if (Test-Path $srcPath) {
      Copy-Item "$srcPath\$($copyMap[$rel])" $dstPath -ErrorAction SilentlyContinue
    }
  }
}

$modifiedJsons = Get-ChildItem $DT_JSON_KO -Filter "*.json" -ErrorAction SilentlyContinue
if (-not $modifiedJsons) {
  Ok "no entries translated yet — nothing to rebuild"
} else {
  foreach ($j in $modifiedJsons) {
    $relPath = $assetPathMap[$j.BaseName]
    if (-not $relPath) {
      # Fallback: assume DataTable
      $relPath = "OutworldStation\Content\Data\$($j.BaseName).uasset"
    }
    $dst = Join-Path $SOURCE_DIR $relPath
    $parentDir = Split-Path $dst
    New-Item -ItemType Directory -Force -Path $parentDir | Out-Null
    $p = Start-Process -FilePath $UASSETGUI -ArgumentList @('fromjson', $j.FullName, $dst) `
      -NoNewWindow -PassThru -Wait `
      -RedirectStandardOutput "$env:TEMP\fj_o.log" -RedirectStandardError "$env:TEMP\fj_e.log"
    if ($p.ExitCode -ne 0 -or -not (Test-Path $dst)) { Die "fromjson failed for $($j.Name) -> $dst" }
    Ok "  $($j.BaseName).uasset rebuilt -> $relPath"
  }
}

# ---------- Step 3: retoc to-zen — pack text mod ----------
Step "retoc to-zen: pack KoreanPatch_P (text)"
Get-ChildItem $MOD_DIR -Filter "KoreanPatch_P.*" -ErrorAction SilentlyContinue | Remove-Item
& $RETOC --override-container-header-version NoExportInfo --override-toc-version OnDemandMetaData `
  to-zen --version UE5_5 $SOURCE_DIR "$MOD_DIR\KoreanPatch_P.utoc" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Die "retoc to-zen failed" }
$verifyOut = & $RETOC verify "$MOD_DIR\KoreanPatch_P.utoc" 2>&1
if ($verifyOut -notmatch 'verified') { Die "retoc verify failed: $verifyOut" }
Ok "verify: $verifyOut"

# ---------- Step 3.5: build ko/Game.locres + locmeta, pack into KoreanPatch_LocRes_P ----------
Step "Build ko/Game.locres (FText localization) and pack KoreanPatch_LocRes_P"
python "$ROOT\scripts\build_ko_locres.py" 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) { Die "build_ko_locres.py failed" }
Get-ChildItem $MOD_DIR -Filter "KoreanPatch_LocRes_P.*" -ErrorAction SilentlyContinue | Remove-Item -Force
& $REPAK pack --version V11 "$ROOT\work\ko_pak_root" "$MOD_DIR\KoreanPatch_LocRes_P.pak" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Die "repak pack KoreanPatch_LocRes_P failed" }
$lpsize = (Get-Item "$MOD_DIR\KoreanPatch_LocRes_P.pak").Length
Ok ("KoreanPatch_LocRes_P.pak rebuilt ({0:N0} bytes)" -f $lpsize)

# ---------- Step 4: rebuild font pak (unless -NoFonts) ----------
if (-not $NoFonts) {
  Step "repak: pack KoreanPatch_Fonts_P (font override)"
  if (-not (Test-Path $FONT_PAK_ROOT)) {
    Die "font pak source missing: $FONT_PAK_ROOT — run Phase 2 setup first"
  }
  Get-ChildItem $MOD_DIR -Filter "KoreanPatch_Fonts_P.*" -ErrorAction SilentlyContinue | Remove-Item
  & $REPAK pack --version V11 $FONT_PAK_ROOT "$MOD_DIR\KoreanPatch_Fonts_P.pak" 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) { Die "repak pack failed" }
  Ok "font pak rebuilt"
}

# ---------- Step 5: install ----------
if (-not $NoInstall) {
  # Prefer the Phase-6 backup folder if install_dev.ps1 has been run.
  # Detection: ~mods exists AND is a reparse point (junction) -> write to backup.
  $BACKUP_DIR = "$env:LOCALAPPDATA\OutworldStation_KR\mods"
  $useBackup = $false
  if (Test-Path $GAME_MODS) {
    $attr = (Get-Item $GAME_MODS -Force).Attributes
    if (($attr -band [IO.FileAttributes]::ReparsePoint) -ne 0) { $useBackup = $true }
  }
  if ($useBackup) {
    Step "Install to backup folder (Phase-6 junction is active)"
    New-Item -ItemType Directory -Force -Path $BACKUP_DIR | Out-Null
    Get-ChildItem $BACKUP_DIR -Filter "KoreanPatch*" -ErrorAction SilentlyContinue | Remove-Item -Force
    Copy-Item "$MOD_DIR\KoreanPatch*" $BACKUP_DIR -Force
    $files = Get-ChildItem $BACKUP_DIR -Filter "KoreanPatch*" | ForEach-Object { "$($_.Name) ($('{0:N0}' -f $_.Length))" }
    Ok "installed (via junction): $($files -join ', ')"
  } else {
    Step "Install to game ~mods (direct copy)"
    if (-not (Test-Path $GAME_MODS)) { New-Item -ItemType Directory -Force -Path $GAME_MODS | Out-Null }
    Get-ChildItem $GAME_MODS -Filter "KoreanPatch*" -ErrorAction SilentlyContinue | Remove-Item -Force
    Copy-Item "$MOD_DIR\KoreanPatch*" $GAME_MODS -Force
    $files = Get-ChildItem $GAME_MODS -Filter "KoreanPatch*" | ForEach-Object { "$($_.Name) ($('{0:N0}' -f $_.Length))" }
    Ok "installed: $($files -join ', ')"
    Ok "tip: run scripts\install_dev.ps1 to switch to junction-based install"
  }
}

# ---------- Step 6: optional verify ----------
if ($Verify) {
  Step "verify.py — Phase 1-4 gates"
  python "$ROOT\scripts\verify.py" --all 2>&1 | Out-Host
  if ($LASTEXITCODE -ne 0) { Die "verify.py reported failures" }
}

# ---------- Step 7: optional .exe installer build (Inno Setup) ----------
if ($Installer) {
  if (-not (Test-Path $ISCC)) { Die "missing Inno Setup compiler at $ISCC" }
  Step "ISCC: compile installer .exe"
  & $ISCC /Q "$ROOT\installer\setup.iss" 2>&1 | Out-Host
  if ($LASTEXITCODE -ne 0) { Die "ISCC compile failed" }
  $exe = Get-ChildItem "$ROOT\installer" -Filter "KoreanPatch_OutworldStation_v*.exe" |
         Sort-Object LastWriteTime -Descending | Select-Object -First 1
  if ($exe) { Ok ("installer ready: {0} ({1:N0} bytes)" -f $exe.Name, $exe.Length) }
}

$sw.Stop()
Write-Host ""
Write-Host ("Build OK in {0:F1}s" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Green
