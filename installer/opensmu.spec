# installer/opensmu.spec
# PyInstaller spec file for opensmu
#
# Usage (run from project root):
#   pyinstaller installer/opensmu.spec
#
# Output will be in installer/dist/opensmu/

import sys
from pathlib import Path

# Project root is one level up from this spec file
project_root = Path(SPECPATH).parent

a = Analysis(
    [str(project_root / 'run.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include config file
        (str(project_root / 'config' / 'config.json'), 'config'),
        # Include view components (PyQt5 .ui files if any exist in future)
        (str(project_root / 'view'), 'view'),
    ],
    hiddenimports=[
        # pyvisa backends
        'pyvisa',
        'pyvisa.resources',
        'pyvisa.resources.messagebased',
        'pyvisa.resources.gpib',
        'pyvisa.resources.usb',
        'pyvisa.resources.tcpip',
        'pyvisa.resources.serial',
        'pyvisa.ctwrapper',
        'pyvisa.ctwrapper.functions',
        # matplotlib backends
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_agg',
        # numpy
        'numpy',
        'numpy.core._dtype_ctypes',
        # PyQt5
        'PyQt5.QtPrintSupport',
        # SMU drivers (lazy imported, PyInstaller won't detect them automatically)
        'devices.keithley2611',
        'devices.keithley26xxab',
        'devices.keithley2450',
        'devices.keithley24xx',
        'devices.keysightB2900',
        'devices.smu_simulation',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='opensmu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,       # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='installer/opensmu.ico',  # Uncomment when icon is available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='opensmu',
)
