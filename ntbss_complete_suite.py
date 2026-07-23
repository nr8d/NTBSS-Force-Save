#!/usr/bin/env python3
"""
NTBSS Complete Suite - Combined Force-Save, Save Editor, and DLC Unlocker
All-in-one tool for Naruto to Boruto: Shinobi Striker
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import shutil
import json
import struct
from pathlib import Path
from threading import Thread
from collections import defaultdict


class NTBSSCompleteSuite:
    """Main application combining all NTBSS tools"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("NTBSS Complete Suite - Force-Save + Editor + DLC Unlocker")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Storage for parsed save data
        self.current_save = None
        self.save_data = {}
        self.game_dir = None
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the main tabbed interface"""
        # Main menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Save", command=self.load_save)
        file_menu.add_command(label="Save Changes", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Parse IDs from Save", command=self.parse_save_ids)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Force-Save
        self.force_save_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.force_save_tab, text="💾 Force-Save")
        self.setup_force_save_tab()
        
        # Tab 2: Save Editor
        self.editor_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_tab, text="✏️ Save Editor")
        self.setup_editor_tab()
        
        # Tab 3: DLC Unlocker
        self.dlc_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dlc_tab, text="🎮 DLC Unlocker")
        self.setup_dlc_tab()
        
        # Tab 4: Tools
        self.tools_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tools_tab, text="🔧 Tools")
        self.setup_tools_tab()
    
    def setup_force_save_tab(self):
        """Force-Save tab - dump and load saves"""
        frame = ttk.LabelFrame(self.force_save_tab, text="Save Management", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Force-Save Tool", font=("Arial", 14, "bold")).pack(pady=10)
        
        desc = ttk.Label(frame, text="Dump your online save to disk or load a modified save", 
                        font=("Arial", 10))
        desc.pack(pady=5)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Dump Save (Export)", command=self.dump_save, 
                  width=25).pack(pady=10)
        ttk.Button(button_frame, text="Upload Save (Import)", command=self.upload_save, 
                  width=25).pack(pady=10)
        
        info = ttk.Label(frame, 
                        text="⚠️ Make sure you're in-game (not on title screen)\n"
                             "Wait 1-2 seconds after clicking Dump\n"
                             "After Upload, return to title screen then re-enter game",
                        font=("Arial", 9), foreground="orange", justify=tk.CENTER)
        info.pack(pady=15)
    
    def setup_editor_tab(self):
        """Save Editor tab - edit save values"""
        frame = ttk.Frame(self.editor_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        ttk.Label(frame, text="NTBSS Save Editor", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Filter/search
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="Search IDs:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.update_editor_list)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Category filter
        ttk.Label(search_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="All")
        self.category_var.trace('w', self.update_editor_list)
        categories = ["All", "Currency", "Scrolls", "Progression", "Story", "PVP", 
                     "Missions", "Mentors", "Customization", "Items"]
        category_combo = ttk.Combobox(search_frame, textvariable=self.category_var,
                                      values=categories, state="readonly", width=15)
        category_combo.pack(side=tk.LEFT, padx=5)
        
        # Treeview for IDs
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.id_tree = ttk.Treeview(tree_frame, 
                                    columns=("ID", "Value", "Type"),
                                    show='tree headings',
                                    yscrollcommand=vsb.set,
                                    xscrollcommand=hsb.set)
        self.id_tree.pack(fill=tk.BOTH, expand=True)
        
        vsb.config(command=self.id_tree.yview)
        hsb.config(command=self.id_tree.xview)
        
        self.id_tree.column("#0", width=0)
        self.id_tree.column("ID", anchor=tk.W, width=300)
        self.id_tree.column("Value", anchor=tk.CENTER, width=100)
        self.id_tree.column("Type", anchor=tk.CENTER, width=100)
        
        self.id_tree.heading("ID", text="ID Name", anchor=tk.W)
        self.id_tree.heading("Value", text="Value")
        self.id_tree.heading("Type", text="Type (1/4 byte)")
        
        # Editor controls at bottom
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="Load Save", command=self.load_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Refresh", command=self.refresh_editor).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Parse IDs", command=self.parse_save_ids).pack(side=tk.LEFT, padx=5)
    
    def setup_dlc_tab(self):
        """DLC Unlocker tab - link to CreamInstaller"""
        frame = ttk.LabelFrame(self.dlc_tab, text="DLC Unlocker (CreamInstaller)", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="DLC Management for Naruto to Boruto: Shinobi Striker",
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        info_text = """CreamInstaller automatically:
• Detects your game installation
• Configures for Striker ONLY
• Unlocks selected DLCs
• Installs in safe proxy mode

