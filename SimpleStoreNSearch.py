import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

# Function to create the artifacts table if it doesn't exist
def create_table():
    conn = sqlite3.connect('artifacts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS artifacts
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, location TEXT)''')
    conn.commit()
    conn.close()

# Function to add a new artifact to the database
def add_artifact():
    name = name_entry.get()
    category = category_entry.get()
    location = location_entry.get()
    
    add_to_db(name, category, location)
    
    name_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    location_entry.delete(0, tk.END)
    
    status_label.config(text="Artifact added successfully!", foreground="green")

def add_to_db(name, category, location):
    conn = sqlite3.connect('artifacts.db')
    c = conn.cursor()
    c.execute("INSERT INTO artifacts (name, category, location) VALUES (?, ?, ?)", (name, category, location))
    conn.commit()
    conn.close()

# Function to import artifacts from a CSV file
def import_artifacts():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            with open(file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                artifacts = []
                for row in reader:
                    artifacts.append(row)
            import_artifacts_to_db(artifacts)
        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {e}")

# Function to import artifacts into the database
def import_artifacts_to_db(artifacts):
    # Check if CSV has necessary columns
    required_columns = {'name', 'category', 'location'}
    csv_columns = set(artifacts[0].keys())
    if not required_columns.issubset(csv_columns):
        confirmation = messagebox.askyesno("Warning", "The CSV file is missing some necessary columns. Proceed anyway?")
        if not confirmation:
            return

    for artifact in artifacts:
        name = artifact.get('name', None)
        category = artifact.get('category', None)
        location = artifact.get('location', None)
        add_to_db(name, category, location)

    messagebox.showinfo("Success", "Artifacts imported successfully!")

# Function to search for artifacts by keyword
def search_artifacts():
    keyword = search_entry.get()
    
    conn = sqlite3.connect('artifacts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM artifacts WHERE name LIKE ? OR category LIKE ? OR location LIKE ?", 
              ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
    artifacts = c.fetchall()
    conn.close()
    
    display_artifacts(artifacts)

# Function to display artifacts
def display_artifacts(artifacts):
    search_results.delete(0, tk.END)
    for artifact in artifacts:
        search_results.insert(tk.END, f"{artifact[0]} {artifact[1]} ({artifact[2]})")

# Function to display details of the selected artifact
def show_details(event):
    index = event.widget.curselection()
    print(f"Current selection: {index}")
    if index:
        artifact = search_results.get(index[0])
        artifact_id = artifact.split()[0]
        conn = sqlite3.connect('artifacts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,))
        artifact_info = c.fetchone()
        conn.close()
        display_details(artifact_info)

def display_details(artifact_info):
    details_window = tk.Toplevel(root)
    details_window.title("Artifact Details")

    name_label = ttk.Label(details_window, text="Name:")
    name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    name_value = tk.StringVar(value=artifact_info[1])
    name_entry = ttk.Entry(details_window, textvariable=name_value, state='readonly')
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    category_label = ttk.Label(details_window, text="Category:")
    category_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    category_value = tk.StringVar(value=artifact_info[2])
    category_entry = ttk.Entry(details_window, textvariable=category_value, state='readonly')
    category_entry.grid(row=1, column=1, padx=5, pady=5)

    location_label = ttk.Label(details_window, text="Location:")
    location_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
    location_value = tk.StringVar(value=artifact_info[3])
    location_entry = ttk.Entry(details_window, textvariable=location_value, state='readonly')
    
    location_entry.grid(row=2, column=1, padx=5, pady=5)

    edit_button = ttk.Button(details_window, text="Edit", command=lambda: edit_details(artifact_info, name_value, name_entry, category_value, category_entry, location_value, location_entry, edit_button))
    edit_button.grid(row=3, column=0, padx=5, pady=5)

    delete_button = ttk.Button(details_window, text="Delete", command=lambda: delete_artifact(artifact_info[0], details_window))
    delete_button.grid(row=3, column=1, padx=5, pady=5)

def edit_details(artifact_info, name_value, name_entry, category_value, category_entry, location_value, location_entry, save_button):
    name_entry.configure(state='normal')
    category_entry.configure(state='normal')
    location_entry.configure(state='normal')
    save_button.configure(text="Save", command=lambda: save_changes(artifact_info, name_value, name_entry, category_value, category_entry,
                                                                    location_value, location_entry, save_button))

def save_changes(artifact_info, name_value, name_entry, category_value, category_entry, location_value, location_entry, edit_button):
    conn = sqlite3.connect('artifacts.db')
    c = conn.cursor()
    c.execute("UPDATE artifacts SET name=?, category=?, location=? WHERE id=?", (name_value.get(), category_value.get(), location_value.get(), artifact_info[0]))
    conn.commit()
    conn.close()
    name_entry.configure(state='readonly')
    category_entry.configure(state='readonly')
    location_entry.configure(state='readonly')
    edit_button.configure(text="Edit", command=lambda: edit_details(artifact_info, name_value, name_entry, category_value, category_entry, location_value, location_entry, edit_button))
    messagebox.showinfo("Success", "Changes saved successfully!")

def delete_artifact(artifact_id, details_window):
    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this artifact?")
    if confirmation:
        conn = sqlite3.connect('artifacts.db')
        c = conn.cursor()
        c.execute("DELETE FROM artifacts WHERE id=?", (artifact_id,))
        conn.commit()
        conn.close()
        details_window.destroy()
        messagebox.showinfo("Success", "Artifact deleted successfully!")

# Main window
root = tk.Tk()
root.title("Simple Store n' Search")

# Create artifacts table
create_table()

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# Add Artifact Frame
add_tab = ttk.Frame(notebook)
notebook.add(add_tab, text="Add Artifact")

name_label = ttk.Label(add_tab, text="Name:")
name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
name_entry = ttk.Entry(add_tab)
name_entry.grid(row=0, column=1, padx=5, pady=5)

category_label = ttk.Label(add_tab, text="Category:")
category_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
category_entry = ttk.Entry(add_tab)
category_entry.grid(row=1, column=1, padx=5, pady=5)

location_label = ttk.Label(add_tab, text="Location:")
location_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
location_entry = ttk.Entry(add_tab)
location_entry.grid(row=2, column=1, padx=5, pady=5)

add_button = ttk.Button(add_tab, text="Add", command=add_artifact)
add_button.grid(row=3, columnspan=2, padx=5, pady=5)

status_label = ttk.Label(add_tab, text="", foreground="red")
status_label.grid(row=4, columnspan=2, padx=5, pady=5)

# Search Artifact Frame
search_tab = ttk.Frame(notebook)
notebook.add(search_tab, text="Search Artifact")

search_entry = ttk.Entry(search_tab, width=30)
search_entry.grid(row=0, column=0, padx=5, pady=5)

search_button = ttk.Button(search_tab, text="Search", command=search_artifacts)
search_button.grid(row=0, column=1, padx=5, pady=5)

search_results = tk.Listbox(search_tab, width=50, height=10, selectmode=tk.SINGLE)
search_results.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
search_results.bind('<<ListboxSelect>>', show_details)

# Import Artifact Tab
import_tab = ttk.Frame(notebook)
notebook.add(import_tab, text="Import Data")

import_button = ttk.Button(import_tab, text="Import", command=import_artifacts)
import_button.grid(row=0, column=0, padx=5, pady=5)

root.mainloop()
