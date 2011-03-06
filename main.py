import platform
import time
import sys

def die(): 
 print "Exit"
 time.sleep(15)
 print "REALDIE"

from updater import AutoUpdater
import updater
if platform.system() == "Windows":
  A = AutoUpdater("http://dl.dropbox.com/u/4410208/test.zip", "test.zip", "bootstrapper.exe", finish_callback=die)
else:
  A = AutoUpdater("http://dl.dropbox.com/u/4410208/test-lin.zip", "test-lin.zip", "bootstrapper.sh", finish_callback=die)
A.start_update()
