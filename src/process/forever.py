#!/usr/bin/python
from subprocess import Popen
from colorama import init, Fore
import sys
init()

while True:
    print(Fore.YELLOW + 'Starting the bot with loop execution...' + Fore.RESET)
    if sys.platform != 'linux' and sys.platform != 'linux2':
        p = Popen("python .\index.py", shell=True)
    if sys.platform == 'linux' or sys.platform == 'linux2':
        p = Popen("python3 .\index.py", shell=True)

    p.wait() 