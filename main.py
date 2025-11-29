import modules.model
import modules.audio
from modules.sites import sitesurls
from modules.logging import mainLogs, chatLogs
from modules import commands
from modules import listener
from dotenv import load_dotenv
import os
import webbrowser
import platform
import shutil
import subprocess
import shlex
import getpass

# Loading environment variables from the .env file
load_dotenv()

# Accessing API Key
apiKey = os.getenv('apiKey')

# Voice model path
VOSK_MODEL = "models/vosk-model-small-en-us-0.15"

# Hola Commands functions.
def holaCommands(text):
    cmds = commands.cmds
    holaCmds = commands.holaCmds

    if text.lower().startswith('install'):
        installSoftwares(text.replace('install', '').strip())
        return

    if text.lower().startswith('uninstall'):
        uninstallSoftwares(text.replace('uninstall', '').strip())
        return

    # Check for exact command match first
    if text.lower() in cmds:
        cmd = text.lower()
        print(holaCmds[cmd]['print']())  
        speak(holaCmds[cmd]['speak']())
        chatLogs(holaCmds[cmd]['chatLogs']())
        return

    # If no exact match, inform user
    print(f"Hola: {text} command not found.")
    speak(f"{text} command not found.")
    chatLogs(f"Hola: {text} command not found.")

pkginstall = {
    'apt': 'sudo -S apt install -y ',
    'dnf': 'sudo -S dnf install -y ',
    'yum': 'sudo -S yum install -y ',
    'zypper': 'sudo -S zypper install -y ',
    'pacman': 'sudo -S pacman -S --noconfirm ',
    'xbps-install': 'sudo -S xbps-install -Sy ', 
    'rpm': 'sudo -S rpm -i --force ',  
    'emerge': 'sudo -S emerge --ask=n ',  
    'apk': 'sudo -S apk add --no-confirm ',
}

pkguninstall = {
    'apt': 'sudo -S apt remove -y ',
    'dnf': 'sudo -S dnf remove -y ',
    'yum': 'sudo -S yum remove -y ',
    'zypper': 'sudo -S zypper remove -y ',
    'pacman': 'sudo -S pacman -R --noconfirm ',
    'xbps-install': 'sudo -S xbps-remove -Ry ', 
    'rpm': 'sudo -S rpm -e --nodeps ',  
    'emerge': 'sudo -S emerge --ask=n --depclean ',  
    'apk': 'sudo -S apk del ',
}

pkgquery = {
    "apt": "apt-cache show ",
    "dnf": "dnf info ",
    "yum": "yum info ",
    "zypper": "zypper info ",
    "pacman": "pacman -Ss ",
    "xbps-install": "xbps-query -Rs ",
    "rpm": "repoquery -i ",
    "emerge": "emerge --search ",
    "apk": "apk search "
}

def detect_package_manager():
    managers = ['apt', 'dnf', 'yum', 'zypper', 'pacman', 'xbps-install', 'rpm', 'emerge', 'apk']
    for mgr in managers:
        if shutil.which(mgr):
            return mgr
    return None

