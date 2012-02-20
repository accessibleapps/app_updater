from glob import glob
from os.path import abspath, join

def py2exe_datafiles():
 import autoupdate
 path = abspath(join(autoupdate.__path__[0], 'bootstrappers', '*.exe'))
 return [('', glob(path))]
