# exports/excel_exporter.py
import pandas as pd
from tkinter import filedialog, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gpa_calculator import calculate_cgpa

class ExcelExporter:
    @staticmethod
    def export_data(db_manager, student_id, student_name_str):
        if not student_id:
            messagebox.showwarning("No Data", "Please select a student first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title=f"Save Excel Export for {student_name_str}"
        )

        if not file_path:
            return

        try:
            # Fetch Marks
            query = """
                SELECT s.semester_number, s.academic_year, sub.subject_code, sub.subject_name, 
                       sub.credits, m.internal_marks, m.external_marks, m.total_marks, m.grade, m.grade_points
                FROM marks m 
                JOIN subjects sub ON m.subject_id = sub.id 
                JOIN semesters s ON sub.semester_id = s.id 
                WHERE s.student_id = %s 
                ORDER BY s.semester_number, sub.subject_name
            """
            with db_manager.connect() as (conn, cursor):
                cursor.execute(query, (student_id,))
                marks_data = cursor.fetchall()
                
            # Fetch SGPA Data
            semesters_data = db_manager.get_all_semesters_with_sgpa(student_id)
            
            # Calculate CGPA
            sgpas = [float(sem['sgpa']) for sem in semesters_data if sem['sgpa'] > 0]
            cgpa = calculate_cgpa(sgpas)

            # Create DataFrames
            df_marks = pd.DataFrame(marks_data)
            if df_marks.empty:
                messagebox.showwarning("No Data", "No marks found for this student.")
                return
                
            # Rename columns nicely
            df_marks.columns = ['Semester', 'Academic Year', 'Sub Code', 'Sub Name', 
                                'Credits', 'Internal', 'External', 'Total', 'Grade', 'Points']
            
            summary_data = [{'Semester': sem['semester_number'], 'Academic Year': sem['academic_year'], 'SGPA': float(sem['sgpa'])} 
                            for sem in semesters_data if sem['sgpa'] > 0]
            df_summary = pd.DataFrame(summary_data)
            
            df_cgpa = pd.DataFrame([{'Student': student_name_str, 'Overall CGPA': cgpa}])

            # Write to Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df_marks.to_excel(writer, sheet_name='All Marks', index=False)
                df_summary.to_excel(writer, sheet_name='SGPA Summary', index=False)
                df_cgpa.to_excel(writer, sheet_name='Overall CGPA', index=False)
            
            messagebox.showinfo("Export Successful", f"Data exported successfully to\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred while exporting:\n{e}")
