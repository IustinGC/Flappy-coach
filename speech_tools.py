import threading
import queue
import io
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import pygame
from elevenlabs.client import ElevenLabs
import config

class Environment:
    def __init__(self):
        self.client = ElevenLabs(api_key=config.EL_API_KEY)
        self.agent_voice_id = config.VOICE_ID # Olga, cus we cool
        self.model_id_speak = config.MODEL_ID_SPEAK
        self.model_id_listen= config.MODEL_ID_LISTEN
        
        # --- Asynchronous Communication Queues ---
        self.tts_payload_queue = queue.Queue() # Holds audio bytes ready to play
        self.stt_result_queue = queue.Queue()  # Holds transcribed text from user
        
        # --- State Flags ---
        self.is_listening = False
        self.is_generating_tts = False # True when downloading audio (before playing)
        
        # --- Audio Channels ---
        # Channel 0 is reserved for 'Reflexes' (flap.py / agent_audio_manager)
        # Channel 1 is reserved for 'LLM Agent' (this file)
        self.reflex_channel_id = 0
        self.agent_channel_id = 1 

    @property
    def is_speaking(self):
        """
        Returns True if the Agent is EITHER generating text OR playing audio.
        Crucially, checks BOTH the LLM channel and the Hard-coded Reflex channel.
        """
        # 1. Is Python currently downloading audio?
        if self.is_generating_tts:
            return True
            
        # 2. Is Pygame playing audio?
        if pygame.mixer.get_init():
            llm_busy = pygame.mixer.Channel(self.agent_channel_id).get_busy()
            reflex_busy = pygame.mixer.Channel(self.reflex_channel_id).get_busy()
            return llm_busy or reflex_busy
            
        return False

    def update(self):
        """
        Must be called every frame to process background threads.
        """
        # Handle Incoming TTS Audio (Agent finished generating speech)
        while not self.tts_payload_queue.empty():
            try:
                audio_bytes = self.tts_payload_queue.get_nowait()
                # Generation is done, now we play (which sets get_busy() to True)
                self.is_generating_tts = False 
                self._play_audio_bytes(audio_bytes)
            except queue.Empty:
                pass

    def get_latest_input(self):
        """
        Non-blocking check for user input.
        Returns text string if STT just finished, otherwise None.
        """
        if not self.stt_result_queue.empty():
            return self.stt_result_queue.get()
        return None

    # --- Public Methods ---

    def speak_to_user(self, text):
        """
        Starts a background thread to fetch audio. Non-blocking.
        """
        if not text: return
        
        # Set Lock IMMEDIATELY so we don't try to listen while downloading
        self.is_generating_tts = True
        print(f"(SPEAKING) Agent queuing speech: {text}")
        
        threading.Thread(target=self._thread_fetch_tts, args=(text,), daemon=True).start()

    def listen_to_user(self, duration=4):
        """
        Starts a background thread to record. 
        Returns True if started, False if rejected (because agent is speaking).
        """
        # If agent is speaking/generating, we REJECT the listen request.
        if self.is_speaking: return False

        if self.is_listening: return False

        self.is_listening = True
        print(f"(LISTENING) Agent listening ({duration}s)...")
        
        threading.Thread(target=self._thread_record_stt, args=(duration,), daemon=True).start()
        return True

    # --- Internal Background Threads ---

    def _thread_fetch_tts(self, text):
        try:
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.agent_voice_id,
                model_id=self.model_id_speak
            )
            audio_data = b"".join(chunk for chunk in audio_generator)
            self.tts_payload_queue.put(audio_data)
        except Exception as e:
            print(f"XXXX TTS Error: {e}")
            self.is_generating_tts = False # Release lock on error

    def _thread_record_stt(self, duration):
        try:
            sample_rate = 44100
            # blocking=True is fine HERE because we are in a background thread
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16', blocking=True)
            
            virtual_file = io.BytesIO()
            wav.write(virtual_file, sample_rate, audio_data)
            virtual_file.seek(0)
            virtual_file.name = "input.wav"

            transcription = self.client.speech_to_text.convert(
                file=virtual_file,
                model_id=self.model_id_listen,
                tag_audio_events=True,
                language_code='eng'
            )
            
            user_text = str(transcription.text).strip()
            print(f"(USER) User said: {user_text}")
            self.stt_result_queue.put(user_text)

        except Exception as e:
            print(f"XXXX STT Error: {e}")
        finally:
            self.is_listening = False

    def _play_audio_bytes(self, audio_data):
        try:
            sound_file = io.BytesIO(audio_data)
            sound = pygame.mixer.Sound(sound_file)
            # Play on Channel 1 (leaving Channel 0 free for game sounds)
            pygame.mixer.Channel(self.agent_channel_id).play(sound)
        except Exception as e:
            print(f"XXXX Playback Error: {e}")