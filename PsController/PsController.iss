[Setup]
AppId={{937076EA-ACAC-42B7-8045-B20BF4A31152}
AppName=PsController
AppVersion=1.0
AppVerName=Ps Controller
AppPublisher=Gudbjorn Einarsson
DefaultDirName={pf}\Ps Controller\
DefaultGroupName=FG\Ps Controller
OutputBaseFilename=PsController setup

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: PsController\build\exe.win32-3.3\*; DestDir:{app}; Flags: recursesubdirs

[Icons]
Name: {commondesktop}\Ps Controller; Filename: {app}\PsController.exe; Tasks: desktopicon

[Run]
Filename: "{app}\PsController.exe"; Description: "Ps Controller"; Flags: nowait postinstall skipifsilent unchecked

