import serial, re, argparse
from playsound import playsound
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

class Foot(object):
  # flags for pressed sensors
  _front_left_pressed = False
  _front_right_pressed = False
  _back_pressed = False
  # current state of the foot (heel/ball/foot/lifted) (use state() to access)
  _foot_state = ''
  # the past step sequence
  _step_sequence = []
  _step_heel_first = ['lifted', 'heel', 'foot']
  _step_ball_first = ['lifted', 'ball', 'foot']
  _step_flat_foot = ['lifted', 'foot']

  def __init__(self, name, pin_front_left, pin_front_right, pin_back):
    # give the foot a fun name
    self.name = name
    # the int of the analog pin connected to the forcesensor on the shoe
    self.pin_front_left = pin_front_left
    self.pin_front_right = pin_front_right
    self.pin_back = pin_back
    # which pins are used on this foot
    self.pins = sorted([pin_front_left, pin_front_right, pin_back])

  # call str(f) to stringify the foot f
  def __repr__(self):
    string = "name: %s\nstate: %s\npins: %s\n---"
    variables = (self.name, self._foot_state, ", ".join([str(p) for p in self.pins]))
    return string % variables

  # called when the user hits with the heel first on the floor
  def on_heel_first(self):
    print('heel first')
    #playsound('air-horn-club-sample_1.mp3')

  # called when the user hits the floor with the ball of this foot first
  def on_ball_first(self):
    print('ball first')
    #playsound('-click-nice_3.mp3')

  # called when the user does a perfect jump and lands on the heel and ball on the same time (rather unlikely)
  def on_flat_foot(self):
    print('flat foot')

  # when the state is changed this function is called
  def on_state_change(self, _old_state):
    print(_old_state, self._foot_state)
    self._step_sequence.append(self._foot_state)

    # check whether the current sequence fit a defined sequence (and cuts the sequence array, such that stuff is not done twice)
    if(len(self._step_heel_first) <= len(self._step_sequence)):
      seq = self._step_sequence[-len(self._step_heel_first):]
      if(self._step_heel_first == seq):
        self.on_heel_first()
        self._step_sequence = self._step_sequence[-len(self._step_heel_first):]
    if(len(self._step_ball_first) <= len(self._step_sequence)):
      seq = self._step_sequence[-len(self._step_ball_first):]
      if(self._step_ball_first == seq):
        self.on_ball_first()
        self._step_sequence = self._step_sequence[-len(self._step_ball_first):]
    if(len(self._step_flat_foot) <= len(self._step_sequence)):
      seq = self._step_sequence[-len(self._step_flat_foot):]
      if(self._step_flat_foot == seq):
        self.on_flat_foot()
        self._step_sequence = self._step_sequence[-len(self._step_flat_foot):]

  # determines the state of the foot (pressure on the heel/ball/foot or lifted if no pressure)
  # writes to the _foot_state variable, can be accessed with the state() method
  def _state(self):
    _old_state = self._foot_state
    if(self.only_heel()):
      self._foot_state = 'heel'
    elif(self.only_ball()):
      self._foot_state = 'ball'
    elif(self.foot()):
      self._foot_state = 'foot'
    elif(self.lifted()):
      self._foot_state = 'lifted'
    if(_old_state != '' and _old_state != self._foot_state):
      self.on_state_change(_old_state)

  # returns the current state of the foot (heel/ball/foot/lifted)
  def state(self):
    return self._foot_state

  # swiches the pressed-state of the pins
  def toggle(self, pin):
    if(pin == self.pin_front_left):
      self._front_left_pressed = not self._front_left_pressed
    elif(pin == self.pin_front_right):
      self._front_right_pressed = not self._front_right_pressed
    elif(pin == self.pin_back):
      self._back_pressed = not self._back_pressed
    self._state()

  # turns the pressed-state off for a pin
  def off(self, pin):
    if(pin == self.pin_front_left):
      self._front_left_pressed = False
    elif(pin == self.pin_front_right):
      self._front_right_pressed = False
    elif(pin == self.pin_back):
      self._back_pressed = False
    self._state()

  # turns the pressed-state on for a pin
  def on(self, pin):
    if(pin == self.pin_front_left):
      self._front_left_pressed = True
    elif(pin == self.pin_front_right):
      self._front_right_pressed = True
    elif(pin == self.pin_back):
      self._back_pressed = True
    self._state()

  # returns True if the user pressures the heel
  def heel(self):
    return self._back_pressed

  # returns True if the user pressures the ball
  def ball(self):
    return self._front_left_pressed and self._front_right_pressed

  # returns True if the user pressures only the heel
  def only_heel(self):
    return self.heel() and not self.ball()

  # returns True if the user pressures only the ball
  def only_ball(self):
    return not self.heel() and self.ball()

  # returns True if the user pressures the whole foot
  def foot(self):
    return self.heel() and self.ball()

  # returns True if the user does not pressure the foot (foot lifted above ground)
  def lifted(self):
    return not self.heel() and not self.ball()

# initialize the feet
# 14 => A0, 15 => A1, ..., 19 => A5 on the arduino
right_foot = Foot('right', 14, 16, 15)
left_foot = Foot('left', 19, 18, 17)
experiment = 0

def callback(indata, outdata, frames, time, status):

    if(experiment == 1):
      print('experiment: ' + str(experiment))

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
        pin = int(pin
)
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
