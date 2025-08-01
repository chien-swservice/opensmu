# Configuration Save/Load Functionality

This document explains how the SMU application saves and loads configuration settings for persistent use across program sessions.

## Overview

The application now automatically saves the configuration to a JSON file (`config/config.json`) and loads it when the program starts. This ensures that your measurement settings are preserved between program runs.

## How It Works

### 1. Configuration Structure

The configuration is organized into three main sections:

- **IV Settings**: Parameters for IV (current-voltage) measurements
- **RT Settings**: Parameters for real-time measurements  
- **Global Settings**: General application settings

### 2. Automatic Saving

The configuration is automatically saved in the following situations:

- When you click "OK" in the Configuration dialog
- When the program exits (via Exit button or window close)
- When configuration is updated from the view

### 3. Automatic Loading

The configuration is automatically loaded when:

- The program starts up
- The configuration dialog is opened (shows saved values)

## Configuration File

The configuration is saved to `config/config.json` in the config folder. The file structure looks like this:

```json
{
    "IV": {
        "source_delay_ms": 50,
        "voltage_range": 2.0,
        "startV": -1.0,
        "stopV": 1.0,
        "stepV": 0.1,
        "current_range": 1e-6
    },
    "RT": {
        "rt_voltage_range": 2.0,
        "rt_voltage_set": 0.5,
        "rt_current_range": 1e-6,
        "rt_aperture": 1.0
    },
    "global": {
        "visa_name": "GPIB1::1::INSTR",
        "terminal": "FRONT",
        "nplc": 1.0,
        "meas_mode": "IV",
        "save_folder": "C:/path/to/data",
        "file_name": "data",
        "y_scale": "linear"
    }
}
```

## Implementation Details

### MainWindow Class

The `MainWindow` class includes these new methods:

- `load_config()`: Loads configuration from `config/config.json`
- `save_config()`: Saves current configuration to `config/config.json`
- `apply_config_to_view()`: Applies loaded configuration to view components

### ConfigDialog Class

The `ConfigDialog` class includes:

- `apply_config_to_dialog()`: Applies loaded configuration to dialog components

## Error Handling

The system includes robust error handling:

- If `config/config.json` doesn't exist, default configuration is used
- If the file is corrupted, default configuration is used
- All errors are logged to the console for debugging

## Testing

You can test the configuration functionality using the provided test script:

```bash
python test_config_save_load.py
```

This script demonstrates:
- Creating a sample configuration
- Saving it to a file
- Loading it back
- Error handling for missing files

## Usage

1. **First Run**: The program will use default settings and create `config/config.json` when you first configure settings
2. **Subsequent Runs**: The program will automatically load your saved settings
3. **Configuration Changes**: Any changes made through the Configuration dialog are automatically saved
4. **Manual Backup**: You can manually backup `config/config.json` to preserve your settings

## Troubleshooting

### Configuration Not Loading

If your configuration isn't loading:

1. Check that `config/config.json` exists in the config folder
2. Verify the file is valid JSON format
3. Check console output for error messages

### Configuration Not Saving

If your configuration isn't saving:

1. Check write permissions in the application directory
2. Verify the application has permission to create/modify files
3. Check console output for error messages

### Reset to Defaults

To reset to default configuration:

1. Delete the `config/config.json` file
2. Restart the application
3. The program will use default settings

## File Locations

- **Windows**: `config/config.json` is saved in the config folder
- **Linux/Mac**: `config/config.json` is saved in the config folder

## Security Notes

- The configuration file contains measurement parameters only
- No sensitive information (passwords, API keys) is stored
- The file is in plain text JSON format for easy inspection and editing 