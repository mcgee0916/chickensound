from __future__ import print_function 
from os import write
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import argparse
import imutils
import cv2
from threading import Thread
from time import sleep
import time
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

WIDTH = 1920
HEIGHT = 1080
recordVideo = True
detected = True
os.system("expert FFMPEG_BINARY='auto-detect'")



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


WAVE_OUTPUT_FILENAME = file_HM + '/original/' + 'Vac_CK_B' + localtime + '.wav'
VIDEO_OUTPUT_FILENAME = file_HM + '/video/' + 'Vac_CK_B_FILM' + localtime + '.avi'
COMBINE_OUTPUT_FILENAME = file_HM + '/combine/' + 'Vac_CK_B_VIDEO' + localtime + '.avi'
Recording = True
RECORD_SECOND = 15
_tick2_frame=0
_tick2_fps= 20000000 # real raw FPS
_tick2_t0=time.time()
def tick(fps=30):
	global _tick2_frame,_tick2_fps,_tick2_t0
	n=_tick2_fps/fps
	_tick2_frame+=n
	while n>0: n-=1
	if time.time()-_tick2_t0>1:
		_tick2_t0=time.time()
		_tick2_fps=_tick2_frame
		_tick2_frame=0
class FPS:
	def __init__(self):
		# store the start time, end time, and total number of frames
		# that were examined between the start and end intervals
		self._start = None
		self._end = None
		self._numFrames = 0

	def start(self):
		# start the timer
		self._start = datetime.now()
		return self

	def stop(self):
		# stop the timer
		self._end = datetime.now()

	def update(self):
		# increment the total number of frames examined during the
		# start and end intervals
		self._numFrames += 1

	def elapsed(self):
		# return the total number of seconds between the start and
		# end interval
		return (self._end - self._start).total_seconds()

	def fps(self):
		# compute the (approximate) frames per second
		return self._numFrames / self.elapsed()			
class WebcamVideoStream:
	def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		self.stream = cv2.VideoCapture(src)
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,HEIGHT)
		self.stream.set(cv2.CAP_PROP_FOCUS,0)
		(self.grabbed, self.frame) = self.stream.read()

		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False
	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self
	
	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()
			
			#print("read it!"+str(fps._numFrames))
	def read(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
class Audio:
	def __init__(self):
		self.p = pyaudio.PyAudio()
		info = self.p.get_host_api_info_by_index(0)
		numdevices = info.get('deviceCount')
		for i in range(0, numdevices):
			if(self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
				self.p.get_device_info_by_host_api_device_index(0, i).get('name')
		self.CHUNK = 512
		self.CHANNELS = 1
		self.FORMAT = pyaudio.paInt16
		self.RATE = 44100
		self.stream = self.p.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK)
		self.wf = wave.open(WAVE_OUTPUT_FILENAME,'wb')
		self.wf.setnchannels(self.CHANNELS)
		self.wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
		self.wf.setframerate(self.RATE)
		self.stopped = False
	def start(self):
		Thread(target = Audio, args=()).start()
		return self
	def recording(self):
		frames = []
		for i in range(0, int(self.RATE / self.CHUNK * RECORD_SECOND)):
			data = self.stream.read(self.CHUNK)
			frames.append(data)
		self.wf.close()
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()
		self.wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
		self.wf.setnchannels(self.CHANNELS)
		self.wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
		self.wf.setframerate(self.RATE)
		self.wf.writeframes(b''.join(frames))
		self.wf.close()

ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

# created a *threaded* video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from webcam...")
aviFile = cv2.VideoWriter(VIDEO_OUTPUT_FILENAME,cv2.VideoWriter_fourcc(*'XVID'),30,(WIDTH,HEIGHT))
vs = WebcamVideoStream(src=0).start()
fps = FPS().start()






#fpssecond.fps_end()
# loop over some frames...this time using the threaded stream
#while fps._numFrames < args["num_frames"]:
starttime=datetime.now()
audio = Audio().start()
while 1:
	#frame = vs.read()
	fps.update()
	aviFile.write(vs.frame)
	tick(30)
	endtime=datetime.now()
	if (endtime-starttime).seconds>= RECORD_SECOND:
        	break
#1 frame per second
# stop the timer and display FPS information
aviFile.release()
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()

sound = AudioFileClip(WAVE_OUTPUT_FILENAME,fps=44100)
film = VideoFileClip(VIDEO_OUTPUT_FILENAME)
ratio = sound.duration / film.duration
print(sound.duration,"----",film.duration,"-----",film.fps)
combine = (film.fl_time(lambda t:t/ratio,apply_to=['video']).set_end(sound.duration))
Combine = CompositeVideoClip([combine]).set_audio(sound)
Combine.write_videofile(COMBINE_OUTPUT_FILENAME,codec='libx264',fps=fps.fps())

   

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


try:
    
    ftp = FTP("140.120.101.117")
    ftp.login('PMML', 'enjoyresearch')

    ftp.cwd('07_Experimental data/NCHU_vaccine/B/original/2021_10_08')
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
  
    ftp.cwd('07_Experimental data/NCHU_vaccine/B/video/film_only/2021_10_08')
    filmfile = VIDEO_OUTPUT_FILENAME
    f = open(filmfile, 'rb')
    ftp.storbinary('STOR %s' % os.path.basename(filmfile), f)
    print("film upload successful")
except:
    print("upload film failed")
try:
  
    ftp = FTP("140.120.101.117")
    ftp.login('PMML', 'enjoyresearch')
   
    ftp.cwd('07_Experimental data/NCHU_vaccine/B/video/2021_10_08')
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
    ftp.cwd('07_Experimental data/NCHU_vaccine/B/filter/2021_10_08')
    #ftp.retrlines('LIST')
    localfile = file_HM + '/butterworthfilter/' + 'BW_' + localtime + '.wav'
    f = open(localfile, 'rb')
    ftp.storbinary('STOR %s' % os.path.basename(localfile), f)
    print("butterworth upload successful.")
except:
    print("upload filter failed")
# os.remove(COMBINE_OUTPUT_FILENAME)
# os.remove(VIDEO_OUTPUT_FILENAME)