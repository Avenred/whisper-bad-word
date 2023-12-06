import pyttsx3
import logging
from colorama import Fore

logging.getLogger("comtypes").setLevel(logging.CRITICAL)


def on_bad_word(badwords_exist: bool, detected_badwords: list, transcription: str):
    engine = pyttsx3.init()
    if badwords_exist:
        print(Fore.RED + f"{str(transcription)}")
        print(Fore.RED + f"You said {detected_badwords[0]}. Idiot.")
        engine.say(f"You said {detected_badwords[0]}. Idiot.")
        engine.runAndWait()
    else:
        print(Fore.GREEN + f"{str(transcription)}")
