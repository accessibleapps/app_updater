def die():
 print "Exit Function"

from updater import AutoUpdater
A = AutoUpdater("http://dl.dropbox.com/u/4410208/bn.zip", "test.zip", "bootstrapper.sh", finish_callback=die)
A.start_update()


