import wave
import threading
from os import remove, mkdir,listdir
from os.path import exists,splitext,basename,join
from datetime import datetime
from time import sleep
from shutil import rmtree
import pyaudio
import numpy
from numpy import array2string
import cv2
from moviepy.editor import *
import time
from ftplib import FTP
from ftplib import error_perm
from scipy.io import wavfile
from scipy import signal
import numpy as np
import soundfile as sf



localtime = time.strftime('%Y%m%d_%H%M', time.localtime(time.time()))
txt_time = time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time()))
#print('localtime=' + localtime)
print(txt_time)

y = time.strftime('%Y', time.localtime(time.time()))
m = time.strftime('%m', time.localtime(time.time()))
d = time.strftime('%d', time.localtime(time.time()))
HM = time.strftime('%H%M', time.localtime(time.time()))

file_y = os.getcwd() + '/' + y
file_m = file_y + '/' + m
file_d = file_m + '/' + d
file_HM = file_d + '/' + HM

if not os.path.exists(file_y):
    os.mkdir(file_y)
    os.mkdir(file_m)
    os.mkdir(file_d)
    os.mkdir(file_HM)
else:
    if not os.path.exists(file_m):
        os.mkdir(file_m)
        os.mkdir(file_d)
        os.mkdir(file_HM)
    else:
        if not os.path.exists(file_d):
            os.mkdir(file_d)
            os.mkdir(file_HM)
        else:
            if not os.path.exists(file_HM):
                os.mkdir(file_HM)

original = file_HM + '/original'
butterworthfilter = file_HM + '/butterworthfilter'
spectral_subtraction= file_HM + '/spectral_subtraction'
vad = file_HM + '/vad'
video = file_HM + '/video'
combine = file_HM + '/combine'
os.mkdir(original)
os.mkdir(butterworthfilter)
os.mkdir(spectral_subtraction)
os.mkdir(vad)
os.mkdir(video)
os.mkdir(combine)


WAVE_OUTPUT_FILENAME = file_HM + '/original/' + 'Vac_CK' + localtime + '.wav'
VIDEO_OUTPUT_FILENAME = file_HM + '/video/' + 'Vac_CK_FILM' + localtime + '.avi'
COMBINE_OUTPUT_FILENAME = file_HM + '/combine/' + 'Vac_CK_VIDEO' + localtime + '.avi'
CHUNK = 512
CHANNELS = 1 
FORMAT = pyaudio.paInt16
RATE = 44100
Recording = True
RECORD_SECOND = 15
FPS = 30
def Audio():
    p = pyaudio.PyAudio()
    print("Audio is ready")
    event.wait()
    sleep(3)
    print("Audio go!")
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    wf = wave.open(WAVE_OUTPUT_FILENAME,'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    #while Recording:
    #    data = stream.read(CHUNK)
    #    wf.writeframes(data)
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECOND)):
        data = stream.read(CHUNK)
        frames.append(data)
    wf.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
WIDTH = 640
HEIGHT = 480

def Video():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,HEIGHT)
    print("Video is ready")
    event.set()
    sleep(3)
    print("video go!")
    repeat =0
    aviFile = cv2.VideoWriter(VIDEO_OUTPUT_FILENAME,cv2.VideoWriter_fourcc(*'XVID'),FPS,(WIDTH,HEIGHT))
    print("successful capture"),
    while Recording :
        repeat +=1
        ret,frame = cap.read()
        if not ret:
            print("video failed!")
            
        aviFile.write(frame)
        if repeat>= FPS*RECORD_SECOND:
            break
    aviFile.release()
    cap.release()

now = str(datetime.now())[:19].replace(":",'_')
sleep(1)
t1 = threading.Thread(target = Audio)
t2 = threading.Thread(target = Video)
event = threading.Event()
event.clear()

for i in (t1,t2):
    i.start()
for i in (t1,t2):
    i.join()
Recording =False



sound = AudioFileClip(WAVE_OUTPUT_FILENAME)
film = VideoFileClip(VIDEO_OUTPUT_FILENAME)
ratio = sound.duration / film.duration

while(1):
    try:
        combine = (film.fl_time(lambda t:t/ratio,apply_to=['video']).set_end(sound.duration))
        Combine = CompositeVideoClip([combine]).set_audio(sound)
        Combine.write_videofile(COMBINE_OUTPUT_FILENAME,codec='libx264',fps=FPS)
        break
    except:
        pass


    

print("BW start")
sr, x = wavfile.read(WAVE_OUTPUT_FILENAME)
nyq = 0.5 * sr
b, a = signal.butter(5, [500.0 / nyq, 6000.0 / nyq], btype='band')
x = signal.lfilter(b, a, x)
x = np.float32(x)
x /= np.max(np.abs(x))
WAVE_FILTER = file_HM + '/butterworthfilter/' + 'BW_' + localtime + '.wav'
wavfile.write(WAVE_FILTER, sr, x)
y, Fs = sf.read(WAVE_FILTER)
sf.write(WAVE_FILTER, y, Fs)
print("butterworth successful.") 

try:
    
    ftp = FTP("140.120.101.117")
    ftp.login('PMML', 'enjoyresearch')

    ftp.cwd('07_Experimental data/NCHU_vaccine/C/original/2021_10_08')
    #ftp.retrlines('LIST')
    localfile = WAVE_OUTPUT_FILENAME
    f = open(localfile, 'rb')
    ftp.storbinary('STOR %s' % os.path.basename(localfile), f)
    print("wave sound upload successful")
except:
    print("upload wav failed")

try:
   
    ftp = FTP("140.120.101.117")
    ftp.login('PMML', 'enjoyresearch')
  
    ftp.cwd('07_Experimental data/NCHU_vaccine/C/video/film_only/2021_10_08')
    filmfile = VIDEO_OUTPUT_FILENAME
    f = open(filmfile, 'rb')
    ftp.storbinary('STOR %s' % os.path.basename(filmfile), f)
    print("film upload successful")
except:
    print("upload film failed")
try:
  
    ftp = FTP("140.120.101.117")
    ftp.login('PMML', 'enjoyresearch')
   
    ftp.cwd('07_Experimental data/NCHU_vaccine/C/video/2021_10_08')
    combinefile = COMBINE_OUTPUT_FILENAME
    f = open(combinefile, 'rb')
    ftp.storbinary('STOR %s' % os.path.basename(combinefile), f)
    print("video upload successful")
except:
    print("upload video failed")

try:
   
    ftp = FTP("140.120.101.117")
    ftp.login('PMML', 'enjoyresearch')
    #ftp.retrlines('LIST')
    ftp.cwd('07_Experimental data/NCHU_vaccine/C/filter/2021_10_08')
    #ftp.retrlines('LIST')
    localfile = file_HM + '/butterworthfilter/' + 'BW_' + localtime + '.wav'
    f = open(localfile, 'rb')
    ftp.storbinary('STOR %s' % os.path.basename(localfile), f)
    print("butterworth upload successful.")
except:
    print("upload filter failed")
