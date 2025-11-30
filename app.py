import pygame
import requests
import keyboard
import time
import pyautogui
import pygetwindow as gw
import win32gui
from datetime import datetime
import colorama
colorama.init()

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
    except Exception as e:
        printError(f"Failed to get nested value for path: {path}",e)
        return None

def syncAction(physicalButtonState, gameButtonState, keyToPress, action):
    try:
        if physicalButtonState and not gameButtonState:
            printInfo(f"Key {keyToPress} to turn ON "+action)
            pressKey(keyToPress)
        elif not physicalButtonState and gameButtonState:
            printInfo(f"Key {keyToPress} to turn OFF "+action)
            pressKey(keyToPress)
        # else:
            # printInfo("No change needed")
    except Exception as e:
        printError(f"SyncAction error for action {action} when keypress {keyToPress}:", e)

def pressKey(keyToPress):
    try:
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
    except Exception as e:
        printError(f"PressKey error for keypress {keyToPress}:", e)

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
try:
    
    pygame.init()
    pygame.joystick.init()
    num_joysticks = pygame.joystick.get_count()
    # List connected joysticks
    if num_joysticks == 0:
        printWarn("No joystick detected!")
        exit()

    # List all joysticks
    printInfo("Connected joysticks:")
    for i in range(num_joysticks):
        joy_name = pygame.joystick.Joystick(i).get_name()
        print(f"  [{i}] {joy_name}")
    print()
    print("  [X] Exit")
    # joy = pygame.joystick.Joystick(0)
    # if pygame.joystick.get_count() == 2:
    #     joy = pygame.joystick.Joystick(1)

    # Ask user to select joystick
    selected_joystick_index = -1
    while True:
        try:
            selected_joystick_index = (input("Select joystick by number: "))
            if selected_joystick_index == 'x' or selected_joystick_index == 'X':
                printInfo("Exiting...")
                exit()
            selected_joystick_index = int(selected_joystick_index)
            if 0 <= selected_joystick_index < num_joysticks:
                break
            else:
                if num_joysticks == 1:
                    printWarn("Please enter 0 since there is only one joystick connected Or X to exit.")
                else:
                    printWarn(f"Please enter a number between 0 and {num_joysticks-1}")
        except ValueError:
            printWarn("Invalid input. Enter a number.")

    # Initialize chosen joystick
    joy = pygame.joystick.Joystick(selected_joystick_index)
    joy.init()
    printInfo(f"Using joystick: {joy.get_name()} with {joy.get_numbuttons()} buttons")

    # Main loop
    while True:

        # Read ETS2 telemetry
        try:
            if if_run_script():
                telemetry = getTelemetry()
                if not telemetry:
                    printWarn("No telemetry data received. Retrying...")
                    time.sleep(1)
                    continue
                else:
                    truck_id = telemetry.get('truck', {}).get('id', None)
                    isGamePaused = telemetry.get('game', {}).get('paused', True)
                    if not truck_id:
                        printWarn("Truck ID is empty or null")
                        time.sleep(1)
                        continue
                    elif not isGamePaused:
                        printInfo(f"Truck ID: {truck_id}")
                        printInfo(f"Game Paused: {isGamePaused}")
                        # Example: Button 1(index=0) → Electricity
                        syncButton(joy, 0, 'truck/electricOn', ['shift', 'e'], "Electricity", telemetry)

                        # Example: Button 5(index=4) → High Beam Lights
                        syncButton(joy, 4, 'truck/lightsBeamHighOn', 'k', "HighBeam", telemetry)

                        # Example: Button 7(index=6) → Beacon Lights
                        syncButton(joy, 6, 'truck/lightsBeaconOn', 'o', "BeaconLights", telemetry)
                    elif isGamePaused:
                        printWarn("Game Paused")
            else:
                printWarn("ETS2 is not the active window. Waiting...")
                time.sleep(5)
        except Exception as e:
            printError("SyncButton failed:", e)
            time.sleep(1)
            continue
        time.sleep(0.1)

except Exception as e:
    printError("Fatal error in main loop:", e)
    