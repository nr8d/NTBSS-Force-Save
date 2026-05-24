import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

# ----------------------------------------
# PATHS
# ----------------------------------------

CMD_PATH = r"C:\temp\ue_cmd.txt"

GAME_SAVE = os.path.join(
    os.path.expanduser("~"),
    "Saved Games",
    "NARUTO TO BORUTO SHINOBI STRIKER",
    "dumped_save.sav"
)

os.makedirs(r"C:\temp", exist_ok=True)

# ----------------------------------------
# SEND COMMAND TO UE4SS
# ----------------------------------------

def send_command(cmd):

    with open(CMD_PATH, "w") as f:
        f.write(cmd)

# ----------------------------------------
# DUMP SAVE
# ----------------------------------------

def dump_save():

    try:
        # Tell UE4SS to dump
        send_command("dump")

        messagebox.showinfo(
            "Dump Started",
            "Wait 1-2 seconds then choose where to save."
        )

        # Ask user where to save file
        save_path = filedialog.asksaveasfilename(
            title="Save Dumped Save",
            defaultextension=".sav",
            filetypes=[("Save Files", "*.sav")]
        )

        if not save_path:
            return

        # Wait a little for UE to finish writing
        root.after(1500, lambda: finish_dump(save_path))

    except Exception as e:
        messagebox.showerror("Error", str(e))

def finish_dump(save_path):

    try:

        if not os.path.exists(GAME_SAVE):
            messagebox.showerror(
                "Error",
                "dumped_save.sav not found yet."
            )
            return

        shutil.copy2(GAME_SAVE, save_path)

        messagebox.showinfo(
            "Success",
            f"Save dumped to:\n{save_path}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ----------------------------------------
# UPLOAD SAVE
# ----------------------------------------

def upload_save():

    try:

        # User chooses save file
        selected_file = filedialog.askopenfilename(
            title="Select Save File",
            filetypes=[("Save Files", "*.sav")]
        )

        if not selected_file:
            return

        # Copy selected save into UE SaveGames folder
        shutil.copy2(selected_file, GAME_SAVE)

        # Tell UE4SS to upload
        send_command("upload")

        messagebox.showinfo(
            "Success",
            "Save uploaded to game."
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ----------------------------------------
# GUI
# ----------------------------------------

root = tk.Tk()

root.title("Naruto Save Tool")
root.geometry("350x180")

title = tk.Label(
    root,
    text="Naruto Save Tool",
    font=("Arial", 14, "bold")
)

title.pack(pady=10)

dump_btn = tk.Button(
    root,
    text="Dump Save",
    command=dump_save,
    width=25,
    height=2
)

dump_btn.pack(pady=10)

upload_btn = tk.Button(
    root,
    text="Upload Save",
    command=upload_save,
    width=25,
    height=2
)

upload_btn.pack(pady=10)

root.mainloop()