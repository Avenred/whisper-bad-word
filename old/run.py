from onbad import BadFinder

# from colorama import Cursor  # unused?

# Function placed in onbad.py

handle = BadFinder(
    custom_script_file="custom.py"
)  # initialize an instance of the class
handle.begin()  # start the threads
while handle.Running:
    try:
        print(end="")  # just to catch errors
    except KeyboardInterrupt:
        handle.Running = False
        exit(0)
