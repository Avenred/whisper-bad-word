import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import os
import random
from colorama import Fore, Back
import pyttsx3

engine = pyttsx3.init()

endphrase = ""


def record_and_save():
    #    print("Recording...")  # debug
    fs = 44100  # Sample rate
    seconds = 5  # Duration of recording
    recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    #    print("Saving...")  # debug
    # pick a random name for the file
    global random_name
    random_name = str(random.randint(0, 999999999))
    write(random_name, fs, recording)  # Save as WAV file


def load_model():
    global endphrase
    print('Model loading...')
    global model
    model = whisper.load_model('tiny.en')
    print('Loaded!\n')
    endphrase = input("Saying the following phrase ends the program: ").lower()
    engine.say("I am ready to RUMBLE")
    engine.runAndWait()


def whisper_transcribe():
    #    print('Transcribing...')  # debug
    result = model.transcribe(random_name)
    global transcribed
    transcribed = str(result['text'])
    # now delete the file
    os.remove(random_name)


def on_bad_word():
    engine.say("Naughty Naughty")
    engine.runAndWait()


def check_for_badwords(bad_words_file: str = "bad_words.txt",
                       end_word: str = "kill me now",
                       catch_reg: bool = False):
    # I would like to load a .txt file with a list of bad words
    # and check if the transcribed text contains any of them
    #    print('Checking for bad words...')  # debug

    try:
        BadWordFile = open(bad_words_file, "r")
        BadWords = BadWordFile.read()
        BadWordFile.close()
    except FileNotFoundError:
        print("File not found\nCreating one...")
        BadWordFile = open(bad_words_file, "w")
        BadWordFile.write("Default")
        BadWordFile.close()
    BadWords = BadWords.split('\n')[0::-1]

    lower_transcribed = transcribed.lower()
    for i in range(0, len(BadWords)):
        try:  # if bad word is found
            result = lower_transcribed.index(BadWords[i])
            if catch_reg:
                print(
                    f"{Back.RED}{Fore.WHITE}BAD WORD FOUND! Index: {result} -> {transcribed}{Back.RESET}{Fore.RESET}                      {' ' * len(str(result))}     {' ' * result}^"
                )

            else:
                if lower_transcribed[result - 1] == ' ' and lower_transcribed[
                        result + len(BadWords[i])] == ' ':
                    print(
                        f'{Back.GREEN}{Fore.BLACK}OK: {transcribed}{Back.RESET}{Fore.RESET}'
                    )
                else:
                    print(
                        f"{Back.RED}{Fore.WHITE}BAD WORD FOUND! Index: {result} -> {transcribed}{Back.RESET}{Fore.RESET}\n                      {' ' * len(str(result))}     {' ' * result}^"
                    )
                    engine.say("Naughty Naughty")
                    engine.runAndWait()
        except ValueError:  # if nice and clean
            print(
                f'{Back.GREEN}{Fore.BLACK}OK: {transcribed}{Back.RESET}{Fore.RESET}'
            )
        try:  # if end word is found
            result = lower_transcribed.index(end_word)
            print(
                f"{Fore.BLACK}{Back.GREEN}Ending words detected. Exiting gracefully.{Fore.RESET}{Back.RESET}"
            )
            exit(0)
        except ValueError:
            continue


load_model()

while True:
    record_and_save()
    whisper_transcribe()
    check_for_badwords(end_word=endphrase)
