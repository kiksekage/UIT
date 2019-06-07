#!/usr/bin/env python3
"""Pass input directly to output.

See https://www.assembla.com/spaces/portaudio/subversion/source/HEAD/portaudio/trunk/test/patest_wire.c

"""
import argparse
import logging
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
import pandas
import scipy.fftpack


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
parser.add_argument('-i', '--input-device', type=int_or_str,
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

fig, ax1 = plt.subplots(1, figsize=(7,7))
ax1.set_ylim(0,1)
line_fft, = ax1.plot(numpy.linspace(0, 512, 512), numpy.asarray([0]*512))


try:
    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        global testing

        #testing = indata

        #testing = indata[:, 0]
        testing = numpy.abs(scipy.fftpack.fft(indata)[:, 0])
        
        #testing[:10, :] = 0.0
        #testing[500:, :] = 0.0
        
        #testing = numpy.fft.ifft2(testing)
        #testing = numpy.real(testing)

        #outdata[:] = right_sound(indata)
        outdata[:] = indata*2

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
    
    ani = FuncAnimation(fig, update_plot, interval=1, blit=False)

    # sample command: python3 wire.py -s 100000 -c 1 -l 0.01
    with sd.Stream(device=(args.input_device, args.output_device),
    samplerate=args.samplerate, blocksize=args.blocksize,
    dtype=args.dtype, latency=args.latency,
    channels=args.channels, callback=callback) as a, sd.Stream(device=(1, args.output_device),
    samplerate=args.samplerate, blocksize=args.blocksize,
    dtype=args.dtype, latency=args.latency,
    channels=args.channels, callback=callback) as b:
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        #plt.show()
        input()
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
