import time
import RPi.GPIO as io
from firebase import Firebase

svy_coordinates_smu = (29807.414688111774, 31137.837192226452)
lat_lng_coordinates_smu = (1.297874, 103.849559)

f = Firebase('https://rum.firebaseio.com/events')

io.setmode(io.BCM)

pir_pin = 18

io.setup(pir_pin, io.IN)

while True:
  if io.input(pir_pin):
    print("1")
    timestamp = time.time()
    dict_firebase = {'easting': svy_coordinates_smu[0], 'northing': svy_coordinates_smu[1], 'lat': lat_lng_coordinates_smu[0], 'lng': lat_lng_coordinates_smu[1], 'time': timestamp, ".priority": timestamp, 'type': 'motion'}
    r = f.push(dict_firebase)
    print dict_firebase
    print r
  else:
    print("0")
  time.sleep(0.5)
  
