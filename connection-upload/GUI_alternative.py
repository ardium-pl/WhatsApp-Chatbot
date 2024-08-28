import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from pymongo import MongoClient
import dotenv
import os

dotenv.load_dotenv()
COSMOSDB_CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")


class DarkTheme(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_create("darktheme", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": "#2c2c2c"}},
            "TNotebook.Tab": {"configure": {"padding": [5, 2], "background": "#1c1c1c", "foreground": "white"},
                              "map": {"background": [("selected", "#3c3c3c")],
                                      "expand": [("selected", [1, 1, 1, 0])]}},
            "TFrame": {"configure": {"background": "#2c2c2c"}},
            "TLabel": {"configure": {"background": "#2c2c2c", "foreground": "white"}},
            "TEntry": {"configure": {"fieldbackground": "#3c3c3c", "foreground": "white", "insertcolor": "white"}},
            "TButton": {"configure": {"background": "#4c4c4c", "foreground": "white"}},
            "Vertical.TScrollbar": {"configure": {"background": "#4c4c4c", "troughcolor": "#2c2c2c"}},
        })
        self.theme_use("darktheme")


class MongoDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MongoDB Manager")
        self.root.geometry("1000x600")
        self.root.configure(bg="#2c2c2c")

        self.style = DarkTheme()

        self.client = None
        self.db = None
        self.collection = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for connection and collection management
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Connection frame
        connection_frame = ttk.LabelFrame(left_panel, text="MongoDB Connection", padding=10)
        connection_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(connection_frame, text="Database:").pack(anchor=tk.W)
        self.db_name_entry = ttk.Entry(connection_frame)
        self.db_name_entry.pack(fill=tk.X, pady=5)

        ttk.Button(connection_frame, text="Connect", command=self.connect_to_db).pack(fill=tk.X)

        # Collection management frame
        collection_frame = ttk.LabelFrame(left_panel, text="Collection Management", padding=10)
        collection_frame.pack(fill=tk.X)

        ttk.Label(collection_frame, text="Collection:").pack(anchor=tk.W)
        self.collection_name_entry = ttk.Entry(collection_frame)
        self.collection_name_entry.pack(fill=tk.X, pady=5)

        ttk.Button(collection_frame, text="Create Collection", command=self.create_collection).pack(fill=tk.X, pady=2)
        ttk.Button(collection_frame, text="Switch Collection", command=self.switch_collection).pack(fill=tk.X, pady=2)
        ttk.Button(collection_frame, text="Delete Collection", command=self.delete_collection).pack(fill=tk.X, pady=2)

        # Right panel for CRUD operations and results
        right_panel = ttk.Notebook(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # CRUD tab
        crud_frame = ttk.Frame(right_panel, padding=10)
        right_panel.add(crud_frame, text="CRUD Operations")

        ttk.Label(crud_frame, text="Document (JSON):").grid(row=0, column=0, sticky=tk.W)
        self.document_text = tk.Text(crud_frame, height=5, bg="#3c3c3c", fg="white", insertbackground="white")
        self.document_text.grid(row=1, column=0, sticky=tk.NSEW)

        ttk.Label(crud_frame, text="Query (JSON):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.query_text = tk.Text(crud_frame, height=5, bg="#3c3c3c", fg="white", insertbackground="white")
        self.query_text.grid(row=3, column=0, sticky=tk.NSEW)

        button_frame = ttk.Frame(crud_frame)
        button_frame.grid(row=4, column=0, pady=10)

        ttk.Button(button_frame, text="Insert", command=self.insert_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Find", command=self.find_documents).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Update", command=self.update_document).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Delete", command=self.delete_document).pack(side=tk.LEFT, padx=2)

        ttk.Label(crud_frame, text="Results:").grid(row=5, column=0, sticky=tk.W)
        self.results_text = tk.Text(crud_frame, height=10, bg="#3c3c3c", fg="white", insertbackground="white")
        self.results_text.grid(row=6, column=0, sticky=tk.NSEW)

        crud_frame.columnconfigure(0, weight=1)
        crud_frame.rowconfigure(1, weight=1)
        crud_frame.rowconfigure(3, weight=1)
        crud_frame.rowconfigure(6, weight=2)

        # Logs tab
        log_frame = ttk.Frame(right_panel, padding=10)
        right_panel.add(log_frame, text="Logs")

        self.log_text = tk.Text(log_frame, bg="#3c3c3c", fg="white", insertbackground="white")
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def connect_to_db(self):
        db_name = self.db_name_entry.get()
        if not db_name:
            messagebox.showerror("Error", "Please enter a database name.")
            return

        try:
            self.client = MongoClient(COSMOSDB_CONNECTION_STRING)
            self.db = self.client[db_name]
            self.log(f"Connected to database: {db_name}")
            messagebox.showinfo("Success", f"Connected to database: {db_name}")
        except Exception as e:
            self.log(f"Failed to connect to database: {e}")
            messagebox.showerror("Error", f"Failed to connect to database: {e}")

    def create_collection(self):
        collection_name = self.collection_name_entry.get()
        if not collection_name:
            messagebox.showerror("Error", "Please enter a collection name.")
            return

        try:
            self.db.create_collection(collection_name)
            self.collection = self.db[collection_name]
            self.log(f"Collection created: {collection_name}")
            messagebox.showinfo("Success", f"Collection created: {collection_name}")
        except Exception as e:
            self.log(f"Failed to create collection: {e}")
            messagebox.showerror("Error", f"Failed to create collection: {e}")

    def switch_collection(self):
        collection_name = self.collection_name_entry.get()
        if not collection_name:
            messagebox.showerror("Error", "Please enter a collection name.")
            return

        try:
            self.collection = self.db[collection_name]
            self.log(f"Switched to collection: {collection_name}")
            messagebox.showinfo("Success", f"Switched to collection: {collection_name}")
        except Exception as e:
            self.log(f"Failed to switch collection: {e}")
            messagebox.showerror("Error", f"Failed to switch collection: {e}")

    def delete_collection(self):
        collection_name = self.collection_name_entry.get()
        if not collection_name:
            messagebox.showerror("Error", "Please enter a collection name.")
            return

        try:
            self.db.drop_collection(collection_name)
            self.log(f"Collection deleted: {collection_name}")
            messagebox.showinfo("Success", f"Collection deleted: {collection_name}")
        except Exception as e:
            self.log(f"Failed to delete collection: {e}")
            messagebox.showerror("Error", f"Failed to delete collection: {e}")

    def insert_document(self):
        document_str = self.document_text.get("1.0", tk.END).strip()
        if not document_str:
            messagebox.showerror("Error", "Please enter a document.")
            return

        try:
            document = json.loads(document_str)
            result = self.collection.insert_one(document)
            self.log(f"Document inserted with ID: {result.inserted_id}")
            messagebox.showinfo("Success", "Document inserted successfully.")
        except Exception as e:
            self.log(f"Failed to insert document: {e}")
            messagebox.showerror("Error", f"Failed to insert document: {e}")

    def find_documents(self):
        query_str = self.query_text.get("1.0", tk.END).strip()
        if not query_str:
            query = {}
        else:
            try:
                query = json.loads(query_str)
            except json.JSONDecodeError:
                self.log("Invalid JSON query.")
                messagebox.showerror("Error", "Invalid JSON query.")
                return

        try:
            documents = list(self.collection.find(query))
            result = json.dumps(documents, indent=2, default=str)
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, result)
            self.log(f"Found {len(documents)} document(s)")
        except Exception as e:
            self.log(f"Failed to find documents: {e}")
            messagebox.showerror("Error", f"Failed to find documents: {e}")

    def update_document(self):
        query_str = self.query_text.get("1.0", tk.END).strip()
        update_str = self.document_text.get("1.0", tk.END).strip()
        if not query_str or not update_str:
            messagebox.showerror("Error", "Please enter both query and update document.")
            return

        try:
            query = json.loads(query_str)
            update = json.loads(update_str)
            result = self.collection.update_one(query, {"$set": update})
            self.log(f"Matched {result.matched_count} document(s), Modified {result.modified_count} document(s)")
            messagebox.showinfo("Success",
                                f"Matched {result.matched_count} document(s), Modified {result.modified_count} document(s)")
        except Exception as e:
            self.log(f"Failed to update document: {e}")
            messagebox.showerror("Error", f"Failed to update document: {e}")

    def delete_document(self):
        query_str = self.query_text.get("1.0", tk.END).strip()
        if not query_str:
            messagebox.showerror("Error", "Please enter a query.")
            return

        try:
            query = json.loads(query_str)
            result = self.collection.delete_one(query)
            self.log(f"Deleted {result.deleted_count} document(s)")
            messagebox.showinfo("Success", f"Deleted {result.deleted_count} document(s)")
        except Exception as e:
            self.log(f"Failed to delete document: {e}")
            messagebox.showerror("Error", f"Failed to delete document: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MongoDBApp(root)
    root.mainloop()
