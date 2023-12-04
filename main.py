import sounddevice as sd
from scipy.io.wavfile import write as wavwrite
import time
import random
import threading
import queue
import os

filename_queue = queue.Queue()  # Create a queue to store the filenames


def record_audio(seconds):
    sample_rate = 44100
    while True:
        directory = "temp_recordings"
        filename = f"{random.randint(0, 999999999)}.wav"  # Generate a random filename
        filepath = os.path.join(directory, filename)
        # Start recording
        recording = sd.rec(
            int(seconds * sample_rate), samplerate=sample_rate, channels=2
        )
        time.sleep(seconds)  # Wait for the recording to finish

        # Save the recording to a file
        wavwrite(filepath, sample_rate, recording)

        # Put the filename into the queue
        filename_queue.put(filepath)


def process_audio():
    while True:
        filename = filename_queue.get()
        time.sleep(2)
        print(f"Proccessed! {filename}")


# Create two threads, one for each task
record_thread = threading.Thread(target=record_audio, args=(5,))
process_thread = threading.Thread(target=process_audio)

# Start the threads!!!
record_thread.start()
process_thread.start()
