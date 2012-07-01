#AutoUpdater
#Released under an MIT license

import logging
logger = logging.getLogger('updater')

from urllib import FancyURLopener, URLopener
import urllib2
import hashlib
import os
from platform_utils import paths
from version import Version, is_newer
try:
 from czipfile import ZipFile
except ImportError:
 from zipfile import ZipFile
import subprocess
import stat
import platform
import shutil
import json
if platform.system() == 'Windows':
 import win32api
import signing_utils

class AutoUpdater(object):

 def __init__(self, URL, save_location, bootstrapper, app_path, postexecute=None, password=None, MD5=None, percentage_callback=None, finish_callback=None, key=None, signature=None):
  """Supply a URL/location/bootstrapper filename to download a zip file from
     The finish_callback argument should be a Python function it'll call when done"""
  #Let's download the file using urllib
  self.complete = 0
  self.finish_callback = finish_callback #What to do on exit
  self.percentage_callback = percentage_callback or self.print_percentage_callback
  self.URL = URL
  self.bootstrapper = bootstrapper
  self.key = key #public key
  self.signature = signature #The signature we expect to get
  #The application path on the Mac should be 1 directory up from where the .app file is.
  tempstr = ""
  if (platform.system() == "Darwin"):
    for x in (app_path.split("/")):
      if (".app" in x):
        break
      else:
        tempstr = os.path.join(tempstr, x)
    app_path = "/" + tempstr + "/"
    #The post-execution path should include the .app file
    tempstr = ""
    for x in (postexecute.split("/")):
      if (".app" in x):
        tempstr = os.path.join(tempstr, x)
        break
      else:
        tempstr = os.path.join(tempstr, x)
    postexecute = "/" + tempstr
  self.app_path = app_path
  self.postexecute = postexecute
  logger.debug("app_path: %s"% app_path)
  logger.debug("postexecute: %s" % postexecute)
  self.password = password  
  self.MD5 = MD5
  self.save_location = save_location
  #self.save_location contains the full path, including the blabla.zip
  self.save_directory = os.path.join(*os.path.split(save_location)[:-1])
  #self.save_directory doesn't contain the blabla.zip

 def prepare_staging_directory(self):
  if not os.path.exists(self.save_directory):
   #We need to make all folders but the last one
   os.makedirs(self.save_directory)
   logger.debug("Created staging directory  %s" % self.save_directory)

 def transfer_callback(self, count, bSize, tSize):
  """Callback to update percentage of download"""
  percent = int(count*bSize*100/tSize)
  self.percentage_callback(percent)

 @staticmethod
 def print_percentage_callback(percent):
  print percent

 def start_update(self):
  """Called to start the whole process"""
  logger.debug("URL: %s   SL: %s" % (self.URL, self.save_location))
  self.prepare_staging_directory()
  Listy = CustomURLOpener().retrieve(self.URL, self.save_location, reporthook=self.transfer_callback)
  if self.MD5:
   #Check the MD5
   if self.MD5File(location) != self.MD5:
    #ReDownload
    self.start_update()
  if self.key:
   if not signing_utils.verify(self.save_location, self.key, self.signature):
    logger.critical("Signature verification failed for %s" % self.save_location)
    return
   else:
    logger.info("Signature verification succeeded for %s" % self.save_location)
  self.download_complete(Listy[0])

 def MD5File(self, filename):
  "Custom function that will get the Md5 sum of our file"
  with open(filename, 'rb') as f:
   return hashlib.md5(f).hexdigest()

 def download_complete(self, location):
  """Called when the file is done downloading, and MD5 has been successfull"""
  logger.debug("Download complete.")
  zippy = ZipFile(location, mode='r')
  extracted_path = os.path.join(self.save_directory, os.path.basename(location).strip(".zip"))
  zippy.extractall(extracted_path, pwd=self.password)
  bootstrapper_path = os.path.join(self.save_directory, self.bootstrapper) #where we will find our bootstrapper
  old_bootstrapper_path = os.path.join(extracted_path, self.bootstrapper)
  if os.path.exists(bootstrapper_path):
   os.chmod(bootstrapper_path, 666)
   os.remove(bootstrapper_path)
  shutil.move(old_bootstrapper_path, self.save_directory) #move bootstrapper
  os.chmod(bootstrapper_path, stat.S_IRUSR|stat.S_IXUSR)
  if platform.system() == "Windows": 
   bootstrapper_command = r'%s' % bootstrapper_path
   bootstrapper_args = r'"%s" "%s" "%s" "%s"' % (os.getpid(), extracted_path, self.app_path, self.postexecute)
   win32api.ShellExecute(0, 'open', bootstrapper_command, bootstrapper_args, "", 5)
  else:
   #bootstrapper_command = [r'sh "%s" -l "%s" -d "%s" "%s"' % (bootstrapper_path, self.app_path, extracted_path, str(os.getpid()))]
   bootstrapper_command = r'"%s" "%s" "%s" "%s" "%s"' % (bootstrapper_path, os.getpid(), extracted_path, self.app_path, self.postexecute)
   shell = True
   subprocess.Popen([bootstrapper_command], shell=shell)
  self.complete = 1
  if callable(self.finish_callback):
   self.finish_callback()

 def cleanup(self):
  """Delete stuff"""
  try:
   shutil.rmtree(self.save_directory)
  except:
   logger.exception("Unable to clean update directory.")

def get_update_info(URL, version):
 """Return update info for the current platform, including URL and signature. If no update is available, return an empty dict.
 Assumes Windows, Linux, or Mac"""
 info = {}
 response = urllib2.urlopen(URL)
 json_str = response.read().strip("\n")
 json_p = json.loads(json_str)
 if is_newer(version, json_p['current_version']):
  info['URL'] = json_p['downloads'][platform.system()]
  if 'signatures' in json_p and platform.system() in json_p['signatures']:
   info['signature'] = json_p['signatures'][platform.system()]
 return info

class CustomURLOpener(FancyURLopener):
 def http_error_default(*a, **k):
  return URLopener.http_error_default(*a, **k)


def check_for_update(update_endpoint, password, app_name, app_version, finish_callback=None, percentage_callback=None, key=None):
 if not paths.is_frozen():
  return
 info = get_update_info(update_endpoint, app_version)
 if info is None:
  logger.info("No update currently available.")
  return
 if (platform.system=='Windows'):
  bootstrapper ='bootstrap.exe'
 else:
  bootstrapper = 'bootstrap.sh'
 sig = info.get('signature', None)
 new_path = os.path.join(paths.app_data_path(app_name), 'updates')
 new_path = os.path.join(new_path, 'update.zip') 
 app_updater = AutoUpdater(info['URL'], new_path, bootstrapper, app_path=paths.app_path(), postexecute=paths.executable_path(), password=password, finish_callback=finish_callback, percentage_callback=percentage_callback, key=key, signature=sig)
 app_updater.start_update()
 