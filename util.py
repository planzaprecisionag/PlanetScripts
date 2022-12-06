from tkinter import filedialog
import tkinter as tk


# %%Function definitions
# display file browse dialog
def browse_files(init_browse_dir, browse_window_title, file_types):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    # NOTE: pass in filetypes as: filetypes = [("Comma separated values", "*.csv"), ("All files", "*.*")])
    fileName = filedialog.askopenfilename(initialdir=init_browse_dir, title=browse_window_title, filetypes=file_types)
    # cleanup then return filename
    root.withdraw()
    return fileName

# display folder browse dialog
def browse_for_directory(init_browse_dir, browse_window_title):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    dir_path = filedialog.askdirectory(parent=root, initialdir=init_browse_dir, title=browse_window_title)
    # cleanup then return dir path
    root.withdraw()
    return dir_path
