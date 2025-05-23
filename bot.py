from gpiozero import Button # needed for push to talk control

from openai import OpenAI # needed for calling OpenAI Audio API
import yaml # needed for config
import time # needed for sleep

import sounddevice as sd # needed to control the microphone
import soundfile as sf # needed to create the audio files
import queue # needed for making the queue that handles real time audio
import sys # needed for file status

from adafruit_servokit import ServoKit # needed for servo movements
import threading # needed for threading

from elevenlabs.client import ElevenLabs # needed for ElevenLabs API / deepfake audio
from elevenlabs import play # needed for ElevenLabs API / deepfake audio

import pygame # needed for audio
pygame.init()

class DeepfakeBot:
    """
    Class that handles the main functionality of the Deepfake Bot
    """

    def __init__(self):
        """
        Initialization method
        """

        # load config settings
        with open("./configs/billing.yaml", "r") as ymlfile:
            config = yaml.safe_load(ymlfile)

        # load openAI keys into client
        self.client = OpenAI(api_key=config["openai"]["API_KEY"])

        # load context settings
        with open("./configs/context.yaml", "r") as ctxfile:
            context = yaml.safe_load(ctxfile)

        self.personality = context["llm"]["PERSONALITY"]
        self.panTiltDes = context["llm"]["PANTILT_DESCRIPTION"]
        self.waitDes = context["llm"]["WAIT_DESCRIPTION"]
        self.textDes = context["llm"]["TEXT_DESCRIPTION"]

        # ElevenLabs variables
        self.elevenLabsClient = ElevenLabs(api_key=config["elevenlabs"]["API_KEY"])
        self.deepfakeVoice = config["elevenlabs"]["VOICE_ID"]

        # audio variables
        self.recordStatus = False # boolean for if the audio is being saved
        self.queue = queue.Queue()
        self.button = Button("BOARD12")

        # setup microphone
        self.deviceInfo = sd.query_devices(kind='input')

        # setup servo kit
        self.kit = ServoKit(channels=16)
        self.oldPanAngle = 90
        self.oldTiltAngle = 90

        # Note these values will change depending on what servos you are using
        self.kit.servo[0].actuation_range = 270
        self.kit.servo[0].set_pulse_width_range(500, 2500)
        self.kit.servo[1].set_pulse_width_range(500, 2500)
        
        print("init servos")
        self.kit.servo[0].angle = 90
        self.kit.servo[1].angle = 90
        time.sleep(1)
        print("Initalization finished")

    def slowPanTilt(self, panAngle, tiltAngle):
        """
        Slowly moves the servos to the desired angles

        Args:
            panAngle (int): The angle to move the pan servo to
            tiltAngle (int): The angle to move the tilt servo to
        """

        # calculate the difference between the current and desired angles
        panDiff = panAngle - self.oldPanAngle
        tiltDiff = tiltAngle - self.oldTiltAngle

        # move the servos in small increments
        for i in range(0, 100, 5):
            self.kit.servo[0].angle = self.oldPanAngle + (panDiff * i / 100)
            self.kit.servo[1].angle = self.oldTiltAngle + (tiltDiff * i / 100)
            time.sleep(0.025)

        # update the old angles
        self.oldPanAngle = panAngle
        self.oldTiltAngle = tiltAngle

    def transcribeAudio(self):
        """
        Transcribes the recorded audio into a text string and returns it

        Returns:
            str: The text representing all speech recorded by the audio file
        """

        # check the file size to make sure audio file is long enough
        f = sf.SoundFile("request.wav")

        #print(f"Runtime = {str(f.frames / f.samplerate)}")

        if (f.frames / f.samplerate) > 0.1:
            audio_file = open("request.wav", "rb")
            transcript = self.client.audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=audio_file, response_format="text")

            return str(transcript)
        else:
            return "Error, recording was too short"
        
    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.queue.put(indata.copy())
        
    def piListener(self):
        """
        records mic while button is pressed, and stops while released
        """
        
        print("press button to record")
        
        sampleRate = int(self.deviceInfo['default_samplerate'])
        with sf.SoundFile(file="request.wav", mode='w', samplerate=sampleRate, channels=1, subtype='PCM_16') as file:
            with sd.InputStream(samplerate=sampleRate, channels=1, callback=self.callback):
                while True:
                    if self.button.is_pressed:
                        self.recordStatus = True
                        file.write(self.queue.get())
                    elif not self.button.is_pressed and self.recordStatus:
                        self.recordStatus = False
                        print("Finished recording")
                        file.close()
                        break
                    elif not self.queue.empty():
                            #print("clearing queue")
                            self.queue.get()


    def deepFakeAudio(self, text):
        """
        Turns the provided text into audio and plays it

        Args:
            text (str): The text to turn to audio
        """

        audio = self.elevenLabsClient.text_to_speech.convert(
            text=text,
            voice_id=self.deepfakeVoice,
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128",
        )
        play(audio)

    def textToSpeech(self, text):
        """
        Turns the provided text into audio and plays it

        Args:
            text (str): The text to turn to audio
        """

        # TODO: change this to elevenlabs API 

        with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=text,
            instructions="Speak in a cheerful and positive tone.",
        ) as response:
            response.stream_to_file("response.mp3")

        #time.sleep(1)

        # plays the response
        channel = pygame.mixer.Sound('response.mp3').play()

        # wait for file to finish playing
        while channel.get_busy():
            pygame.time.wait(100) # wait 100 ms

    def callLLM(self, question):
        """
        passes the given question to the LLM

        Args:
            question (str): The string representing the user question
        """
        
        movementString = ""

        completion = self.client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": f"{str(self.personality)}"},
            {"role": "system", "content": f"{str(self.panTiltDes)}"},
            {"role": "system", "content": f"{str(self.waitDes)}"},
            {"role": "system", "content": f"{str(self.textDes)}"},
            {"role": "system", "content": "You may combine and chain commands together however each command must be on a new line, and only one command is allowed per line.  The command should be the only thing on the line, nothing else.  Do not respond with anything other than commands, and do not abbreviate or title the commands anything other than what has been provided to you.  "},
            {"role": "system", "content": "Using these formatting instructions, try to answer the following question from the user."},
            {"role": "user", "content": f"{str(question)}"}
        ]
        )

        output = str(completion.choices[0].message.content)
        print("")
        print(output)
        
        lines = [line.strip() for line in output.split("\n")]

        for i in range(len(lines)):

            message = lines[i].replace("[","").replace("]","")
            #print(message)
            if len(message) > 0: # make sure line isn't empty
                if message.startswith("TEXT"):
                    #print("text")
                    message = message.split(',', 1)[1] # gets rid of the TEXT part of the message
                    #self.textToSpeech(message) # sends the message to the text to speech function
                    self.deepFakeAudio(message) # sends the message to the deepfake audio function
                elif message.startswith("WAIT"):
                    #print("wait")
                    message = message.split(", ", 1)[1]
                    
                    try:
                        time.sleep(float(message))
                    except ValueError:
                        print("Sleep time unable to be turned into float")
                elif message.startswith("PANTILT"):
                    #print("pan/tilt")
                    print(f"Pan/Tilt message sent: {str(message)}")

                    message = message.split(", ", 1)[1]
                    message = message.split(",")
                    
                    panAngle = int(message[0])
                    tiltAngle = int(message[1])
                    #print(f"Pan/Tilt angles: {str(panAngle)}, {str(tiltAngle)}")
                    self.slowPanTilt(panAngle, tiltAngle)
                else:
                    print("Error, unknown message generated, possible hallucination.  ")
                    print(f"Message: {str(message)}")

if __name__ == '__main__':
    deepFakeBot = DeepfakeBot()

    while True:
        deepFakeBot.piListener()
        text = deepFakeBot.transcribeAudio()
        deepFakeBot.callLLM(text)