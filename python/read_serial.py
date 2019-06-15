import re, argparse
import serial
from foot import Foot
import sounddevice as sd
import librosa
import time as Time
import queue
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
import random
#import pandas

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


def left_right_sound(indata, factor):
    if (factor > 0): #Play sound to right ear
        return numpy.c_[indata[:,0], indata[:,1]*(1+(factor/3))]
    elif (factor < 0): #Play sound to left ear 
        return numpy.c_[indata[:,0]*(1+(abs(factor)/3)), indata[:,1]]
    else: #Do nothing
        return indata

def left_sound(indata):
    return left_right_sound(indata,-3)*2

def right_sound(indata):
    return left_right_sound(indata,3)*2

#In order to avoid lag, blocksize has to be increased. On the other hand, it introduces a delay
def higher_pitch(indata):
    #parser.add_argument('-b', '--blocksize', type=int, default=12000, help='block size')
    return numpy.c_[librosa.effects.pitch_shift(indata[:, 0], args.samplerate, n_steps=1, bins_per_octave=2),
            librosa.effects.pitch_shift(indata[:, 1], args.samplerate, n_steps=1, bins_per_octave=2)]

#In order to avoid lag, blocksize has to be increased. On the other hand, it introduces a delay
def lower_pitch(indata):
    #parser.add_argument('-b', '--blocksize', type=int, default=12000, help='block size')
    return numpy.c_[librosa.effects.pitch_shift(indata[:, 0], args.samplerate, n_steps=-1, bins_per_octave=2),
            librosa.effects.pitch_shift(indata[:, 1], args.samplerate, n_steps=-1, bins_per_octave=2)]
"""
Delaying sound from one input device, can be done by controlling the blocksize. A higher blocksize delays the sound output.
Can be done individually for callback_right or callback_left, when parsing input arguments.

"""


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '-t', '--threshold', type=float, default=200, metavar='THRESHOLD',
    help='threshold for the force sensor values')
parser.add_argument('-li', '--input-left', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-ri', '--input-right', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-o', '--output', type=int_or_str,
                    help='output device ID or substring')
parser.add_argument('-c', '--channels', type=int, default=2,
                    help='number of channels')
parser.add_argument('-q', '--dtype', help='audio data type')
parser.add_argument('-s', '--samplerate', type=float, help='sampling rate')
parser.add_argument('-b', '--blocksize', type=int, help='block size')
parser.add_argument('-l', '--latency', type=float, help='latency in seconds')
args = parser.parse_args()

#ser = serial.Serial('/dev/ttyACM0',9600)
ser = serial.Serial('/dev/tty.SLAB_USBtoUART',9600)

# initialize the feet
# 14 => A0, 15 => A1, ..., 19 => A5 on the arduino
right_foot = Foot('right', 14, 16, 15)
left_foot = Foot('left', 19, 18, 17)
experiment = 0

# read_serial.py -li 2 -ri 3 -o 1 -s 10000 -b 512 -c 1 -l 0.001

def callback_left(indata, outdata, frames, time, status):
  if the_foot.lifted():
    outdata[:] = indata
  elif experiment == 0:
    outdata[:] = indata
  elif experiment == 1:
    outdata[:,0] = librosa.effects.pitch_shift(indata[:,0], args.samplerate, n_steps=-1, bins_per_octave=2)
  elif experiment == 2:
    outdata[:,0] = librosa.effects.pitch_shift(indata[:,0], args.samplerate, n_steps=1, bins_per_octave=2)
  elif experiment == 3:
    outdata[:] = indata*1.25
  elif experiment == 4:
    outdata[:] = indata*1.5

def callback_right(indata, outdata, frames, time, status):
  if the_foot.lifted():
    outdata[:] = indata
  elif experiment == 0:
    outdata[:] = indata
  elif experiment == 1:
    outdata[:,0] = librosa.effects.pitch_shift(indata[:,0], args.samplerate, n_steps=-1, bins_per_octave=2)
  elif experiment == 2:
    outdata[:,0] = librosa.effects.pitch_shift(indata[:,0], args.samplerate, n_steps=1, bins_per_octave=2)
  elif experiment == 3:
    outdata[:] = indata*1.25
  elif experiment == 4:
    outdata[:] = indata*1.5

the_foot = random.choice([right_foot, left_foot])
try:
  with sd.Stream(device=(args.input_left, args.output),
    samplerate=args.samplerate, blocksize=args.blocksize,
    dtype=args.dtype, latency=args.latency,
    channels=args.channels, callback=callback_left, clip_off=True) as a, sd.Stream(device=(args.input_right, args.output),
    samplerate=args.samplerate, blocksize=args.blocksize,
    dtype=args.dtype, latency=args.latency,
    channels=args.channels, callback=callback_right, clip_off=True) as b:
    
    while True:
      read_serial = str(ser.readline())
      found = re.findall("([0-9]+): ([0-9]+\.?[0-9]+)", read_serial)
      for pin, v in found:
        # fsr output
        v = float(v)
        # pin on the arduino
        pin = int(pin)
        # when the value is over some threshold turn the pin on, when it goes under, turn it off
        if(v > args.threshold):
          if(pin in left_foot.pins): left_foot.on(pin)
          if(pin in right_foot.pins): right_foot.on(pin)
        else:
          if(pin in left_foot.pins): left_foot.off(pin)
          if(pin in right_foot.pins): right_foot.off(pin)

      state = re.findall("state: (\d+)", read_serial)
      if experiment != int(state[0]):
        print("#"*20)
        the_foot = random.choice([right_foot, left_foot])
        experiment = int(state[0])
        print(the_foot.name)
        print(int(state[0]))
        print("#"*20)
    
    print('#' * 80)
    print('press Return to quit')
    print('#' * 80)
    input()

except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))


# # loop that looks for some input from the arduino, parses it and toggles some pins on the feet
# while True:
#   read_serial = ser.readline()
#   found = re.findall("([0-9]+): ([0-9]+\.?[0-9]+)", read_serial)
#   for pin, v in found:
#     # fsr output
#     v = float(v)
#     # pin on the arduino
#     pin = int(pin)
#     # when the value is over some threshold turn the pin on, when it goes under, turn it off
#     if(v > args.threshold):
#       if(pin in left_foot.pins): left_foot.on(pin)
#       if(pin in right_foot.pins): right_foot.on(pin)
#     else:
#       if(pin in left_foot.pins): left_foot.off(pin)
#       if(pin in right_foot.pins): right_foot.off(pin)
