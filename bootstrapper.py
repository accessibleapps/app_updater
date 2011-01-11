#This is a bootstrapper
import sys
import os
import shutil

def main():
 """Our main function. Must do something like: python boostrapper.py -l MainAppLocation"""
 #-r is optional, and means the main application will be restarted
 if sys.argv[1] == "-l":
  #Our next argument will be location
  location = sys.argv[2]
 if "-r" in sys.argv:
  doLoad = True
  #This means we will start the main application when done
 else:
  doLoad = False
 print location
 #So we have our location which is where the Main Application is located
 #IE: /home/family/Desktop/updater
 dirList=os.listdir(location)
 for x in dirList:
  print "FROM: " + os.path.join(location, x) + " TO " +   os.path.join(os.getcwd(), x)
  shutil.move(os.path.join(location, x), os.path.join(os.getcwd(), x))
 

main()
