
osmocat.py
==========

This repo provides a Python (2.7) gnuradio script named osmocat.py.
The script sends samples from any gr-osmosdr supported device to 
standard output.  I created the script namely to connect my AirspyHF+ radio to 
the Openwebrx software receiver.  At the time of this writing only 
SDR# and gr-osmosdr clients support the AirspyHF+.

To use Openwebrx with a particular SDR radio, a command line
program that can write samples to standard output is required.
For example to listen to a RTL-SDR, Openwebrx can use the
program rtl\_sdr.  In other words osmocat.py is like rtl\_sdr but for
gr-osmosdr devices. 

To see the script's help screen run:

    $ python osmocat.py -h

    usage: osmocat.py [-h] [--args ARGS] [--freq FREQ] [--rate RATE] [--corr CORR]
                      [--gain GAIN] [--mode MODE]

    optional arguments:
      -h, --help   show this help message and exit
      --args ARGS  device arguments
      --freq FREQ  center frequency (Hz)
      --rate RATE  sample rate (Hz)
      --corr CORR  freq correction (ppm)
      --gain GAIN  gain (dB)
      --mode MODE  gain mode (0 or 1)

Setting the gain mode to 1 turns on automatic gain.

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

Now to listen to your AirspyHF+, change the variables, for example, to:

    device_args = "airspyhf=0"
    gain_mode = 0
    samp_rate = 768000
    center_freq = 1000000

The AirspyHF+ gr-osmosdr device only supports a sample rate of 768000.
It also does not support, as I found out, "--mode" or "--gain", which it
simply ignores.  Note, if the waterfall on Openwebrx is all black, click
the auto-adjust waterfall colors button to rescale.  The button looks 
like a mountain range landscape. 
 

- Copyright 2018 (c) roseengineering
