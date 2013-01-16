import platform
from glob import glob
from os.path import abspath, join

def find_datafiles():
 import autoupdate
 system = platform.system()
 if system == 'Windows':
  file_ext = '*.exe'
 else:
  file_ext = '*.sh'
 path = abspath(join(autoupdate.__path__[0], 'bootstrappers', file_ext))
 return [('', glob(path))]
