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
Dim $src = @ScriptDir & "\" & $zip_contents
Run(@ComSpec & ' /c xcopy /e /h /y "' & $src & '" "' & $location & '"', "", @SW_HIDE)