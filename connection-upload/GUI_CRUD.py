import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import time
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import numpy as np
import dotenv
import os

dotenv.load_dotenv()
COSMOSDB_CONNECTION_STRING = os.getenv("COSMOSDB_CONNECTION_STRING")


class MongoDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MongoDB CRUD Operations")

        self.client = None
        self.db = None
        self.collection = None

        self.create_widgets()

    def create_widgets(self):
        # Connection frame
        connection_frame = ttk.LabelFrame(self.root, text="MongoDB Connection")
        connection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(connection_frame, text="Database Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.db_name_entry = ttk.Entry(connection_frame)
        self.db_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(connection_frame, text="Collection Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.collection_name_entry = ttk.Entry(connection_frame)
        self.collection_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect_to_db)
        connect_button.grid(row=2, column=0, columnspan=2, pady=5)

        # New Collection frame
        new_collection_frame = ttk.LabelFrame(self.root, text="Create/Delete Collection")
        new_collection_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(new_collection_frame, text="New Collection Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_collection_name_entry = ttk.Entry(new_collection_frame)
        self.new_collection_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        create_collection_button = ttk.Button(new_collection_frame, text="Create Collection",
                                              command=self.create_collection)
        create_collection_button.grid(row=1, column=0, columnspan=2, pady=5)

        delete_collection_button = ttk.Button(new_collection_frame, text="Delete Collection",
                                              command=self.delete_collection)
        delete_collection_button.grid(row=2, column=0, columnspan=2, pady=5)

        # CRUD operations frame
        crud_frame = ttk.LabelFrame(self.root, text="CRUD Operations")
        crud_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(crud_frame, text="Document (JSON):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.document_entry = ttk.Entry(crud_frame)
        self.document_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        insert_button = ttk.Button(crud_frame, text="Insert Document", command=self.insert_document)
        insert_button.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Label(crud_frame, text="Query (JSON):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.query_entry = ttk.Entry(crud_frame)
        self.query_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        read_button = ttk.Button(crud_frame, text="Read Documents", command=self.read_documents)
        read_button.grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Label(crud_frame, text="New Values (JSON):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.new_values_entry = ttk.Entry(crud_frame)
        self.new_values_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        update_button = ttk.Button(crud_frame, text="Update Document", command=self.update_document)
        update_button.grid(row=5, column=0, columnspan=2, pady=5)

        delete_button = ttk.Button(crud_frame, text="Delete Document", command=self.delete_document)
        delete_button.grid(row=6, column=0, columnspan=2, pady=5)

        # File upload frame
        file_frame = ttk.LabelFrame(self.root, text="File Operations")
        file_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        upload_button = ttk.Button(file_frame, text="Upload File", command=self.upload_file)
        upload_button.grid(row=0, column=0, padx=5, pady=5)

        # Logging frame
        log_frame = ttk.LabelFrame(self.root, text="Logs")
        log_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.log_text = scrolledtext.ScrolledText(log_frame, width=60, height=10, bg='black', fg='white')
        self.log_text.grid(row=0, column=0, padx=5, pady=5)

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def connect_to_db(self):
        db_name = self.db_name_entry.get()
        collection_name = self.collection_name_entry.get()
        if not db_name or not collection_name:
            messagebox.showerror("Error", "Please enter both database and collection names.")
            return

        try:
            self.client = MongoClient(COSMOSDB_CONNECTION_STRING)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            self.log("Connected to MongoDB successfully.")
            messagebox.showinfo("Success", "Connected to MongoDB successfully.")
        except Exception as e:
            self.log(f"Failed to connect to MongoDB: {e}")
            messagebox.showerror("Error", f"Failed to connect to MongoDB: {e}")

    def create_collection(self):
        new_collection_name = self.new_collection_name_entry.get()
        if not new_collection_name:
            messagebox.showerror("Error", "Please enter a collection name.")
            return

        try:
            self.db.create_collection(new_collection_name)
            self.log(f"Collection '{new_collection_name}' created successfully.")
            messagebox.showinfo("Success", f"Collection '{new_collection_name}' created successfully.")
        except Exception as e:
            self.log(f"Failed to create collection: {e}")
            messagebox.showerror("Error", f"Failed to create collection: {e}")

    def delete_collection(self):
        collection_name = self.new_collection_name_entry.get()
        if not collection_name:
            messagebox.showerror("Error", "Please enter a collection name.")
            return

        try:
            self.db.drop_collection(collection_name)
            self.log(f"Collection '{collection_name}' deleted successfully.")
            messagebox.showinfo("Success", f"Collection '{collection_name}' deleted successfully.")
        except Exception as e:
            self.log(f"Failed to delete collection: {e}")
            messagebox.showerror("Error", f"Failed to delete collection: {e}")

    def insert_document(self):
        document_str = self.document_entry.get()
        if not document_str:
            messagebox.showerror("Error", "Please enter a document.")
            return

        try:
            document = eval(document_str)
            self.collection.insert_one(document)
            self.log("Document inserted successfully.")
            messagebox.showinfo("Success", "Document inserted successfully.")
        except Exception as e:
            self.log(f"Failed to insert document: {e}")
            messagebox.showerror("Error", f"Failed to insert document: {e}")

    def read_documents(self):
        query_str = self.query_entry.get()
        if not query_str:
            query = {}
        else:
            try:
                query = eval(query_str)
            except Exception as e:
                self.log(f"Invalid query: {e}")
                messagebox.showerror("Error", f"Invalid query: {e}")
                return

        try:
            documents = self.collection.find(query)
            result = "\n".join([str(doc) for doc in documents])
            if not result:
                result = "No documents found."
            self.log(result)
            messagebox.showinfo("Documents", result)
        except Exception as e:
            self.log(f"Failed to read documents: {e}")
            messagebox.showerror("Error", f"Failed to read documents: {e}")

    def update_document(self):
        query_str = self.query_entry.get()
        new_values_str = self.new_values_entry.get()
        if not query_str or not new_values_str:
            messagebox.showerror("Error", "Please enter both query and new values.")
            return

        try:
            query = eval(query_str)
            new_values = {"$set": eval(new_values_str)}
            result = self.collection.update_one(query, new_values)
            if result.matched_count == 0:
                self.log("No documents matched the query.")
                messagebox.showinfo("Info", "No documents matched the query.")
            else:
                self.log("Document updated successfully.")
                messagebox.showinfo("Success", "Document updated successfully.")
        except Exception as e:
            self.log(f"Failed to update document: {e}")
            messagebox.showerror("Error", f"Failed to update document: {e}")

    def delete_document(self):
        query_str = self.query_entry.get()
        if not query_str:
            messagebox.showerror("Error", "Please enter a query.")
            return

        try:
            query = eval(query_str)
            result = self.collection.delete_one(query)
            if result.deleted_count == 0:
                self.log("No documents matched the query.")
                messagebox.showinfo("Info", "No documents matched the query.")
            else:
                self.log("Document deleted successfully.")
                messagebox.showinfo("Success", "Document deleted successfully.")
        except Exception as e:
            self.log(f"Failed to delete document: {e}")
            messagebox.showerror("Error", f"Failed to delete document: {e}")

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                data = file.read()
                document = eval(data)
                self.collection.insert_one(document)
                self.log("File uploaded and document inserted successfully.")
                messagebox.showinfo("Success", "File uploaded and document inserted successfully.")
        except Exception as e:
            self.log(f"Failed to upload file: {e}")
            messagebox.showerror("Error", f"Failed to upload file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MongoDBApp(root)
    root.mainloop()
