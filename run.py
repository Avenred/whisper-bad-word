from onbad import BadFinder
from colorama import Cursor

# Function placed in onbad.py

handle = BadFinder(custom_script_file="custom.py")
handle.begin()
while handle.Running:
    try:
        print(end="")
    except KeyboardInterrupt:
        handle.Running = False
        exit(0)