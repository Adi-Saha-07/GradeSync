import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gpa_calculator import calculate_cgpa, get_performance_remark

class DashboardView(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.student_id = None
        
        self._create_widgets()

    def set_student(self, student_id):
        self.student_id = student_id
        self.refresh_data()

    def _create_widgets(self):

        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cgpa_label = ttk.Label(top_frame, text="Overall CGPA: --", font=("Helvetica", 24, "bold"), foreground="#2E86C1")
        self.cgpa_label.pack(side=tk.LEFT)
        
        self.remark_label = ttk.Label(top_frame, text="", font=("Helvetica", 14, "italic"), foreground="#7F8C8D")
        self.remark_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        self.refresh_btn = ttk.Button(top_frame, text="Refresh Data", command=self.refresh_data)
        self.refresh_btn.pack(side=tk.RIGHT)

        content_frame = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        content_frame.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(content_frame)
        content_frame.add(table_frame, weight=1)

        columns = ('id', 'sem', 'subject', 'credits', 'total', 'grade', 'points')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.column('id', width=30, anchor=tk.CENTER)
        self.tree.heading('sem', text='Semester')
        self.tree.column('sem', width=40, anchor=tk.CENTER)
        self.tree.heading('subject', text='Subject')
        self.tree.column('subject', width=150)
        self.tree.heading('credits', text='Credits')
        self.tree.column('credits', width=40, anchor=tk.CENTER)
        self.tree.heading('total', text='Total')
        self.tree.column('total', width=50, anchor=tk.CENTER)
        self.tree.heading('grade', text='Grade')
        self.tree.column('grade', width=50, anchor=tk.CENTER)
        self.tree.heading('points', text='Points')
        self.tree.column('points', width=40, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind('<Delete>', self._delete_selected)

        chart_frame = ttk.Frame(content_frame)
        content_frame.add(chart_frame, weight=1)
        
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=10)
        
        self.del_mark_btn = tk.Button(bottom_frame, text="Delete Selected Mark from Table", command=self._delete_selected_btn, bg="#E74C3C", fg="white", activebackground="#C0392B", activeforeground="white", relief="flat", font=("Helvetica", 10, "bold"), cursor="hand2", padx=15, pady=5)
        self.del_mark_btn.pack(side=tk.LEFT)

    def refresh_data(self):
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.student_id:
            self.cgpa_label.config(text="Overall CGPA: --", foreground="#7F8C8D")
            self.remark_label.config(text="")
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'No data to display', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes, color='#888888', fontdict={'size': 12, 'style': 'italic'})
            self.fig.patch.set_facecolor('#1c1c1c')
            self.ax.set_facecolor('#1c1c1c')
            self.canvas.draw()
            return
            
        query = """
            SELECT m.id, s.semester_number, sub.subject_name, sub.credits, m.total_marks, m.grade, m.grade_points
            FROM marks m 
            JOIN subjects sub ON m.subject_id = sub.id 
            JOIN semesters s ON sub.semester_id = s.id 
            WHERE s.student_id = %s 
            ORDER BY s.semester_number, sub.subject_name
        """
        with self.db_manager.connect() as (conn, cursor):
            cursor.execute(query, (self.student_id,))
            marks = cursor.fetchall()
            
        for m in marks:
            self.tree.insert('', tk.END, values=(
                m['id'], m['semester_number'], m['subject_name'], 
                m['credits'], m['total_marks'], m['grade'], m['grade_points']
            ))

        semesters_data = self.db_manager.get_all_semesters_with_sgpa(self.student_id)
        
        sgpas = []
        sem_numbers = []
        for sem in semesters_data:
            if sem['sgpa'] > 0:
                sgpas.append(float(sem['sgpa']))
                sem_numbers.append(sem['semester_number'])
                
        cgpa = calculate_cgpa(sgpas)
        remark = get_performance_remark(cgpa)
        
        if cgpa >= 7.0:
            color_hex = "#2ECC71"
        elif cgpa >= 5.0:
            color_hex = "#F1C40F"
        else:
            color_hex = "#E74C3C"

        self.cgpa_label.config(text=f"Overall CGPA: {cgpa:.2f}", foreground=color_hex)
        if cgpa > 0:
            self.remark_label.config(text=f"({remark})", foreground=color_hex)
        else:
            self.remark_label.config(text="")
            
        self.ax.clear()
        self.fig.patch.set_facecolor('#1c1c1c')
        self.ax.set_facecolor('#1c1c1c')
        
        if not sgpas:
            self.ax.text(0.5, 0.5, 'No data to display', horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes, color='#888888', fontdict={'size': 12, 'style': 'italic'})
        else:
            self.ax.plot(sem_numbers, sgpas, marker='o', linestyle='-', color=color_hex, linewidth=2.5, markersize=8, markerfacecolor='white')

            for x, y in zip(sem_numbers, sgpas):
                self.ax.annotate(f'{y:.2f}', xy=(x, y), xytext=(0, 5), textcoords='offset points', ha='center', va='bottom', fontsize=9, color='white', fontweight='bold')
                
            self.ax.set_title('SGPA Trend Analysis', color='white', fontsize=12, fontweight='bold', pad=15)
            self.ax.set_xlabel('Semester', color='#AAAAAA', fontsize=10, fontweight='bold')
            self.ax.set_ylabel('SGPA', color='#AAAAAA', fontsize=10, fontweight='bold')
            self.ax.set_ylim(0, 11)
            self.ax.set_xticks(sem_numbers)
            self.ax.grid(True, linestyle='--', alpha=0.2, color='#ffffff')
            self.ax.tick_params(colors='#AAAAAA')
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            self.ax.spines['bottom'].set_color('#555555')
            self.ax.spines['left'].set_color('#555555')
            
        self.fig.tight_layout()
        self.canvas.draw()

    def _delete_selected_btn(self):
        self._delete_selected(None)

    def _delete_selected(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item[0])['values']
            mark_id = values[0]
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this mark?"):
                if self.db_manager.delete_mark(mark_id):
                    self.refresh_data()
