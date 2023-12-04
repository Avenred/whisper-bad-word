import sounddevice as sd
from scipy.io.wavfile import write as wavwrite
import time
import random
import threading
import queue
import os
import whisper

# TODO: Set up logging instead of print statements
filename_queue = queue.Queue()  # Create a queue to store the filenames
transcription_queue = queue.Queue()
file_written_event = threading.Event()
print("Loading model. This could take a while...")
whisper_model = whisper.load_model("tiny.en")
print("Loaded!")

def record_audio(seconds):
    sample_rate = 44100
    while True:
        directory = "temp_recordings"
        filename = f"{random.randint(0, 999999999)}.wav"  # There's a 1/999999999 chance of a collision. Whoops.
        filepath = os.path.join(directory, str(filename))
        print("Recording...")
        recording = sd.rec(
            int(seconds * sample_rate), samplerate=sample_rate, channels=2
        )
        time.sleep(seconds)  # To avoid writing to the file while it is being recorded
        wavwrite(filepath, sample_rate, recording)

        # Helps to avoid a race condition where the file is read/attempted to be transcribed before it is written
        file_written_event.set()
        print("Done recording!")

        # Put the filename into the queue
        filename_queue.put(filename)


def process_audio():
    while True:
        filename = filename_queue.get()
        file_written_event.wait()
        # print(filename)
        transcription = whisper_model.transcribe(f"temp_recordings/{filename}")
        print(transcription["text"])
        transcription_queue.put(transcription["text"])
        file_written_event.clear()


def return_badwords(transcription):
    with open('badwords.txt') as f:
        badwords = [line.strip().lower() for line in f.readlines()]
    transcription = transcription.lower()
    detected_badwords = [badword for badword in badwords if badword in transcription]
    # We want to return both the badwords it detected and a boolean of whether badwords exist;
    # my idea is to run a function in another file that will only run if badwords exist.
    # I believe that function should have as much access to this file as possible to make development easier.
    if len(detected_badwords) > 0:
        badwords_exist = True
        return badwords_exist, detected_badwords
    else:
        badwords_exist = False
        detected_badwords = None
        return badwords_exist, detected_badwords


def check_badwords_string():
    while True:
        transcribe = transcription_queue.get()
        badwords_exist, detected_badwords = return_badwords(transcribe)
        if badwords_exist:
            print(f"Bad word(s) detected! {detected_badwords}")

# Create two threads, one for each task
record_thread = threading.Thread(target=record_audio, args=(15,))
process_thread = threading.Thread(target=process_audio)
check_thread = threading.Thread(target=check_badwords_string)

# Start the threads!!!
record_thread.start()
process_thread.start()
check_thread.start()
