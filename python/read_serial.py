import serial, re, argparse
from playsound import playsound
from foot import Foot
import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
#import pandas

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '-t', '--threshold', type=float, default=200, metavar='THRESHOLD',
    help='threshold for the force sensor values')
parser.add_argument('-i', '--input-device', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-o', '--output-device', type=int_or_str,
                    help='output device ID or substring')
parser.add_argument('-c', '--channels', type=int, default=2,
                    help='number of channels')
parser.add_argument('-q', '--dtype', help='audio data type')
parser.add_argument('-s', '--samplerate', type=float, help='sampling rate')
parser.add_argument('-b', '--blocksize', type=int, help='block size')
parser.add_argument('-l', '--latency', type=float, help='latency in seconds')
args = parser.parse_args()

#ser = serial.Serial('/dev/ttyACM0',9600)
ser = serial.Serial('/dev/ttyUSB0',9600)

# initialize the feet
# 14 => A0, 15 => A1, ..., 19 => A5 on the arduino
right_foot = Foot('right', 14, 16, 15)
left_foot = Foot('left', 19, 18, 17)
experiment = 0

def callback(indata, outdata, frames, time, status):

    print('experiment: ' + str(experiment))
    #if(experiment == 1):

    if right_foot.lifted():
      outdata[:] = 0.0
    else:
      outdata[:] = indata

try:
  with sd.Stream(device=(args.input_device, args.output_device),
                     samplerate=args.samplerate, blocksize=args.blocksize,
                     dtype=args.dtype, latency=args.latency,
                     channels=args.channels, callback=callback):
    
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
      experiment = int(state[0])

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
