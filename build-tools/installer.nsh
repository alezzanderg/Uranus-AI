# Uranus-AI Editor NSIS Installer Script
# Custom installer configurations and actions

# Include modern UI
!include "MUI2.nsh"

# Installer attributes
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "header.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP "welcome.bmp"

# Welcome page
!define MUI_WELCOMEPAGE_TITLE "Welcome to Uranus-AI Editor Setup"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of Uranus-AI Editor.$\r$\n$\r$\nUranus-AI is an AI-enhanced code editor with native multi-model support, based on Code-OSS.$\r$\n$\r$\nClick Next to continue."

# Finish page
!define MUI_FINISHPAGE_TITLE "Uranus-AI Editor Installation Complete"
!define MUI_FINISHPAGE_TEXT "Uranus-AI Editor has been successfully installed on your computer.$\r$\n$\r$\nFeatures included:$\r$\n• Multi-model AI support (OpenAI, Claude, Gemini, Grok, etc.)$\r$\n• Native AI assistant integration$\r$\n• Code analysis and refactoring$\r$\n• PostgreSQL configuration storage$\r$\n$\r$\nClick Finish to close this wizard."

!define MUI_FINISHPAGE_RUN "$INSTDIR\Uranus-AI Editor.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Uranus-AI Editor"

# Custom functions
Function .onInit
    # Check if another instance is running
    System::Call 'kernel32::CreateMutex(i 0, i 0, t "UranusAIInstaller") i .r1 ?e'
    Pop $R0
    StrCmp $R0 0 +3
        MessageBox MB_OK|MB_ICONEXCLAMATION "The installer is already running."
        Abort
        
    # Check Windows version
    ${IfNot} ${AtLeastWin10}
        MessageBox MB_OK|MB_ICONSTOP "Uranus-AI Editor requires Windows 10 or later."
        Abort
    ${EndIf}
    
    # Check if .NET Framework is installed (if needed)
    # ReadRegStr $0 HKLM "SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" "Release"
    # IntCmp $0 461808 +3 0 +3  # .NET 4.7.2
    #     MessageBox MB_OK|MB_ICONSTOP "Uranus-AI Editor requires .NET Framework 4.7.2 or later."
    #     Abort
FunctionEnd

Function .onInstSuccess
    # Create desktop shortcut
    CreateShortcut "$DESKTOP\Uranus-AI Editor.lnk" "$INSTDIR\Uranus-AI Editor.exe" "" "$INSTDIR\Uranus-AI Editor.exe" 0
    
    # Create start menu shortcuts
    CreateDirectory "$SMPROGRAMS\Uranus-AI"
    CreateShortcut "$SMPROGRAMS\Uranus-AI\Uranus-AI Editor.lnk" "$INSTDIR\Uranus-AI Editor.exe" "" "$INSTDIR\Uranus-AI Editor.exe" 0
    CreateShortcut "$SMPROGRAMS\Uranus-AI\Uninstall.lnk" "$INSTDIR\Uninstall Uranus-AI Editor.exe"
    
    # Register file associations
    WriteRegStr HKCR ".uranusai" "" "UranusAI.Project"
    WriteRegStr HKCR "UranusAI.Project" "" "Uranus-AI Project File"
    WriteRegStr HKCR "UranusAI.Project\DefaultIcon" "" "$INSTDIR\Uranus-AI Editor.exe,0"
    WriteRegStr HKCR "UranusAI.Project\shell\open\command" "" '"$INSTDIR\Uranus-AI Editor.exe" "%1"'
    
    # Add to Windows Programs list
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "DisplayName" "Uranus-AI Editor"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "DisplayVersion" "1.2.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "Publisher" "Uranus-AI Team"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "DisplayIcon" "$INSTDIR\Uranus-AI Editor.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "UninstallString" "$INSTDIR\Uninstall Uranus-AI Editor.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI" "NoRepair" 1
    
    # Refresh shell icons
    System::Call 'shell32.dll::SHChangeNotify(l, l, i, i) v (0x08000000, 0, 0, 0)'
FunctionEnd

Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove Uranus-AI Editor and all of its components?" IDYES +2
    Abort
FunctionEnd

Function un.onUninstSuccess
    # Remove registry entries
    DeleteRegKey HKCR ".uranusai"
    DeleteRegKey HKCR "UranusAI.Project"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\UranusAI"
    
    # Remove shortcuts
    Delete "$DESKTOP\Uranus-AI Editor.lnk"
    RMDir /r "$SMPROGRAMS\Uranus-AI"
    
    # Refresh shell icons
    System::Call 'shell32.dll::SHChangeNotify(l, l, i, i) v (0x08000000, 0, 0, 0)'
    
    MessageBox MB_OK "Uranus-AI Editor has been successfully removed from your computer."
