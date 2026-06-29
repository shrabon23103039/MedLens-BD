from gtts import gTTS
import os
import tempfile

def generate_audio(bengali_text):
    try:
        tts = gTTS(text=bengali_text, lang='bn', slow=False)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        tts.save(tmp.name)
        return tmp.name
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

if __name__ == "__main__":
    print("Testing Bengali TTS...")
    path = generate_audio("আপনার ওষুধ সঠিকভাবে খান এবং সুস্থ থাকুন।")
    if path:
        print(f"✅ Audio saved to: {path}")
    else:
        print("❌ TTS failed")