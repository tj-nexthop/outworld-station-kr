@echo off
rem Outworld Station Korean Patch ??wrapper for Steam launch.
rem Re-creates the ~mods junction if Steam (or anything else) cleaned it.

set "BACKUP=%LOCALAPPDATA%\OutworldStation_KR\mods"
set "MODS=C:\Program Files (x86)\Steam\steamapps\common\OutworldStation\OutworldStation\Content\Paks\~mods"

if not exist "%MODS%\KoreanPatch_P.utoc" (
  if exist "%MODS%" rmdir /Q "%MODS%" 2>nul
  mklink /J "%MODS%" "%BACKUP%" >nul
)

rem Pass through to whatever Steam wanted to run.
%*
