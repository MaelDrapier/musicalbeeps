#!/usr/bin/env python3

import os
import sys
import time
import numpy as np
import simpleaudio as sa


class Player:
    def __init__(self, volume: float = 0.3,
                mute_output: bool = False):

        if volume < 0 or volume > 1:
            raise ValueError("Volume must be a float between 0 and 1")

        # Frequencies for the lowest octave
        self.note_frequencies =  {
            'A': 27.50000,
            'B': 30.86771,
            'C': 16.35160,
            'D': 18.35405,
            'E': 20.60172,
            'F': 21.82676,
            'G': 24.49971
        }

        self.volume = volume
        self.mute_output = mute_output
        self.rate = 44100
        self.freq = 0
        self.fade = 800
        self._valid_note = True
        self._fade_in = np.arange(0., 1., 1 / self.fade)
        self._fade_out = np.arange(1., 0., -1 / self.fade)
        self._play_obj = None
        self._destructor_sleep = 0

    def __set_base_frequency(self, note: str):
        letter = note[:1].upper()
        try:
            self.freq = self.note_frequencies[letter]
        except:
            self._valid_note = False
            print("Error: invalid note: '"
                                    + note[:1]
                                    + "'",
                                    file=sys.stderr)

    def __set_octave(self, octave: str = '4'):
        if not self._valid_note:
            return
        try:
            octaveValue = int(octave)
            if octaveValue < 0 or octaveValue > 8:
                raise ValueError('octave value error')
            self.freq *= (2 ** octaveValue)
        except:
            self._valid_note = False
            print("Error: invalid octave: '"
                                    + octave
                                    + "'",
                                    file=sys.stderr)

    def __set_semitone(self, symbol: str):
        if not self._valid_note:
            return
        if symbol == '#':
            self.freq *= (2 ** (1. / 12.))
        elif symbol == 'b':
            self.freq /= (2 ** (1. / 12.))
        else:
            self._valid_note = False
            print("Error: invalid symbol: '"
                                    + symbol
                                    + "'",
                                    file=sys.stderr)

    def __calc_frequency(self, note: str):
        self.__set_base_frequency(note)
        if len(note) == 1:
            self.__set_octave()
        elif len(note) == 2:
            if note[1:2] == '#' or note[1:2] == 'b':
                self.__set_octave()
                self.__set_semitone(note[1:2])
            else:
                self.__set_octave(note[1:2])
        elif len(note) == 3:
            self.__set_octave(note[1:2])
            self.__set_semitone(note[2:3])
        else:
            if self._valid_note:
                print("Errror: invalid note: '"
                                        + note
                                        + "'",
                                        file=sys.stderr)
                self._valid_note = False

    def __wait_for_prev_sound(self):
        if self._play_obj is not None:
            while self._play_obj.is_playing(): pass


    def __write_stream(self, duration: float):
        t = np.linspace(0, duration, int(duration * self.rate), False)
        audio = np.sin(self.freq * t * 2 * np.pi)
        audio *= 32767 / np.max(np.abs(audio))
        audio *= self.volume

        if len(audio) > self.fade:
            audio[:self.fade] *= self._fade_in
            audio[-self.fade:] *= self._fade_out

        audio = audio.astype(np.int16)

        self.__wait_for_prev_sound()
        self._play_obj = sa.play_buffer(audio, 1, 2, self.rate)

    def __print_played_note(self, note: str, duration: float):
        if self.mute_output or not self._valid_note:
            return
        if note == 'pause':
            print("Pausing for " + str(duration) + "s")
        else:
            print("Playing " + note + " (" + format(self.freq, '.2f') + " Hz) for " + str(duration) + "s")

    def play_note(self, note: str, duration: float = 0.5):
        self._valid_note = True
        if note == 'pause':
            self.__wait_for_prev_sound()
            self.__print_played_note(note, duration)
            time.sleep(duration)
            self._destructor_sleep = 0
        else:
            self.__calc_frequency(note)
            if self._valid_note:
                self.__write_stream(duration)
                self.__print_played_note(note, duration)
                self._destructor_sleep = duration

    def __del__(self):
        time.sleep(self._destructor_sleep)