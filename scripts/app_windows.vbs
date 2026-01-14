Set WshShell = CreateObject("WScript.Shell")

' Ensure working directory is this scripts/ folder, so relative paths work
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Run the batch file hidden (0 = no window)
WshShell.Run Chr(34) & "run_windows.bat" & Chr(34), 0

Set WshShell = Nothing
