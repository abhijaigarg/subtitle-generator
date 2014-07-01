import pyaudio
import wave
import os
import urllib2
import urllib
import time
import math

#TOTAL DURATION OF AUDIO FILE
TOTAL_DURATION = 0


# GOOGLE SPEECH TO TEXT CONVERTER
LANG_CODE = 'en-US'  # Language to use

GOOGLE_SPEECH_URL = 'https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&pfilter=2&lang=%s&maxresults=6' % (LANG_CODE)

def stt_google_wav(audio_fname):
    """ Sends audio file (audio_fname) to Google's text to speech 
        service and returns service's response. We need a FLAC 
        converter if audio is not FLAC (check FLAC_CONV). """
        
    print "Sending ", audio_fname
    #Convert to flac first
    filename = audio_fname
    del_flac = False
    if 'flac' not in filename:
        del_flac = True
        print "Converting to flac"
        print FLAC_CONV + filename
        os.system(FLAC_CONV + ' ' + filename)
        filename = filename.split('.')[0] + '.flac'

    f = open(filename, 'rb')
    flac_cont = f.read()
    f.close()

    # Headers. A common Chromium (Linux) User-Agent
    hrs = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7", 
           'Content-type': 'audio/x-flac; rate=16000'}  

    req = urllib2.Request(GOOGLE_SPEECH_URL, data=flac_cont, headers=hrs)
    print "Sending request to Google TTS"
    #print "response", response
    try:
        p = urllib2.urlopen(req)
        response = p.read()
        res = eval(response)['hypotheses']
    except:
        print "Couldn't parse service response"
        res = None

    if del_flac:
        os.remove(filename)  # Remove temp file

    return res
#--------------------------------------------------------------------------#


def convert_to_mins(sec):
	
	secs = sec%60
	mins = sec/60
	hours = mins/60
	mins = mins%60

	if hours<10:
		hours = str(0)+str(hours)
	if mins<10:
		mins = str(0)+str(mins)
	if secs<10:
		secs = str(0)+str(secs)

	return str(hours)+":"+str(mins)+":"+str(secs)

def coalesce_silences(silence):
	pos_to_delete = []
	for i in range(len(silence)-1):
		if(silence[i]==silence[i+1]):
			pos_to_delete.append(i)
	
	#reverse list
	pos_to_delete = pos_to_delete[::-1]
	
	for i in pos_to_delete:
		silence.pop(i)
	return silence

def get_speech_timestamp_in_seconds(silence):
	speech_mins = []
	speech_sec = []
	temp1 = ""
	temp2 = ""
	for i in range(len(silence)-1):
		temp1 = str(convert_to_mins(silence[i])) + " --> " + str(convert_to_mins(silence[i+1]))
		temp2 = str(silence[i]) + " --> " + str(silence[i+1])
		speech_mins.append(temp1)
		speech_sec.append(temp2)
	return speech_mins,speech_sec

def write_srt_file(speech_mins,speech_sec):
	f = open('sub.srt', 'a')
	write_chunk = ""
	for i in range(len(speech_mins)):
		string = split_audio_file(speech_sec[i])
		print string
		
		if not string:
			write_chunk = str(i+1) + "\n" + str(speech_mins[i]) + "\n\n"
		elif string:
			write_chunk = str(i+1) + "\n" + str(speech_mins[i]) + "\n" + str(string[0]['utterance']) + "\n\n"

		f.write(write_chunk)
	f.close()

def timestamping():
	print "Calculating time stamps based on silence intervals\n"
	w = wave.open('audio.wav','r')
	frame = True
	start = 0
	THRESHOLD = 90
	MAJORITY = 0.6
	CHUNK = int(math.floor(w.getframerate()/3))
	num_of_chunks = 0
	silence = []
	fi = 1
	count = 1
	while frame:
		frame = w.readframes(CHUNK)
		flag = True
		count = 0
		for i in range(len(frame)):
			if ord(frame[i])<THRESHOLD:
				count+=1
		num_of_chunks+=1
		#print count, w.getframerate()
		if (float(count)/w.getframerate()) > MAJORITY:
			silence.append((w.tell()-CHUNK)/w.getframerate())
	TOTAL_DURATION = float(num_of_chunks)/3
	silence.append(int(TOTAL_DURATION))
	silence = coalesce_silences(silence)
	speech_mins,speech_sec = get_speech_timestamp_in_seconds(silence)
	print speech_mins, speech_sec
	#write_srt_file(speech_mins,speech_sec)
	
def split_audio_file(time):
	time = time.split()
	if time[0]<1:
		startTime = str(time[0])
		duration = str(int(time[2]) - int(time[0]) + 1)
	elif(time[2]>=TOTAL_DURATION-1):
		startTime = str(int(time[0])-1)
		duration = str(int(time[2]) - int(time[0]))
	else:
		startTime = str(int(time[0])-1)
		duration = str(int(time[2]) - int(time[0]) + 1)
	command = "ffmpeg -ss " + startTime + " -t " + duration + " -i audio.mp3 -vn -ac 1 -ar 16000 -acodec flac convert.flac"
	os.system(command)
	string =  stt_google_wav('convert.flac')
	command = "rm convert.flac"
	os.system(command)
	return string

timestamping()