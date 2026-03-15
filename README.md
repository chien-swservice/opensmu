# Support
If this software helped you with your measurements, consider supporting the project:
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/chiennguyen123)

# OpenSMU — IV and Real-Time Current Measurement

A desktop application for **IV sweep** and **real-time current measurements** using Source Measurement Units (SMUs) from Keithley and Keysight.

---

## Supported Hardware

| Device | Protocol | Status |
|---|---|---|
| Keithley 2611 | TSP | Tested (firmware 1.4.2) |
| Keithley 26xxAB (2635A, 2636A, 2637A, 2638A) | TSP | Implemented |
| Keithley 2450 | SCPI | Implemented |
| Keithley 24xx (2400, 2401, 2410, 2425 ...) | SCPI | Implemented |
| Keysight B2900 Series | SCPI | Implemented, not yet tested |
| Simulation (no hardware needed) | — | Built-in |

---

## Installation Options

There are two ways to use OpenSMU. Choose the one that fits you best:

| | Option A: Windows Installer | Option B: Run from Source |
|---|---|---|
| Requires Python | No | Yes |
| Platforms | Windows only | Windows, macOS, Linux |
| Best for | Lab users, non-programmers | Developers, contributors |

---

## Option A — Windows Installer (Recommended for most users)

### Prerequisites

**NI-VISA** must be installed to communicate with real hardware instruments (Keithley, Keysight).
Download it here: [https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html)

> Simulation mode works without NI-VISA.

### Install

1. Download `opensmu_setup_v0.1.1.exe` from the [Releases page](https://github.com/chien-swservice/opensmu/releases)
2. Run the installer — Windows will ask for administrator permission, click **Yes**
3. Follow the setup wizard (choose Start Menu shortcut, optional desktop shortcut)
4. Launch **opensmu** from the Start Menu or desktop

### Uninstall

Go to **Windows Settings → Apps → opensmu → Uninstall**.

---

## Option B — Run from Source Code

Use this option if you want to modify the code, contribute, or run on macOS / Linux.

### Step 1 — Install Python

1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download **Python 3.9 or newer** (3.12 recommended)
3. Run the installer
   - **Windows**: check the box **"Add Python to PATH"** before clicking Install

To verify:
```
python --version
```
You should see something like `Python 3.12.10`.

---

### Step 2 — Install Git

1. Go to [https://git-scm.com/downloads](https://git-scm.com/downloads)
2. Download and install Git for your operating system
3. Use all default options during installation

To verify:
```
git --version
```

---

### Step 3 — Download the Project

Open a terminal and run:
```
git clone https://github.com/chien-swservice/opensmu.git
cd opensmu
```

---

### Step 4 — Create a Virtual Environment

**Windows:**
```
python -m venv .venv
```

**macOS / Linux:**
```
python3 -m venv .venv
```

---

### Step 5 — Install Dependencies

**Windows:**
```
.venv\Scripts\pip install -r requirements.txt
```

**macOS / Linux:**
```
.venv/bin/pip install -r requirements.txt
```

This installs all required libraries (PyQt5, pyvisa, matplotlib, numpy, pytest).

---

### Step 6 — Activate the Virtual Environment

You need to activate the virtual environment each time you open a new terminal.

**Windows:**
```
.venv\Scripts\activate
```

**macOS / Linux:**
```
source .venv/bin/activate
```

Your terminal prompt will change to show `(.venv)` — this means the environment is active.

---

### Step 7 — Run the Program

With the virtual environment active:
```
python run.py
```

The application window will open. By default it starts in **Simulation mode** — no hardware required.

---

### Using with VS Code

1. Open the `opensmu` folder in VS Code (`File → Open Folder`)
2. Press `Ctrl+Shift+P` → type `Python: Select Interpreter`
3. Choose the interpreter inside `.venv` (shown as **Recommended**)
4. Open `run.py` and press `F5` to launch the application

---

### Running Tests

To verify your installation:

**Windows:**
```
.venv\Scripts\python -m pytest test/ -v
```

**macOS / Linux:**
```
.venv/bin/python -m pytest test/ -v
```

Expected result: **63 passed**.

---

## Using the Application

### First Launch

The program opens in **Simulation mode** with default settings. You can:
- Click **Start** to run a simulated IV sweep immediately
- Click **Configuration** to change measurement parameters
- Click **Stop** to end a measurement
- Click **Clear Graph** to reset the plot
- Click **Exit** to close the program

Measurement data is automatically saved to `~/opensmu_data/` (your home folder) as a `.txt` file.

---

### Configuration

Click the **Configuration** button to open the settings dialog.

**SMU Control tab:**
| Setting | Description |
|---|---|
| SMU Type | Select your hardware (`simulation` if no hardware) |
| VISA Address | GPIB/USB address of your instrument (e.g. `GPIB0::24::INSTR`) |
| Terminal | Front or Rear terminals |
| NPLC | Integration time (1.0 = 1 power line cycle, ~20 ms) |
| Measurement Mode | IV sweep or Real-time |

**IV tab** — settings for voltage sweep:
| Setting | Description |
|---|---|
| Start Voltage (V) | Beginning of the sweep |
| Stop Voltage (V) | End of the sweep |
| Step Voltage (V) | Voltage increment per step |
| Voltage Range (V) | Maximum expected voltage |
| Current Range (A) | Maximum expected current |
| Source Delay (ms) | Wait time after setting voltage before measuring |

**RT tab** — settings for real-time monitoring:
| Setting | Description |
|---|---|
| Voltage Set (V) | Fixed voltage applied during measurement |
| Voltage Range (V) | Maximum expected voltage |
| Current Range (A) | Maximum expected current |
| Aperture (s) | Sampling interval |

**File tab:**
| Setting | Description |
|---|---|
| Save Folder | Folder where data files are saved |
| File Name | Prefix for data file names |

---

### Connecting a Real SMU

1. Connect your SMU to the PC via GPIB, USB, or LAN
2. Install NI-VISA: [https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html)
3. Open **Configuration**, set **SMU Type** to your device, and enter the **VISA Address**
4. Click **Start**

> **Tip:** Use NI MAX (Windows) or run the following to find your instrument's VISA address:
> ```
> python -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"
> ```

---

## Data Files

Measurement data is saved as tab-separated `.txt` files in your configured save folder (`~/opensmu_data/` by default).

- **IV files**: `IV<filename><timestamp>.txt` — columns: `voltage`, `current`
- **RT files**: `RT<filename><timestamp>.txt` — columns: `time`, `current`

These can be opened directly in Excel, Origin, or any text editor.

---

## Building the Installer (developers only)

To build the Windows installer from source:

1. Install PyInstaller:
   ```
   .venv\Scripts\pip install pyinstaller
   ```

2. Build the executable:
   ```
   .venv\Scripts\pyinstaller installer/opensmu.spec --distpath installer/dist --workpath installer/build
   ```

3. Build the installer (requires [Inno Setup](https://jrsoftware.org/isdl.php)):
   ```
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\opensmu_installer.iss
   ```

Output: `installer/dist/opensmu_setup_v0.1.1.exe`

---

## License

MIT License — Copyright (c) 2026 Thanh Chien Nguyen. See [LICENSE](LICENSE) for details.
