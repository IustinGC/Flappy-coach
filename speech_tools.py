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
        self.agent_voice_id = config.VOICE_ID
        self.model_id_speak = config.MODEL_ID_SPEAK
        self.model_id_listen = config.MODEL_ID_LISTEN

        self.tts_payload_queue = queue.Queue()
        self.stt_result_queue = queue.Queue()

        self.is_listening = False
        self.is_generating_tts = False

        self.reflex_channel_id = 0
        self.agent_channel_id = 1

        self.last_speech_finish_time = 0.0
        self.SPEECH_COOLDOWN_SECONDS = 1.0

        # Flag to indicate if we forcibly stopped recording to speak
        self.listening_interrupted = False

    @property
    def is_speaking(self):
        if self.is_generating_tts:
            return True
        if pygame.mixer.get_init():
            llm_busy = pygame.mixer.Channel(self.agent_channel_id).get_busy()
            reflex_busy = pygame.mixer.Channel(self.reflex_channel_id).get_busy()
            return llm_busy or reflex_busy
        return False

    def update(self):
        if self.is_speaking:
            self.last_speech_finish_time = time.time()

        while not self.tts_payload_queue.empty():
            try:
                audio_bytes = self.tts_payload_queue.get_nowait()
                self._play_audio_bytes(audio_bytes)
                self.is_generating_tts = False
            except queue.Empty:
                pass

    def get_latest_input(self):
        if not self.stt_result_queue.empty():
            return self.stt_result_queue.get()
        return None

    def speak_to_user(self, text):
        if not text: return

        # --- FIX: PRIORITY INTERRUPT ---
        # If we are about to speak, we MUST stop listening immediately.
        # Otherwise, we will record our own voice.
        if self.is_listening:
            self.stop_listening()

        self.is_generating_tts = True
        print(f"(SPEAKING) Agent queuing speech: {text}")
        threading.Thread(target=self._thread_fetch_tts, args=(text,), daemon=True).start()

    def stop_listening(self):
        """
        Forces the recording thread to stop and discard input.
        """
        if self.is_listening:
            print("[System] Priority Interrupt: Stopping microphone to speak.")
            self.listening_interrupted = True
            try:
                sd.stop()  # Stops the stream in the background thread
            except Exception as e:
                print(f"Error stopping stream: {e}")

    def listen_to_user(self, duration=4):
        if self.is_speaking: return False
        if self.is_listening: return False

        time_since_speech = time.time() - self.last_speech_finish_time
        if time_since_speech < self.SPEECH_COOLDOWN_SECONDS:
            return False

        self.is_listening = True
        self.listening_interrupted = False  # Reset flag

        print(f"(LISTENING) Agent listening ({duration}s)...")
        threading.Thread(target=self._thread_record_stt, args=(duration,), daemon=True).start()
        return True

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
            self.is_generating_tts = False

    def _thread_record_stt(self, duration):
        try:
            sample_rate = 44100
            # blocking=True will be interrupted by sd.stop() in main thread
            audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16',
                                blocking=True)

            # --- FIX: CHECK INTERRUPTION ---
            # If main thread flagged interruption, we DISCARD this recording.
            if self.listening_interrupted:
                print("[System] Discarding recording (Interrupted by Agent Speech)")
                return

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
            # If sd.stop() caused an error or other issue
            if not self.listening_interrupted:
                print(f"XXXX STT Error: {e}")
        finally:
            self.is_listening = False

    def _play_audio_bytes(self, audio_data):
        try:
            sound_file = io.BytesIO(audio_data)
            sound = pygame.mixer.Sound(sound_file)
            pygame.mixer.Channel(self.agent_channel_id).play(sound)
        except Exception as e:
            print(f"XXXX Playback Error: {e}")