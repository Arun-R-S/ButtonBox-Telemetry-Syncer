import pygame
import requests
import keyboard
import time
import pyautogui
import pygetwindow as gw
import win32gui
from datetime import datetime

# --- Color codes ---
RESET = "\033[0m"
COLOR_DEBUG = "\033[36m"   # Cyan
COLOR_INFO  = "\033[32m"   # Green
COLOR_WARN  = "\033[33m"   # Yellow
COLOR_ERROR = "\033[31m"   # Red

def _timestamp():
    """Return formatted timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def LogPrint(level, color, message, exception=None):
    """Base logging function with color and timestamp."""
    print(f"[{_timestamp()}] {color}{level:<7}{RESET} {message} {f'Exception: {exception}' if exception else ''}")

def printDebug(message):
    LogPrint("DEBUG", COLOR_DEBUG, message)

def printInfo(message):
    LogPrint("INFO", COLOR_INFO, message)

def printWarn(message):
    LogPrint("WARN", COLOR_WARN, message)

def printError(message, exception=None):
    LogPrint("ERROR", COLOR_ERROR, message, exception)

def get_nested_value(data, path):
    """Get nested JSON value from 'path' like 'truck/electricOn'"""
    try:
        keys = path.split('/')
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError):
        return None

def syncAction(physicalButtonState, gameButtonState, keyToPress, action):
    if physicalButtonState and not gameButtonState:
        printInfo(f"Key {keyToPress} to turn ON "+action)
        pressKey(keyToPress)
    elif not physicalButtonState and gameButtonState:
        printInfo(f"Key {keyToPress} to turn OFF "+action)
        pressKey(keyToPress)
    # else:
        # printInfo("No change needed")

def pressKey(keyToPress):
    if isinstance(keyToPress, str):
        # printDebug("It's a string")
        printDebug(f"Pressing {keyToPress}")
        keyboard.press_and_release(keyToPress)
        time.sleep(0.3)    
    elif isinstance(keyToPress, (list, tuple)) and all(isinstance(x, str) for x in keyToPress):
        #printDebug("It's a list or tuple of strings")
        printDebug(f"Pressing {keyToPress}")
        keyboard.press(keyToPress[0])
        keyboard.press_and_release(keyToPress[1])
        keyboard.release(keyToPress[0])
        time.sleep(0.3)
    else:
        printInfo("Something else")

def getTelemetry():
    try:
        telemetry = requests.get('http://localhost:25555/api/ets2/telemetry').json()
        return telemetry
    except Exception as e:
        printError("Telemetry read failed:", e)
        return None


# ---------------------
# Core Function
# ---------------------
def syncButton(joy, buttonIndex, telemetryPath, keyToPress, actionName, telemetry):
    """Sync one joystick button with one telemetry variable."""
    try:
        pygame.event.pump()
        physical_state = joy.get_button(buttonIndex)
        game_state = get_nested_value(telemetry, telemetryPath)

        if game_state is not None:
            syncAction(physical_state, game_state, keyToPress, actionName)
        else:
            printWarn(f"⚠️ Telemetry path not found: {telemetryPath}")
    except Exception as e:
        printError(f"SyncButton error for {actionName} when keypress {keyToPress}:", e)

# --- Settings ---
ETS2_WINDOW_TITLE = "Euro Truck Simulator 2"  # Partial match is fine
RUN_SCRIPT_ONLY_IN_ETS2 = True

def if_run_script():
    """Check if the currently active window is ETS2."""
    try:
        if not RUN_SCRIPT_ONLY_IN_ETS2:
            return True
        else:
            printInfo("Checking active window...")
            active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            printInfo(f"Active window: {active_window}")
            return ETS2_WINDOW_TITLE.lower() in active_window.lower()
    except Exception as e:
        printError("Failed to get active window", e)
        return False

# Initialize Pygame joystick
pygame.init()
pygame.joystick.init()

# List connected joysticks
if pygame.joystick.get_count() == 0:
    printWarn("No joystick detected!")
    exit()

joy = pygame.joystick.Joystick(0)
if pygame.joystick.get_count() == 2:
    joy = pygame.joystick.Joystick(1)

joy.init()
printInfo(f"Using joystick: {joy.get_name()} with {joy.get_numbuttons()} buttons")

# Main loop
while True:

    # Read ETS2 telemetry
    try:
        if if_run_script():
            telemetry = getTelemetry()
            if not telemetry:
                time.sleep(1)
                continue
            else:
                # Example: Button 1(index=0) → Electricity
                syncButton(joy, 0, 'truck/electricOn', ['shift', 'e'], "Electricity", telemetry)

                # Example: Button 5(index=4) → High Beam Lights
                syncButton(joy, 4, 'truck/lightsBeamHighOn', 'k', "HighBeam", telemetry)

                # Example: Button 7(index=6) → Beacon Lights
                syncButton(joy, 6, 'truck/lightsBeaconOn', 'o', "BeaconLights", telemetry)
        else:
            printWarn("ETS2 is not the active window. Waiting...")
            time.sleep(5)
    except Exception as e:
        printError("SyncButton failed:", e)
        time.sleep(1)
        continue

    time.sleep(0.1)

    