#!/usr/bin/env python3
"""Pass input directly to output.

See https://www.assembla.com/spaces/portaudio/subversion/source/HEAD/portaudio/trunk/test/patest_wire.c

"""
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

import argparse
#import librosa
import logging
#import matplotlib.pyplot as plt
#from matplotlib.animation import FuncAnimation
import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
#import pandas
#import scipy.fftpack


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

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-li', '--left-input', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-ri', '--right-input', type=int_or_str,
                    help='input device ID or substring')
parser.add_argument('-o', '--output-device', type=int_or_str,
                    help='output device ID or substring')
parser.add_argument('-c', '--channels', type=int, default=2,
                    help='number of channels')
parser.add_argument('-t', '--dtype', help='audio data type')
parser.add_argument('-s', '--samplerate', type=float, help='sampling rate')
parser.add_argument('-b', '--blocksize', type=int, help='block size')
parser.add_argument('-l', '--latency', type=float, help='latency in seconds')
args = parser.parse_args()

#fig, ax1 = plt.subplots(1, figsize=(7,7))
#ax1.set_ylim(0,1)
#line_fft, = ax1.plot(numpy.linspace(0, 512, 512), numpy.asarray([0]*512))


try:
    def callback_left(indata, outdata, frames, time, status):

        #print('experiment: ' + "oppe i den venstre")
        #if(experiment == 1):
        print(outdata.shape)
        print(indata.shape)
        if right_foot.lifted():
            outdata[:, 0] = librosa.effects.pitch_shift(indata[:, 0], args.samplerate, n_steps=2)
            if numpy.max(outdata > 1) or numpy.min(outdata < -1):
                print("clipping")
        else:
            outdata[:, 0] = librosa.effects.pitch_shift(indata[:, 0], args.samplerate, n_steps=2)
            if numpy.max(outdata > 1) or numpy.min(outdata < -1):
                print("clipping")
            #outdata[:,1] = indata

    def callback_right(indata, outdata, frames, time, status):

        #print('experiment: ' + "oppe i den højre")
        #if(experiment == 1):
        print(outdata.shape)
        print(indata.shape)

        if left_foot.lifted():
            outdata[:] = indata
        else:
            outdata[:] = indata

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        global testing

        #testing = indata

        #testing = indata[:, 0]
        #testing = numpy.abs(scipy.fftpack.fft(indata)[:, 0])
        
        #testing[:10, :] = 0.0
        #testing[500:, :] = 0.0
        
        #testing = numpy.fft.ifft2(testing)
        #testing = numpy.real(testing)
        
        #outdata[:,0] = librosa.effects.pitch_shift(indata[:, 0], args.samplerate, n_steps=4)
        #outdata[:,1] = indata[:,1]
        outdata[:] = indata[:]
        """

        testing = indata
        testing = numpy.fft.rfft2(testing)
        
        #testing[:10, :] = 0.0
        #testing[500:, :] = 0.0
        
        testing = numpy.fft.ifft2(testing) """

    
    def update_plot(frame):
        global testing

        print(testing.shape)
        #print(numpy.ptp(testing))

        line_fft.set_ydata(testing)
        return line_fft,
    
    #ani = FuncAnimation(fig, update_plot, interval=1, blit=False)

    # sample command: python3 wire.py -s 100000 -c 1 -l 0.01
    
    with sd.Stream(device=(args.left_input, args.output_device),
    samplerate=args.samplerate, blocksize=args.blocksize,
    dtype=args.dtype, latency=args.latency,
    channels=args.channels, callback=callback_left) as a, sd.Stream(device=(args.right_input, args.output_device),
    samplerate=args.samplerate, blocksize=args.blocksize,
    dtype=args.dtype, latency=args.latency,
    channels=args.channels, callback=callback_right) as b:
    
        '''with sd.Stream(device=(args.input_device, args.output_device),
        samplerate=args.samplerate, blocksize=args.blocksize,
        dtype=args.dtype, latency=args.latency,
        channels=args.channels, callback=callback):'''
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        #plt.show()
        input()
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
