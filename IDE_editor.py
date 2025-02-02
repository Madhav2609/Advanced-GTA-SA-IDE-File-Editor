import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

class IDEFileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced GTA SA IDE File Editor")
        self.root.geometry("1000x600")

        # Variables
        self.ide_files = []
        self.current_directory = None
        self.file_sections = {}
        self.original_contents = {}
        self.search_results = []
        self.current_search_index = -1

        # Styling
        self.root.configure(bg="#2E2E2E")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#3A3A3A", foreground="white", font=("Arial", 10))
        style.configure("TLabel", background="#2E2E2E", foreground="white", font=("Arial", 12))

        # Sidebar Panel (File Explorer)
        self.sidebar = tk.Frame(self.root, bg="#252525", width=250)
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)
        
        tk.Label(self.sidebar, text="IDE Files", bg="#252525", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
        self.file_list = tk.Listbox(self.sidebar, bg="#1E1E1E", fg="white", font=("Arial", 11), selectbackground="#555555")
        self.file_list.pack(fill="both", expand=True, padx=5, pady=5)
        self.file_list.bind("<<ListboxSelect>>", self.navigate_to_file)

        # Search Bar
        self.search_frame = tk.Frame(self.root, bg="#2E2E2E")
        self.search_frame.pack(fill="x", padx=10, pady=5)
        
        self.search_entry = tk.Entry(self.search_frame, font=("Arial", 12), width=40)
        self.search_entry.pack(side="left", padx=5)
        
        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_text)
        self.search_button.pack(side="left", padx=5)
        
        self.next_button = ttk.Button(self.search_frame, text="Next", command=self.next_search_result)
        self.next_button.pack(side="left", padx=5)

        self.prev_button = ttk.Button(self.search_frame, text="Previous", command=self.previous_search_result)
        self.prev_button.pack(side="left", padx=5)

        self.clear_button = ttk.Button(self.search_frame, text="Clear", command=self.clear_search)
        self.clear_button.pack(side="left", padx=5)

        # Text Editor
        self.text_editor = scrolledtext.ScrolledText(self.root, wrap="word", undo=True, font=("Consolas", 12), bg="#1E1E1E", fg="white", insertbackground="white")
        self.text_editor.pack(expand=True, fill="both", padx=10, pady=10)

        # Menu
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open IDE Files", command=self.open_and_edit_files)
        file_menu.add_command(label="Save Changes", command=self.save_edits)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        

        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Generate Unused IDs & Description of IDEs", command=self.generate_unused_ids)
        tools_menu.add_command(label="IDE Renumberer", command=self.launch_IDE_Renumber_tool)
        tools_menu.add_command(label="IPL LOD SEPARATOR", command=self.launch_IPL_LOD_Separator_Tool)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        # Status Bar
        self.status_bar = ttk.Label(self.root, text="No file loaded", anchor="w")
        self.status_bar.pack(fill="x", side="bottom")

    def search_text(self):
        self.text_editor.tag_remove("search_highlight", "1.0", tk.END)
        search_query = self.search_entry.get().strip()
        if not search_query:
            return

        self.search_results = []
        self.current_search_index = -1
        start_pos = "1.0"
        
        while True:
            start_pos = self.text_editor.search(search_query, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_query)}c"
            self.text_editor.tag_add("search_highlight", start_pos, end_pos)
            self.search_results.append(start_pos)
            start_pos = end_pos  # Move forward

        self.text_editor.tag_config("search_highlight", background="yellow", foreground="black")
        self.next_search_result()  # Move to first match

    def next_search_result(self):
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.text_editor.see(self.search_results[self.current_search_index])

    def previous_search_result(self):
        if self.search_results:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.text_editor.see(self.search_results[self.current_search_index])

    def clear_search(self):
        self.text_editor.tag_remove("search_highlight", "1.0", tk.END)
        self.search_results = []
        self.current_search_index = -1

    def launch_IDE_Renumber_tool(self):
        tool_path = os.path.join(os.path.dirname(__file__), "IDE renumber.py")
        if os.path.exists(tool_path):
           subprocess.Popen(["python", tool_path], shell=True)
        else:
           messagebox.showerror("Error", "Tool script not found!")

    def launch_IPL_LOD_Separator_Tool(self):
        tool_path = os.path.join(os.path.dirname(__file__), "ipl lod separator.py")
        if os.path.exists(tool_path):
           subprocess.Popen(["python", tool_path], shell=True)
        else:
           messagebox.showerror("Error", "Tool script not found!")

    def generate_unused_ids(self):
        if not self.current_directory:
            messagebox.showwarning("No Directory Selected", "Please open an IDE directory first.")
            return

        output_path = os.path.join(self.current_directory, "unused_ids_and_description_of_IDEs.txt")
        used_ids = set()
        ide_details = []

        # Extracting used IDs from IDE files
        for ide_file in self.ide_files:
            ids, total_entries = self.extract_ids_from_ide(ide_file)
            used_ids.update(ids)
            ide_details.append(self.describe_ide_file(ide_file, ids, total_entries))

        unused_ids_formatted = self.find_unused_ids(used_ids)

        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write("\n".join(ide_details))
            output_file.write("\nUnused IDs from 0 to 90000:\n")
            output_file.write(unused_ids_formatted + "\n")

        messagebox.showinfo("Success", f"Unused IDs saved to {output_path}")

    def extract_ids_from_ide(self, file_path):
        ids = set()
        total_entries = 0
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    parts = line.strip().split(',')
                    if parts and parts[0].isdigit():
                        id_value = int(parts[0])
                        ids.add(id_value)
                        total_entries += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        return ids, total_entries

    def describe_ide_file(self, file_path, ids, total_entries):
        file_name = os.path.basename(file_path)
        min_id, max_id = (min(ids), max(ids)) if ids else ("N/A", "N/A")

        if "vehicle" in file_name.lower():
            description = "Defines all vehicles in the game."
        elif "map" in file_name.lower() or "objects" in file_name.lower():
            description = "Defines world objects and buildings."
        elif "ped" in file_name.lower():
            description = "Defines pedestrian models and behavior."
        else:
            description = "General game objects and assets."

        return f"File: {file_name}\nDescription: {description}\nID Range: {min_id} - {max_id}\nTotal Entries: {total_entries}\n{'-'*40}\n"

    def find_unused_ids(self, used_ids, id_range=90000):
        all_ids = set(range(id_range + 1))
        unused_ids = sorted(all_ids - used_ids)

        compressed_ranges = []
        start = None

        for i in range(len(unused_ids)):
            if start is None:
                start = unused_ids[i]
            if i == len(unused_ids) - 1 or unused_ids[i] + 1 != unused_ids[i + 1]:
                if start == unused_ids[i]:
                    compressed_ranges.append(str(start))
                else:
                    compressed_ranges.append(f"{start}-{unused_ids[i]}")
                start = None

        return ", ".join(compressed_ranges)
    def open_and_edit_files(self):
        self.current_directory = filedialog.askdirectory(title="Select GTA SA Directory")
        if not self.current_directory:
            return
        
        self.ide_files = []
        self.file_sections.clear()
        self.original_contents.clear()
        self.file_list.delete(0, tk.END)
        self.text_editor.delete("1.0", tk.END)

        for dirpath, _, filenames in os.walk(self.current_directory):
            for file in filenames:
                if file.lower().endswith(".ide"):
                    file_path = os.path.join(dirpath, file)
                    self.ide_files.append(file_path)

                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            file_content = f.read()
                            self.original_contents[file_path] = file_content

                            start_index = self.text_editor.index(tk.END)
                            self.text_editor.insert(tk.END, f"// --- {os.path.basename(file_path)} --- //\n", "file_header")
                            self.text_editor.insert(tk.END, file_content + "\n\n")
                            end_index = self.text_editor.index(tk.END)

                            self.file_sections[file_path] = (start_index, end_index)
                            self.file_list.insert(tk.END, os.path.basename(file_path))
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")

        self.status_bar.config(text=f"Loaded {len(self.ide_files)} IDE files")

    def navigate_to_file(self, event):
        try:
            self.text_editor.tag_remove("highlight", "1.0", tk.END)

            selected_file = self.file_list.get(self.file_list.curselection())
            for path, (start, end) in self.file_sections.items():
                if os.path.basename(path) == selected_file:
                    self.text_editor.see(start)
                    self.text_editor.tag_add("highlight", start, end)
                    self.text_editor.tag_config("highlight", background="#444444")
                    return
        except Exception:
            pass

    def save_edits(self):
        if not self.ide_files:
            messagebox.showwarning("No Files Loaded", "Please open IDE files first.")
            return

        full_text = self.text_editor.get("1.0", tk.END)

        try:
            for ide_file in self.ide_files:
                file_basename = os.path.basename(ide_file)
                start_marker = f"// --- {file_basename} --- //\n"

                start_index = full_text.find(start_marker)
                if start_index == -1:
                    continue

                start_index += len(start_marker)
                next_section_index = full_text.find("// ---", start_index)

                new_content = full_text[start_index:next_section_index].strip() if next_section_index != -1 else full_text[start_index:].strip()

                with open(ide_file, "w", encoding="utf-8", errors="ignore") as file:
                    file.write(new_content)

            messagebox.showinfo("Success", "Changes saved successfully!")
            self.status_bar.config(text="Changes saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving changes: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = IDEFileEditor(root)
    root.mainloop()
