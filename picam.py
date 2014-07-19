#!/usr/bin/python

# original script by brainflakes, improved by pageauc, peewee2 and Kesthal
# www.raspberrypi.org/phpBB3/viewtopic.php?f=43&t=45235

# You need to install PIL to run this script
# type "sudo apt-get install python-imaging-tk" in an terminal window to do this

import StringIO
import subprocess
import os
import time
from datetime import datetime
from PIL import Image
import dropbox
#from firebase import firebase
from firebase import Firebase

#firebase = firebase.FirebaseApplication('https://rum.firebaseio.com', None)
f = Firebase('https://rum.firebaseio.com/events')

#new_event = 

svy_coordinates_smu = (29807.414688111774, 31137.837192226452)

#app_key = 'bogm2ug139bpntr'
#app_secret = 'ikd7q5kf52dizi7'
#flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

#access_token = None

#TOKENS = 'dropbox_token.txt'
#if os.path.isfile(TOKENS):
#    global access_token
#    token_file = open(TOKENS)
    #token_key, token_secret  = token_file.read().split('|')
#    access_token = token_file.read()
#    token_file.close()
#else:
#    global access_token
#    authorize_url = flow.start()
#    print '1. Go to: ' + authorize_url
#    print '2. Click "Allow" (you might have tio log in first'
#    print '3. Copy the authorization code.'
#    code = raw_input("Enter the authorization code here: ").strip()
#    access_token, user_id = flow.finish(code)
#    token_file = open(TOKENS, 'w')
    #token_file.write("%s|%s" % (access_token.key, access_token.secret) )
#    token_file.write("%s" % (access_token) )
#    token_file.close()

#print "Access Token Key = " + access_token.key
#print "Access Token Secret = " + access_token.secret

#print "Access Token = " + access_token

#client = dropbox.client.DropboxClient(access_token)
#print 'linked account: ', client.account_info()

# Motion detection settings:
# Threshold          - how much a pixel has to change by to be marked as "changed"
# Sensitivity        - how many changed pixels before capturing an image, needs to be higher if noisy view
# ForceCapture       - whether to force an image to be captured every forceCaptureTime seconds, values True or False
# filepath           - location of folder to save photos
# filenamePrefix     - string that prefixes the file name for easier identification of files.
# diskSpaceToReserve - Delete oldest images to avoid filling disk. How much byte to keep free on disk.
# cameraSettings     - "" = no extra settings; "-hf" = Set horizontal flip of image; "-vf" = Set vertical flip; "-hf -vf" = both horizontal and vertical flip
#threshold = 10
threshold = 10
#sensitivity = 20
sensitivity = 100
forceCapture = True
forceCaptureTime = 60 * 60 # Once an hour
filepath = "/home/pi/picam"
filenamePrefix = "capture"
diskSpaceToReserve = 40 * 1024 * 1024 # Keep 40 mb free on disk
cameraSettings = ""

# settings of the photos to save
#saveWidth   = 1296
#saveHeight  = 972
#saveQuality = 15 # Set jpeg quality (0 to 100)
saveWidth   = 400
saveHeight  = 300
saveQuality = 10 # Set jpeg quality (0 to 100)


# Test-Image settings
#testWidth = 100
#testHeight = 75
testWidth = 50
testHeight = 38

# this is the default setting, if the whole image should be scanned for changed pixel
testAreaCount = 1
testBorders = [ [[1,testWidth],[1,testHeight]] ]  # [ [[start pixel on left side,end pixel on right side],[start pixel on top side,stop pixel on bottom side]] ]
# testBorders are NOT zero-based, the first pixel is 1 and the last pixel is testWith or testHeight

# with "testBorders", you can define areas, where the script should scan for changed pixel
# for example, if your picture looks like this:
#
#     ....XXXX
#     ........
#     ........
#
# "." is a street or a house, "X" are trees which move arround like crazy when the wind is blowing
# because of the wind in the trees, there will be taken photos all the time. to prevent this, your setting might look like this:

# testAreaCount = 2
# testBorders = [ [[1,50],[1,75]], [[51,100],[26,75]] ] # area y=1 to 25 not scanned in x=51 to 100

# even more complex example
# testAreaCount = 4
# testBorders = [ [[1,39],[1,75]], [[40,67],[43,75]], [[68,85],[48,75]], [[86,100],[41,75]] ]

# in debug mode, a file debug.bmp is written to disk with marked changed pixel an with marked border of scan-area
# debug mode should only be turned on while testing the parameters above
debugMode = True # False or True

