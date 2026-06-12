import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gpa_calculator import marks_to_grade, grade_to_points

class AddMarksView(ttk.Frame):
    def __init__(self, parent, db_manager, refresh_callback):
        super().__init__(parent, padding="20")
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback
        self.student_id = None
        
        self.semesters_list = []
        self.subjects_list = []
        
        self._create_widgets()

    def set_student(self, student_id):
        self.student_id = student_id
        self.refresh_semesters()

    def _create_widgets(self):
        
        title_label = ttk.Label(self, text="Add Marks for Student", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(self, text="Semester:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.semester_var = tk.StringVar()
        self.semester_combo = ttk.Combobox(self, textvariable=self.semester_var, state="readonly", width=25)
        self.semester_combo.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.semester_combo.bind("<<ComboboxSelected>>", self._on_semester_selected)
        
        ttk.Button(self, text="+ New Sem", command=self._add_semester_dialog).grid(row=1, column=2, padx=10, pady=5)
=
        ttk.Label(self, text="Subject:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(self, textvariable=self.subject_var, state="readonly", width=25)
        self.subject_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        subj_btn_frame = ttk.Frame(self)
        subj_btn_frame.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)
        ttk.Button(subj_btn_frame, text="+ New Subj", command=self._add_subject_dialog).pack(side=tk.LEFT, padx=(0, 5))
        
        del_subj_btn = tk.Button(subj_btn_frame, text="Delete Subj", command=self.delete_subject, bg="#E74C3C", fg="white", activebackground="#C0392B", activeforeground="white", relief="flat", font=("Helvetica", 9, "bold"), cursor="hand2", padx=8, pady=2)
        del_subj_btn.pack(side=tk.LEFT)

        ttk.Label(self, text="Internal Marks:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.internal_var = tk.StringVar()
        self.internal_entry = ttk.Entry(self, textvariable=self.internal_var, width=28)
        self.internal_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)

        ttk.Label(self, text="External Marks:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.external_var = tk.StringVar()
        self.external_entry = ttk.Entry(self, textvariable=self.external_var, width=28)
        self.external_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        self.internal_entry.bind('<Return>', self.save_marks)
        self.external_entry.bind('<Return>', self.save_marks)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.add_btn = tk.Button(btn_frame, text="Save Marks", command=self.save_marks, bg="#2ECC71", fg="white", activebackground="#27AE60", activeforeground="white", relief="flat", font=("Helvetica", 11, "bold"), cursor="hand2", padx=20, pady=6)
        self.add_btn.pack(side=tk.LEFT, padx=10)
        
        self.delete_marks_btn = tk.Button(btn_frame, text="Delete Marks", command=self.delete_marks, bg="#E74C3C", fg="white", activebackground="#C0392B", activeforeground="white", relief="flat", font=("Helvetica", 11, "bold"), cursor="hand2", padx=20, pady=6)
        self.delete_marks_btn.pack(side=tk.LEFT, padx=10)

    def refresh_semesters(self):
        if not self.student_id:
            self.semester_combo['values'] = []
            self.semester_combo.set("")
            self.semesters_list = []
            self.refresh_subjects()
            return
            
        with self.db_manager.connect() as (conn, cursor):
            cursor.execute("SELECT * FROM semesters WHERE student_id = %s ORDER BY semester_number", (self.student_id,))
            self.semesters_list = cursor.fetchall()
            
        self.semester_combo['values'] = [f"Sem {s['semester_number']} ({s['academic_year']})" for s in self.semesters_list]
        if self.semesters_list:
            self.semester_combo.current(0)
            self._on_semester_selected(None)
        else:
            self.semester_combo.set("")
            self.refresh_subjects()

    def _on_semester_selected(self, event):
        self.refresh_subjects()

    def refresh_subjects(self):
        idx = self.semester_combo.current()
        if idx < 0:
            self.subject_combo['values'] = []
            self.subject_combo.set("")
            self.subjects_list = []
            return
            
        sem_id = self.semesters_list[idx]['id']
        with self.db_manager.connect() as (conn, cursor):
            cursor.execute("SELECT * FROM subjects WHERE semester_id = %s ORDER BY subject_name", (sem_id,))
            self.subjects_list = cursor.fetchall()
            
        self.subject_combo['values'] = [f"{s['subject_name']} ({s['credits']} Cr)" for s in self.subjects_list]
        if self.subjects_list:
            self.subject_combo.current(0)
        else:
            self.subject_combo.set("")

    def _add_semester_dialog(self):
        if not self.student_id:
            messagebox.showwarning("Warning", "Select a student first!")
            return
            
        dialog = tk.Toplevel(self)
        dialog.title("Add Semester")
        
        w, h = 350, 250
        dialog.update_idletasks()
        x = int(dialog.winfo_screenwidth()/2 - w/2)
        y = int(dialog.winfo_screenheight()/2 - h/2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        ttk.Label(dialog, text="Semester Number:").pack(pady=(10, 2))
        sem_num_var = tk.StringVar()
        ttk.Spinbox(dialog, from_=1, to=10, textvariable=sem_num_var).pack(pady=2)
        
        ttk.Label(dialog, text="Academic Year (e.g. 2023-24):").pack(pady=(5, 2))
        acad_year_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=acad_year_var).pack(pady=2)
        
        def save(event=None):
            num = sem_num_var.get()
            ay = acad_year_var.get().strip()
            if not num or not ay:
                return
            self.db_manager.add_semester(self.student_id, int(num), ay)
            self.refresh_semesters()
            dialog.destroy()
            
        ttk.Button(dialog, text="Save", command=save, style='Success.TButton').pack(pady=10)
        dialog.bind('<Return>', save)

    def _add_subject_dialog(self):
        idx = self.semester_combo.current()
        if idx < 0:
            messagebox.showwarning("Warning", "Select a semester first!")
            return
        sem_id = self.semesters_list[idx]['id']
        
        dialog = tk.Toplevel(self)
        dialog.title("Add Subject")
        
        w, h = 400, 300
        dialog.update_idletasks()
        x = int(dialog.winfo_screenwidth()/2 - w/2)
        y = int(dialog.winfo_screenheight()/2 - h/2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        ttk.Label(dialog, text="Subject Name:").pack(pady=(10, 2))
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var).pack(pady=2)
        
        ttk.Label(dialog, text="Subject Code:").pack(pady=(5, 2))
        code_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=code_var).pack(pady=2)
        
        ttk.Label(dialog, text="Credits:").pack(pady=(5, 2))
        credits_var = tk.StringVar(value="3")
        ttk.Spinbox(dialog, from_=1, to=10, textvariable=credits_var).pack(pady=2)
        
        def save(event=None):
            name = name_var.get().strip()
            code = code_var.get().strip()
            cr = credits_var.get()
            if not name or not code or not cr:
                return
            self.db_manager.add_subject(sem_id, name, code, int(cr))
            self.refresh_subjects()
            dialog.destroy()
            
        ttk.Button(dialog, text="Save", command=save, style='Success.TButton').pack(pady=10)
        dialog.bind('<Return>', save)

    def save_marks(self, event=None):
        subj_idx = self.subject_combo.current()
        if subj_idx < 0:
            messagebox.showerror("Error", "Please select a subject.")
            return
            
        subject_id = self.subjects_list[subj_idx]['id']
        
        try:
            internal = float(self.internal_var.get() or 0)
            external = float(self.external_var.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Marks must be numeric.")
            return
            
        total = internal + external
        grade = marks_to_grade(total)
        points = grade_to_points(grade)
        
        success = self.db_manager.add_mark(subject_id, internal, external, total, grade, points)
        if success:
            messagebox.showinfo("Success", f"Marks saved! Total: {total}, Grade: {grade}")
            self.internal_var.set("")
            self.external_var.set("")
            if self.refresh_callback:
                self.refresh_callback()
        else:
            messagebox.showerror("Error", "Failed to save marks.")

    def delete_subject(self):
        subj_idx = self.subject_combo.current()
        if subj_idx < 0:
            messagebox.showwarning("Warning", "Please select a subject to delete.")
            return
            
        subject_id = self.subjects_list[subj_idx]['id']
        subject_name = self.subjects_list[subj_idx]['subject_name']
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to completely delete the subject '{subject_name}' and all its associated marks? This cannot be undone.")
        if confirm:
            if self.db_manager.delete_subject(subject_id):
                messagebox.showinfo("Success", f"Subject '{subject_name}' deleted successfully.")
                self.refresh_subjects()
                if self.refresh_callback:
                    self.refresh_callback()
            else:
                messagebox.showerror("Error", "Failed to delete subject from database.")

    def delete_marks(self):
        subj_idx = self.subject_combo.current()
        if subj_idx < 0:
            messagebox.showwarning("Warning", "Please select a subject first.")
            return
            
        subject_id = self.subjects_list[subj_idx]['id']
        
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete ALL marks for this specific subject?")
        if confirm:
            try:
                with self.db_manager.connect() as (conn, cursor):
                    cursor.execute("DELETE FROM marks WHERE subject_id = %s", (subject_id,))
                    conn.commit()
                messagebox.showinfo("Success", "Marks deleted successfully.")
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete marks: {e}")
