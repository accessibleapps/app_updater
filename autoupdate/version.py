from functools import total_ordering

@total_ordering
class Version(object):
 VERSION_QUALIFIERS = {
  'alpha': 1,
  'beta': 2,
  'rc': 3
 }

 def __init__(self, version):
  self.version = version
  self.version_qualifier = None
  self.version_qualifier_num = None
  self.sub_version = None
  if isinstance(version, basestring):
   version = version.lower()
   if '-' not in version:
    for q in self.VERSION_QUALIFIERS:
     if q in version:
      self.version_qualifier = q
      self.version_qualifier_num = self.VERSION_QUALIFIERS[q]
      split_version = version.split(q)
      self.version_number = float(split_version[0])
      if len(split_version) > 1:
       self.sub_version = split_version[1]
      return
    self.version_number= float(version)
    return
   split_version = version.split('-')
   self.version_number= float(split_version[0])
   self.version_qualifier = split_version [1]
   self.version_qualifier_num = self.VERSION_QUALIFIERS[self.version_qualifier]
   if len(split_version) == 3:
    self.sub_version = int(split_version[2])
  else:
   self.version_number= float(version)

 def __lt__(self, other):
  if not isinstance(other, self.__class__):
   other = Version(other)
  if other.version_qualifier == self.version_qualifier == None:
   return self.version_number< other.version_number
  if self.version_number < other.version_number:
   return True
  elif self.version_number > other.version_number:
   return False
  if other.version_number == self.version_number and not other.version_qualifier_num and self.version_qualifier_num:
   return True
  if other.version_number == self.version_number and self.version_qualifier_num == self.version_qualifier_num and self.sub_version < other.sub_version:
   return True
  return self.version_qualifier_num < other.version_qualifier_num

 def __gt__(self, other):
  if not isinstance(other, self.__class__):
   other = Version(other)
  if other.version_qualifier == self.version_qualifier == None:
   return self.version_number > other.version_number
  if self.version_number < other.version_number:
   return False
  elif self.version_number > other.version_number:
   return True
  if other.version_number == self.version_number and not other.version_qualifier_num and self.version_qualifier_num:
   return False
  if other.version_number == self.version_number and self.version_qualifier_num == self.version_qualifier_num and self.sub_version > other.sub_version:
   return True
  return self.version_qualifier_num > other.version_qualifier_num

def is_newer(local_version, remote_version):
 """Returns True if the remote version is newer than the local version."""
 return Version(remote_version) > local_version
