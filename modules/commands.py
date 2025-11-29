import datetime
import psutil
import shutil
import os
import subprocess

def checkFreeram():
    try:
        free_mem_in_kb = ""
        with open('/proc/meminfo') as f:
            for line in f:
                if 'MemFree' in line:
                    free_mem_in_kb = line.split()[1]
                    break

        
        mem = int(free_mem_in_kb)/1024
        return mem
    except:
        pass

def checkCpuUsage():
    try:
        cpu_usage = psutil.cpu_percent(interval=2)
  
        return str(cpu_usage)
    except:
        pass

def checkFreeStorage():
    try:
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)

        return free_gb
    except:
        pass 

def getSystemUptime():
    try:
        uptime = os.popen('uptime -p').read()[3:]
        return uptime
    except:
        pass   
    


cmds = ["help", "tell date", "tell time", "check free ram", "check cpu usage", "check storage", "check system uptime", 'install', 'uninstall'] 

holaCmds = {
    "help": {
        "print": lambda: f"Hola: Here are some available commands\n{'\n'.join(cmds)}",
        "speak": lambda: f"Here are some available commands\n{'\n'.join(cmds)}",
        "chatLogs": lambda: f"Hola: Here are some available commands\n{'\n'.join(cmds)}",
    },

    "tell date": {
        "print": lambda: f"Hola: Today is {datetime.date.today().strftime("%B %d, %Y")}",
        "speak": lambda: f"Today is {datetime.date.today().strftime("%B %d, %Y")}",
        "chatLogs": lambda: f"Hola: Today is {datetime.date.today().strftime("%B %d, %Y")}"
    },

    "tell time": {
        "print": lambda: f"Hola: Its {datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")}",
        "speak": lambda: f"Its {datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")}",
        "chatLogs": lambda: f"Hola: Its {datetime.datetime.now().strftime("%B %d, %Y %I:%M %p")}"
    },
    
    "check free ram": {
        "print": lambda: f"Hola: {checkFreeram():.2f} MegaBytes of ram is available.",
        "speak": lambda: f"{checkFreeram():.2f} MegaBytes of ram is available.",
        "chatLogs": lambda: f"Hola: {checkFreeram():.2f} MegaBytes of ram is available.",
    },

    "check cpu usage": {
        "print": lambda: f"Hola: CPU is running at {checkCpuUsage()} percent.",
        "speak": lambda: f"CPU is running at {checkCpuUsage()} percent.",
        "chatLogs": lambda: f"Hola: CPU is running at {checkCpuUsage()} percent.",
    },

    "check storage": {
        "print": lambda: f"Hola: {checkFreeStorage():.2f} GigaBytes of storage is available.",
        "speak": lambda: f"{checkFreeStorage():.2f} GigaBytes of storage is available.",
        "chatLogs": lambda: f"Hola: {checkFreeStorage():.2f} GigaBytes of storage is available.",
    },

    "check system uptime": {
        "print": lambda: f"Hola: System is up for {getSystemUptime()}",
        "speak": lambda: f"System is up for {getSystemUptime()}",
        "chatLogs": lambda: f"Hola: System is up for {getSystemUptime()}",
    }


}
