# main.py
import tkinter as tk
from tkinter import messagebox
import sys
import os

from database.db_manager import DBManager
from views.main_window import MainWindow

def main():
    try:
        db_manager = DBManager()
    except Exception as e:
        # If DB fails to initialize, show a basic tk window with the error
        root = tk.Tk()
        root.withdraw() # hide the main window
        messagebox.showerror(
            "Database Error", 
            f"Failed to connect or initialize the database.\n"
            f"Please ensure MySQL is running and credentials in config.py are correct.\n\n"
            f"Error Details: {e}"
        )
        sys.exit(1)

    app = MainWindow(db_manager)
    
    # Handle window close to clean up DB connection
    def on_closing():
        db_manager.close()
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()
