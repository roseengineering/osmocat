#!/usr/bin/env python

from __future__ import print_function

from gnuradio import gr
from gnuradio import blocks
import osmosdr
import sys, struct, argparse


class queue_sink(gr.hier_block2):

    def __init__(self):
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

    def __init__(self, **kw):
        gr.top_block.__init__(self)
        self.source = source = osmosdr.source(kw['args'])
        self.sink = sink = queue_sink()
        self.valid_ranges('valid sampling rates', source.get_sample_rates())
        self.valid_ranges('valid gains', source.get_gain_range())
        self.valid_ranges('valid frequencies', source.get_freq_range())
        source.set_center_freq(int(kw['freq'] or 100e6))
        if kw.get('rate') != None: source.set_sample_rate(kw['rate'])
        if kw.get('corr') != None: source.set_freq_corr(kw['corr'])
        if kw.get('gain') != None: source.set_gain(kw['gain'])
        if kw.get('mode') != None: source.set_gain_mode(bool(kw['mode']))
        self.connect(source, sink)
  
    def status(self):
        source = self.source 
        print('rate = %d' % source.get_sample_rate(), file=sys.stderr)
        print('freq = %d' % source.get_center_freq(), file=sys.stderr)
        print('corr = %d' % source.get_freq_corr(), file=sys.stderr)
        print('gain = %d' % source.get_gain(), file=sys.stderr)
        print('mode = %s' % source.get_gain_mode(), file=sys.stderr)

    def valid_ranges(self, name, r):
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--args", help="device arguments", default="")
    parser.add_argument("--freq", help="center frequency (Hz)", type=float)
    parser.add_argument("--rate", help="sample rate (Hz)", type=float)
    parser.add_argument("--corr", help="freq correction (ppm)", type=float)
    parser.add_argument("--gain", help="gain (dB)", type=float)
    parser.add_argument("--mode", help="gain mode (0 or 1)", type=int)
    args = parser.parse_args()

    stream = radio_stream(**args.__dict__)
    stream.status()
    stream.start()

    for c in stream:
        sys.stdout.write(c)

