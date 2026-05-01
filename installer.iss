[Setup]
AppName=Listy
AppVersion=1.0
DefaultDirName={autopf}\Listy
DefaultGroupName=Listy
UninstallDisplayIcon={app}\Listy.exe
Compression=lzma
SolidCompression=yes
OutputDir=Output
OutputBaseFilename=Listy_Setup
SetupIconFile=assets/icons/favicon.ico 

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Берем все файлы из папки, которую создал PyInstaller
Source: "dist\Listy\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\Listy\Listy.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Listy"; Filename: "{app}\Listy.exe"; IconFilename: "{app}\Listy.exe"
Name: "{commondesktop}\Listy"; Filename: "{app}\Listy.exe"; Tasks: desktopicon; IconFilename: "{app}\Listy.exe"

[Run]
Filename: "{app}\Listy.exe"; Description: "{cm:LaunchProgram,Listy}"; Flags: nowait postinstall skipifsilent
