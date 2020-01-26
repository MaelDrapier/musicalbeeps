#!/usr/bin/env python3

import os
import sys

null_fd = os.open(os.devnull, os.O_RDWR)
saved_fd = os.dup(2)
os.dup2(null_fd, 2)

from pysine import sine

for line in sys.stdin:
    print(line)
    sine(440.0, 0.1)
    sine(300.0, 0.2)
    sine(500.0, 0.2)

os.dup2(saved_fd, 2)
os.close(null_fd)
