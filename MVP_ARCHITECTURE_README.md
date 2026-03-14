# OpenSMU — Architecture Documentation

## Architecture Overview

The application uses **Model-View-Presenter (MVP)** combined with a **Hardware Abstraction Layer (HAL)** and a **Hierarchical State Machine**.

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    View     │◄──►│   Presenter  │◄──►│    Model    │
│  (UI Only)  │    │ (Controller) │    │  (Business  │
│             │    │              │    │   Logic)    │
└─────────────┘    └──────────────┘    └──────┬──────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │   HAL (devices/)   │
                                    │  SMUBase (abstract)│
                                    │  SMUSimulation     │
                                    │  keithley_2450     │
                                    │  keithley_24xx     │
                                    │  keithley_2611     │
                                    │  keithley_26xxab   │
                                    │  keysight_b2900    │
                                    └────────────────────┘
```

---

## File Structure

```
opensmu/
├── model/
│   ├── smu_model.py          # Business logic + state machine
│   └── measurement_data.py   # MeasurementData dataclass
├── presenter/
│   └── main_presenter.py     # Event handling, timer, UI coordination
├── view/
│   ├── view.py               # Main window, matplotlib canvas
│   └── components/
│       ├── config_dialog.py
│       ├── smu_control_widget.py
│       ├── iv_settings_widget.py
│       ├── rt_settings_widget.py
│       └── file_settings_widget.py
├── devices/
│   ├── smu_base.py           # Abstract base class (21 abstract methods)
│   ├── smu_simulation.py     # Simulation driver (no hardware needed)
│   ├── keithley2450.py       # SCPI
│   ├── keithley24xx.py       # SCPI
│   ├── keithley2611.py       # TSP
│   ├── keithley26xxab.py     # TSP
│   └── keysightB2900.py      # SCPI (not yet tested on hardware)
├── test/
│   ├── test_mvp.py
│   ├── test_simulation_driver.py
│   ├── test_state_machine.py
│   ├── test_measurement_data.py
│   ├── test_config_save_load.py
│   ├── test_smu_selection.py
│   └── test_view.py          # Visual launcher (not a pytest test)
├── config/
│   └── config.json           # Persistent configuration (auto save/load)
├── main_window.py            # Thin entry point
└── run.py                    # QApplication launcher
```

---

## Component Responsibilities

### Model (`model/smu_model.py`)
- All SMU operations, measurement logic, state machine
- Configuration load/save (`config/config.json`)
- HAL device instantiation based on configured SMU type
- No UI dependencies — can be used and tested independently

**Key methods:**
- `starter()`, `iv_starter()`, `rt_starter()` — measurement initialization
- `iv_get_plot()`, `rt_get_plot()` — data collection per timer tick
- `stoper()`, `saver()` — measurement completion and file handling
- `load_config()`, `save_config()`, `update_config()` — configuration management
- `set_state(SMUState)`, `get_current_state()` — state machine interface

### Presenter (`presenter/main_presenter.py`)
- Connects Model and View — neither layer knows about the other
- Handles all button signals and routes them to the model
- Owns the `QTimer` that drives measurements
- Updates the view with data returned by the model

**Key methods:**
- `start_clicked()`, `stop_clicked()`, `exit_clicked()` — UI event handlers
- `timeOutEvent()` — timer callback, calls `iv_get_plot()` or `rt_get_plot()`
- `open_config_dialog()` — opens config dialog and applies result to model

### View (`view/view.py`)
- Pure presentation — no business logic
- Renders matplotlib plots for IV and RT measurements
- Emits `closeSignal` on window close (presenter handles it)

**Key methods:**
- `plot_iv()`, `plot_rt()` — plot current data + historical runs
- `message()` — append status text to the communication box
- `clear_plot()` — reset the graph

### HAL (`devices/`)
- `SMUBase` defines 21 abstract methods that every driver must implement
- Each driver translates those calls into device-specific SCPI or TSP commands
- `SMUSimulation` implements all methods in memory (I = V/1kΩ + noise)
- Swapping hardware requires only changing `smu_type` in config — no code change

---

## State Machine

The state machine is implemented in `SMUModel` using the `SMUState` enum.

### SMUState Enum

```python
class SMUState(Enum):
    INITIALIZE     = auto()
    WAIT_FOR_EVENT = auto()
    START          = auto()
    STOP           = auto()
    EXIT           = auto()
    SAVE_DATA      = auto()
```

Using an `Enum` instead of a plain integer dictionary provides:
- **Type safety** — `SMUState.START` is unambiguous
- **IDE autocomplete** — all valid states are discoverable
- **Readability** — state comparisons are self-documenting

### State Transitions

```
INITIALIZE ──► WAIT_FOR_EVENT ──► START ──► WAIT_FOR_EVENT (measurement ticking)
                    ▲                │
                    │                ▼
                    └──── STOP ◄─── SAVE_DATA
                            ▲
                    EXIT ───┘  (if measurement was running)
```

### How the switcher works

```python
self.switcher = {
    SMUState.INITIALIZE:     self.initializer,
    SMUState.WAIT_FOR_EVENT: self.waiter,
    SMUState.START:          self.starter,
    SMUState.STOP:           self.stoper,
    SMUState.EXIT:           self.exiter,
    SMUState.SAVE_DATA:      self.saver,
}
```

`set_state(state)` assigns `self.currState` and immediately calls `state_machine_function()`, which dispatches to the correct handler via the switcher.

---

## Data Flow

### Measurement flow (IV example):
1. User clicks **Start** → `Presenter.start_clicked()`
2. Presenter calls `Model.set_state(SMUState.START)` → `starter()` runs
3. Presenter calls `Model.iv_starter()` → SMU configured, returns timer interval (ms)
4. Presenter starts `QTimer` with that interval
5. Each timer tick → `Presenter.timeOutEvent()` → `Model.iv_get_plot()`
6. Model sets next voltage, reads current, appends to data, returns `(x_vals, y_vals)`
7. Presenter calls `View.plot_iv()` to update the graph
8. When all voltage steps done, model sets `SMUState.SAVE_DATA`
9. Presenter detects this → calls `stop_clicked()` → `Model.set_state(SMUState.STOP)`

### Configuration flow:
1. User clicks **Configuration** → `Presenter.open_config_dialog()`
2. Dialog pre-filled from `Model.get_config()`
3. User edits and clicks OK → `Presenter` calls `Model.update_config(new_config)`
4. Model recreates SMU instance if `smu_type` changed, saves to `config/config.json`

---

## Running Tests

```bash
pytest test/ -v
```

Expected: **63 passed** (1 skipped if PyQt5 not available in headless environment).

Test files:
| File | Covers |
|---|---|
| `test_simulation_driver.py` | All 21 HAL methods on SMUSimulation |
| `test_state_machine.py` | All state transitions using SMUState enum |
| `test_measurement_data.py` | MeasurementData dataclass methods |
| `test_config_save_load.py` | Config load/save/roundtrip |
| `test_smu_selection.py` | SMU instance creation for all driver types |
| `test_mvp.py` | Model imports, defaults, initial state |

---

## Dependencies

| Package | Purpose |
|---|---|
| `PyQt5>=5.15` | GUI framework |
| `pyvisa>=1.13` | VISA instrument communication |
| `matplotlib>=3.7` | Real-time plotting |
| `numpy>=1.24` | Numerical operations (matplotlib dependency) |
| `pytest>=7.4` | Test runner |

Install all with:
```bash
pip install -r requirements.txt
```
