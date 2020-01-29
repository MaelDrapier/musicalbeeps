#!/usr/bin/env python3

import os
import sys
import time
import pyaudio
import numpy as np


class Player:
    def __init__(self, volume: float = 0.5,
                mute_output: bool = False,
                hide_warnings: bool = True):


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
        self._valid_note = True
        self._hide_warnings = hide_warnings

        # Hide warnings triggered by PortAudio by muting stderr
        if self._hide_warnings:
            self._stderr_fd = os.dup(2)
            self._null_fd = os.open(os.devnull, os.O_RDWR)
            self.__mute_stderr()

        # PyAudio stream initialization
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(format=pyaudio.paFloat32,
                                        channels=1,
                                        rate=self.rate,
                                        output=True)

        # Set stderr back to its original value
        if self._hide_warnings:
            self.__unmute_stderr()

    def __mute_stderr(self):
        os.dup2(self._null_fd, 2)

    def __unmute_stderr(self):
        os.dup2(self._stderr_fd, 2)

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

    def __write_stream(self, duration: float):
        frames = [np.sin(np.arange(int(duration * self.rate))
            * (float(self.freq)
            * (np.pi * 2) / self.rate)).astype(np.float32)]
        frames = np.concatenate(frames) * self.volume
        fade = 1000
        fade_in = np.arange(0., 1., 1/fade)
        fade_out = np.arange(1., 0., -1/fade)
        frames[:fade] = np.multiply(frames[:fade], fade_in)
        frames[-fade:] = np.multiply(frames[-fade:], fade_out)

        if self._hide_warnings:
            self.__mute_stderr()

        self._stream.write(frames.tostring())

        if self._hide_warnings:
            self.__unmute_stderr()

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
            self.__print_played_note(note, duration)
            time.sleep(duration)
        else:
            self.__calc_frequency(note)
            if self._valid_note:
                self.__print_played_note(note, duration)
                self.__write_stream(duration)

    def __del__(self):
        # Stop and close pyaudio
        if hasattr(self, '_pyaudio') and hasattr(self, '_stream'):
            time.sleep(0.1)
            self._stream.stop_stream()
            self._stream.close()
            self._pyaudio.terminate()

        if hasattr(self, '_hide_warnings') and self._hide_warnings:
            os.close(self._null_fd)