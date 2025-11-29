import datetime

mainLogsFilename = "logs.txt"       # Filename of every main logs
chatLogsFilename = "chatLogs.txt"       # Filename of every chat logs.

def mainLogs(text):
    if not text:
        return
    
    text = str(text).strip()
    try:
        with open(mainLogsFilename, 'a', encoding='utf-8') as f:  # Saving logs into a file.
            currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Defining current time 

            log = f"==========[ {currentTime} ]==========\n{text}\n==========[ ******************* ]==========\n\n"
            f.write(log)    # Writing log to "logs.txt".

    except Exception as e: # Catching Errors.
        print(f"[Error]: Unable to save main logs.\nReason: {e}")
        return

def chatLogs(text):
    if not text:
        return

    text = str(text).strip()

    try:
        with open(chatLogsFilename, 'a', encoding='utf-8') as f: # Saving logs itno a file.
            currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Current time.

            log = f"==========[ {currentTime} ]==========\n{text}\n==========[ ******************* ]==========\n\n"
            f.write(log)    # Writing logs to "chatLogs.txt".

    except Exception as e: # Catching Errors.
        print(f"[Error]: Unable to save chat logs.\nReason: {e}")
        return