FunctionEnd

# Custom page for configuration
Page custom ConfigPage ConfigPageLeave

Function ConfigPage
    !insertmacro MUI_HEADER_TEXT "Configuration" "Configure Uranus-AI Editor settings"
    
    nsDialogs::Create 1018
    Pop $0
    
    ${NSD_CreateLabel} 0 0 100% 20u "Choose your preferred AI provider (you can change this later):"
    Pop $0
    
    ${NSD_CreateRadioButton} 10 30 100% 15u "OpenAI (GPT-4, GPT-3.5)"
    Pop $1
    
    ${NSD_CreateRadioButton} 10 50 100% 15u "Anthropic (Claude 3)"
    Pop $2
    
    ${NSD_CreateRadioButton} 10 70 100% 15u "Google (Gemini Pro)"
    Pop $3
    
    ${NSD_CreateRadioButton} 10 90 100% 15u "Multiple providers (recommended)"
    Pop $4
    
    ${NSD_Check} $4  # Default to multiple providers
    
    ${NSD_CreateLabel} 0 120 100% 40u "Note: You can configure API keys and change providers after installation through the application settings."
    Pop $0
    
    nsDialogs::Show
FunctionEnd

Function ConfigPageLeave
    # Store user preference (could be used for initial configuration)
    ${NSD_GetState} $1 $R1
    ${NSD_GetState} $2 $R2
    ${NSD_GetState} $3 $R3
    ${NSD_GetState} $4 $R4
    
    # Write preference to registry for first-time setup
    ${If} $R1 == 1
        WriteRegStr HKCU "Software\UranusAI\Setup" "PreferredProvider" "openai"
    ${ElseIf} $R2 == 1
        WriteRegStr HKCU "Software\UranusAI\Setup" "PreferredProvider" "anthropic"
    ${ElseIf} $R3 == 1
        WriteRegStr HKCU "Software\UranusAI\Setup" "PreferredProvider" "google"
    ${Else}
        WriteRegStr HKCU "Software\UranusAI\Setup" "PreferredProvider" "multiple"
    ${EndIf}
FunctionEnd

# Sections for installation components
Section "Core Application" SecCore
    SectionIn RO  # Read-only, always installed
    
    # Install main application files
    SetOutPath "$INSTDIR"
    File /r "${BUILD_DIR}\*.*"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\Uninstall Uranus-AI Editor.exe"
SectionEnd

Section "Desktop Integration" SecDesktop
    # File associations and context menu entries
    WriteRegStr HKCR "*\shell\UranusAI" "" "Open with Uranus-AI"
    WriteRegStr HKCR "*\shell\UranusAI\command" "" '"$INSTDIR\Uranus-AI Editor.exe" "%1"'
    
    # Add to "Open with" menu for code files
    WriteRegStr HKCR "SystemFileAssociations\.js\shell\UranusAI" "" "Edit with Uranus-AI"
    WriteRegStr HKCR "SystemFileAssociations\.js\shell\UranusAI\command" "" '"$INSTDIR\Uranus-AI Editor.exe" "%1"'
    WriteRegStr HKCR "SystemFileAssociations\.ts\shell\UranusAI" "" "Edit with Uranus-AI"
    WriteRegStr HKCR "SystemFileAssociations\.ts\shell\UranusAI\command" "" '"$INSTDIR\Uranus-AI Editor.exe" "%1"'
    WriteRegStr HKCR "SystemFileAssociations\.py\shell\UranusAI" "" "Edit with Uranus-AI"
    WriteRegStr HKCR "SystemFileAssociations\.py\shell\UranusAI\command" "" '"$INSTDIR\Uranus-AI Editor.exe" "%1"'
SectionEnd

Section "Visual C++ Redistributable" SecVCRedist
    # Check if VC++ Redistributable is needed and install it
    SetOutPath "$TEMP"
    File "vcredist_x64.exe"
    ExecWait '"$TEMP\vcredist_x64.exe" /quiet /norestart'
    Delete "$TEMP\vcredist_x64.exe"
SectionEnd

# Section descriptions
LangString DESC_SecCore ${LANG_ENGLISH} "Core Uranus-AI Editor application files (required)"
LangString DESC_SecDesktop ${LANG_ENGLISH} "Desktop integration including file associations and context menu entries"
LangString DESC_SecVCRedist ${LANG_ENGLISH} "Microsoft Visual C++ Redistributable (required for proper operation)"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} $(DESC_SecCore)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktop} $(DESC_SecDesktop)
    !insertmacro MUI_DESCRIPTION_TEXT ${SecVCRedist} $(DESC_SecVCRedist)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