def installSoftwares(pkg):
    try:
        pkgManager = detect_package_manager()

        if not pkg:
            print("Hola: No package name provided.")
            speak("No package name provided.")
            return

        if not pkgManager:
            print("Hola: Unsupported package manager detected.")
            speak("Unsupported package manager detected.")
            chatLogs("Hola: Unsupported package manager detected.")
            return

        # Validate package name (basic security check)
        if not pkg.replace('-', '').replace('_', '').isalnum():
            print("Hola: Invalid package name.")
            speak("Invalid package name.")
            return

        print(f'Hola: Searching the repository.')
        speak(f'Searching the repository.')
        chatLogs(f'Hola: Searching the repository.')

        queryCmd = f"{pkgquery[pkgManager]} {shlex.quote(pkg)}"
        queryResult = subprocess.run(queryCmd, shell=True, capture_output=True, text=True)

        if queryResult.stderr and "not found" in queryResult.stderr.lower():
            print(f"Hola: Failed to get query for {pkg}.")
            speak(f"Failed to get query for {pkg}.")
            chatLogs(f"Hola: Failed to get query for {pkg}.")
            return
            
        if queryResult.stdout:
            print(f"Hola: Found a package for {pkg}.")
            speak(f"Found a package for {pkg}.")
            chatLogs(f"Hola: Found a package for {pkg}.")

            print(f"Hola: Installing.")
            speak(f"Installing.")
            chatLogs(f"Hola: Installing.")
            
            installCmd = f"{pkginstall[pkgManager]} {shlex.quote(pkg)}"

            print(f"Hola: Enter your user password to proceed.")
            speak(f"Enter your user password to proceed.")
            chatLogs(f"Hola: Enter your user password to proceed.")
            
            passwd = getpass.getpass("USER PASSWORD: ")

            if passwd:
                installResult = subprocess.run(
                    installCmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    input=f"{passwd}\n"
                )

                if 'already installed' in installResult.stderr.lower() or 'already installed' in installResult.stdout.lower():
                    print(f"Hola: {pkg} already installed.")
                    speak(f"{pkg} already installed.")
                    chatLogs(f"Hola: {pkg} already installed.")
                    return

                if "done" in installResult.stdout.lower() or "installed" in installResult.stdout.lower():
                    print(f"Hola: {pkg} package successfully installed.")            
                    speak(f"{pkg} package successfully installed.")
                    chatLogs(f"Hola: {pkg} package successfully installed.")
                else:
                    print(f"Hola: {pkg} package failed to install.\nError: {installResult.stderr}")            
                    speak(f"{pkg} package failed to install.")
                    chatLogs(f"Hola: {pkg} package failed to install.\nError: {installResult.stderr}")
        else:
            print(f"Hola: {pkg} not found in repository.")
            speak(f"{pkg} not found in repository.")
            chatLogs(f"Hola: {pkg} not found in repository.")     

    except Exception as e:
        print(f"Hola: An error has occurred, Check logs for more information.")
        speak(f"An error has occurred, Check logs for more information.")
        mainLogs(e)
    
def uninstallSoftwares(pkg):
    try:
        pkgManager = detect_package_manager()

        if not pkg:
            print("Hola: No package name provided.")
            speak("No package name provided.")
            return

        if not pkgManager:
            print("Hola: Unsupported package manager detected.")
            speak("Unsupported package manager detected.")
            chatLogs("Hola: Unsupported package manager detected.")
            return
        
        # Validate package name
        if not pkg.replace('-', '').replace('_', '').isalnum():
            print("Hola: Invalid package name.")
            speak("Invalid package name.")
            return

        uninstallCmd = f"{pkguninstall[pkgManager]} {shlex.quote(pkg)}"

        print(f"Hola: Uninstalling {pkg}.")
        speak(f"Uninstalling {pkg}.")
        chatLogs(f"Hola: Uninstalling {pkg}.")

        print(f"Hola: Enter your user password to proceed.")
        speak(f"Enter your user password to proceed.")
        chatLogs(f"Hola: Enter your user password to proceed.")
        
        passwd = getpass.getpass("USER PASSWORD: ")

        if passwd:
            uninstallResult = subprocess.run(
                uninstallCmd, 
                capture_output=True, 
                text=True, 
                shell=True, 
                input=f"{passwd}\n"
            )

            if 'not currently installed' in uninstallResult.stderr.lower() or 'not installed' in uninstallResult.stderr.lower():
                print(f"Hola: {pkg} not installed.")
                speak(f"{pkg} not installed.")
                chatLogs(f"Hola: {pkg} not installed.")
                return

            if uninstallResult.returncode == 0:
                print(f"Hola: {pkg} package successfully uninstalled.")            
                speak(f"{pkg} package successfully uninstalled.")
                chatLogs(f"Hola: {pkg} package successfully uninstalled.")
            else:
                print(f"Hola: Failed to uninstall {pkg}.\nError: {uninstallResult.stderr}")            
                speak(f"Failed to uninstall {pkg}.")
                chatLogs(f"Hola: Failed to uninstall {pkg}.\nError: {uninstallResult.stderr}")

    except Exception as e:
        print(f"Hola: An error has occurred, Check logs for more information.")
        speak(f"An error has occurred, Check logs for more information.")
        mainLogs(e)

