from ttsfm import TTSClient, Voice, AudioFormat
import subprocess
import os

client = TTSClient()

def holaSpeak(text):
    try:
        resp = client.generate_speech(text=text, voice=Voice.ALLOY, response_format=AudioFormat.MP3, validate_length=False)
        resp.save_to_file("hola.mp3")

        subprocess.run(["mpv", "--no-terminal", "hola.mp3"])
        
        os.remove("hola.mp3")
          
    except Exception as e:
        with open("audioError.txt", "a") as f:
            f.write(f"{e}")