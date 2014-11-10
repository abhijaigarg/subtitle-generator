subtitle-generator
==================

Subtitle generating script for .mp4 videos.

The script takes an mp4 file as an input and is able to generate time stamp based on silent intervals of the audio.
Depending on audio quality, parameters might need to be changed.

```
THRESHOLD = 90 --> Value of threshold to measure silence
MAJORITY = 0.6 --> Silence is determined based on a majority vote over a small time interval. Depending on the quality of audio, this value needs to be changed. I currently set it to 60% 
```
Extra libaries and APIs used

```
FFMPEG
Google Speech API
```

Feel free to suggest changes
