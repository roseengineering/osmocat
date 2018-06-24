#!/usr/bin/env python
# Copyright (c) 2018 roseengineering

from __future__ import print_function

from gnuradio import gr
from gnuradio import blocks
import osmosdr
import sys, struct, argparse
import numpy as np

tick = 0


def cast_stream(buf, byte=False, word=False, left=False, peak=False):
    data = np.ndarray(shape=(len(buf)/4,), dtype='f', buffer=buf)
    if peak:
        global tick
        n = max(abs(data.min()), abs(data.max()))
        n = 20 * np.log10(n + .0000000001)
        print("%6.1f dBFS (peak) %s " % (n, "/-\|"[tick % 4]), file=sys.stderr, end='\r') 
        tick += 1
    if word:
        data = data * 32768
        buf = data.astype('h').tobytes()
    elif left:
        data = data * 32768 + 128
        buf = data.astype('B').tobytes()
    elif byte:
        data = data * 128 + 128
        buf = data.astype('B').tobytes()
    return buf


class queue_sink(gr.hier_block2):

    def __init__(self, options):
        item_size = gr.sizeof_gr_complex
        gr.hier_block2.__init__(self, "queue_sink",
            gr.io_signature(1, 1, item_size),
            gr.io_signature(0, 0, 0))
        self.qu = gr.msg_queue(0)
        message_sink = blocks.message_sink(item_size, self.qu, False)
        self.connect(self, message_sink)
		
    def next(self):
        msg = self.qu.delete_head()
        return msg.to_string()


class radio_stream(gr.top_block):

    def __init__(self, options):
        gr.top_block.__init__(self)
        self.options = options
        self.source = source = osmosdr.source(options['args'])
        self.sink = sink = queue_sink(options)
        self.connect(source, sink)

    def initialize(self):
        options = self.options
        source = self.source
        source.set_center_freq(int(options['freq'] or 100e6))
        if options['rate'] != None: source.set_sample_rate(options['rate'])
        if options['corr'] != None: source.set_freq_corr(options['corr'])
        if options['gain'] != None: source.set_gain(options['gain'])
        if options['auto'] != None: source.set_gain_mode(options['auto'])
  
    def print_ranges(self):
        source = self.source
        self.print_range('valid sampling rates', source.get_sample_rates())
        self.print_range('valid gains', source.get_gain_range())
        self.print_range('valid frequencies', source.get_freq_range())

    def print_status(self):
        source = self.source 
        print('rate = %d' % source.get_sample_rate(), file=sys.stderr)
        print('freq = %d' % source.get_center_freq(), file=sys.stderr)
        print('corr = %d' % source.get_freq_corr(), file=sys.stderr)
        print('gain = %d' % source.get_gain(), file=sys.stderr)
        print('auto = %s' % source.get_gain_mode(), file=sys.stderr)

    def print_range(self, name, r):
        print(name + ":", end="", file=sys.stderr)
        if r.empty():
            print(" <none>", file=sys.stderr)
            return
        for x in r:
            start = x.start()
            stop = x.stop()
            if start == stop: 
                print(" %d" % start, end="", file=sys.stderr)
            else:
                print(" %d-%d" % (start, stop), end="", file=sys.stderr)
        print(file=sys.stderr)

    def __iter__(self):
        return self.sink


parser = argparse.ArgumentParser()
parser.add_argument("--args", help="device arguments", default="")
parser.add_argument("--freq", help="center frequency (Hz)", type=float)
parser.add_argument("--rate", help="sample rate (Hz)", type=float)
parser.add_argument("--corr", help="freq correction (ppm)", type=float)
parser.add_argument("--gain", help="gain (dB)", type=float)
parser.add_argument("--peak", help="show peak values in dBFS", action="store_true")
parser.add_argument("--auto", help="turn on automatic gain", action="store_true")
parser.add_argument("--word", help="signed word samples", action="store_true")
parser.add_argument("--left", help="left justified unsigned byte samples", action="store_true")
parser.add_argument("--byte", help="unsigned byte samples", action="store_true")
parser.add_argument("--output", help="output file to save 32-bit float samples")
args = parser.parse_args()

########################################

# start stream
stream = radio_stream(args.__dict__)
stream.print_ranges()
stream.initialize()
stream.print_status()
stream.start()

output_file = None
if args.output:
    output_file = open(args.output, "wb")

try:
    for data in stream:
        if output_file:
            output_file.write(data)
        data = cast_stream(data, byte=args.byte, word=args.word, left=args.left, peak=args.peak)
        sys.stdout.write(data)
except KeyboardInterrupt:
    print("control-c caught, closing server", file=sys.stderr)

if output_file:
    print('closing file %s' % args.output, file=sys.stderr)
    output_file.close()

