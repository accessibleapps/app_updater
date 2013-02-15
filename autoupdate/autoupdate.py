from logging import getLogger
logger = getLogger('autoupdate')

import contextlib
import io
import os
import platform
import requests
import tempfile
try:
 import czipfile as zipfile
except ImportError:
 import zipfile

from platform_utils import paths

def perform_update(endpoint, current_version, password=None, update_available_callback=None, progress_callback=None, update_complete_callback=None):
 available_update = find_update(endpoint, current_version)
 if not available_update:
  return
 if callable(update_available_callback) and not update_available_callback(): #update_available_callback should return a falsy value to stop the process
  logger.info("User canceled update.")
  return
 base_path = tempfile.mkdtemp()
 download_path = os.path.join(base_path, 'update.zip')
 update_path = os.path.join(base_path, 'update')
 downloaded = download_update(available_update, download_path, progress_callback=progress_callback)
 extracted = extract_update(downloaded, update_path, password=password)
 bootstrap_path = move_bootstrap(extracted)
 execute_bootstrap(bootstrap_path, extracted)
 logger.info("Update prepared for installation.")
 if callable(update_complete_callback):
  update_complete_callback()

def find_update(endpoint, version):
 response = requests.get(endpoint)
 response.raise_for_status()
 content = response.json()
 if str(content['current_version']) > str(version) and platform.system() in content['downloads']:
  logger.info("A new update is available. Version %s" % content['current_version'])
  return content['downloads'].get(platform.system())

def download_update(update_url, update_destination, progress_callback=None, chunk_size=io.DEFAULT_BUFFER_SIZE):
 total_downloaded = total_size = 0
 with io.open(update_destination, 'w+b') as outfile:
  download = requests.get(update_url, stream=True)
  total_size = int(download.headers.get('content-length', 0))
  logger.debug("Total update size: %d" % total_size)
  download.raise_for_status()
  for chunk in download.iter_content(chunk_size):
   outfile.write(chunk)
   total_downloaded += len(chunk)
   if callable(progress_callback):
    call_callback(progress_callback, total_downloaded, total_size)
 logger.debug("Update downloaded")
 return update_destination

def extract_update(update_archive, destination, password=None):
 """Given an update archive, extracts it. Returns the directory to which it has been extracted"""
 with contextlib.closing(zipfile.ZipFile(update_archive)) as archive:
  if password:
   archive.setpassword(password)
  archive.extractall(path=destination)
 logger.debug("Update extracted")
 return destination

def move_bootstrap(extracted_path):
 working_path = os.path.abspath(os.path.join(extracted_path, '..'))
 if platform.system() == 'Darwin':
  extracted_path = os.path.join(extracted_path, 'Contents', 'Resources')
 downloaded_bootstrap = os.path.join(extracted_path, bootstrap_name())
 new_bootstrap_path = os.path.join(working_path, bootstrap_name())
 os.rename(downloaded_bootstrap, new_bootstrap_path)
 return new_bootstrap_path

def execute_bootstrap(bootstrap_path, source_path):
 command = r'"%s" "%s" "%s" "%s"' % (os.getpid(), source_path, paths.app_path(), paths.executable_path())
 if platform.system() == 'Windows':
  import win32api
  win32api.ShellExecute(0, 'open', bootstrap_path, command, "", 5)
 else:  
  subprocess.Popen(['%s %s' % (bootstrap_path, command)], shell=True)
 logger.info("Bootstrap executed")

def bootstrap_name():
 if platform.system() == 'Windows': return 'bootstrap.exe'
 if platform.system() == 'Darwin': return 'bootstrap-mac.sh'
 return 'bootstrap-lin.sh'

def call_callback(callback, *args, **kwargs):
 try:
  callback(*args, **kwargs)
 except:
  logger.exception("Failed calling callback %r with args %r and kwargs %r" % (callback, args, kwargs))
