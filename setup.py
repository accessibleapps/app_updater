from setuptools import setup, find_packages

__version__ = 0.23

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
  'requests',
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
