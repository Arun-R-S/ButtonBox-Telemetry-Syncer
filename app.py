import sys
import os
# mute output
stdout_backup = sys.stdout
sys.stdout = open(os.devnull, 'w')

import pygame

# restore output
sys.stdout = stdout_backup
import requests
import keyboard
import time
import pyautogui
import pygetwindow as gw
import win32gui
from datetime import datetime
import colorama
colorama.init()
#from config import JOYSTICK_BUTTON_MAPPINGS
import json


# --- Color codes ---
COLOR_RESET = "\033[0m"
COLOR_DEBUG = "\033[36m"        # Cyan
COLOR_DEBUG_WARN = "\033[95m"   # Bright Magenta
COLOR_INFO  = "\033[32m"        # Green
COLOR_WARN  = "\033[33m"        # Yellow
COLOR_ERROR = "\033[31m"        # Red

from colorama import Fore, Style, init
init(autoreset=True)

ascii_art = f"""
{Fore.RED}   ░███                                      ░█████████       ░██████   {COLOR_RESET}
{Fore.RED}  ░██░██                                     ░██     ░██     ░██   ░██  {COLOR_RESET}
{Fore.RED} ░██  ░██  ░██░████ ░██    ░██ ░████████     ░██     ░██    ░██         {COLOR_RESET}
{Fore.YELLOW}░█████████ ░███     ░██    ░██ ░██    ░██    ░█████████      ░████████  {COLOR_RESET}
{Fore.YELLOW}░██    ░██ ░██      ░██    ░██ ░██    ░██    ░██   ░██              ░██ {COLOR_RESET}
{Fore.RED}░██    ░██ ░██      ░██   ░███ ░██    ░██    ░██    ░██      ░██   ░██  {COLOR_RESET}
{Fore.RED}░██    ░██ ░██       ░█████░██ ░██    ░██    ░██     ░██      ░██████   {COLOR_RESET}
{Fore.GREEN}🚛 Welcome to ETS2 ButtonBox Syncer 🚛
"""

print(ascii_art)


GLOBAL_CONFIG = {}
GLOBAL_JOYSTICKS = pygame.joystick

def load_config():
    """Load JSON config file and return the mappings list."""
    config_path = "config.json"

    if getattr(sys, 'frozen', False):
    # running from PyInstaller EXE
        exe_dir = os.path.dirname(sys.executable)
    else:
        # running from source
        exe_dir = os.path.dirname(__file__)

    config_path = os.path.join(exe_dir, 'config.json')

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Missing config file: {config_path}")

    with open(config_path, "r") as f:
        data = json.load(f)

    return data

