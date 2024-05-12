import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

class SSNS:

    def __init__(self) -> None:
        self.init_window()
 
    # Function to create the artifacts table if it doesn't exist
    def create_table(self):
        conn = sqlite3.connect('artifacts.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS artifacts
                    (id INTEGER PRIMARY KEY, name TEXT, collection TEXT, category TEXT, location TEXT)''')
        conn.commit()
        conn.close()

    def drop_table(self):
        conn = sqlite3.connect('artifacts.db')
        c = conn.cursor()
        c.execute('''DROP TABLE artifacts''')
        conn.commit()  
        conn.close()

    # Function to add a new artifact to the database
    def add_artifact(self):
        self.add_to_db(self.name_entry.get(), self.collection_entry.get(), self.category_entry.get(), self.location_entry.get())
        
        self.name_entry.delete(0, tk.END)
        self.collection_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        
        self.status_label.config(text="Artifact added successfully!", foreground="green")

    def add_to_db(self, name, collection, category, location):
        conn = sqlite3.connect('artifacts.db')
        c = conn.cursor()
        c.execute("INSERT INTO artifacts (name, collection, category, location) VALUES (?, ?, ?, ?)", (name, collection, category, location))
        conn.commit()
        conn.close()

    # Function to import artifacts from a CSV file
    def import_artifacts(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                with open(file_path, newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    artifacts = []
                    for row in reader:
                        artifacts.append(row)
                self.import_artifacts_to_db(artifacts)
            except Exception as e:
                messagebox.showerror("Error", f"Error importing data: {e}")

    # Function to import artifacts into the database
    def import_artifacts_to_db(self, artifacts):
        # Check if CSV has necessary columns
        required_columns = {'name', 'collection', 'category', 'location'}
        csv_columns = set(artifacts[0].keys())
        if not required_columns.issubset(csv_columns):
            confirmation = messagebox.askyesno("Warning", "The CSV file is missing some necessary columns. Proceed anyway?")
            if not confirmation:
                return

        for artifact in artifacts:
            name = artifact.get('name', None)
            collection = artifact.get('collection', None)
            category = artifact.get('category', None)
            location = artifact.get('location', None)
            self.add_to_db(name, collection, category, location)

        messagebox.showinfo("Success", "Artifacts imported successfully!")

    # Function to search for artifacts by keyword
    def search_artifacts(self):
        keyword = self.search_entry.get()
        
        conn = sqlite3.connect('artifacts.db')
        c = conn.cursor()
        c.execute("SELECT * FROM artifacts WHERE name LIKE ? OR collection LIKE ? OR category LIKE ? OR location LIKE ?", 
                ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%'))
        artifacts = c.fetchall()
        conn.close()
        
        self.display_artifacts(artifacts)

    # Function to display artifacts
    def display_artifacts(self, artifacts):
        self.search_results.delete(0, tk.END)
        for artifact in artifacts:
            self.search_results.insert(tk.END, f"{artifact[0]} {artifact[1]} ({artifact[3]})")

    # Function to display details of the selected artifact
    def show_details(self, event):
        index = event.widget.curselection()
        # print(f"Current selection: {index}")
        if index:
            artifact = self.search_results.get(index[0])
            artifact_id = artifact.split()[0]
            conn = sqlite3.connect('artifacts.db')
            c = conn.cursor()
            c.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,))
            artifact_info = c.fetchone()
            conn.close()
            self.display_details(artifact_info)

    def display_details(self, artifact_info):
        self.details_window = tk.Toplevel(self.root)
        self.details_window.title("Artifact Details")

        self.details_frame = ttk.Frame(self.details_window)
        self.details_frame.grid(row=0, column=0, padx=10, pady=10)

        self.details_name_label = ttk.Label(self.details_window, text="Name:")
        self.details_name_label.grid(row=0, column=0, padx=5, pady=5) #, sticky="w")
        self.details_name_value = tk.StringVar(value=artifact_info[1])
        self.details_name_entry = ttk.Entry(self.details_window, textvariable=self.details_name_value, state='readonly')
        self.details_name_entry.grid(row=0, column=1, padx=5, pady=5) # , sticky='ew')

        self.details_collection_label = ttk.Label(self.details_window, text="Collection:")
        self.details_collection_label.grid(row=1, column=0, padx=5, pady=5) #, sticky="w")
        self.details_collection_value = tk.StringVar(value=artifact_info[2])
        self.details_collection_entry = ttk.Entry(self.details_window, textvariable=self.details_collection_value, state='readonly')
        self.details_collection_entry.grid(row=1, column=1, padx=5, pady=5) # , sticky='ew')

        self.details_category_label = ttk.Label(self.details_window, text="Category:")
        self.details_category_label.grid(row=2, column=0, padx=5, pady=5) # , sticky="w")
        self.details_category_value = tk.StringVar(value=artifact_info[3])
        self.details_category_entry = ttk.Entry(self.details_window, textvariable=self.details_category_value, state='readonly')
        self.details_category_entry.grid(row=2, column=1, padx=5, pady=5) # , sticky='ew')

        self.details_location_label = ttk.Label(self.details_window, text="Location:")
        self.details_location_label.grid(row=3, column=0, padx=5, pady=5) # , sticky="w")
        self.details_location_value = tk.StringVar(value=artifact_info[4])
        self.details_location_entry = ttk.Entry(self.details_window, textvariable=self.details_location_value, state='readonly')
        self.details_location_entry.grid(row=3, column=1, padx=5, pady=5) #, sticky='ew')

        # self.buttons_frame = ttk.Frame(self.details_window)
        # self.buttons_frame.grid(row=1, column=0, padx=10, pady=10)

        self.details_edit_save_button = ttk.Button(self.details_window, text="Edit", command=lambda: self.edit_details(artifact_info))
        self.details_edit_save_button.grid(row=4, column=0, padx=5, pady=5)

        self.details_delete_button = ttk.Button(self.details_window, text="Delete", command=lambda: self.delete_artifact(artifact_info[0]))
        self.details_delete_button.grid(row=4, column=1, padx=5, pady=5)

    def edit_details(self, artifact_info):
        self.details_name_entry.configure(state='normal')
        self.details_collection_entry.configure(state='normal')
        self.details_category_entry.configure(state='normal')
        self.details_location_entry.configure(state='normal')
        self.details_edit_save_button.configure(text="Save", command=lambda: self.save_changes(artifact_info))

    def save_changes(self, artifact_info):
        conn = sqlite3.connect('artifacts.db')
        c = conn.cursor()
        c.execute("UPDATE artifacts SET name=?, collection=?, category=?, location=? WHERE id=?", (self.details_name_value.get(), self.details_category_value.get(),
                                                                            self.details_collection_value.get(), self.details_location_value.get(), artifact_info[0]))
        conn.commit()
        conn.close()
        self.details_name_entry.configure(state='readonly')
        self.details_collection_entry.configure(state='readonly')
        self.details_category_entry.configure(state='readonly')
        self.details_location_entry.configure(state='readonly')
        self.details_edit_save_button.configure(text="Edit", command=lambda: self.edit_details(artifact_info))
        messagebox.showinfo("Success", "Changes saved successfully!")

    def delete_artifact(self, artifact_id):
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete this artifact?")
        if confirmation:
            conn = sqlite3.connect('artifacts.db')
            c = conn.cursor()
            c.execute("DELETE FROM artifacts WHERE id=?", (artifact_id,))
            conn.commit()
            conn.close()
            self.details_window.destroy()
            messagebox.showinfo("Success", "Artifact deleted successfully!")

    def init_window(self):
        # Main window
        self.root = tk.Tk()
        self.root.title("Simple Store n' Search")

        # self.root.rowconfigure(0, weight=1)
        # self.root.columnconfigure(0, weight=1)

        # Create artifacts table
        self.drop_table()
        self.create_table()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Add Artifact Frame
        self.add_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_tab, text="Add Artifact", sticky='nsew')

        # self.add_tab.rowconfigure(1, weight=1)
        # self.add_tab.columnconfigure((0,1), weight=1)

        self.name_label = ttk.Label(self.add_tab, text="Name:")
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(self.add_tab)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.collection_label = ttk.Label(self.add_tab, text="Collection:")
        self.collection_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.collection_entry = ttk.Entry(self.add_tab)
        self.collection_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.category_label = ttk.Label(self.add_tab, text="Category:")
        self.category_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.category_entry = ttk.Entry(self.add_tab)
        self.category_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        self.location_label = ttk.Label(self.add_tab, text="Location:")
        self.location_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.location_entry = ttk.Entry(self.add_tab)
        self.location_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        self.add_button = ttk.Button(self.add_tab, text="Add", command=self.add_artifact)
        self.add_button.grid(row=4, columnspan=2, padx=5, pady=5)

        self.status_label = ttk.Label(self.add_tab, text="", foreground="red")
        self.status_label.grid(row=5, columnspan=2, padx=5, pady=5)

        # Search Artifact Frame
        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Search Artifact")

        # self.search_tab.rowconfigure(1, weight=1)
        # self.search_tab.columnconfigure((0, 1), weight=1)

        self.search_entry = ttk.Entry(self.search_tab) # , width=30)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.search_button = ttk.Button(self.search_tab, text="Search", command=self.search_artifacts)
        self.search_button.grid(row=0, column=1, padx=5, pady=5)

        self.search_results = tk.Listbox(self.search_tab, selectmode=tk.SINGLE) # , width=50, height=10
        self.search_results.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')
        self.search_results.bind('<<ListboxSelect>>', self.show_details)

        # Import Artifact Tab
        self.import_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.import_tab, text="Import Data")

        # self.import_tab.rowconfigure(0, weight=1)
        # self.import_tab.columnconfigure(0, weight=1)

        self.import_button = ttk.Button(self.import_tab, text="Import", command=self.import_artifacts)
        self.import_button.grid(row=0, column=0, padx=5, pady=5)

if __name__ == "__main__":

    ssns = SSNS()
    ssns.root.mainloop()

    # dynamic scaling: https://stackoverflow.com/questions/28883687/tkinter-label-change-font-size-by-text-length/28906292#28906292