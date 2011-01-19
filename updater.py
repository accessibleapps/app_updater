#AutoUpdater
#Released under a GNU GPL
import urllib
import urllib2
import platform_utils
import hashlib
import os
from zipfile import ZipFile
import subprocess
import stat
import platform
import shutil
import json

class AutoUpdater(object):

 def __init__(self, URL, save_location, bootstrapper, MD5=None, percentage_callback=None, finish_callback=None):
  """Supply a URL/location/bootstrapper filename to download a zip file from
     The finish_callback argument should be a Python function it'll call when done"""
  #Let's download the file using urllib
  self.complete = 0
  self.finish_callback = finish_callback #What to do on exit
  self.percentage_callback = percentage_callback or self.print_percentage_callback
  self.URL = URL
  self.bootstrapper = bootstrapper
  self.MD5 = MD5
  #Change our location to not be local -- use platform_utils
  self.save_location = os.path.join(platform_utils.paths.app_data_path('updater'), save_location)
  platform_utils.paths.prepare_app_data_path('updater')


 def hookProg(self, count, bSize, tSize):
  """Callback to update percentage of download"""
  percent = int(count*bSize*100/tSize)
  self.percentage_callback(percent)

 @staticmethod
 def print_percentage_callback(percent):
  print percent

 def start_update(self):
  """Called to start the whole process"""
  Listy = urllib.urlretrieve(self.URL, self.save_location, reporthook=self.hookProg)
  if self.MD5:
   #Check the MD5
   if self.MD5File(location) != self.MD5:
    #ReDownload
    print "MD5 HASH FAIL -- RETRY DOWNLOAD"
    self.start_update()
   else:
    #It redownloaded properly
    self.download_complete(Listy[0])
  else:
   #We don't know if it downloaded properly
   #The programmer didn't give us an MD5. So we have to assume it was valid.
   self.download_complete(Listy[0])

 def MD5File(self, fileName):
  "Custom function that will get the Md5 sum of our file"
  file_reference=open(fileName, 'rb').read() 
  return hashlib.md5(file_reference).hexdigest()

 def download_complete(self, location):
  """Called when the file is done downloading, and MD5 has been successfull"""
  CurD = os.getcwd() #Store our current working directory (of main app)
  print location
  zippy = ZipFile(location, 'r')
  Pathy = os.path.join(platform_utils.paths.app_data_path('updater'), os.path.basename(location).strip(".zip"))
  zippy.extractall(Pathy)
  BootStr = os.path.join(platform_utils.paths.app_data_path('updater'), self.bootstrapper) #where we will find out bootstrapper
  shutil.move(os.path.join(Pathy, self.bootstrapper), platform_utils.paths.app_data_path('updater')) #move bootstrapper
  os.chmod(BootStr, stat.S_IRUSR|stat.S_IXUSR)
  print "BOOTSTR " +  BootStr
  # if platform.system() == "Linux" or 1==1:
  print '"%s" -l "%s" -d "%s"' % (BootStr, CurD, os.path.basename(location).strip(".zip"))
  #subprocess.call(['python "%s" -l "%s"' % (BootStr, Pathy)], shell=True) 
  ##subprocess.check_call(['"%s" -l "%s" -d "%s"' % (BootStr, CurD, os.path.basename(location).strip(".zip"))], shell=True)
  if platform.system() == "Windows": 
    subprocess.Popen(r'"%s" -l "%s" -d "%s"' % (BootStr, CurD, os.path.basename(location).strip(".zip")))
  else:
    print r'sh "%s" -l "%s" -d "%s"' % (BootStr, CurD, os.path.basename(location).strip(".zip"))
    subprocess.call([r'sh "%s" -l "%s" -d "%s"' % (BootStr, CurD, os.path.basename(location).strip(".zip"))], shell=True)
  # subprocess.call([BootStr + " -l " + Pathy], shell=True)
  self.complete = 1
  self.finish_callback()

def check_update(URL, cversion):
  """Return a URL to an update of the application for the current platform at the given URL if one exists, or None""
     Assumes Windows, Linux, or Mac"""
  response = urllib2.urlopen(URL)
  jsonStr = response.read().strip("\n")
  print str(jsonStr)
  print json.loads(jsonStr)
  jsonP = json.loads(jsonStr)
  if jsonP['current_version'] > cversion:
    return jsonP['downloads'][platform.system()]
  else:
   return None
