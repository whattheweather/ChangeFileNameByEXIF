import os
# import exifread
# from hachoir import (metadata, parser)
import sys, getopt

PHOTO_POSTFIX = ['.dng']
VIDEO_POSTFIX = ['.mov']

def isPhoto(postfix):
    return 1 if postfix.lower() in PHOTO_POSTFIX else 0

def isVideo(postfix):
    return 1 if postfix.lower() in VIDEO_POSTFIX else 0

def recordException(filename, info):
    with open('exception.txt', 'a') as f:
        f.write('Exception {}: {}\n'.format(info, filename))

def changePhotoName(filename, postfix):
    with open(filename, 'rb') as f:
        exif = exifread.process_file(f)

    if('Image Model' not in exif or \
        'EXIF DateTimeOriginal' not in exif):
        recordException(filename, 'no create time')
        return

    model = str(exif['Image Model'])

    if model == 'MX(35)':
        model = 'MX3'
    elif model == 'FC220':
        model = 'MavicPro'

    createTime = str(exif['EXIF DateTimeOriginal']).replace(':', '-') \
        .replace('201', '1').replace(' ', '_')

    newname = createTime + '_' + model + postfix.lower()
    
    if(os.path.exists(newname)):
        recordException(filename, 'name occupied')

    os.rename(filename, newname)

    print(filename, '->', newname)

def changeVideoName(filename):

    dji = iphone = 0
    if 'DJI' in filename:
        dji = 1
    elif 'IMG' in filename:
        iphone = 1

    fileParser = parser.createParser(filename)
    with fileParser:
        metadataDecode = metadata.extractMetadata(fileParser)
        metadataList = metadataDecode.exportPlaintext(line_prefix="")
        for i in range(len(metadataList)):
            if 'Creation date' in metadataList[i]:
                createTime = metadataList[i]
                year = createTime[15:19]
                month = createTime[20:22]
                day = int(createTime[23:25])
                hour = int(createTime[26:28])
                minute = createTime[29:31]
                second = createTime[32:34]
                if iphone:
                    hour += 8
                    if hour > 24:
                        hour -= 24
                        day += 1
                hour = str(hour).zfill(2)
                day = str(day).zfill(2)

        time = year[2:] + '-' + month + '-' + day + '_' + hour + '-' + minute + '-' + second

        if dji:
            newname = time + '_MavicPro' + postfix.lower()
        elif iphone:
            newname = time + '_iPhone6s' + postfix.lower()

    if(os.path.exists(newname)):
        recordException(filename, 'name occupied')

    os.rename(filename, newname)

    print(filename, '->', newname)

change_photo = change_video = 0
opts, args = getopt.getopt(sys.argv[1:], "pv")
for op,val in opts:
    print(op)
    if op == "-p":
        change_photo = 1
    elif op == "-v":
        change_video = 1

if not change_photo + change_video:
    print('No file type specified, use -v for videos and -p for photos')

for parent, dirnames, filenames in os.walk('.'):
    for filename in filenames:
        if len(filename) < 5:
            continue
        postfix = filename[-4:]
        if change_photo and isPhoto(postfix):
            changePhotoName(filename, postfix)
        if change_video and isVideo(postfix):
            changeVideoName(filename, postfix)
