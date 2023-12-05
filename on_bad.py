import pyttsx3
import logging

logging.getLogger("comtypes").setLevel(logging.CRITICAL)

def on_bad_word(badwords_exist: bool, detected_badwords: list, transcription: str):
    engine = pyttsx3.init()
    if badwords_exist:
        engine.say(f"You said {detected_badwords[0]}. Idiot.")
        engine.runAndWait()
    else:
        pass
