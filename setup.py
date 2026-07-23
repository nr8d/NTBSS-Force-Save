#!/usr/bin/env python3
"""
NTBSS-Force-Save Automated Setup Script
Handles installation, file placement, and configuration
"""

import os
import sys
import shutil
import winreg
from pathlib import Path


def get_game_directory():
    """Find the Naruto to Boruto game directory via Steam registry."""
    try:
        # Try to find Steam installation
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
            steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
            game_path = os.path.join(
                steam_path,
                "steamapps",
                "common",
                "Naruto To Boruto"
            )
            if os.path.exists(game_path):
                return game_path
    except:
        pass
    
    # Fallback: ask user
    print("Could not find game installation automatically.")
    print("Please enter the path to 'Naruto To Boruto' directory")
    print("(e.g., D:\\steam\\steamapps\\common\\Naruto To Boruto)")
    
    while True:
        user_path = input("Game directory: ").strip('"')
        if os.path.exists(user_path):
            return user_path
        print("Path not found. Try again.")


def create_temp_directory():
    """Create C:\\temp directory if it doesn't exist."""
    temp_dir = r"C:\temp"
    os.makedirs(temp_dir, exist_ok=True)
    print(f"✓ Temp directory ready: {temp_dir}")


def copy_ue4ss_files(game_dir):
    """Copy UE4SS files to game directory."""
    script_dir = Path(__file__).parent
    ue4ss_source = script_dir / "ue4ss"
    ue4ss_dest = Path(game_dir) / "NARUTO" / "Binaries" / "Win64"
    
    if not ue4ss_source.exists():
        print("⚠ Warning: ue4ss folder not found in repository")
        print(f"  Please manually copy UE4SS files to: {ue4ss_dest}")
        return False
    
    if not ue4ss_dest.exists():
        ue4ss_dest.mkdir(parents=True, exist_ok=True)
    
    # Copy all files from ue4ss folder
    for item in ue4ss_source.glob("*"):
        if item.is_file():
            shutil.copy2(item, ue4ss_dest / item.name)
            print(f"  ✓ Copied: {item.name}")
        elif item.is_dir():
            dest_subdir = ue4ss_dest / item.name
            if dest_subdir.exists():
                shutil.rmtree(dest_subdir)
            shutil.copytree(item, dest_subdir)
            print(f"  ✓ Copied folder: {item.name}")
    
    print(f"✓ UE4SS files installed to: {ue4ss_dest}")
    return True


def copy_lua_script(game_dir):
    """Copy main.lua to game directory."""
    script_dir = Path(__file__).parent
    lua_source = script_dir / "main.lua"
    lua_dest = Path(game_dir) / "NARUTO" / "Binaries" / "Win64" / "main.lua"
    
    if lua_source.exists():
        shutil.copy2(lua_source, lua_dest)
        print(f"✓ Lua script installed: {lua_dest}")
        return True
    else:
        print(f"⚠ Warning: main.lua not found at {lua_source}")
        return False


def verify_game_exe(game_dir):
    """Check if modified Naruto.exe exists."""
    exe_path = Path(game_dir) / "Naruto.exe"
    if exe_path.exists():
        print(f"✓ Game executable found: {exe_path}")
        return True
    else:
        print(f"⚠ Warning: Game executable not found at {exe_path}")
        print("  You need to replace Naruto.exe with the modified version")
        print("  (Backup your original first!)")
        return False


def create_savedata_directory():
    """Create SaveGames directory if needed."""
    save_dir = Path.home() / "Saved Games" / "NARUTO TO BORUTO SHINOBI STRIKER"
    save_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Save directory ready: {save_dir}")


def create_desktop_shortcut():
    """Create desktop shortcut for GUI."""
    try:
        from win32com.client import Dispatch
        
        desktop = Path.home() / "Desktop"
        script_path = Path(__file__).parent / "gui.py"
        shortcut_path = desktop / "Naruto Save Tool.lnk"
        
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(script_path)
        shortcut.WorkingDirectory = str(script_path.parent)
        shortcut.IconLocation = str(script_path.parent / "icon.ico")
        shortcut.save()
        
        print(f"✓ Desktop shortcut created: {shortcut_path}")
        return True
    except ImportError:
        print("⚠ Optional: pywin32 not installed (shortcut skipped)")
        print("  Install with: pip install pywin32")
        return False
    except Exception as e:
        print(f"⚠ Could not create shortcut: {e}")
        return False


def print_final_steps(game_dir):
    """Print remaining manual steps."""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nRemaining steps:")
    print("1. ✓ Temp directory created")
    print("2. ✓ UE4SS files installed")
    print("3. ✓ Lua script installed")
    print("4. TODO: Replace game .exe (if not done)")
    print("   - Backup: " + str(Path(game_dir) / "Naruto.exe"))
    print("   - Replace with modified version from parent repo")
    print("\nTo use the tool:")
    print("1. Launch the game and load into a lobby")
    print("2. Run: python gui.py")
    print("3. Click 'Dump Save' to export or 'Upload Save' to load")
    print("\n" + "="*60)


def main():
    """Main setup flow."""
    print("\n" + "="*60)
    print("NTBSS-Force-Save Setup")
    print("="*60 + "\n")
    
    # Step 1: Find game directory
    print("Step 1: Locating game directory...")
    game_dir = get_game_directory()
    print(f"✓ Found: {game_dir}\n")
    
    # Step 2: Create temp directory
    print("Step 2: Creating temp directory...")
    create_temp_directory()
    print()
    
    # Step 3: Create save directory
    print("Step 3: Creating save directory...")
    create_savedata_directory()
    print()
    
    # Step 4: Copy UE4SS files
    print("Step 4: Installing UE4SS files...")
    try:
        copy_ue4ss_files(game_dir)
    except Exception as e:
        print(f"✗ Error installing UE4SS: {e}")
    print()
    
    # Step 5: Copy Lua script
    print("Step 5: Installing Lua script...")
    try:
        copy_lua_script(game_dir)
    except Exception as e:
        print(f"✗ Error installing Lua script: {e}")
    print()
    
    # Step 6: Verify game exe
    print("Step 6: Checking game executable...")
    verify_game_exe(game_dir)
    print()
    
    # Step 7: Create desktop shortcut (optional)
    print("Step 7: Creating desktop shortcut...")
    create_desktop_shortcut()
    print()
    
    # Print final instructions
    print_final_steps(game_dir)
    
    input("\nPress Enter to close...")


if __name__ == "__main__":
    # Check if running on Windows
    if sys.platform != "win32":
        print("Error: This setup script requires Windows")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