def _timestamp():
    """Return formatted timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def LogPrint(level, color, message, exception=None):
    """Base logging function with color and timestamp."""
    print(f"[{_timestamp()}] {color}{level:<7}{COLOR_RESET} {message} {f'Exception: {exception}' if exception else ''}")

def printLog(message):
    LogPrint("LOG", COLOR_RESET, message)

def printDebug(message):
    if GLOBAL_CONFIG.get("LoggingLevels", {}).get("DEBUG", False):
        LogPrint("DEBUG", COLOR_DEBUG, message)

def printDebugWarn(message):
    if GLOBAL_CONFIG.get("LoggingLevels", {}).get("DEBUGWARN", False):
        LogPrint("DEBUG-WARN", COLOR_DEBUG_WARN, message)

def printInfo(message):
    if GLOBAL_CONFIG.get("LoggingLevels", {}).get("INFO", False):
        LogPrint("INFO", COLOR_INFO, message)

def printWarn(message):
    if GLOBAL_CONFIG.get("LoggingLevels", {}).get("WARN", False):
        LogPrint("WARN", COLOR_WARN, message)

def printError(message, exception=None):
    if GLOBAL_CONFIG.get("LoggingLevels", {}).get("ERROR", False):
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
        printDebug(f"SyncAction: Physical: {physicalButtonState}, Game: {gameButtonState}, Key: {keyToPress}, Action: {action}")
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
            printError("PressKey: Key assignment is not defined correctly.")
    except Exception as e:
        printError(f"PressKey error for keypress {keyToPress}:", e)

def getTelemetry():
    try:
        telemetry = requests.get(GLOBAL_CONFIG["TelemetryAPIAddress"]).json()
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
            printError(f"⚠️ Telemetry path not found: {telemetryPath}")
    except Exception as e:
        printError(f"SyncButton error for {actionName} when keypress {keyToPress}:", e)

# --- Settings ---
# ETS2_WINDOW_TITLE = "Euro Truck Simulator 2"  # Partial match is fine
# ACTIVATE_SCRIPT_ONLY_IN_ETS2 = True

def if_run_script():
    """Check if the currently active window is ETS2."""
    try:
        if not GLOBAL_CONFIG["ACTIVATE_SCRIPT_ONLY_IN_ETS2"]:
            return True
        else:
            printDebug("Checking active window...")
            active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            printDebug(f"Active window: {active_window}")
            return GLOBAL_CONFIG["ETS2_WINDOW_TITLE"].lower() in active_window.lower()
    except Exception as e:
        printError("Failed to get active window", e)
        return False

def print_table(headers, rows):
    # ANSI Colors
    HEADER = "\033[1;36m"  # bright cyan
    RESET  = "\033[0m"

    # Double-line table borders
    TL = "╔"; TM = "╦"; TR = "╗"
    ML = "╠"; MM = "╬"; MR = "╣"
    BL = "╚"; BM = "╩"; BR = "╝"
    VL = "║"; HL = "═"

    # Compute column widths (auto-size)
    col_widths = []
    for col in range(len(headers)):
        max_len = len(headers[col])
        for row in rows:
            max_len = max(max_len, len(str(row[col])))
        col_widths.append(max_len)

    # Build border lines
    def border(left, mid, right):
        line = left
        for i, w in enumerate(col_widths):
            line += HL * (w + 2)
            line += mid if i < len(col_widths) - 1 else right
        return line

    top_border    = border(TL, TM, TR)
    middle_border = border(ML, MM, MR)
    bottom_border = border(BL, BM, BR)

    # Print table
    print(top_border)

    # Header row (colored)
    header_line = VL
    for i, h in enumerate(headers):
        header_line += f" {HEADER}{h}{RESET}{' ' * (col_widths[i] - len(h))} {VL}"
    print(header_line)

    print(middle_border)

    # Rows
    for row in rows:
        row_line = VL
        for i, col in enumerate(row):
            col = str(col)
            row_line += f" {col}{' ' * (col_widths[i] - len(col))} {VL}"
        print(row_line)

    print(bottom_border)


def listAllJoysticks(reload=False):
    if reload:
        pygame.joystick.quit()
        pygame.quit()
    pygame.init()
    pygame.joystick.init()
    GLOBAL_JOYSTICKS = pygame.joystick
    number_of_joysticks = GLOBAL_JOYSTICKS.get_count()
    # List connected joysticks
    if number_of_joysticks == 0:
        printWarn("No joystick detected!")
        print()
        print("  [X] Exit")
        print("  [R] Refresh Joysticks List again")
        print("---------------------------------------------------")
    else:
        # List all joysticks
        printInfo("Connected joysticks:")
        # table header
        # print("┌───────┬─────────────────────────────────────────┬───────────────────────────────────────┐")
        # print("│ ID    │ NAME                                    │ GUID                                  │")
        # print("├───────┼─────────────────────────────────────────┼───────────────────────────────────────┤")

        # for i in range(number_of_joysticks):
        #     index = f"[{i}]"
        #     joy_name = pygame.joystick.Joystick(i).get_name()
        #     print(f"|  {index:<5}| {joy_name:<40}| {pygame.joystick.Joystick(i).get_guid():<38}|")
        # print("└───────┴─────────────────────────────────────────┴───────────────────────────────────────┘")
        rows = []
        for i in range(number_of_joysticks):
            js = GLOBAL_JOYSTICKS.Joystick(i)
            rows.append([
                f"[{i}]",
                js.get_name(),
                js.get_guid(),
                js.get_numbuttons()
            ])
        print_table(
            headers=["ID", "NAME", "GUID", "NumButtons"],
            rows=rows
        )
        print()
        print("  [X] Exit")
        print("  [R] Refresh Joysticks List again")
        print("---------------------------------------------------")

def loading_animation(duration=2):
    print("Loading", end="", flush=True)
    start_time = time.time()
    while (time.time() - start_time) < duration:
        for dot_count in range(1, 4):
            # Print dots after "Loading", overwrite only the dots
            print("\rLoading" + "." * dot_count + " " * (3 - dot_count), end="", flush=True)
            time.sleep(0.5)
    print("\rLoading... Done!  ")  # Final message
    
# Initialize Pygame joystick
try:
    GLOBAL_CONFIG = load_config()

    listAllJoysticks()
    # joy = pygame.joystick.Joystick(0)
    # if pygame.joystick.get_count() == 2:
    #     joy = pygame.joystick.Joystick(1)

    # Ask user to select joystick
    selected_joystick_index = -1
    while True:
        try:
            selected_joystick_index = (input("Select joystick by ID number: "))
            if selected_joystick_index == 'x' or selected_joystick_index == 'X':
                printLog("Exiting...")
                exit()
            if selected_joystick_index == "r" or selected_joystick_index == "R":
                listAllJoysticks(True)
                continue
            else:
                num_joysticks = GLOBAL_JOYSTICKS.get_count()
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
    time.sleep(2)
    printLog("---------------------------Telemetry Syncer Started-----------------------------")
    printLog("-----------------------------Press Ctrl+C to exit-------------------------------")
    loading_animation(5)
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
                        printDebug("Truck ID is empty or null")
                        time.sleep(1)
                        continue
                    elif not isGamePaused:
                        printDebug(f"Truck ID: {truck_id}")
                        printDebug(f"Game Paused: {isGamePaused}")
                        # # Example: Button 1(index=0) → Electricity
                        # syncButton(joy, 0, 'truck/electricOn', ['shift', 'e'], "Electricity", telemetry)

                        # # Example: Button 5(index=4) → High Beam Lights
                        # syncButton(joy, 4, 'truck/lightsBeamHighOn', 'k', "HighBeam", telemetry)

                        # # Example: Button 7(index=6) → Beacon Lights
                        # syncButton(joy, 6, 'truck/lightsBeaconOn', 'o', "BeaconLights", telemetry)
                        
                        JOYSTICK_BUTTON_MAPPINGS = GLOBAL_CONFIG.get("JOYSTICK_BUTTON_MAPPINGS", [])
                        joystick_button_index_correction = 0
                        if GLOBAL_CONFIG["isButtonNumberIndex"] == False:
                            joystick_button_index_correction = -1
                        for cfg in JOYSTICK_BUTTON_MAPPINGS:
                            syncButton(
                                joy,
                                cfg["joystickButtonNumber"]+joystick_button_index_correction,
                                cfg["telemetryPathToSync"],
                                cfg["keyToPress"],
                                cfg["actionName"],
                                telemetry
                            )
                    elif isGamePaused:
                        printDebugWarn("Game Paused")
            else:
                printDebugWarn("ETS2 is not the active window. Waiting...")
                time.sleep(5)
        except Exception as e:
            printError("SyncButton failed:", e)
            time.sleep(1)
            continue
        time.sleep(0.1)

except Exception as e:
    printError("Fatal error in main loop:", e)
    