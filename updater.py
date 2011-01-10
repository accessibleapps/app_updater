#AutoUpdater
#Released under a GNU GPL
import urllib
import platform_utils
import hashlib
import os
from zipfile import ZipFile
import subprocess
import stat

class AutoUpdater(object):

 def __init__(self, URL, location, bootstrapper, MD5=None, percentage_callback=None, finish_callback=None):
  """Supply a URL/location/bootstrapper filename to download a zip file from
     The finish_callback argument should be a Python function it'll call when done"""
  #Let's download the file using urllib
  self.complete = 0
  self.finish_callback = finish_callback #What to do on exit
  self.percentage_callback = percentage_callback or self.print_percentage_callback
  #Change our location to not be local -- use platform_utils
  location = os.path.join(platform_utils.paths.app_data_path('updater'), location)
  platform_utils.paths.prepare_app_data_path('updater')
  #os.chmod(platform_utils.paths.app_data_path('updater'), 777)
  #os.chmod(platform_utils.paths.app_data_path('updater'), stat.S_IRWXU)
  self.start(URL, location, bootstrapper, MD5)


 def hookProg(self, count, bSize, tSize):
  """Callback to update percentage of download"""
  percent = int(count*bSize*100/tSize)
  self.percentage_callback(percent)

 @staticmethod
 def print_percentage_callback(percent):
  print percent

 def start(self, URL, location, bootstrapper, MD5):
  """Called by __init__ to start the whole process"""
  Listy = urllib.urlretrieve(URL, location, reporthook=self.hookProg)
  if MD5:
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
  os.chmod(BootStr, stat.S_IEXEC|stat.S_IWRITE)
  print BootStr
  subprocess.call([BootStr], shell=True)
  self.complete = 1
  self.finish_callback()
