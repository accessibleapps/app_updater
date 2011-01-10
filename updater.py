#AutoUpdater
#Released under a GNU GPL
import urllib
import platform_utils
import hashlib
import os
from zipfile import ZipFile
import subprocess
import stat

class AutoUpdater():
 def __init__(self, URL, location, bootstrapper, onExit, MD5="none"):
  """Supply a URL/location/bootstrapper filename to download a zip file from
     The onExit argument should be a Python function it'll call when done"""
  #Let's download the file using urllib
  self.percent = 0
  self.attempts = 0 
  self.complete = 0
  self.onExit = onExit #What to do on exit
  #Change our location to not be local -- use platform_utils
  location = os.path.join(platform_utils.paths.app_data_path('updater'), location)
  platform_utils.paths.prepare_app_data_path('updater')
  #os.chmod(platform_utils.paths.app_data_path('updater'), 777)
  #os.chmod(platform_utils.paths.app_data_path('updater'), stat.S_IRWXU)
  self.start(URL, location, bootstrapper, MD5)
 
 def hookProg(self, count, bSize, tSize):
   #This nice little function gets called a few times a second
   #It'll update the percent
   self.percent = int(count*bSize*100/tSize)
   print str(self.percent)
 
 def get_percent(self):
  """Returns a string of the current percent"""
  return str(self.percent)

 def start(self, URL, location, bootstrapper, MD5):
  """Called by __init__ to start the whole process"""
  self.attempts = self.attempts + 1
  Listy = urllib.urlretrieve(URL, location, reporthook=self.hookProg)
  if self.attempts >= 3:
   #If we have had 3 or more attempts where the MD5 did not match, throw an error.
   raise(Exception, "Three Attempts have been made to download the file. None have matched MD5. Contact the developer.")
  #So once we get to this line, the file has been downloaded
  if not MD5 == "none":
   #Check the MD5
   if self.MD5File(location) != MD5:
    #ReDownload
    print "MD5 HASH FAIL -- RETRY DOWNLOAD"
    self.start(URL, location, bootstrapper, MD5)
   else:
    #It redownloaded properly
    self.DoneDownload(Listy[0], bootstrapper)
  else:
   #We don't know if it downloaded properly
   #The programmer didn't give us an MD5. So we have to assume it was valid.
   self.DoneDownload(Listy[0], bootstrapper)

 def MD5File(self, fileName):
  "Custom function that will get the Md5 sum of our file"
  file_reference=open(fileName, 'rb').read() 
  return hashlib.md5(file_reference).hexdigest()

 def DoneDownload(self, location, bootstrapper):
  """Called when the file is done downloading, and MD5 has been successfull"""
  CurD = os.getcwd() #Store our current working directory (of main app)
  print location
 # os.chmod(location, 777)
  zippy = ZipFile(location, 'r')
  Pathy = os.path.join(platform_utils.paths.app_data_path('updater'), os.path.basename(location).strip(".zip"))
  #os.chmod(Pathy, 775)
  zippy.extractall(Pathy)
  BootStr = os.path.join(Pathy, bootstrapper)
  os.chmod(BootStr, 666)
  print BootStr
  subprocess.call([BootStr], shell=True)
  self.complete = 1
  print "DONE!!!!"
  self.onExit()
