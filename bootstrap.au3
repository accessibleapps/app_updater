#RequireAdmin

func MoveToTarget($source, $target)
 DirCopy($source, $target, 1)
 DirRemove($source, 1)
EndFunc

func WaitForProcessToEnd($process, $interval)
 while ProcessExists($process)
  sleep($interval)
 WEnd
EndFunc
 
func RunApplication($executable)
 ShellExecute($executable)
EndFunc

func main()
 if ($CmdLine[0] < 4) then
  MsgBox(48, "Update Bootstrapper", "Please note: this is a stand-alone bootstrapper for the autoupdate facility. It cannot be run independently.")
  return
 endif
 $pid = $CmdLine[1]
 $SourcePath = $CmdLine[2]
 $DestPath = $CmdLine[3]
 $ToExecute = $CmdLine[4]
 WaitForProcessToEnd($pid, 500)
 MoveToTarget($SourcePath, $DestPath)
 RunApplication($ToExecute)
EndFunc

main()
