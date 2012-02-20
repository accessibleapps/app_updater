from setuptools import setup, find_packages
from glob import glob

__version__ = 0.02

setup(
 name = 'autoupdate',
 version = __version__,
 description = 'Autoupdate of end-user binaries on Windows, Linux and OSX',
 package_dir = {'autoupdate': 'autoupdate'},
 packages = find_packages(),
 package_data = {'autoupdate': [
  'bootstrappers/*',
 ]},
 install_requires = [
  'platform_utils',
 ],
 classifiers = [
  'Development Status :: 4 - Beta',
  'Intended Audience :: Developers',
  'Programming Language :: Python',
  'License :: OSI Approved :: MIT License',
  'Topic :: Software Development :: Libraries'
 ],
)