# Capture a small test image (for motion detection)
def captureTestImage(settings, width, height):
    command = "raspistill %s -w %s -h %s -t 200 -e bmp -n -o -" % (settings, width, height)
    imageData = StringIO.StringIO()
    imageData.write(subprocess.check_output(command, shell=True))
    imageData.seek(0)
    im = Image.open(imageData)
    buffer = im.load()
    imageData.close()
    return im, buffer

# Save a full size image to disk
def saveImage(settings, width, height, quality, diskSpaceToReserve):
    keepDiskSpaceFree(diskSpaceToReserve)
    time = datetime.now()
    filename = filepath + "/" + filenamePrefix + "-%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    subprocess.call("raspistill %s -w %s -h %s -t 200 -e jpg -q %s -n -o %s" % (settings, width, height, quality, filename), shell=True)
    print "Captured %s" % filename
    #f = open(filename, 'rb')
    #response = client.put_file(filenamePrefix + "-%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second), f)
    #print "uploaded:", response
    #photofile = "/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload " + filename + " " + filenamePrefix + "-%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    #subprocess.call([photofile], shell=True)

# Keep free space above given level
def keepDiskSpaceFree(bytesToReserve):
    if (getFreeSpace() < bytesToReserve):
        for filename in sorted(os.listdir(filepath + "/")):
            if filename.startswith(filenamePrefix) and filename.endswith(".jpg"):
                os.remove(filepath + "/" + filename)
                print "Deleted %s/%s to avoid filling disk" % (filepath,filename)
                if (getFreeSpace() > bytesToReserve):
                    return

# Get available disk space
def getFreeSpace():
    st = os.statvfs(filepath + "/")
    du = st.f_bavail * st.f_frsize
    return du

# Get first image
print "Started capturing first image"
image1, buffer1 = captureTestImage(cameraSettings, testWidth, testHeight)

# Reset last capture time
lastCapture = time.time()

while (True):

    # Get comparison image
    image2, buffer2 = captureTestImage(cameraSettings, testWidth, testHeight)

    # Count changed pixels
    changedPixels = 0
    takePicture = False

    if (debugMode): # in debug mode, save a bitmap-file with marked changed pixels and with visible testarea-borders
        debugimage = Image.new("RGB",(testWidth, testHeight))
        debugim = debugimage.load()

    for z in xrange(0, testAreaCount): # = xrange(0,1) with default-values = z will only have the value of 0 = only one scan-area = whole picture
        for x in xrange(testBorders[z][0][0]-1, testBorders[z][0][1]): # = xrange(0,100) with default-values
            for y in xrange(testBorders[z][1][0]-1, testBorders[z][1][1]):   # = xrange(0,75) with default-values; testBorders are NOT zero-based, buffer1[x,y] are zero-based (0,0 is top left of image, testWidth-1,testHeight-1 is botton right)
                if (debugMode):
                    debugim[x,y] = buffer2[x,y]
                    if ((x == testBorders[z][0][0]-1) or (x == testBorders[z][0][1]-1) or (y == testBorders[z][1][0]-1) or (y == testBorders[z][1][1]-1)):
                        # print "Border %s %s" % (x,y)
                        debugim[x,y] = (0, 0, 255) # in debug mode, mark all border pixel to blue
                # Just check green channel as it's the highest quality channel
                pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                if pixdiff > threshold:
                    changedPixels += 1
                    if (debugMode):
                        debugim[x,y] = (0, 255, 0) # in debug mode, mark all changed pixel to green
                # Save an image if pixels changed
                if (changedPixels > sensitivity):
                    takePicture = True # will shoot the photo later
                if ((debugMode == False) and (changedPixels > sensitivity)):
                    break  # break the y loop
            if ((debugMode == False) and (changedPixels > sensitivity)):
                break  # break the x loop
        if ((debugMode == False) and (changedPixels > sensitivity)):
            break  # break the z loop

    if (debugMode):
        debugimage.save(filepath + "/debug.bmp") # save debug image as bmp
        print "debug.bmp saved, %s changed pixel" % changedPixels
    # else:
    #     print "%s changed pixel" % changedPixels

    # Check force capture
    if forceCapture:
        if time.time() - lastCapture > forceCaptureTime:
            takePicture = True

    if takePicture:
        lastCapture = time.time()
        saveImage(cameraSettings, saveWidth, saveHeight, saveQuality, diskSpaceToReserve)

    # Swap comparison buffers
    image1 = image2
    buffer1 = buffer2
