; installer/opensmu_installer.iss
; Inno Setup script for opensmu
;
; Prerequisites:
;   1. Run PyInstaller first (from project root):
;      pyinstaller installer/opensmu.spec
;   2. Then compile this script with Inno Setup Compiler
;
; Download Inno Setup: https://jrsoftware.org/isdl.php

#define AppName "opensmu"
#define AppVersion "0.1.1"
#define AppPublisher "Thanh Chien Nguyen"
#define AppExeName "opensmu.exe"
#define SourceDir "..\installer\dist\opensmu"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL=https://github.com/chien-swservice/opensmu
AppSupportURL=https://github.com/chien-swservice/opensmu/issues
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=.\dist
OutputBaseFilename=opensmu_setup_v{#AppVersion}
SetupIconFile=..\resources\opensmulogo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Require 64-bit Windows
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\opensmu"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall opensmu"; Filename: "{uninstallexe}"
Name: "{autodesktop}\opensmu"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch opensmu"; Flags: nowait postinstall skipifsilent

[Messages]
WelcomeLabel2=This will install [name/ver] on your computer.%n%nIMPORTANT: opensmu requires NI-VISA to communicate with real hardware instruments (Keithley, Keysight).%n%nIf you have not installed NI-VISA yet, download it from:%nhttps://www.ni.com/en/support/downloads/drivers/download.ni-visa.html%n%nSimulation mode works without NI-VISA.%n%nClick Next to continue.
