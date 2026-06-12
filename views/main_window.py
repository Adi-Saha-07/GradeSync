import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from views.dashboard_view import DashboardView
from views.add_marks_view import AddMarksView
from exports.excel_exporter import ExcelExporter

class MainWindow(tk.Tk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        
        self.title("GradeSync")

        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print("Failed to load icon:", e)
        
        window_width = 1000
        window_height = 750
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.minsize(900, 650)

        try:
            import sv_ttk
            sv_ttk.set_theme("dark")
        except ImportError:
            pass
            
        self.current_student_id = None
        self.students_list = []
        
        self._create_widgets()
        self.refresh_students()
        
    def _create_widgets(self):

        toolbar = ttk.Frame(self, padding="10")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ttk.Label(toolbar, text="Select Student:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(toolbar, textvariable=self.student_var, state="readonly", width=30)
        self.student_combo.pack(side=tk.LEFT)
        self.student_combo.bind("<<ComboboxSelected>>", self._on_student_selected)
        
        add_student_btn = tk.Button(toolbar, text="+ New Student", command=self._add_student_dialog, bg="#2ECC71", fg="white", activebackground="#27AE60", activeforeground="white", relief="flat", font=("Helvetica", 9, "bold"), cursor="hand2", padx=10, pady=4)
        add_student_btn.pack(side=tk.LEFT, padx=10)
        
        self.delete_student_btn = tk.Button(toolbar, text="Delete Student", command=self.delete_student, bg="#E74C3C", fg="white", activebackground="#C0392B", activeforeground="white", relief="flat", font=("Helvetica", 9, "bold"), cursor="hand2", padx=10, pady=4)
        self.delete_student_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = ttk.Button(toolbar, text="Export Student Data", command=self.export_data)
        export_btn.pack(side=tk.RIGHT)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.dashboard_tab = DashboardView(self.notebook, self.db_manager)
        self.notebook.add(self.dashboard_tab, text="Dashboard")

        self.add_marks_tab = AddMarksView(
            self.notebook, 
            self.db_manager, 
            refresh_callback=self.dashboard_tab.refresh_data
        )
        self.notebook.add(self.add_marks_tab, text="Add Marks")

    def refresh_students(self):
        with self.db_manager.connect() as (conn, cursor):
            cursor.execute("SELECT * FROM students ORDER BY name")
            self.students_list = cursor.fetchall()
            
        combo_values = [f"{s['name']} ({s['roll_number']})" for s in self.students_list]
        self.student_combo['values'] = combo_values
        
        if self.students_list:
            if not self.current_student_id:
                self.student_combo.current(0)
                self._on_student_selected(None)
            else:
                found = False
                for i, s in enumerate(self.students_list):
                    if s['id'] == self.current_student_id:
                        self.student_combo.current(i)
                        found = True
                        break
                if not found:
                    self.student_combo.current(0)
                    self._on_student_selected(None)
        else:
            self.current_student_id = None
            self.student_var.set("")
            self.dashboard_tab.set_student(None)
            self.add_marks_tab.set_student(None)

    def _on_student_selected(self, event):
        idx = self.student_combo.current()
        if idx >= 0:
            student = self.students_list[idx]
            self.current_student_id = student['id']
            self.dashboard_tab.set_student(self.current_student_id)
            self.add_marks_tab.set_student(self.current_student_id)

    def _add_student_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Student")

        w, h = 400, 350
        dialog.update_idletasks()
        x = int(dialog.winfo_screenwidth()/2 - w/2)
        y = int(dialog.winfo_screenheight()/2 - h/2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").pack(pady=(10, 0))
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Roll Number:").pack()
        roll_entry = ttk.Entry(dialog)
        roll_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Branch:").pack()
        branch_entry = ttk.Entry(dialog)
        branch_entry.pack(pady=5)
        
        ttk.Label(dialog, text="Year of Joining:").pack()
        year_entry = ttk.Entry(dialog)
        year_entry.pack(pady=5)
        
        def save(event=None):
            name = name_entry.get().strip()
            roll = roll_entry.get().strip()
            branch = branch_entry.get().strip()
            try:
                year = int(year_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Year must be a number", parent=dialog)
                return
                
            if not all([name, roll, branch]):
                messagebox.showerror("Error", "All fields are required", parent=dialog)
                return
                
            student_id = self.db_manager.add_student(name, roll, branch, year)
            if student_id:
                self.current_student_id = student_id
                self.refresh_students()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add student (Roll Number might be duplicate)", parent=dialog)

        save_btn = tk.Button(dialog, text="Save Student", command=save, bg="#2ECC71", fg="white", activebackground="#27AE60", activeforeground="white", relief="flat", font=("Helvetica", 10, "bold"), cursor="hand2", padx=20, pady=5)
        save_btn.pack(pady=10)
        dialog.bind('<Return>', save)

    def delete_student(self):
        if not self.current_student_id:
            messagebox.showwarning("Warning", "Please select a student to delete.")
            return
            
        student_name = self.student_var.get()
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to completely delete {student_name} and ALL their marks, subjects, and semesters? This action cannot be undone.")
        
        if confirm:
            if self.db_manager.delete_student(self.current_student_id):
                messagebox.showinfo("Success", f"{student_name} deleted successfully.")
                self.current_student_id = None
                self.refresh_students()
            else:
                messagebox.showerror("Error", "Failed to delete student from database.")

    def export_data(self):
        if not self.current_student_id:
            messagebox.showwarning("Warning", "Please select a student first.")
            return
            
        student_name = self.student_var.get()
        ExcelExporter.export_data(self.db_manager, self.current_student_id, student_name)
