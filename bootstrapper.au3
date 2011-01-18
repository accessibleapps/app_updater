;This is a bootstrapper for an Auto Update Python Script
;It was originally written in Python, but converted to AutoIt/BASH for size
#Include <File.au3>
#Include <Array.au3>
Dim $location = ""
Dim $zip_contents = ""
Dim $ResInt = -1
#RequireAdmin ;Require Administration
if $CmdLine[1] == "-l" Then
	$location = $CmdLine[2] ;our location is in argument
endif
if $CmdLine[3] == "-d" Then
	$zip_contents = $CmdLine[4]
EndIf
MsgBox(0, "R", $location)
MsgBox(0, "zipfile", $zip_contents)
;Okay, we are now going to move everything from the current directory to $location
$ResInt = DirMove(@ScriptDir & "/" & $zip_contents, $location, 1) ;1 indicates over-write
if ($ResInt == 0) Then
	;OnError is 0, notify user
	MsgBox(4096, "Error!", "There was an error trying to copy " & @ScriptDir & " to " & $location & " Please contact the developer of the program you are trying to update.")
EndIf

$FileList = _FileListToArray(@ScriptDir & "/" & $zip_contents)
for $i = 1 to $FileList[0]
	MsgBox(0, "F", "FROM " & @ScriptDir & "/" & $zip_contents & "/" & $FileList[$i] & " TO " & $location & "/" & $FileList[$i])
	DirMove(@ScriptDir & "/" & $zip_contents & "/" & $FileList[$i], $location & "/" & $FileList[$i])
Next 