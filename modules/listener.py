import sounddevice as sd
import vosk
import json
import queue
import numpy as np
import sys

q = queue.Queue()

def callback(indata, frames, time, status):
    """Callback function to continuously capture audio data"""
    if status:
        print(f"[Audio Status]: {status}", file=sys.stderr)
    q.put(bytes(indata))

def list_audio_devices():
    """List all available audio input devices"""
    print("\n=== Available Audio Devices ===")
    devices = sd.query_devices()
    input_devices = []
    
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append(idx)
            default = " [DEFAULT]" if idx == sd.default.device[0] else ""
            print(f"Device {idx}: {device['name']}{default}")
            print(f"  Channels: {device['max_input_channels']}, Rate: {device['default_samplerate']}")
    
    print("=" * 40)
    return input_devices

def get_default_input_device():
    """Get the default input device ID"""
    try:
        default = sd.default.device[0]
        print(f"[Info] Default input device: {default}")
        return default
    except Exception as e:
        print(f"[Error getting default device]: {e}")
        return None

def test_microphone(device_id=None, duration=3):
    """Test if microphone is working"""
    try:
        print(f"\n[Testing microphone for {duration} seconds...]")
        print("Make some noise!")
        
        recording = sd.rec(
            int(duration * 16000),
            samplerate=16000,
            channels=1,
            dtype='int16',
            device=device_id
        )
        sd.wait()
        
        level = np.abs(recording).mean()
        print(f"[Audio level: {level:.2f}]")
        
        if level < 10:
            print("[WARNING] Audio level very low - check microphone!")
            return False
        else:
            print("[SUCCESS] Microphone working!")
            return True
            
    except Exception as e:
        print(f"[Error testing microphone]: {e}")
        return False

def listen(vosk_model, device_id=None, timeout=10):
    """
    Listen for speech and return recognized text

    """
    try:
        print(f"[Loading Vosk model...]")
        model = vosk.Model(vosk_model)
        rec = vosk.KaldiRecognizer(model, 16000)
        rec.SetWords(True)
        
        # Clear the queue
        while not q.empty():
            q.get()

        print(f"[Opening audio stream on device {device_id}...]")
        
        with sd.RawInputStream(
            samplerate=16000,    # Changed from 48000 to 16000 directly
            blocksize=8000,
            dtype='int16',
            channels=1,
            device=device_id,
            callback=callback
        ):
            print("[🎤 Listening... Speak now!]")
            
            iterations = 0
            max_iterations = timeout * 2 if timeout else 1000  # ~2 iterations per second at 16kHz
            
            recognized_parts = []
            
            while iterations < max_iterations:
                try:
                    data = q.get(timeout=1)
                except queue.Empty:
                    iterations += 1
                    continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    
                    if text:
                        recognized_parts.append(text)
                        print(f"[✓ Recognized]: {text}")
                        # Return immediately after getting text
                        return text
                else:
                    # Show partial results
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        print(f"[Partial]: {partial_text}", end='\r')
                
                iterations += 1
            
            # Get final result if timeout reached
            final = json.loads(rec.FinalResult())
            final_text = final.get("text", "").strip()
            
            if final_text:
                print(f"\n[✓ Final]: {final_text}")
                return final_text
            
            if recognized_parts:
                full_text = " ".join(recognized_parts)
                print(f"\n[✓ Complete]: {full_text}")
                return full_text
            
            print("\n[Timeout: No speech detected]")
            return ""
                
    except Exception as e:
        print(f"[Listener Error]: {e}")
        import traceback
        traceback.print_exc()
        return ""

def listen_for_wake_word(vosk_model, device_id=None, wake_word="hola", timeout=None):
    """
    Continuously listen for a wake word
    Returns True when wake word is detected
    """
    try:
        model = vosk.Model(vosk_model)
        rec = vosk.KaldiRecognizer(model, 16000)
        
        # Clear queue
        while not q.empty():
            q.get()

        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            device=device_id,
            callback=callback
        ):
            print(f"[👂 Listening for wake word: '{wake_word}'...]")
            
            iterations = 0
            max_iterations = timeout * 2 if timeout else float('inf')
            
            while iterations < max_iterations:
                try:
                    data = q.get(timeout=1)
                except queue.Empty:
                    iterations += 1
                    continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip().lower()
                    
                    if text:
                        print(f"[Heard]: {text}")
                        
                        if wake_word.lower() in text:
                            print(f"[🔔 Wake word detected!]")
                            return True
                
                iterations += 1
            
            return False
                
    except Exception as e:
        print(f"[Wake Word Listener Error]: {e}")
        import traceback
        traceback.print_exc()
        return False

def continuous_listen(vosk_model, device_id=None, wake_word="hola", callback_func=None):
    """
    Continuously listen for wake word, then capture command

    """
    try:
        print(f"\n{'='*60}")
        print(f"CONTINUOUS LISTENING MODE")
        print(f"Wake word: '{wake_word}'")
        print(f"Say 'stop listening' or press Ctrl+C to exit")
        print(f"{'='*60}\n")
        
        while True:
            # Listen for wake word
            if listen_for_wake_word(vosk_model, device_id, wake_word):
                print(f"\n[💬 Listening for command...]")
                
                # Listen for command
                command = listen(vosk_model, device_id, timeout=5)
                
                if command:
                    print(f"[📝 Command]: {command}\n")
                    
                    # Check for exit commands
                    if any(word in command.lower() for word in ["stop listening", "exit listening", "goodbye"]):
                        print("[👋 Stopping continuous listening]")
                        break
                    
                    # Call callback function
                    if callback_func:
                        result = callback_func(command)
                        if result == "EXIT":
                            break
                else:
                    print("[⚠ No command received]\n")
            
            # Small delay before listening again
            import time
            time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\n[👋 Continuous listening stopped by user]")
    except Exception as e:
        print(f"[Continuous Listen Error]: {e}")
        import traceback
        traceback.print_exc()