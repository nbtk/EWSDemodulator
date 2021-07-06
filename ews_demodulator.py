#!/usr/bin/env python3

import pyaudio
import numpy as np
import time

class EWSDemodulator():
    # Args for pyaudio
    audio_args =  {'format':   pyaudio.paInt16,
                   'rate':     44100,
                   'channels': 1,
                   #'input_device_index': 2,
                   'input':    True,
                   'frames_per_buffer': 4096,}
    stream_args = (4096, False)
    
    # Carrier Frequency Hi/Low [Hz]
    carrier_freq        = 640
    carrier_freq_margin = 30
    # Signal Frequency Hi/Low [Hz]
    signal_freq        = 1024
    signal_freq_margin = 30

    # Carrier Detection Counter Threshold
    carrier_count_threshold = 5
    # Signal Detection Counter Threshold
    signal_count_threshold = 5

    # Terminator
    none_signal_buffer = 44100 # 1 sec

    # Baud Rate [Hz]
    baud_rate = 64
    corrected_baud_rate = baud_rate + 6 # Delay until detection.

    # Voltage Offset
    v_off = 256

    def __init__(self, audio_args=audio_args):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(**audio_args)
        self.sampling_rate = audio_args['rate']
        self.clock = 0
        self.carrier_freq_hi    = self.carrier_freq + self.carrier_freq_margin 
        self.carrier_freq_low   = self.carrier_freq - self.carrier_freq_margin 
        self.signal_freq_hi     = self.signal_freq + self.signal_freq_margin
        self.signal_freq_low    = self.signal_freq - self.signal_freq_margin

        class dict2(dict): 
            def __init__(self, *args, **kwargs): 
                super().__init__(*args, **kwargs) 
                self.__dict__ = self 
        self.carrier_vars = dict2({'count': 0, 'window': 0, 'barrier': 0, 'threshold': self.carrier_count_threshold})
        self.signal_vars = dict2({'count': 0, 'window': 0, 'barrier': 0, 'threshold': self.signal_count_threshold})

    def demodurator(self, wave_freq, clock):
        signal = None
        if self.carrier_freq_low <= wave_freq and wave_freq <= self.carrier_freq_hi:
            signal = 0
            vars_flip = self.carrier_vars
            vars_flop = self.signal_vars
        elif self.signal_freq_low <= wave_freq and wave_freq <= self.signal_freq_hi:
            signal = 1
            vars_flip = self.signal_vars
            vars_flop = self.carrier_vars
        else:
            signal = None
            return

        if vars_flip.barrier > clock:
            # needs to wait a next baud.
            return
        else:
            vars_flop.window = 0
            if vars_flip.window < clock:
                # resets the baud window and counter.
                vars_flip.window = clock + self.sampling_rate / (self.corrected_baud_rate * 2)
                vars_flip.count = 1
                return
    
            vars_flip.count += 1
            if vars_flip.count == self.carrier_count_threshold and clock < vars_flip.window:
                vars_flip.barrier = vars_flip.window + self.sampling_rate / (self.corrected_baud_rate * 2)
                return signal


    def start(self, stream_args=stream_args, callback=print):
        wave_count = 0
        none_count = 0
        command = []
        
        while self.stream.is_active():
            try:
                data = self.stream.read(*stream_args)
                data = np.frombuffer(data, dtype='int16')
                for data_point in data:
                    self.clock += 1
                    if data_point > self.v_off:
                       wave_count += 1
                    elif wave_count >= 1:
                        wave_freq = 1 / (wave_count / self.sampling_rate) / 2
                        wave_count = 0
                        signal = self.demodurator(wave_freq, self.clock)
                        if signal == 1 or signal == 0:
                            command.append(signal)
                            none_count = 0
                    if len(command) > 0 and none_count > self.none_signal_buffer: 
                        callback(command)
                        command = []
                    none_count += 1
            except KeyboardInterrupt:
                break

        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


if __name__ == '__main__':
    demod = EWSDemodulator()
    demod.start()

