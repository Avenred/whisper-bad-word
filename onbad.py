from threading import Thread
from colorama import Fore, Back, Cursor
import whisper
import sounddevice as sd
from scipy.io.wavfile import write
import os
from platform import system as system_os
import random
import onbad


class BadFinder:
    endphrase   = ""
    catch       = ""
    model       = ""
    transcribed = ""
    random_name = ""
    ready       = False # ready, check, and done are for communication between the threads
    done        = False
    check       = False

    Running = True # for stopping the thread

    custom_file = ""

    def __init__(self,
                 custom_script_file: str = None,
                 custom_script_str: str = None,
                 use_custom: bool = True):
        self.custom_c = use_custom

        self.load_model()
        self.setup()

        if system_os() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

        if use_custom:
            if custom_script_file != None:
                if custom_script_file.endswith(".py"):
                    self.bad_c = __import__(custom_script_file[0:-3])
                else:
                    raise ValueError(
                        'A python file must be used for a custom script.')
            elif custom_script_str != None:
                with open("Default_name.py", "a") as PythonScriptFile_mw:
                    PythonScriptFile_mw.close()
                with open("Default_name.py", "w") as PythonScriptFile:
                    PythonScriptFile.write(custom_script_str)
                    PythonScriptFile.close()
                self.bad_c = __import__("Default_name")
            else:
                raise ValueError('No script was specified.')
        else:
            pass

    def load_model(self):
        print('Model loading...')
        self.model = whisper.load_model('tiny.en')
        print('Loaded!\n')

    def setup(self):
        self.endphrase = input(
            "Saying the following phrase ends the program: ").lower()
        use_catch_reg = input(
            "Use fuzzy mode?\nAny word containing the bad words will be caught \nEx: \"thing\" will be caught in \"anything\"\ny/n >>> "
        )[0].lower()
        self.custom_file = input(
            "If you have a custom set of bad words input the file name (leave blank to use the default) >>> "
        )
        if self.custom_file == "":
            self.custom_file = "bad_words.txt"
        if use_catch_reg == "y":
            self.catch = True
        else:
            self.catch = False

    def whisper_transcribe(self):
        while self.Running:
            if self.done:
                try:
                    print(f"{Cursor.POS(1, 2)}Whisper Stauts: {Fore.BLACK}{Back.GREEN}Transcribing{Fore.RESET}{Back.RESET}")
                    #    print('Transcribing...')  # debug
                    result = self.model.transcribe(self.random_name)
                    transcribed = str(result['text'])
                    # now delete the file
                    os.remove(self.random_name)
                    self.transcribed = transcribed
                    print(f"{Cursor.POS(1, 2)}Whisper Stauts: {Fore.BLACK}{Back.RED}Waiting{Fore.RESET}{Back.RESET}                  ")
                    while self.check:
                        pass # waits until the check thread is ready to accept the next string
                    self.ready = True
                    self.done = False
                    self.check = True
                    print(f"{Cursor.POS(1, 2)}Whisper Stauts: {Fore.BLACK}{Back.RED}Idle{Fore.RESET}{Back.RESET}            ")
                except Exception as e:
                    print(f"Whisper: {e}")
                    self.Running = False

    def record_and_save(self, duration: int = 10, sample_rate: int = 44100):
        while self.Running:
            if self.ready:
                try:
                    print(f"{Cursor.POS(1, 1)}Recording Stauts: {Fore.BLACK}{Back.GREEN}Recording{Fore.RESET}{Back.RESET}")
                    #    print("Recording...")  # debug
                    recording = sd.rec(int(duration * sample_rate),
                                       samplerate=sample_rate,
                                       channels=2)
                    print(f"{Cursor.POS(1, 1)}Recording Stauts: {Fore.BLACK}{Back.GREEN}Waiting{Fore.RESET}{Back.RESET}")
                    sd.wait()  # Wait until recording is finished
                    #    print("Saving...")  # debug
                    # pick a random name for the file
                    self.random_name = str(random.randint(0, 999999999))
                    print(f"{Cursor.POS(1, 1)}Recording Stauts: {Fore.BLACK}{Back.GREEN}Saving{Fore.RESET}{Back.RESET}                ")
                    write(self.random_name, sample_rate, recording)  # Save as WAV file
                    self.done = True
                    self.ready = False
                    print(f"{Cursor.POS(1, 1)}Recording Stauts: {Fore.BLACK}{Back.RED}Idle{Fore.RESET}{Back.RESET}              ")
                except Exception as e:  # NO MORE BARE EXCEPT I AM GOING TO KILL YOU
                    print(f"Recorder: {e}")
                    self.Running = False

    def bad_word_action(self, transcribed: str = None):
        if self.custom_c:
            self.bad_c.custom(transcribed)  # might work, im not sure
        else:
            self.default_check(transcribed=transcribed)

    # You can place any custom code into a function named "custom". The class will import this and use it whenever running your custom script.

    def begin(self, sample_rate: int=44100, duration: int=10):
        record_thread     = Thread(target=self.record_and_save, args=(duration, sample_rate,))
        transcribe_thread = Thread(target=self.whisper_transcribe, args=())
        check_thread      = Thread(target=self.check, args=())
        self.done = False
        self.ready = True
        self.check = False # for checking the previous while recording the new one

        print(f"{Cursor.POS(1, 1)}Recording Stauts: {Fore.BLACK}{Back.RED}Idle{Fore.RESET}{Back.RESET}")
        print(f"{Cursor.POS(1, 2)}Whisper Stauts: {Fore.BLACK}{Back.RED}Idle{Fore.RESET}{Back.RESET}")
        print(f"{Cursor.POS(1, 3)}Checker Stauts: {Fore.BLACK}{Back.RED}Idle{Fore.RESET}{Back.RESET}")

        record_thread.start()
        transcribe_thread.start()
        check_thread.start()

    def check(self):
        transcribed = self.transcribed
        bad_words_file = self.custom_file
        catch_reg = self.catch
        end_word  = self.endphrase

        badwords = None
        try:
            badwordfile = open(bad_words_file, "r")
            badwords = badwordfile.read()
            badwordfile.close()
        except FileNotFoundError:
            print("File not found\nCreating one...")
            badwordfile = open(bad_words_file, "w")
            badwordfile.write("Default")
            badwordfile.close()

        if badwords is None:
            badwords = badwords.split('\n')[0::-1]
        else:
            badwords = ["Default"]

        while self.Running:
            if self.check:
                try:
                    print(f"{Cursor.POS(1, 3)}Checker Stauts: {Fore.BLACK}{Back.GREEN}Checking{Fore.RESET}{Back.RESET}")
                    # I would like to load a .txt file with a list of bad words
                    # and check if the transcribed text contains any of them
                    #    print('Checking for bad words...')  # debug

                    # everything should work now...
                    # hopefully i did everything right.

                    lower_transcribed = transcribed.lower()
                    for i in range(0, len(badwords)):
                        try:  # if bad word is found
                            result = lower_transcribed.index(badwords[i])
                            if catch_reg:  # if fuzzy mode
                                self.bad_c.custom(False)

                            else:  # if not fuzzy
                                if lower_transcribed[result -
                                                     1] == ' ' and lower_transcribed[
                                                         result + len(badwords[i])] == ' ':
                                    self.bad_c.custom(True)
                                else:  # if not fuzzy + bad word used
                                    #print(
                                    #    f"{Back.RED}{Fore.WHITE}Index: {result} -> {transcribed}{Back.RESET}{Fore.RESET}\n      {' ' * len(str(result))}     {' ' * result}^"
                                    #) # too beautifull to remove
                                    self.bad_c.custom(False)
                        except (ValueError, IndexError):  # if nice and clean
                            self.bad_c.custom(True)
                        try:
                            lower_transcribed.index(end_word)
                            print(
                                f"{Fore.BLACK}{Back.GREEN}Ending words detected. Exiting gracefully.{Fore.RESET}{Back.RESET}"
                            )
                            self.Running = False
                        except ValueError:
                            continue
                    self.check = False
                    print(f"{Cursor.POS(1, 2)}Checker Stauts: {Fore.BLACK}{Back.RED}Idle{Fore.RESET}{Back.RESET}       ")
                except Exception as e:
                    print(f"Checker: {e}")
                    self.Running = False
