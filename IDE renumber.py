import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def get_ide_files(directory):
    return glob.glob(os.path.join(directory, "*.ide"))

def renumber_ide_files(directory, start_id, mode, file_ids=None):
    ide_files_list = get_ide_files(directory)
    if not ide_files_list:
        messagebox.showerror("Error", "No IDE files found in the selected directory.")
        return

    try:
        start_id = int(start_id)
    except ValueError:
        messagebox.showerror("Error", "Invalid start ID. Please enter a number.")
        return
    
    for file_path in ide_files_list:
        temp_file = os.path.join(directory, "temp_ide.txt")
        file_start_id = start_id if mode == "Batch" else file_ids.get(file_path, start_id)
        
        try:
            file_start_id = int(file_start_id)
        except ValueError:
            messagebox.showerror("Error", f"Invalid start ID for {os.path.basename(file_path)}.")
            continue

        with open(file_path, 'r') as source_file, open(temp_file, 'w') as dst_file:
            valid_line = False
            for line in source_file:
                if line.startswith(("objs", "tobj")):
                    valid_line = True
                
                if not (line.startswith('#') or line.startswith('\n') or line[0].isalpha()):
                    if valid_line:
                        ide_line = line.split(',')
                        ide_line[0] = str(file_start_id)
                        ide_line.pop()
                        ide_line = ",".join(ide_line) + ", 0\n"
                        dst_file.write(ide_line)
                        file_start_id += 1
                        start_id += 1  # Ensure start_id continues across files in Batch Mode
                    else:
                        dst_file.write(line)
                else:
                    dst_file.write(line)
                
                if line.startswith("end"):
                    valid_line = False
        
        os.remove(file_path)
        os.rename(temp_file, file_path)
    
    messagebox.showinfo("Success", "IDE files renumbered successfully!")

def browse_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)
    update_file_list()

def update_file_list():
    directory = folder_path.get()
    ide_files = get_ide_files(directory)
    
    for widget in file_list_frame.winfo_children():
        widget.destroy()

    file_canvas.yview_moveto(0)  # Reset scroll position
    file_entries.clear()
    
    if mode_var.get() == "Individual":
        for file in ide_files:
            frame = tk.Frame(file_list_frame, bg="#1E1E1E")
            frame.pack(fill='x', pady=2, padx=5)
            
            tk.Label(frame, text=os.path.basename(file), width=25, anchor="w", bg="#1E1E1E", fg="white").pack(side='left', padx=5)
            entry = tk.Entry(frame, width=10, bg="#3A3A3A", fg="white")
            entry.pack(side='right', padx=5)
            file_entries[file] = entry

    # Update scrollable region after adding new content
    file_canvas.update_idletasks()
    file_canvas.configure(scrollregion=file_canvas.bbox("all"))

def start_renumbering():
    directory = folder_path.get()
    start_id_str = start_id_entry.get().strip()  # Add strip() to remove any whitespace
    mode = mode_var.get()
    
    if not directory:
        messagebox.showerror("Error", "Please select a folder.")
        return
    
    if not start_id_str:
        messagebox.showerror("Error", "Please enter a Start ID.")
        return
        
    # Debug print to see what value we're getting
    print(f"Start ID entered: '{start_id_str}'")
    
    try:
        start_id = int(start_id_str)
        print(f"Converted to integer: {start_id}")
    except ValueError:
        messagebox.showerror("Error", f"Invalid Start ID: '{start_id_str}'. Please enter a number only.")
        return
    
    file_ids = {file: entry.get().strip() for file, entry in file_entries.items()} if mode == "Individual" else None
    renumber_ide_files(directory, start_id, mode, file_ids)

# GUI Setup
root = tk.Tk()
root.title("IDE ID Renumber Script")
root.geometry("550x700")
root.configure(bg="#2E2E2E")

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", background="#3A3A3A", foreground="white", font=("Arial", 10))
style.configure("TLabel", background="#2E2E2E", foreground="white", font=("Arial", 12))

folder_path = tk.StringVar()
mode_var = tk.StringVar(value="Batch")
file_entries = {}

# Folder Selection
frame_top = tk.Frame(root, bg="#2E2E2E")
frame_top.pack(fill="x", padx=10, pady=5)

tk.Label(frame_top, text="Select IDE Files Folder:", bg="#2E2E2E", fg="white").pack(anchor="w")
entry_folder = tk.Entry(frame_top, textvariable=folder_path, width=50, state="readonly", bg="#1E1E1E", fg="white")
entry_folder.pack(side="left", padx=5, pady=5)
ttk.Button(frame_top, text="Browse", command=browse_folder).pack(side="right", padx=5)

# Mode Selection
frame_mode = tk.Frame(root, bg="#2E2E2E")
frame_mode.pack(fill="x", padx=10, pady=5)

tk.Label(frame_mode, text="Mode:", bg="#2E2E2E", fg="white").pack(anchor="w")
tk.Radiobutton(frame_mode, text="Batch - Single start ID for all files", variable=mode_var, value="Batch", command=update_file_list, bg="#2E2E2E", fg="white", selectcolor="#444").pack(anchor="w")
tk.Radiobutton(frame_mode, text="Individual - Unique start ID for each file", variable=mode_var, value="Individual", command=update_file_list, bg="#2E2E2E", fg="white", selectcolor="#444").pack(anchor="w")

# Start ID Entry
frame_id = tk.Frame(root, bg="#2E2E2E")
frame_id.pack(fill="x", padx=10, pady=5)

tk.Label(frame_id, text="Enter Start ID (Batch Mode):", bg="#2E2E2E", fg="white").pack(anchor="w")
start_id_entry = tk.Entry(frame_id, width=10, bg="#1E1E1E", fg="white", insertbackground="white")
start_id_entry.pack(anchor="w", pady=5)

# Scrollable File List
frame_files = tk.Frame(root, bg="#2E2E2E", bd=2, relief="sunken")
frame_files.pack(fill="both", expand=True, padx=10, pady=5)

file_canvas = tk.Canvas(frame_files, bg="#1E1E1E", highlightthickness=0)
file_scrollbar = ttk.Scrollbar(frame_files, orient="vertical", command=file_canvas.yview)
file_frame_container = tk.Frame(file_canvas, bg="#1E1E1E")

file_canvas.create_window((0, 0), window=file_frame_container, anchor="nw")
file_canvas.configure(yscrollcommand=file_scrollbar.set)

file_scrollbar.pack(side="right", fill="y")
file_canvas.pack(side="left", fill="both", expand=True)

file_list_frame = tk.Frame(file_frame_container, bg="#1E1E1E")
file_list_frame.pack(fill="both", expand=True)

# Start Button
style.configure("Bold.TButton", font=("Arial", 10, "bold"))
start_button = ttk.Button(root, text="Renumber IDs", command=start_renumbering, style="Bold.TButton")
start_button.pack(pady=10)

root.mainloop()