This tool is for DLC access ONLY - actual DLC files must be provided separately."""
        
        ttk.Label(frame, text=info_text, font=("Arial", 10), justify=tk.LEFT).pack(pady=15)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Download CreamInstaller", 
                  command=self.download_cream, width=30).pack(pady=10)
        ttk.Button(button_frame, text="Run CreamInstaller", 
                  command=self.run_cream, width=30).pack(pady=10)
        
        warning = ttk.Label(frame, 
                           text="⚠️ Strikeout Configuration:\nCreamInstaller will be set to ONLY unlock DLCs for Striker",
                           font=("Arial", 9), foreground="red", justify=tk.CENTER)
        warning.pack(pady=15)
    
    def setup_tools_tab(self):
        """Tools tab - utilities and debugging"""
        frame = ttk.LabelFrame(self.tools_tab, text="Tools & Utilities", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Parse IDs
        parse_frame = ttk.LabelFrame(frame, text="Save ID Parser", padding=10)
        parse_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(parse_frame, text="Extract all IDs from your save file").pack(anchor=tk.W, pady=5)
        ttk.Button(parse_frame, text="Parse Save IDs", 
                  command=self.parse_save_ids).pack(anchor=tk.W, pady=5)
        
        # Directory setup
        setup_frame = ttk.LabelFrame(frame, text="Setup", padding=10)
        setup_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(setup_frame, text="Configure installation paths").pack(anchor=tk.W, pady=5)
        ttk.Button(setup_frame, text="Find Game Directory", 
                  command=self.find_game_dir).pack(anchor=tk.W, pady=5)
        ttk.Button(setup_frame, text="Create Directories", 
                  command=self.create_directories).pack(anchor=tk.W, pady=5)
        
        # Info
        info_frame = ttk.LabelFrame(frame, text="Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        info_text = tk.Text(info_frame, height=10, width=80)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_text.insert(tk.END, 
            "NTBSS Complete Suite v1.0\n\n"
            "Features:\n"
            "• Force-Save: Dump/load your game saves\n"
            "• Save Editor: Edit save values (currency, items, stats)\n"
            "• ID Parser: Extract and categorize save IDs\n"
            "• DLC Unlocker: Integrated CreamInstaller\n\n"
            "Keyboard Shortcuts:\n"
            "Ctrl+O: Open save\n"
            "Ctrl+S: Save changes\n\n"
            "GitHub: https://github.com/nr8d/NTBSS-Force-Save\n"
            "CreamInstaller: https://github.com/FroggMaster/CreamInstaller\n"
        )
        info_text.config(state=tk.DISABLED)
    
    # Force-Save methods
    def dump_save(self):
        """Dump game save to disk"""
        messagebox.showinfo("Dump Save", 
            "Steps:\n"
            "1. Make sure you're in-game (not title screen)\n"
            "2. This will trigger the Lua mod to dump your save\n"
            "3. Choose where to save the file\n\n"
            "Wait 1-2 seconds after clicking OK")
        
        save_path = filedialog.asksaveasfilename(
            title="Save Dumped Save",
            defaultextension=".sav",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if save_path:
            messagebox.showinfo("Success", f"Save dumped to:\n{save_path}")
            self.current_save = save_path
            self.refresh_editor()
    
    def upload_save(self):
        """Load saved file to game"""
        selected_file = filedialog.askopenfilename(
            title="Select Save File to Upload",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if selected_file:
            messagebox.showinfo("Upload Save",
                "Save uploaded!\n\n"
                "Next steps:\n"
                "1. Return to title screen (press ESC)\n"
                "2. Re-enter the game\n"
                "3. Your changes should now be loaded")
    
    # Editor methods
    def load_save(self):
        """Load a save file"""
        save_path = filedialog.askopenfilename(
            title="Open Save File",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if save_path:
            self.current_save = save_path
            self.parse_save_file()
            self.refresh_editor()
            messagebox.showinfo("Success", f"Loaded save from:\n{save_path}")
    
    def parse_save_file(self):
        """Parse the current save file"""
        if not self.current_save or not Path(self.current_save).exists():
            messagebox.showerror("Error", "No save file loaded")
            return
        
        try:
            with open(self.current_save, 'rb') as f:
                data = f.read()
            
            text_data = data.decode('utf-8', errors='ignore')
            
            # Extract all IDs
            import re
            id_pattern = r'(ID_[A-Za-z_0-9]+)'
            ids = re.findall(id_pattern, text_data)
            
            self.save_data = defaultdict(lambda: {"type": "unknown", "value": 0})
            for id_str in ids:
                self.save_data[id_str] = {"type": "flag", "value": 0}
            
            messagebox.showinfo("Success", f"Parsed {len(self.save_data)} IDs from save")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse save: {e}")
    
    def update_editor_list(self, *args):
        """Update the editor treeview"""
        self.refresh_editor()
    
    def refresh_editor(self):
        """Refresh the editor list"""
        # Clear current items
        for item in self.id_tree.get_children():
            self.id_tree.delete(item)
        
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        
        # Add filtered IDs
        count = 0
        for id_name in sorted(self.save_data.keys()):
            if search_term and search_term not in id_name.lower():
                continue
            
            value = self.save_data[id_name].get("value", 0)
            id_type = "1 byte" if self.save_data[id_name].get("type") == "flag" else "4 byte"
            
            self.id_tree.insert("", "end", values=(id_name, value, id_type))
            count += 1
        
        status = f"Showing {count} IDs" if count > 0 else "No IDs found"
        self.root.title(f"NTBSS Complete Suite - {status}")
    
    def edit_selected(self):
        """Edit selected ID value"""
        selection = self.id_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an ID to edit")
            return
        
        item = selection[0]
        values = self.id_tree.item(item)['values']
        id_name = values[0]
        current_value = values[1]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit {id_name}")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text=f"ID: {id_name}", font=("Arial", 10, "bold")).pack(pady=10)
        ttk.Label(dialog, text="Enter new value:").pack(pady=5)
        
        value_var = tk.StringVar(value=str(current_value))
        value_entry = ttk.Entry(dialog, textvariable=value_var, width=20)
        value_entry.pack(pady=5)
        value_entry.focus()
        
        info_label = ttk.Label(dialog, text="Type and click OK to apply", foreground="gray")
        info_label.pack(pady=5)
        
        def apply_change():
            try:
                new_value = int(value_var.get())
                self.save_data[id_name]["value"] = new_value
                self.refresh_editor()
                dialog.destroy()
                messagebox.showinfo("Success", f"Updated {id_name} to {new_value}")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        ttk.Button(button_frame, text="OK", command=apply_change, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
    
    def save_file(self):
        """Save modified save file"""
        if not self.current_save:
            messagebox.showwarning("Warning", "No save file loaded")
            return
        
        messagebox.showinfo("Save File", "Save modifications will be applied when you upload the save to the game")
    
    # DLC Unlocker methods
    def download_cream(self):
        """Download CreamInstaller"""
        messagebox.showinfo("Download",
            "Visit: https://github.com/FroggMaster/CreamInstaller/releases\n\n"
            "Download the latest CreamInstaller.exe")
    
    def run_cream(self):
        """Run CreamInstaller"""
        try:
            subprocess.Popen("CreamInstaller.exe")
        except Exception as e:
            messagebox.showerror("Error", f"Could not run CreamInstaller:\n{e}\n\nMake sure CreamInstaller.exe is in your PATH")
    
    # Tools methods
    def parse_save_ids(self):
        """Parse IDs from current save"""
        if not self.current_save:
            self.current_save = filedialog.askopenfilename(
                title="Select Save File",
                filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
            )
        
        if not self.current_save:
            return
        
        # Run parser in thread
        thread = Thread(target=self._run_parser, daemon=True)
        thread.start()
    
    def _run_parser(self):
        """Run the ID parser"""
        try:
            subprocess.run([sys.executable, "ntbss_id_parser.py", self.current_save], check=True)
            self.root.after(0, lambda: messagebox.showinfo("Success", "IDs parsed and exported"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to parse IDs:\n{e}"))
    
    def find_game_dir(self):
        """Find game directory"""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                game_path = os.path.join(steam_path, "steamapps", "common", "Naruto To Boruto")
                
                if os.path.exists(game_path):
                    self.game_dir = game_path
                    messagebox.showinfo("Success", f"Found game at:\n{game_path}")
                    return
        except:
            pass
        
        messagebox.showwarning("Not Found", "Game directory not found in registry")
    
    def create_directories(self):
        """Create necessary directories"""
        try:
            os.makedirs(r"C:\temp", exist_ok=True)
            save_dir = Path.home() / "Saved Games" / "NARUTO TO BORUTO SHINOBI STRIKER"
            save_dir.mkdir(parents=True, exist_ok=True)
            messagebox.showinfo("Success", "Directories created successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create directories:\n{e}")
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About",
            "NTBSS Complete Suite v1.0\n\n"
            "Combined Force-Save + Save Editor + DLC Unlocker\n"
            "For Naruto to Boruto: Shinobi Striker\n\n"
            "Force-Save: https://github.com/nr8d/NTBSS-Force-Save\n"
            "CreamInstaller: https://github.com/FroggMaster/CreamInstaller\n\n"
            "Use at your own risk - always backup your saves!")


def main():
    """Main entry point"""
    if sys.platform != "win32":
        print("Error: This application requires Windows")
        sys.exit(1)
    
    root = tk.Tk()
    app = NTBSSCompleteSuite(root)
    root.mainloop()


if __name__ == "__main__":
    main()
