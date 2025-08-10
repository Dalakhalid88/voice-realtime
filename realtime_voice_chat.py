import os, re, subprocess
import sounddevice as sd
from scipy.io.wavfile import write as wav_write
import whisper, cohere
from gtts import gTTS

SAMPLE_RATE=16000
CHANNELS=1
SECONDS=5
TMP_WAV="mic_input.wav"
TTS_MP3="bot_reply.mp3"
AR=re.compile(r"[\u0600-\u06FF]")

def rec():
    a=sd.rec(int(SECONDS*SAMPLE_RATE),samplerate=SAMPLE_RATE,channels=CHANNELS,dtype='int16')
    sd.wait()
    wav_write(TMP_WAV,SAMPLE_RATE,a)
    return TMP_WAV

_model=[None]
def stt(p):
    if _model[0] is None: _model[0]=whisper.load_model("base")
    r=_model[0].transcribe(p,fp16=False)
    return (r.get("text") or "").strip()

def llm(t):
    c=cohere.Client(os.getenv("COHERE_API_KEY"))
    try:
        r=c.chat(message=t,preamble="You are a helpful AI assistant. Answer briefly (<= 20 words).",model="command")
        return r.text.strip()
    except:
        g=c.generate(model="command",prompt=f"You are a helpful assistant. Reply shortly to:\n\n{t}\n\nAnswer:",max_tokens=180,temperature=0.7)
        return g.generations[0].text.strip()

def tts(txt):
    lang="ar" if AR.search(txt) else "en"
    gTTS(text=txt,lang=lang).save(TTS_MP3)
    subprocess.run(["afplay",TTS_MP3],check=False)

def main():
    print("Press Enter to record, type q then Enter to quit.")
    while True:
        cmd=input()
        if cmd.strip().lower()=="q": break
        wav=rec()
        text=stt(wav)
        if not text: 
            print("Could not understand. Try again."); 
            continue
        print("You said:",text)
        ans=llm(text)
        print("Bot:",ans)
        print("SYNTHESIS FINISHED")
        tts(ans)

if __name__=="__main__":
    main()