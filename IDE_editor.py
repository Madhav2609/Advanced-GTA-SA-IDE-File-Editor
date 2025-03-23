import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import re

class IDEFileEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced GTA SA IDE File Editor by Madhav2609")
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

        # Text Editor with syntax highlighting configuration
        self.text_editor = scrolledtext.ScrolledText(self.root, wrap="word", undo=True, 
            font=("Consolas", 12), bg="#1E1E1E", fg="white", insertbackground="white")
        self.text_editor.pack(expand=True, fill="both", padx=10, pady=10)

        # Configure syntax highlighting tags
        self.text_editor.tag_configure("section", foreground="#00FF00")      # Section headers
        self.text_editor.tag_configure("id", foreground="#FFA500")          # ID numbers
        self.text_editor.tag_configure("modelname", foreground="#ADD8E6")   # Model names
        self.text_editor.tag_configure("coordinate", foreground="#FF69B4")   # Coordinates
        self.text_editor.tag_configure("comment", foreground="#808080")     # Comments
        self.text_editor.tag_configure("keyword", foreground="#FF00FF")     # Special keywords
        
        # Bind syntax highlighting to text changes
        self.text_editor.bind("<KeyRelease>", self.highlight_syntax)

        # Menu
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open IDE Files (Scans Folders)", command=self.open_and_edit_files)
        file_menu.add_command(label="Open IDE Files (Multiple)", command=self.open_multiple_files)
        file_menu.add_command(label="Save Changes", command=self.save_edits)
        file_menu.add_command(label="Save Selected File", command=self.save_selected_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        

        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Generate Unused IDs & Description of IDEs", command=self.generate_unused_ids)
        tools_menu.add_command(label="Generate Duplicated IDs of IDEs", command=self.generate_duplicate_ids)
        tools_menu.add_command(label="IDE Renumbering", command=self.launch_IDE_Renumber_tool)
        tools_menu.add_command(label="IPL Lod Separator", command=self.launch_IPL_LOD_Separator_Tool)
        tools_menu.add_command(label="IPL ID Sorting", command=self.launch_IPL_ID_Sorting_Tool)
        
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
    
    def launch_IPL_ID_Sorting_Tool(self):
        tool_path = os.path.join(os.path.dirname(__file__), "IPL ID Sorting Script.py")
        if os.path.exists(tool_path):
           subprocess.Popen(["python", tool_path], shell=True)
        else:
           messagebox.showerror("Error", "Tool script not found!")



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


    def generate_duplicate_ids(self):
        if not self.current_directory:
            messagebox.showwarning("No Directory Selected", "Please open an IDE directory first.")
            return

        output_path = os.path.join(self.current_directory, "duplicated_objects.txt")
        id_dict = {}  # Format: {id_number: [(ide_file, model_name), ...]}
        model_dict = {}  # Format: {model_name_lower: [(ide_file, original_model_name), ...]}
        id_duplicates = []
        model_duplicates = []

        # Keywords to ignore
        ignore_keywords = {"objs", "end", "tobj", "path", "2dfx", "anim", "txdp"}

        # First pass: collect all IDs and model names
        for ide_file in self.ide_files:
            if ide_file.endswith(".ide") and os.path.exists(ide_file):
                try:
                    with open(ide_file, 'r', encoding="utf-8") as file:
                        current_section = None
                        for line in file:
                            line = line.strip()
                            
                            if not line or line.startswith("#"):
                                continue
                            
                            # Update section tracking    
                            lower_line = line.lower()
                            if lower_line in {"objs", "tobj", "weap", "peds", "cars", "hier", "end", "path", "2dfx", "anim", "txdp"}:
                                current_section = lower_line
                                continue
                            
                            # Skip processing for non-data sections
                            if not current_section or current_section in {"end", "path", "2dfx", "anim", "txdp"}:
                                continue

                            parts = [part.strip() for part in line.split(',')]
                            
                            # Get ID and model name regardless of section type
                            # Just check if we have at least 2 parts and first is a number
                            if len(parts) >= 2 and parts[0].strip().isdigit():
                                id_number = parts[0].strip()
                                model_name = parts[1].strip()
                                
                                # Store the section type with the data for better reporting
                                if id_number not in id_dict:
                                    id_dict[id_number] = []
                                id_dict[id_number].append((ide_file, model_name, current_section))

                                # Store model name occurrences (case-insensitive)
                                if model_name:
                                    model_name_lower = model_name.lower()
                                    if model_name_lower not in model_dict:
                                        model_dict[model_name_lower] = []
                                    model_dict[model_name_lower].append((ide_file, model_name, current_section))

                except Exception as e:
                    print(f"Error processing {ide_file}: {e}")

        # Second pass: identify duplicates
        for id_number, occurrences in id_dict.items():
            if len(occurrences) > 1:
                files_info = [f"{os.path.basename(file)} ({section})" for file, _, section in occurrences]
                duplicate_entry = f"ID {id_number} is used by: {' and '.join(files_info)}"
                id_duplicates.append(duplicate_entry)

        for model_name_lower, occurrences in model_dict.items():
            if len(occurrences) > 1:
                # Filter out duplicates from the same file
                unique_files = {(os.path.basename(file), section) for file, _, section in occurrences}
                if len(unique_files) > 1:
                    files_info = [f"{file} ({section})" for file, section in unique_files]
                    model_name = occurrences[0][1]  # Use the first occurrence's original model name
                    duplicate_entry = f"Model {model_name} is used by: {' and '.join(sorted(files_info))}"
                    model_duplicates.append(duplicate_entry)

        # Write results to file
        with open(output_path, "w", encoding="utf-8") as output_file:
            output_file.write("=== Duplicate IDs ===\n")
            if id_duplicates:
                output_file.write("\n".join(sorted(id_duplicates)) + "\n")
            else:
                output_file.write("No duplicate IDs found.\n")

            output_file.write("\n=== Duplicate Model Names ===\n")
            if model_duplicates:
                output_file.write("\n".join(sorted(model_duplicates)) + "\n")
            else:
                output_file.write("No duplicate model names found.\n")

        messagebox.showinfo("Success", f"Duplicate IDs and model names saved to {output_path}")

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
                    self.load_file_into_editor(file_path)

        self.status_bar.config(text=f"Loaded {len(self.ide_files)} IDE files")
        self.highlight_syntax()

    def open_multiple_files(self):
        file_paths = filedialog.askopenfilenames(title="Select IDE Files", filetypes=[("IDE Files", "*.ide")])
        if not file_paths:
            return

        self.ide_files = []
        self.file_sections.clear()
        self.original_contents.clear()
        self.file_list.delete(0, tk.END)
        self.text_editor.delete("1.0", tk.END)

        for file_path in file_paths:
            self.ide_files.append(file_path)
            self.load_file_into_editor(file_path)

        self.status_bar.config(text=f"Loaded {len(self.ide_files)} IDE files")
        self.highlight_syntax()

    def load_file_into_editor(self, file_path):
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
                if (start_index == -1):
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

    def save_selected_file(self):
        try:
            selected_file = self.file_list.get(self.file_list.curselection())
            for path, (start, end) in self.file_sections.items():
                if os.path.basename(path) == selected_file:
                    full_text = self.text_editor.get("1.0", tk.END)
                    start_marker = f"// --- {selected_file} --- //\n"

                    start_index = full_text.find(start_marker)
                    if (start_index == -1):
                        messagebox.showerror("Error", "Could not find selected file in editor.")
                        return

                    start_index += len(start_marker)
                    next_section_index = full_text.find("// ---", start_index)

                    new_content = full_text[start_index:next_section_index].strip() if next_section_index != -1 else full_text[start_index:].strip()

                    with open(path, "w", encoding="utf-8", errors="ignore") as file:
                        file.write(new_content)

                    messagebox.showinfo("Success", f"{selected_file} saved successfully!")
                    self.status_bar.config(text=f"{selected_file} saved successfully")
                    return
            messagebox.showerror("Error", "Could not find selected file.")
        except Exception:
            messagebox.showerror("Error", "No file selected.")

    def highlight_syntax(self, event=None):
        # Clear existing tags
        for tag in ["section", "id", "modelname", "coordinate", "comment", "keyword"]:
            self.text_editor.tag_remove(tag, "1.0", "end")
        
        # Get all text content
        content = self.text_editor.get("1.0", "end")
        
        # Process line by line
        for line_num, line in enumerate(content.split('\n'), 1):
            # Skip empty lines
            if not line.strip():
                continue
                
            # Highlight comments
            if '#' in line:
                comment_start = line.index('#')
                start_index = f"{line_num}.{comment_start}"
                self.text_editor.tag_add("comment", start_index, f"{line_num}.end")
                continue
            
            # Highlight section headers
            if line.strip().lower() in {"objs", "tobj", "anim", "inst", "path", "2dfx", "txdp", "end"}:
                self.text_editor.tag_add("section", f"{line_num}.0", f"{line_num}.end")
                continue
            
            # Process data lines
            parts = line.strip().split(',')
            if len(parts) > 1:
                # Highlight ID (first number)
                if parts[0].strip().isdigit():
                    self.text_editor.tag_add("id", f"{line_num}.0", f"{line_num}.{len(parts[0])}")
                
                # Highlight model name (second part)
                if len(parts) > 1:
                    start_pos = len(parts[0]) + 1
                    end_pos = start_pos + len(parts[1])
                    self.text_editor.tag_add("modelname", f"{line_num}.{start_pos}", f"{line_num}.{end_pos}")
                
                # Highlight coordinates (floating point numbers)
                for i, part in enumerate(parts[2:], 2):
                    if re.match(r'-?\d*\.?\d+', part.strip()):
                        start_pos = sum(len(p) + 1 for p in parts[:i])
                        end_pos = start_pos + len(part)
                        self.text_editor.tag_add("coordinate", f"{line_num}.{start_pos}", f"{line_num}.{end_pos}")

if __name__ == "__main__":
    root = tk.Tk()
    app = IDEFileEditor(root)
    root.mainloop()
