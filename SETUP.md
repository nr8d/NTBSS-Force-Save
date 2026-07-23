# NTBSS-Force-Save Setup Guide

## Automated Setup (Recommended)

### Prerequisites
- Windows OS
- Python 3.6+
- Game installed at default Steam location: `D:\steam\steamapps\common\Naruto To Boruto\` (or similar)

### Installation Steps

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/nr8d/NTBSS-Force-Save.git
   cd NTBSS-Force-Save
   ```

2. **Run the automated setup script**
   ```bash
   python setup.py
   ```

3. **The script will automatically:**
   - Locate your game directory (or ask for manual path)
   - Create necessary temp directories (`C:\temp`)
   - Create save data directory (`%USERPROFILE%\Saved Games\NARUTO TO BORUTO SHINOBI STRIKER`)
   - Copy UE4SS mod files to the game directory
   - Install the Lua command listener script
   - Create a desktop shortcut (optional)

4. **Manual step - Replace game executable:**
   - Backup your original `Naruto.exe` from the game root directory
   - Replace it with the modified version
   - (The modified exe is available in the parent repository: [alfizari/NTBSS-Force-Save](https://github.com/alfizari/NTBSS-Force-Save))

5. **Verify setup:**
   - Check that these files exist:
     - `C:\temp\` (will be used for commands)
     - `%USERPROFILE%\Saved Games\NARUTO TO BORUTO SHINOBI STRIKER\` (for save files)
     - Game directory has UE4SS files in: `NARUTO\Binaries\Win64\`

## Manual Setup (Alternative)

If the automated setup doesn't work, follow these steps:

### 1. Prepare Directories
```
C:\temp\
%USERPROFILE%\Saved Games\NARUTO TO BORUTO SHINOBI STRIKER\
```

### 2. Copy Files to Game Directory
- Copy contents of `ue4ss` folder to: `D:\steam\steamapps\common\Naruto To Boruto\NARUTO\Binaries\Win64\`
- Copy `main.lua` to: `D:\steam\steamapps\common\Naruto To Boruto\NARUTO\Binaries\Win64\`

### 3. Replace Game Executable
- Backup: `D:\steam\steamapps\common\Naruto To Boruto\Naruto.exe`
- Replace with modified version from parent repository

## Usage

### Option A: GUI (Recommended)
```bash
python gui.py
```
A window will appear with two buttons:
- **Dump Save**: Export your current game save to disk
- **Upload Save**: Load a modified save into the game

### Option B: Python Script (Advanced)
```bash
# Dump save
python -c "from gui import dump_save; dump_save()"

# Upload save
python -c "from gui import upload_save; upload_save()"
```

## How It Works

1. **Python GUI** (`gui.py`) - User interface for dumping/loading saves
   - Communicates via command files (`C:\temp\ue_cmd.txt`)
   - Manages save file locations

2. **Lua Script** (`main.lua`) - Game-side mod
   - Loaded by UE4SS (UE Unreal Speculative Script)
   - Listens for commands from Python GUI
   - Interfaces with Unreal Engine save system
   - Executes dump/upload operations

3. **Modified Game Executable** - Enabled mod support
   - Allows UE4SS Lua scripts to run
   - Required for the mod to function

## Troubleshooting

### "dumped_save.sav not found yet"
- Make sure you're in-game (not on title screen)
- Wait a moment and try dump again
- Check that `C:\temp\ue_cmd.txt` exists

### GUI won't start
- Ensure Python 3.6+ is installed
- Run in command line to see error messages:
  ```bash
  python gui.py
  ```

### Saves not syncing to Steam
- After uploading a save, return to title screen
- Re-enter the game
- The Steam sync should occur automatically

### Game crashes
- Make sure you backed up the original `Naruto.exe`
- Verify UE4SS files are properly installed
- Check that `main.lua` is in the correct location

## File Structure

```
NTBSS-Force-Save/
├── setup.py              # Automated setup script
├── gui.py                # Python GUI application
├── main.lua              # UE4SS Lua mod script
├── ue4ss/                # UE4SS mod files
│   └── [UE4SS files]
├── SETUP.md              # This file
├── README.md             # Original readme
└── LICENSE               # GPL-2.0 License
```

## Safety Notes

⚠️ **Important:**
- Always backup your original `Naruto.exe`
- Always backup your save files before testing modifications
- This tool modifies your game executable - use at your own risk
- The parent repository contains the modified executable

## Support

For issues with:
- **This setup script**: Check the troubleshooting section above
- **UE4SS/Lua scripts**: See the original repository: [alfizari/NTBSS-Force-Save](https://github.com/alfizari/NTBSS-Force-Save)
- **Game compatibility**: Ensure your game version matches the mod requirements

## License

GNU General Public License v2.0 - See LICENSE file
