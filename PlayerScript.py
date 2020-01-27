#!/usr/bin/env python3

import os
import sys
import argparse
import MusicNotesPlayer as mnplayer

def setupArgparse():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                    description='A python script playing musical notes',
                                    epilog='''\

how to use:
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
    For exemple, 'pause:5' will pause the player for 5 seconds.
    ''')
    parser.add_argument("file",
                        nargs="?",
                        help="a file containing music notes")
    parser.add_argument("--silent",
                        help="disable player output",
                        action='store_true')
    parser.add_argument("--volume",
                        help="volume between 0 and 1 (default=0.5)",
                        type=float,
                        default=0.5)
    args = parser.parse_args()
    if args.file:
        input_file = open(args.file, 'r')
    else:
        input_file = sys.stdin
    return args, input_file


def playerLoop(args, inputFile):
    notesPlayer = mnplayer.Player(args.volume, args.silent)

    for line in inputFile:
        validDuration = True
        line = line.rstrip()
        if len(line) > 0:
            try:
                note, durationStr = line.split(':')
            except:
                note, durationStr = line, '.5'
            try:
                duration = float(durationStr)
            except:
                validDuration = False
                error = str.encode("Error: invalid duration: '" + durationStr + "'" + os.linesep)
                os.write(notesPlayer.stderrFd, error)
            if validDuration:
                notesPlayer.playNote(note, duration)


def main():
    args, inputFile = setupArgparse()
    playerLoop(args, inputFile)
    if not args.silent:
        print("Done")
    if inputFile is not sys.stdin:
        inputFile.close


if __name__ == "__main__":
    main()