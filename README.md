# 🎮 ButtonBox-Telemetry-Syncer  

**Sync your physical ButtonBox with Euro Truck Simulator 2 (ETS2) — keep device LEDs/buttons and in-game functions in sync.**  

---

## 📘 Table of Contents  

- [What is this project?](#what-is-this-project)  
- [Features ⭐](#features-)  
- [Requirements ✅](#requirements-)  
- [Installation & Setup 🚀](#installation--setup-)  
- [Configuration 🔧](#configuration-config.json)  
- [Running the Syncer 🏃](#running-the-syncer-)  
- [Troubleshooting & Tips 🛠️](#troubleshooting--tips-)  
- [Contributing 🤝](#contributing-)  
- [License 📄](#license-)  

---

## What is this project?  
**Sync your physical ButtonBox (joystick/HID) state with Euro Truck Simulator 2 (ETS2) telemetry / functionality.**  
This tool watches ETS2 telemetry and your ButtonBox and keeps the device state and in-game state synchronized (press a physical toggle → the script sends the corresponding key to ETS2 and mirrors state).

A small Windows utility that binds a physical button box (joystick) to Euro Truck Simulator 2 telemetry signals.

---

## Features ⭐  

- Raw input reading from ButtonBox using standard HID/joystick libraries (pygame/keyboard).  
- Configurable mapping between physical buttons on ButtonBox and ETS2 keyboard controls, via `config.json`.    
- Keeping your in-game state synced with the hardware switches by sending keystrokes to ETS2.
- Runs as a Python script (for development) **or** as a bundled Windows executable (via PyInstaller) — easy distribution.  
- Option to run with administrator privileges (helps with global input injection / HID access).  

	**Important Note**: Assign any keyboard key or combo keys(modifier + key) as primary for each and then assign button box physical switches as secondary in the ETS2 Key Binding Settings. So that this tool can able to sync the Physical Switch state with the ETS2 state through the keyboard key. If you assign just the primary or secondary key as button box key then this tool can't able to sync. So it need another key binding as keyboard key.
---

## Requirements ✅  

- **OS**: Windows (since the project uses Windows-specific APIs for global keyboard injection / window detection)  
- **ETS2**: Required Euro Truck Simulator 2 Game in your windows. [Buy Game](https://store.steampowered.com/app/227300/Euro_Truck_Simulator_2/)
- **ETS2-Telemetry-Server**: You need to run the ETS2 Telemetry server windows app. You can get it from this repo - [Funbit/ets2-telemetry-server](https://github.com/Funbit/ets2-telemetry-server)
- **Python**: 3.7+ recommended  
- **Python packages** (install via `pip`):  
  - `pygame`  
  - `keyboard`  
  - `pyautogui`, `pygetwindow` (or similar, depending on your implementation)  
  - `pywin32` or other Windows GUI / window-focus libraries  
  - `requests` (if used for any telemetry / external API — depending on your code)  

> If you plan to use the compiled executable (in `dist/`), you do **not** need Python installed on the target machine — just run the `.exe`.  

---

## Installation & Setup 🚀  

#### 1. Clone the repo  

```
git clone https://github.com/Arun-R-S/ButtonBox-Telemetry-Syncer.git  
cd ButtonBox-Telemetry-Syncer  
```

#### 2. (Optional) Create + activate virtual environment
```
python -m venv venv  
venv\Scripts\activate 
```

#### 3. Install dependencies
```
pip install pygame keyboard pyautogui pygetwindow pywin32 requests  
```

#### 4. Configure the project — see below.

#### 5. Run the syncer: either as Python script or using the bundled executable.
---

## Configuration 🔧(`config.json`) 

Your `config.json` is the heart of the mapping logic. Below is a **template + explanation** of the key fields.

### ⚙️ `config.json` — full explanation

Here is the exact config you provided (reformatted). I explain every key below.

```JSON
{
    "LoggingLevels": {
        "INFO": true,
        "WARN": true,
        "DEBUG": false,
        "DEBUGWARN": false,
        "ERROR": true
    },
    "ACTIVATE_SCRIPT_ONLY_IN_ETS2": true,
    "ETS2_WINDOW_TITLE": "Euro Truck Simulator 2",
    "isButtonNumberIndex": false,
    "TelemetryAPIAddress": "http://localhost:25555/api/ets2/telemetry",
    "JOYSTICK_BUTTON_MAPPINGS": [
		{
			"joystickButtonNumber": 1,
			"actionName": "Electricity",
			"telemetryPathToSync": "truck/electricOn",
			"keyToPress": [
					"shift",
					"e"
				]
		},
		{
			"joystickButtonNumber": 5,
			"actionName": "HighBeam",
			"telemetryPathToSync": "truck/lightsBeamHighOn",
			"keyToPress": "k"
		}
	]
}
``` 

### Meaning of each setting

-   **`LoggingLevels`** — toggle which logging levels are enabled:
    
    -   `INFO`, `WARN`, `DEBUG`, `DEBUGWARN`, `ERROR` — `true`/`false`.
        
    -   Set `DEBUG` to `true` while mapping buttons to get verbose console logs.
        
-   **`ACTIVATE_SCRIPT_ONLY_IN_ETS2`** — when `true`, the script will only perform key sends or sync actions when ETS2 window is detected (prevents accidental keypresses when ETS2 is not running). Recommended: `true`. ✅
    
-   **`ETS2_WINDOW_TITLE`** — partial/exact title used to detect ETS2 game window (default `"Euro Truck Simulator 2"`). If ETS2 uses a language/launcher that changes title, update this.
    
-   **`isButtonNumberIndex`** — boolean flag deciding how `joystickButtonNumber` values are interpreted:
    
    -   `false` (as in your config): the script expects **joystick button numbers starting at 1** (human-friendly numbering).
        
    -   `true`: the script will treat button numbers as **0-based indices** (typical of some libraries).  
        Use this to match what your input device library reports. (See mapping section below.)
        
-   **`TelemetryAPIAddress`** — URL the script polls to get ETS2 telemetry state (your default: `http://localhost:25555/api/ets2/telemetry`).
    
    -   Make sure an ETS2 telemetry server (mod/plugin) is running and exposing telemetry JSON at this address & port. The config expects the telemetry JSON to contain paths such as `truck/electricOn` or `truck/lightsBeamHighOn`. 🔌
        
-   **`JOYSTICK_BUTTON_MAPPINGS`** — array of mappings. Each mapping includes:
    
    -   `joystickButtonNumber` — the number/index of the physical button on your joystick box. How to interpret depends on `isButtonNumberIndex`.
        
    -   `actionName` — friendly name (for logs and UI).
        
    -   `telemetryPathToSync` — JSON path in ETS2 telemetry to read for current in-game status (the script will sync the device state with this telemetry value).
        
    -   `keyToPress` — the keyboard key(s) to send to ETS2 when the physical button state is not in sync. Can be a string (e.g. `"k"`) or an array for modifiers + key (e.g. `["shift", "e"]`). 

    **Important Note**: Assign any keyboard key or combo keys(modifier + key) as primary for each and then assign button box physical switches as secondary in the ETS2 Key Binding Settings. So that this tool can able to sync the Physical Switch state with the ETS2 state through the keyboard key. If you assign just the primary or secondary key as button box key then this tool can't able to sync. So it need another key binding as keyboard key.
---

## Running the Syncer 🏃

### As Python script (development mode)

`python app.py` 

If your `config.json` is not in the same folder, or named differently,  then the `app.py` will crash.

### As packaged executable (production / non-Python users)

-   Go to `dist/` directory — run the `.exe` (e.g. `ButtonBox-Telemetry-Syncer.exe`).
    
-   For best results, run as **Administrator** (right-click → “Run as administrator” or use the included `Run Syncer As Admin.bat`).
----

## Troubleshooting & Tips 🛠️

| Problem / Symptom | Possible Cause / Fix |
|--|--|
| Button presses not detected | Wrong `button_index` or wrong device ID — use debug script to verify. |
| Keypresses not working in ETS2 | Syncer not running as Admin; ETS2 not in foreground; wrong key mapping / ETS2 profile mismatch. |


💡 Enable `"DEBUG": true` and `"DEBUGWARN": true` in config to log all events to `console` — helps in diagnosing issues.

**Important Note**: Assign any keyboard key or combo keys(modifier + key) as primary for each and then assign button box physical switches as secondary in the ETS2 Key Binding Settings. So that this tool can 	able to sync the Physical Switch state with the ETS2 state through the keyboard key. If you assign just the primary or secondary key as button box key then this tool can't able to sync. So it need another key binding as keyboard key.

---

## Contributing 🤝
Contributions are welcome for this repository!


## License 📄
MIT License
