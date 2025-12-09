import os
import io
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import config


class Environment:
    def __init__(self):
        self.client = ElevenLabs(api_key=config.API_KEY)
        # Adam, for a standard
        self.agent_voice_id = config.VOICE_ID

    def listen_to_user(self, duration=5):
        """
        Records the user's microphone for a fixed duration, 
        then sends the audio to ElevenLabs Scribe for transcription.
        """
        print(f"--- Listening for {duration} seconds... ---")

        # sample audio rate 44100Hz
        sample_rate = 44100
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # wait until recording is finished
        print("Processing speech...")

        # Numpy Array to temporary WAV file in memory (virtual), as BytesIO lets us not save to disk
        virtual_file = io.BytesIO()
        wav.write(virtual_file, sample_rate, audio_data)
        virtual_file.seek(0)  # tells python to play the audio file from the beninging
        virtual_file.name = "input.wav"

        # ElevenLabs STT
        try:
            transcription = self.client.speech_to_text.convert(
                file=virtual_file,
                model_id="scribe_v1",  # this is the model for STT
                tag_audio_events=True,  # we want the laughter, or sign sounds
                language_code='eng',
                diarize=False
            )

            # turning it into a string to be safe
            user_text = str(transcription.text)
            print(f"User said: {user_text}")
            return user_text

        except Exception as e:
            print(f"Error hearing user: {e}")
            return ""

    def speak_to_user(self, text):
        """
        Takes text input and plays it aloud using ElevenLabs TTS.
        Used for both 'Hard-coded' reflexes and 'Agent' responses.
        """
        if not text:
            return

        print(f"Agent saying: {text}")
        try:
            # get the audio from the text
            audio_stream = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.agent_voice_id,
                model_id="eleven_multilingual_v2"  # low latency model (allegedly, I have not played around with this)
            )

            # play the audio immediately, no waiting (at least for now)
            play(audio_stream)

        except Exception as e:
            print(f"Error speaking: {e}")


# example usage (how we can call in the Game Loop)
if __name__ == "__main__":
    env = Environment()

    # testing TTS
    env.speak_to_user("System check complete. I am ready to listen.")

    # testing STT (on actual input)
    user_input = env.listen_to_user(duration=4)
    # we could add some trigger to this: press key, or some game event, for the Environment to start listening to the user
    # (ominous wording, I know)