
from dirtools import Dir, DirState
import time
import ftplib
import os
from firebase import Firebase
import re
import time
import datetime
import collections
#import threading

#q = collections.deque()

svy_coordinates_smu = (29807.414688111774, 31137.837192226452)

f = Firebase('https://rum.firebaseio.com/events')

session = ftplib.FTP('128.199.139.46', 'uploader', 'rum123NUS', timeout=20)

directory_location = '/home/pi/picam'
d = Dir(directory_location, exclude_file='exclude.txt')
dir_state = DirState(d)

def extract_time_stamp_from_file_name(file_name):
  print "I am here"
  p = re.compile(ur'capture-([0-9][0-9][0-9][0-9])([0-9][0-9])([0-9][0-9])-([0-9][0-9])([0-9][0-9])([0-9][0-9]).jpg')
  groups = re.match(p, file_name).groups()
  year = int(groups[0])
  month = int(groups[1])
  day = int(groups[2])
  hour = int(groups[3])
  minute = int(groups[4])
  second = int(groups[5])
  dt = datetime.datetime(year, month, day, hour, minute, second)
  return time.mktime(dt.timetuple())

#def timeout():
#  session.abort()
#  session.close()
#  print "Quitting session"
  
#timerthread = [threading.Timer(5, timeout)]

#def callback(data, *args, **kwargs):
#  if timerthread[0] is not None:
#    timerthread[0].cancel()
#  timer_thread[0]  = threading.Timer(5, timeout)
#  timerthread[0].start()

while(True):
  #time.sleep(3)
  dir_state2 = DirState(d)
  changes = dir_state2 - dir_state
  for i  in range(0, len( changes['created'])):
    print changes['created']  
    created_file = changes['created'][i]
    file_path = directory_location + '/' + created_file
    if file_path.endswith('~'):
      continue
    file = open(file_path, 'rb')
    command = 'STOR /website/camera_photos/' + created_file
    print command
    # timerthread[0].start()
    try:
      session.storbinary(command, file)
    except Exception:
        print i
        i = i - 1
        print i
        print "Timeout occured"
        file.close()
    else:
      timestamp =  extract_time_stamp_from_file_name(created_file)
      dict_firebase = {'easting': svy_coordinates_smu[0], 'lat': 1.297874, 'lng': 103.849559, 'northing': svy_coordinates_smu[1], 'time': timestamp, ".priority": timestamp, 'type': 'camera', 'image-url': 'http://128.199.139.46/camera_photos/' + created_file}
      r = f.push(dict_firebase)
      print r
      os.remove(file_path)
      file.close()
  dir_state = dir_state2
session.quit()