def detectMicrophone():
    """Detect if a microphone is available"""
    try:
        systemOS = platform.system()
        if systemOS.lower() == 'linux':
            output = subprocess.run(
                'arecord -l | grep "card"',
                capture_output=True,
                text=True,
                shell=True,
            )
            return bool(output.stdout)
        return False
    except:
        return False

# Speaking function for Hola.
def speak(text):
    try:  
        if not text:
            return  
        modules.audio.holaSpeak(text)
    except Exception as e:
        mainLogs(e) 

def searchInternet(text):
    """Search the internet using DuckDuckGo"""
    if not text:
        return
    
    # Join search terms with +
    query = "+".join(text.split())
    url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
    
    try:
        webbrowser.open(url)
        print(f"Hola: Searching for: {' '.join(text.split())}")
        speak(f"Searching for: {' '.join(text.split())}")
    except Exception as e:
        print(f"[Error]: {e}")
        speak(f"Error while opening the browser, check logs for more information.")
        chatLogs(f"[Error]: {e}")

def launchProgram(programPath):
    try:
        if not programPath:    
            return    

        subprocess.Popen(
            shlex.split(programPath),
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Hola: Unable to launch the program. Check logs for more information.")
        speak(f"Unable to launch the program. Check logs for more information.")
        mainLogs(e)

def runProgram(program):
    try:
        if not program:  
            return

        systemOS = platform.system()
        path = shutil.which(program.lower().strip())

        if systemOS.lower() == 'linux':      
            if path:
                print(f"Hola: Launching {program}")
                speak(f"Launching {program}")
                chatLogs(f"Hola: Launching {program}")
                launchProgram(path)   
            else:
                print(f"Hola: {program} path not found.")
                speak(f"{program} path not found.")
                chatLogs(f"Hola: {program} path not found.")    
        else:
            print(f"Hola: Unable to launch {program} for {systemOS.lower()}.")
            speak(f"Unable to launch {program} for {systemOS.lower()}.")
            chatLogs(f"Hola: Unable to launch {program} for {systemOS.lower()}.")      

    except Exception as e:
        print("Hola: Unable to run the program. Check logs for more information.")
        speak("Unable to run the program. Check logs for more information.")    
        mainLogs(e)

def openProgramsAndSites(text):
    try:
        if not text:
            return

        query = text.lower().strip()

        # Program Opening Commands
        trigger_words = ["open", "start", "launch"]

        for trigger in trigger_words:
            if query.startswith(trigger):
                program_name = query.replace(trigger, '').strip()
                if program_name in sitesurls:
                    # It's a website
                    print(f"Hola: Opening {program_name}")
                    speak(f"Opening {program_name}")
                    chatLogs(f"Hola: Opening {program_name}")
                    webbrowser.open(sitesurls[program_name])
                    return
                elif program_name:
                    # It's a program
                    runProgram(program_name)
                    return

        # Check if it's just a website name
        for site in sitesurls:
            if site in query.split():
                print(f"Hola: Opening {site}")
                speak(f"Opening {site}")
                chatLogs(f"Hola: Opening {site}")
                webbrowser.open(sitesurls[site])
                return

        print("Hola: No matching program or website found.")
        speak("No matching program or website found.")
        chatLogs("Hola: No matching program or website found.")

    except Exception as e:
        print("Hola: An Error has occurred. Check logs for more information.")
        speak("An Error has occurred. Check logs for more information.")
        mainLogs(e)

def process_command(prompt):
    """Process a command from either text or voice input"""
    if not prompt:
        return
    
    prompt = prompt.strip()
    chatLogs(f"You: {prompt}")

    # Exit conditions
    if any(word in prompt.lower() for word in ["exit", "quit", "bye", "goodbye", "shutdown"]):
        print("Hola: Good Bye!!")
        speak("Good Bye!!")
        chatLogs("Hola: Good Bye!!")
        return "EXIT"

    # Open/Launch programs and sites
    if any(word in prompt.lower().split() for word in ["open", "start", "launch"]):
        openProgramsAndSites(prompt.lower())
        return

    # Search the internet
    if prompt.lower().startswith('search'):
        search_query = prompt.replace('search', '').strip()
        print(f"Hola: Searching {search_query}")
        speak(f"Searching {search_query}")
        searchInternet(search_query)
        return

    # Hola commands
    if prompt.lower().startswith('hola'):
        holaCommands(prompt.lower().replace('hola', '').strip())
        return

    # AI conversation
    holaResponse = modules.model.runAi(prompt, apiKey)

    if holaResponse and not holaResponse.startswith("[Error"):
        print(f"Hola: {holaResponse}")
        speak(holaResponse)
        chatLogs(f"Hola: {holaResponse}")
    else:
        print("Hola: Something went wrong.")
        speak("Something went wrong.")
        if holaResponse:
            chatLogs(holaResponse)


def voice_mode():
    """Run Hola in voice mode with continuous listening"""
    print("\n" + "="*50)
    print("HOLA - VOICE MODE")
    print("="*50)
    print("Say 'hola' followed by your command")
    print("Say 'stop listening' to exit")
    print("="*50 + "\n")
    
    # List available devices
    input_devices = listener.list_audio_devices()
    
    if not input_devices:
        print("[Error] No input devices found!")
        print("Please connect a microphone and try again.")
        return
    
    # Get device ID
    device_id = listener.get_default_input_device()
    
    if device_id is None or device_id not in input_devices:
        device_input = input("\nEnter device ID to use (or press Enter to exit): ").strip()
        if not device_input:
            return
        try:
            device_id = int(device_input)
            if device_id not in input_devices:
                print(f"[Error] Device {device_id} is not an input device!")
                return
        except ValueError:
            print("[Error] Invalid device ID!")
            return
    
    print(f"\n[Using device {device_id}]")
    
    # Test microphone
    print("\n[Testing microphone...]")
    if not listener.test_microphone(device_id, duration=2):
        print("[Error] Microphone test failed!")
        retry = input("Continue anyway? (y/n): ").strip().lower()
        if retry != 'y':
            return
    
    speak("Voice mode activated. Say hola followed by your command.")
    
    def handle_voice_command(command):
        """Callback for processing voice commands"""
        result = process_command(command)
        if result == "EXIT":
            return "EXIT"
    
    try:
        listener.continuous_listen(
            vosk_model=VOSK_MODEL,
            device_id=device_id,
            wake_word="hola",
            callback_func=handle_voice_command
        )
    except Exception as e:
        print(f"[Voice Mode Error]: {e}")
        import traceback
        traceback.print_exc()
        mainLogs(e)


def chat_mode():
    """Run Hola in text chat mode"""
    print("\n" + "="*50)
    print("HOLA - CHAT MODE")
    print("="*50)
    print("Type your commands or chat with Hola")
    print("Type 'exit', 'quit', or 'bye' to stop")
    print("="*50 + "\n")
    
    speak("Welcome to Hola chat mode.")
    
    try:
        while True:
            prompt = input("You: ").strip()
            
            result = process_command(prompt)
            if result == "EXIT":
                break

    except KeyboardInterrupt:
        print("\n\nHola: Goodbye!")
        speak("Goodbye!")
    except Exception as e:
        print(f"[Error]: {e}")
        mainLogs(f"[Error]: {e}")

def main():
    try:
        if not apiKey:
            print("[Error]: API Key not found. Please set 'apiKey' in .env file")
            return

        print("\n" + "="*50)
        print("WELCOME TO HOLA")
        print("Your Personal AI Assistant")
        print("="*50 + "\n")

        # Check for microphone
        has_mic = detectMicrophone()
        
        if has_mic:
            mode = input("Choose mode:\n1. Voice Mode\n2. Chat Mode\n\nEnter choice (1/2): ").strip()
            
            if mode == "1":
                voice_mode()
            else:
                chat_mode()
        else:
            print("[Info]: No microphone detected. Starting in Chat Mode.\n")
            chat_mode()

    except Exception as e: 
        print(f"[Main Error]: {e}")
        mainLogs(f"[Main]: {e}")

if __name__ == '__main__':
    main()