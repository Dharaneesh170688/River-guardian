import os
import base64
import requests
import subprocess
import tempfile
import sys
from dotenv import load_dotenv

# Try to import winsound (standard on Windows)
try:
    import winsound
except ImportError:
    winsound = None

load_dotenv()

# Translate the alert message into the supported languages
TRANSLATIONS = {
    "english": "Possible drowning detected. Please assist immediately.",
    "hindi": "संभावित डूबने की घटना पाई गई है। कृपया तुरंत सहायता करें।",
    "tamil": "சாத்தியமான நீரில் மூழ்கும் விபத்து கண்டறியப்பட்டுள்ளது. தயவுசெய்து உடனடியாக உதவுங்கள்.",
    "kannada": "ನೀರಿನಲ್ಲಿ ಮುಳುಗುವ ಸಾಧ್ಯತೆ ಪತ್ತೆಯಾಗಿದೆ. ದಯವಿಟ್ಟು ತಕ್ಷಣ ಸಹಾಯ ಮಾಡಿ."
}

# Map language names to Sarvam API codes
LANGUAGE_MAP = {
    "english": "en-IN",
    "hindi": "hi-IN",
    "tamil": "ta-IN",
    "kannada": "kn-IN"
}

class SarvamAlertSystem:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.endpoint = "https://api.sarvam.ai/text-to-speech"
        
        if self.api_key:
            print("[Sarvam] API Key loaded. TTS API active.")
        else:
            print("[Sarvam] No API Key (SARVAM_API_KEY). Offline fallback voice will be used.")

    def play_wav(self, file_path: str):
        """Plays a WAV file using winsound or standard PowerShell command."""
        if winsound:
            try:
                winsound.PlaySound(file_path, winsound.SND_FILENAME)
                return True
            except Exception as e:
                print(f"[Sarvam] winsound play failed: {e}")
        
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["powershell", "-c", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"],
                    capture_output=True,
                    check=True
                )
                return True
        except Exception as e:
            print(f"[Sarvam] Audio playback failed: {e}")
        return False

    def speak_local_fallback(self, text: str, language: str = "english"):
        """Uses Windows native PowerShell SpeechSynthesizer to read out the alert text."""
        try:
            print(f"[Sarvam-Fallback] Speech alert: '{text}' in language: {language}")
        except UnicodeEncodeError:
            print(f"[Sarvam-Fallback] Speech alert in language: {language} (text hidden due to console encoding)")
        
        # PowerShell speech synthesis
        escaped_text = text.replace("'", "''")
        ps_script = (
            f"Add-Type -AssemblyName System.Speech; "
            f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$synth.Speak('{escaped_text}')"
        )
        try:
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True, check=True)
            return True
        except Exception as e:
            print(f"[Sarvam-Fallback] PowerShell speech failed: {e}")
            
        # If powershell fails, try importing pyttsx3
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            print(f"[Sarvam-Fallback] pyttsx3 speech failed: {e}")
            
        return False

    def trigger_alert(self, language: str = "english") -> bool:
        """
        Triggers the voice alert for EMERGENCY states.
        Uses the pre-translated warning message and contacts Sarvam API or uses offline TTS.
        """
        lang = language.lower()
        if lang not in TRANSLATIONS:
            lang = "english"
            
        text_to_speak = TRANSLATIONS[lang]
        lang_code = LANGUAGE_MAP.get(lang, "en-IN")
        
        if not self.api_key:
            return self.speak_local_fallback(text_to_speak, lang)

        payload = {
            "inputs": [text_to_speak],
            "target_language_code": lang_code,
            "speaker": "anushka",
            "speech_rate": 1.0,
            "pitch": 0.0,
            "model": "bulbul:v1"
        }
        
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            print(f"[Sarvam] Requesting TTS API in {lang_code}...")
            response = requests.post(self.endpoint, json=payload, headers=headers, timeout=8)
            
            if response.status_code == 200:
                res_data = response.json()
                audio_base64 = res_data.get("audio_content")
                if audio_base64:
                    audio_bytes = base64.b64decode(audio_base64)
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        f.write(audio_bytes)
                        temp_path = f.name
                    
                    try:
                        print(f"[Sarvam] Playing returned TTS audio...")
                        self.play_wav(temp_path)
                    finally:
                        try:
                            os.unlink(temp_path)
                        except OSError:
                            pass
                    return True
                else:
                    print("[Sarvam] Empty audio_content returned.")
            else:
                print(f"[Sarvam] API error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"[Sarvam] Connection error: {e}")

        # Fallback to local TTS
        return self.speak_local_fallback(text_to_speak, lang)
