
osmocat.py
==========

This repo provides a Python (2.7) gnuradio script named osmocat.py.
The script sends samples from any gr-osmosdr supported device to 
standard output.  Basically osmocat.py is rtl\_sdr but for 
gr-osmosdr devices. 

I created the python script namely to connect a AirspyHF+ radio to 
the Openwebrx software receiver.  At the time of writing 
SDR# and gr-osmosdr clients support the AirspyHF+, as well as dl9rdz's 
airspyhf\_rx. [1] 

To use Openwebrx with a particular SDR radio, a command line
program that can write samples to standard output is required.
For example to listen to a RTL-SDR, Openwebrx normally uses 
rtl\_sdr, but you can also use osmocat.py:

    $ python osmocat.py -h

    usage: osmocat.py [-h] [--args ARGS] [--freq FREQ] [--rate RATE] [--corr CORR]
                      [--gain GAIN] [--auto] [--word] [--left] [--byte]

    optional arguments:
      -h, --help   show this help message and exit
      --args ARGS  device arguments
      --freq FREQ  center frequency (Hz)
      --rate RATE  sample rate (Hz)
      --corr CORR  freq correction (ppm)
      --gain GAIN  gain (dB)
      --auto       automatic gain
      --word       signed word samples
      --left       left justify sample
      --byte       unsigned byte samples

By default osmocat outputs raw 32-bit floating point IQ samples.
Use the --word option to output raw signed word IQ samples.
Or use the --byte option to output raw unsigned byte IQ samples.

To use osmocat.py with Openwebrx add the following lines at
the end of config\_webrx.py:

    start_rtl_command=("python osmocat.py "
                       "--args '{device_args}' "
                       "--mode {gain_mode} "
                       "--freq {center_freq} "
                       "--rate {samp_rate}").format(
        center_freq=center_freq, 
        samp_rate=samp_rate, 
        gain_mode=gain_mode, 
        device_args=device_args)
    format_conversion=""

So, for example, to listen to a RTL-SDR device, change the following variables
in config\_webrx.py to:

    device_args = "rtl=0"
    gain_mode = 1
    samp_rate = 2400000
    center_freq = 470000000

Since a blank device argument picks up the first
gr-osmosdr radio found, device\_args can be set to:

    device_args = ""

Now to listen to your AirspyHF+[2], change the variables, for example, to:

    device_args = "airspyhf=0"
    gain_mode = 0
    samp_rate = 768000
    center_freq = 1000000

 
- Copyright 2018 (c) roseengineering

Footnotes
---------

[1] To compile, clone https://github.com/dl9rdz/airspyhf, cd into airspyhf/tools/src and run gcc -o airspyhf\_rx airspyhf\_rx.c -I /usr/local/include/libairspyhf -lairspyhf -lm

[2] The AirspyHF+ gr-osmosdr device only supports a sample rate of 768000.
It also does not support, as I found out, "--auto" or "--gain", which 
the gr-osmosdr implementation ignores.  Note, if the waterfall on Openwebrx is all black, click
the auto-adjust waterfall colors button to rescale.  The button looks 
like a mountain range landscape. 

