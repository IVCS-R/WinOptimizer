; WinOptimizer Installer
; Requires NSIS 3.0+

!include "MUI2.nsh"

; ── General ──────────────────────────────────────────────────────
Name "WinOptimizer"
OutFile "WinOptimizer_Setup.exe"
InstallDir "$PROGRAMFILES\WinOptimizer"
InstallDirRegKey HKLM "Software\WinOptimizer" "InstallDir"
RequestExecutionLevel admin

; ── Version Info ─────────────────────────────────────────────────
VIProductVersion "2.0.0.0"
VIAddVersionKey "ProductName" "WinOptimizer"
VIAddVersionKey "CompanyName" "IVCS"
VIAddVersionKey "FileDescription" "Advanced Windows Optimization Suite"
VIAddVersionKey "FileVersion" "2.0.0"
VIAddVersionKey "ProductVersion" "2.0.0"

; ── Icon ─────────────────────────────────────────────────────────
!define MUI_ICON "folder_icon.ico"
!define MUI_UNICON "folder_icon.ico"

; ── Pages ────────────────────────────────────────────────────────
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ── Languages ────────────────────────────────────────────────────
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Spanish"

; ── Installer Sections ──────────────────────────────────────────
Section "Install" SecInstall
    SetOutPath "$INSTDIR"

    ; Files
    File "dist\WinOptimizer_Setup.exe"
    File "folder_icon.ico"
    File "LICENSE"
    File "requirements.txt"

    ; Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Registry
    WriteRegStr HKLM "Software\WinOptimizer" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinOptimizer" "DisplayName" "WinOptimizer"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinOptimizer" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinOptimizer" "DisplayIcon" '"$INSTDIR\folder_icon.ico"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinOptimizer" "Publisher" "IVCS"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinOptimizer" "DisplayVersion" "2.0.0"

    ; Start Menu shortcut
    CreateDirectory "$SMPROGRAMS\WinOptimizer"
    CreateShortCut "$SMPROGRAMS\WinOptimizer\WinOptimizer.lnk" "$INSTDIR\WinOptimizer_Setup.exe" "" "$INSTDIR\folder_icon.ico"
    CreateShortCut "$SMPROGRAMS\WinOptimizer\Uninstall.lnk" "$INSTDIR\Uninstall.exe"

    ; Desktop shortcut
    CreateShortCut "$DESKTOP\WinOptimizer.lnk" "$INSTDIR\WinOptimizer_Setup.exe" "" "$INSTDIR\folder_icon.ico"
SectionEnd

; ── Uninstaller Section ─────────────────────────────────────────
Section "Uninstall"
    Delete "$INSTDIR\WinOptimizer_Setup.exe"
    Delete "$INSTDIR\folder_icon.ico"
    Delete "$INSTDIR\LICENSE"
    Delete "$INSTDIR\requirements.txt"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"

    Delete "$SMPROGRAMS\WinOptimizer\WinOptimizer.lnk"
    Delete "$SMPROGRAMS\WinOptimizer\Uninstall.lnk"
    RMDir "$SMPROGRAMS\WinOptimizer"

    Delete "$DESKTOP\WinOptimizer.lnk"

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\WinOptimizer"
    DeleteRegKey HKLM "Software\WinOptimizer"
SectionEnd
