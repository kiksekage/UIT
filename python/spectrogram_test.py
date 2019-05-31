# -*- coding: utf-8 -*-
"""
Created on Mon May 27 20:33:21 2019

@author: Austin Muschott with lots of help from the internet
"""

#!/usr/bin/env python3
"""Plot the live microphone signal(s) with matplotlib.

Matplotlib and NumPy have to be installed.

"""
import argparse
import queue
import sys
import math
import numpy as np




def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

CHUNK = 2205#1024 * 2 

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
parser.add_argument(
    '-d', '--device', type=int_or_str, default=1,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-w', '--window', type=float, default=20000, metavar='DURATION',
    help='visible time slot (default: %(default)s ms)')
parser.add_argument(
    '-i', '--interval', type=float, default=30,
    help='minimum time between plot updates (default: %(default)s ms)')
parser.add_argument(
    '-b', '--blocksize', type=int, default=50, help='block size (in samples)')
parser.add_argument(
    '-r', '--samplerate', type=float, default=41000, help='sampling rate of audio device')
parser.add_argument(
    '-n', '--downsample', type=int, default=1, metavar='N',
    help='display every Nth sample (default: %(default)s)')
parser.add_argument('-g', '--gain', type=float, default=10,
                    help='initial gain factor (default %(default)s)')
parser.add_argument('-rr', '--range', type=float, nargs=2,
                    metavar=('LOW', 'HIGH'), default=[0, 2000],
                    help='frequency range (default %(default)s Hz)')
parser.add_argument(
    'channels', type=int, default=[2], nargs='*', metavar='CHANNEL',
    help='input channels to plot (default: the first)')
parser.add_argument('-bb', '--block-duration', type=float,
                    metavar='DURATION', default=50,
                    help='block size (default %(default)s milliseconds)')
args = parser.parse_args()

low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')
mapping = [c - 1 for c in args.channels]  # Channel numbers start with 1
q = queue.Queue()
######################plot
import matplotlib.pyplot as plt
RATE = 44100 
    
fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))

# variable for plotting
x = np.arange(0, 2 * CHUNK, 2)       # samples (waveform)
xf = np.linspace(0, RATE, CHUNK)     # frequencies (spectrum)

# create a line object with random data
line, = ax1.plot(x, np.random.rand(CHUNK), '-', lw=2)

# create semilogx line for spectrum
line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-', lw=2)
###########################end plot

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

global plotdata2
yf=np.zeros((CHUNK))

def callback(indata, frames, time, status):
    
    global yf
    yf = np.fft.rfft2(indata)
    yf =np.abs(yf)
    

def update_plot(frame):
    """This is called by matplotlib for each plot update.

    Typically, audio callbacks happen more frequently than plot updates,
    therefore the queue tends to contain multiple blocks of audio data.

    """

    # create semilogx line for spectrum
    global yf
    global line_fft
    ax2.clear()
    #line_fft.set_data([],[])
    #yf[:][0]
    if(frame==0):
        line_fft, = ax2.semilogx(xf, yf[:,0], '-', lw=2)
    else:
        line_fft, = ax2.semilogx(xf, yf[:,0], '-', lw=2)
    #line_fft.set_data(xf,yf[:,0])

    return line_fft,
    


try:
    from matplotlib.animation import FuncAnimation
   
    import numpy as np
    import sounddevice as sd

    
    
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, 'input')
        args.samplerate = device_info['default_samplerate']

    length = int(args.window * args.samplerate / (1000 * args.downsample))
    plotdata = np.zeros((low, high))
    
    ###########################################good
    
    #this section might not be needed if your just using high/low range
    
    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']#overrides args delete args?
    
    columns = high-low#note change this according to the spectrum scale you want
    
    delta_f = (high - low) / (columns - 1)#divides plot space into equal frequencies
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)
    
    
    ##########evenly divides the space
    ################plotting
    
    
    # format waveform axes
    ax1.set_title('AUDIO WAVEFORM')
    ax1.set_xlabel('samples')
    ax1.set_ylabel('volume')
    ax1.set_ylim(0, 255)
    ax1.set_xlim(0, 2 * CHUNK)
    plt.setp(ax1, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])
    
    # format spectrum axes
    ax2.set_xlim(20, RATE / 2)
    ##################################

    stream = sd.InputStream(
        device=args.device, channels=max(args.channels),
        samplerate=args.samplerate, callback=callback, blocksize=int(samplerate * args.block_duration / 1000))
    ani = FuncAnimation(fig, update_plot, interval=args.interval, blit=True)
    with stream:
        plt.show()
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
