def die():
 print "Exit Function"

from updater import AutoUpdater
A = AutoUpdater("http://dl.dropbox.com/u/4410208/test.zip", "test.zip", "bootstrapper.exe", finish_callback=die)
A.start_update()


