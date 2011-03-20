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
  self.save_location = save_location
  #self.save_location contains the full path, including the blabla.zip
  if platform.system() == "Windows":
      backSlash = "\"
  else:
      backSlash = "/"
  save_location = save_location.split(backSlash)
  save_location.pop()
  save_location = str(backSlash.join(save_location))
  self.save_location_nofile = save_location
  #self.save_location_nofile doesn't contain the blabla.zip
  if not os.path.exists(self.save_location):
   #We need to make all folders but the last one
   os.makedirs(self.save_location_nofile)

 def transfer_callback(self, count, bSize, tSize):
  """Callback to update percentage of download"""
  percent = int(count*bSize*100/tSize)
  self.percentage_callback(percent)

 @staticmethod
 def print_percentage_callback(percent):
  print percent

 def start_update(self):
  """Called to start the whole process"""
  print "URL: " + self.URL + "   SL:  " + self.save_location
  Listy = urllib.urlretrieve(self.URL, self.save_location, reporthook=self.transfer_callback)
  if self.MD5:
   #Check the MD5
   if self.MD5File(location) != self.MD5:
    #ReDownload
    self.start_update()
  self.download_complete(Listy[0])

 def MD5File(self, fileName):
  "Custom function that will get the Md5 sum of our file"
  file_reference=open(fileName, 'rb').read() 
  return hashlib.md5(file_reference).hexdigest()

 def download_complete(self, location):
  """Called when the file is done downloading, and MD5 has been successfull"""
  CurD = os.getcwd() #Store our current working directory (of main app)
  print "DOWNLOAD COMPLETE: " + str(location)
  zippy = ZipFile(location, 'r')
  Pathy = os.path.join(self.save_location_nofile, os.path.basename(location).strip(".zip"))
  zippy.extractall(Pathy)
  BootStr = os.path.join(self.save_location_nofile, self.bootstrapper) #where we will find our bootstrapper
  shutil.move(os.path.join(Pathy, self.bootstrapper), self.save_location_nofile) #move bootstrapper
  os.chmod(BootStr, stat.S_IRUSR|stat.S_IXUSR)
  if platform.system() == "Windows": 
    subprocess.Popen(r'"%s" -l "%s" -d "%s" "%s"' % (BootStr, CurD, os.path.basename(location).strip(".zip"), str(os.getpid())))
  else:
    subprocess.Popen([r'sh "%s" -l "%s" -d "%s" "%s"' % (BootStr, CurD, os.path.basename(location).strip(".zip"), str(os.getpid()))], shell=True)
  self.complete = 1
  if callable(self.finish_callback):
   self.finish_callback()

 def cleanup(self):
  """Delete stuff"""
  try:
   shutil.rmtree(self.save_location_nofile)
  except any:
   return

def find_update_url(URL, version):
  """Return a URL to an update of the application for the current platform at the given URL if one exists, or None""
     Assumes Windows, Linux, or Mac"""
  response = urllib2.urlopen(URL)
  json_str = response.read().strip("\n")
  json_p = json.loads(json_str)
  if json_p['current_version'] > version:
    return json_p['downloads'][platform.system()]


