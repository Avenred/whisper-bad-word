import sounddevice as sd
from scipy.io.wavfile import write as wavwrite
import time
import random
import threading
import queue
import os
import whisper
import logging
import yaml

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - [%(levelname)s] %(message)s')
filename_queue = queue.Queue()  # Create a queue to store the filenames
transcription_queue = queue.Queue()
file_written_event = threading.Event()

def load_config():
    with open("config.yaml") as f:
        loaded_config = yaml.load(f, Loader=yaml.FullLoader)
    return loaded_config

def init_whisper(config_loaded):
    logging.info("Loading model. This could take a while...")
    model_name = config_loaded["whisper"]["model"]
    init_whisper_model = whisper.load_model(model_name)
    logging.info("Model loaded!")
    return init_whisper_model

def record_audio(seconds):
    sample_rate = 44100
    while True:
        directory = "temp_recordings"
        filename = f"{random.randint(0, 999999999)}.wav"  # There's a 1/999999999 chance of a collision. Whoops.
        filepath = os.path.join(directory, str(filename))
        logging.debug("Recording to %s...", filepath)
        recording = sd.rec(
            int(seconds * sample_rate), samplerate=sample_rate, channels=2
        )
        time.sleep(seconds)  # To avoid writing to the file while it is being recorded
        wavwrite(filepath, sample_rate, recording)

        # Helps to avoid a race condition where the file is read/attempted to be transcribed before it is written
        file_written_event.set()
        logging.debug("File written to %s!", filepath)

        # Put the filename into the queue
        filename_queue.put(filename)


def process_audio(loaded_whisper_model):
    while True:
        filename = filename_queue.get()
        file_written_event.wait()
        transcription = loaded_whisper_model.transcribe(f"temp_recordings/{filename}")
        logging.debug("Transcription: " + transcription["text"])
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
            logging.debug("Badwords detected! " + str(detected_badwords))


if __name__ == "__main__":
    config = load_config()
    whisper_model = init_whisper(config)
    recorder_seconds = config["recorder"]["seconds"]

    # Create two threads, one for each task
    record_thread = threading.Thread(target=record_audio, args=(recorder_seconds,))
    process_thread = threading.Thread(target=process_audio, args=(whisper_model,))
    check_thread = threading.Thread(target=check_badwords_string)

    # Start the threads!!!
    record_thread.start()
    process_thread.start()
    check_thread.start()
