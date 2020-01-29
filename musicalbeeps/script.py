#!/usr/bin/env python3

import os
import sys
import argparse
import musicalbeeps


def setup_argparse():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description='Play sound beeps corresponding to musical notes.',
                                    epilog='''\

how to play notes:
    Notes are read from a file passed as argument, or directly from the
    standard input. Each note must be on a new line.

note format:
    Each note must be formatted like so: 'A5#:1.5' (without quotes)
    Where:
        - 'A' is the note (between A and G, can be lowercase)
        - '5' is the octave (between 0 and 8, default=4)
        - '#' (or 'b') is optional and used to play a sharp or flat note
        - ':1.5' is the duration of the note (1.5 seconds here, default=0.5)

pause:
    You can pause the player by replacing the note by the 'pause' word.
    For exemple, 'pause:5' will pause the player for 5 seconds.''')
    parser.add_argument("file",
                        nargs="?",
                        help="a file containing musical notes")
    parser.add_argument("--silent",
                        help="disable player output",
                        action='store_true')
    parser.add_argument("--volume",
                        help="volume between 0 and 1 (default=0.3)",
                        type=float,
                        default=0.3)
    args = parser.parse_args()
    if args.file:
        input_file = open(args.file, 'r')
    else:
        input_file = sys.stdin
    return args, input_file

def player_loop(args, input_file):
    notes_player = musicalbeeps.Player(args.volume, args.silent)

    for line in input_file:
        valid_duration = True
        line = line.rstrip()
        if len(line) > 0:
            try:
                note, duration_str = line.split(':')
            except:
                note, duration_str = line, '.5'
            try:
                duration = float(duration_str)
            except:
                valid_duration = False
                print("Error: invalid duration: '"
                                        + duration_str
                                        + "'",
                                        file=sys.stderr)
            if valid_duration:
                notes_player.play_note(note, duration)

def main():
    try:
        args, input_file = setup_argparse()
        player_loop(args, input_file)
        if not args.silent:
            print("Done")
        if input_file is not sys.stdin:
            input_file.close
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e, file=sys.stderr)

if __name__ == "__main__":
    main()