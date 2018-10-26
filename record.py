from sys import byteorder
from array import array
from struct import pack

import numpy as np
import matplotlib.pyplot as plt

from scipy.signal import freqz, butter, lfilter #for bandpass filtering

import pyaudio
import wave

THRESHOLD = 4000 #500 is too low for the office 5000 is with a room with some basic bacground noise
CUTOFF_LOW = 8000
CUTOFF_HIGH = 20000
CHUNK_SIZE = 1024 
FORMAT = pyaudio.paInt16 #format = 8
print("FORMAT: ", type(FORMAT))
RATE = 44100

def is_silent(snd_data):
	"Returns 'True' if below the 'silent' threshold"
	return max(snd_data) < THRESHOLD



def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
	nyq = 0.5 * fs
	low = lowcut / nyq
	high = highcut / nyq
	b, a = butter(order, [low, high], btype='band')
	y = lfilter(b, a, data)
	return y


def normalize(snd_data):
	"Average the volume out"
	MAXIMUM = 16384
	times = float(MAXIMUM)/max(abs(i) for i in snd_data)

	r = array('h')
	for i in snd_data:
		r.append(int(i*times))
	return r

def trim(snd_data):
	"Trim the blank spots at the start and end"
	def _trim(snd_data):
		snd_started = False
		r = array('h')

		for i in snd_data:
			if not snd_started and abs(i)>THRESHOLD:
				snd_started = True
				r.append(i)

			elif snd_started:
				r.append(i)
		return r

	# Trim to the left
	snd_data = _trim(snd_data)

	# Trim to the right
	snd_data.reverse()
	snd_data = _trim(snd_data)
	snd_data.reverse()
	return snd_data

def add_silence(snd_data, seconds):
	"Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
	r = array('h', [0 for i in range(int(seconds*RATE))])
	r.extend(snd_data)
	r.extend([0 for i in range(int(seconds*RATE))])
	return r

def record():
	"""
	Record from the microphone for some time and
	return the data as an array of signed shorts.

	Normalizes the audio, bandpass filters the sound, 
	trims silence from the start and end, and pads with 0.5 seconds of 
	blank sound to make sure VLC et al can play 
	it without getting chopped off.
	"""
	p = pyaudio.PyAudio() #create stream
	stream = p.open(format=FORMAT, channels=1, rate=RATE,
		input=True, output=True,
		frames_per_buffer=CHUNK_SIZE) #open stream

	#init vars
	num_silent = 0 
	snd_started = False

	#init recording array
	r = array('h')

	while 1:  #Loop until break
		# little endian, signed short
		snd_data = array('h', stream.read(CHUNK_SIZE))
		if byteorder == 'big':
			snd_data.byteswap()
		r.extend(snd_data) #this appends to the r array of recorded audio

		silent = is_silent(snd_data)

		if silent and snd_started:
			num_silent += 1
		elif not silent and not snd_started:
			#start recording?
			snd_started = True

		if snd_started and num_silent > 30:
			break

	sample_width = p.get_sample_size(FORMAT)
	stream.stop_stream()
	stream.close()
	p.terminate()

	
	r = normalize(r)
	x = np.arange(len(r))
	fig = plt.figure(0)
	plt.plot(x,r)#,label='Noisy signal')
	# plt.show()
	print("type:", type(r))
	r = butter_bandpass_filter(r,CUTOFF_LOW,CUTOFF_HIGH,RATE,9)
	
	plt.plot(x,r) #,label='Filtered signal')	
	r = np.asarray(r, dtype="int")
	print("type:", type(r))
	plt.show()
	
	#r = trim(r)
	#r = add_silence(r, 0.5)
	return sample_width, r

def record_to_file(path):
	"Records from the microphone and outputs the resulting data to 'path'"
	sample_width, data = record()
	data = pack('<' + ('h'*len(data)), *data)

	wf = wave.open(path, 'wb')
	wf.setnchannels(1)
	wf.setsampwidth(sample_width)
	wf.setframerate(RATE)
	wf.writeframes(data)
	wf.close()

if __name__ == '__main__':
	print("please speak a word into the microphone")
	record_to_file('demo.wav')
	print("done - result written to demo.wav")