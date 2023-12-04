import sounddevice as sd
from scipy.io.wavfile import write as wavwrite
import time
import random
import threading
import queue
import os
import whisper

filename_queue = queue.Queue()  # Create a queue to store the filenames
file_written_event = threading.Event()


def record_audio(seconds):
    sample_rate = 44100
    while True:
        directory = "temp_recordings"
        filename = f"{random.randint(0, 999999999)}.wav"  # Generate a random filename
        filepath = os.path.join(directory, str(filename))
        # Start recording
        print("Recording...")
        recording = sd.rec(
            int(seconds * sample_rate), samplerate=sample_rate, channels=2
        )
        time.sleep(seconds)  # Wait for the recording to finish
        # TODO: See if we can do this without using os.fsync()
        f = open(filepath, "wb")
        # Save the recording to a file
        wavwrite(f, sample_rate, recording)
        os.fsync(f.fileno())
        f.close()

        # Signal that the file has been written
        file_written_event.set()

        # Put the filename into the queue
        filename_queue.put(filename)


def process_audio():
    print("Loading model. This could take a while...")
    whisper_model = whisper.load_model("tiny.en")
    print("Loaded!")
    while True:
        filename = filename_queue.get()
        file_written_event.wait()
        # print(filename)
        transcription = whisper_model.transcribe(f"temp_recordings/{filename}")
        # TODO: Actually print the transcription's text
        print(transcription)
        file_written_event.clear()


# Create two threads, one for each task
record_thread = threading.Thread(target=record_audio, args=(5,))
process_thread = threading.Thread(target=process_audio)

# Start the threads!!!
record_thread.start()
process_thread.start()
