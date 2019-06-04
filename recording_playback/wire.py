#!/usr/bin/env python3
"""Pass input directly to output.

See https://www.assembla.com/spaces/portaudio/subversion/source/HEAD/portaudio/trunk/test/patest_wire.c

"""
import argparse
import logging
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


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

#fig, ax1 = plt.subplots(1, figsize=(7,7))

try:
    import sounddevice as sd
    import numpy  # Make sure NumPy is loaded before it is used in the callback
    assert numpy  # avoid "imported but unused" message (W0611)
    import pandas

    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        outdata[:] = indata

        """global testing

        testing = indata
        testing = numpy.fft.rfft2(testing)
        
        #testing[:10, :] = 0.0
        #testing[500:, :] = 0.0
        
        testing = numpy.fft.ifft2(testing) """

    """
    def update_plot(frame):
        global testing
        global line_fft
        print(numpy.max(testing))
        ax1.clear()
        line_fft, = ax1.semilogx(numpy.linspace(0, 20000, 512), testing[:,0], '-', lw=2)
        return line_fft,
    
    ani = FuncAnimation(fig, update_plot, interval=25, blit=True) """

    with sd.Stream(device=(args.input_device, args.output_device),
                   samplerate=args.samplerate, blocksize=args.blocksize,
                   dtype=args.dtype, latency=args.latency,
                   channels=args.channels, callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        #plt.show()
        input()
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
