# utils/gpa_calculator.py

def marks_to_grade(total_marks: float) -> str:
    """
    Converts total marks into a grade string.
    
    Grading Scale:
    - 90-100 -> 'O' (Outstanding)
    - 80-89  -> 'A+' (Excellent)
    - 70-79  -> 'A'  (Very Good)
    - 60-69  -> 'B+' (Good)
    - 50-59  -> 'B'  (Above Average)
    - 40-49  -> 'C'  (Average)
    - < 40   -> 'F'  (Fail)
    
    Args:
        total_marks (float): The total marks obtained by the student (0-100).
        
    Returns:
        str: The corresponding grade letter.
    """
    if total_marks >= 90:
        return 'O'
    elif total_marks >= 80:
        return 'A+'
    elif total_marks >= 70:
        return 'A'
    elif total_marks >= 60:
        return 'B+'
    elif total_marks >= 50:
        return 'B'
    elif total_marks >= 40:
        return 'C'
    else:
        return 'F'

def grade_to_points(grade: str) -> float:
    """
    Converts a grade string into grade points.
    
    Points Scale:
    - O  = 10.0
    - A+ = 9.0
    - A  = 8.0
    - B+ = 7.0
    - B  = 6.0
    - C  = 5.0
    - F  = 0.0
    
    Args:
        grade (str): The grade letter (e.g., 'A+', 'B').
        
    Returns:
        float: The corresponding grade points.
    """
    mapping = {
        'O': 10.0,
        'A+': 9.0,
        'A': 8.0,
        'B+': 7.0,
        'B': 6.0,
        'C': 5.0,
        'F': 0.0
    }
    return mapping.get(grade.upper(), 0.0)

def calculate_sgpa(subjects_list: list[dict]) -> float:
    """
    Calculates the Semester Grade Point Average (SGPA).
    Formula: Sum of (credits * grade_points) / Sum of (credits)
    
    Args:
        subjects_list (list of dict): A list of dictionaries representing subjects.
                                      Each dict must contain 'credits' and 'grade_points'.
                                      Example: [{'credits': 4, 'grade_points': 9}, ...]
                                      
    Returns:
        float: The calculated SGPA, rounded to 2 decimal places. Returns 0.0 if no credits.
    """
    total_credit_points = 0.0
    total_credits = 0
    
    for subject in subjects_list:
        credits = subject.get('credits', 0)
        grade_points = subject.get('grade_points', 0.0)
        
        total_credit_points += credits * grade_points
        total_credits += credits
        
    if total_credits == 0:
        return 0.0
        
    return round(total_credit_points / total_credits, 2)

def calculate_cgpa(sgpa_list: list[float]) -> float:
    """
    Calculates the Cumulative Grade Point Average (CGPA).
    Formula: Simple average of all given SGPAs.
    
    Args:
        sgpa_list (list of float): A list containing SGPAs for all completed semesters.
        
    Returns:
        float: The calculated CGPA, rounded to 2 decimal places. Returns 0.0 if list is empty.
    """
    if not sgpa_list:
        return 0.0
    return round(sum(sgpa_list) / len(sgpa_list), 2)

def get_performance_remark(cgpa: float) -> str:
    """
    Returns a performance remark based on the CGPA.
    
    Remarks Scale:
    - 9.0 - 10.0 : 'Outstanding'
    - 8.0 - 8.99 : 'Excellent'
    - 7.0 - 7.99 : 'Very Good'
    - 6.0 - 6.99 : 'Good'
    - 5.0 - 5.99 : 'Average'
    - < 5.0      : 'Needs Improvement'
    
    Args:
        cgpa (float): The overall Cumulative Grade Point Average.
        
    Returns:
        str: The performance remark.
    """
    if cgpa >= 9.0:
        return 'Outstanding'
    elif cgpa >= 8.0:
        return 'Excellent'
    elif cgpa >= 7.0:
        return 'Very Good'
    elif cgpa >= 6.0:
        return 'Good'
    elif cgpa >= 5.0:
        return 'Average'
    else:
        return 'Needs Improvement'


# ==========================================
# UNIT TEST EXAMPLES
# ==========================================
# """
# if __name__ == "__main__":
#     # 1. Test marks_to_grade
#     assert marks_to_grade(95) == 'O'
#     assert marks_to_grade(82) == 'A+'
#     assert marks_to_grade(35) == 'F'
#     print("marks_to_grade tests passed!")
# 
#     # 2. Test grade_to_points
#     assert grade_to_points('A+') == 9.0
#     assert grade_to_points('F') == 0.0
#     assert grade_to_points('INVALID') == 0.0
#     print("grade_to_points tests passed!")
# 
#     # 3. Test calculate_sgpa
#     subjects = [
#         {'credits': 4, 'grade_points': 9.0}, # 36
#         {'credits': 3, 'grade_points': 8.0}, # 24
#         {'credits': 2, 'grade_points': 10.0} # 20
#     ]
#     # Total credits = 9. Total points = 80. SGPA = 80 / 9 = 8.89
#     assert calculate_sgpa(subjects) == 8.89
#     assert calculate_sgpa([]) == 0.0
#     print("calculate_sgpa tests passed!")
# 
#     # 4. Test calculate_cgpa
#     sgpas = [8.5, 9.0, 8.8] # sum = 26.3. cgpa = 26.3 / 3 = 8.77
#     assert calculate_cgpa(sgpas) == 8.77
#     assert calculate_cgpa([]) == 0.0
#     print("calculate_cgpa tests passed!")
# 
#     # 5. Test get_performance_remark
#     assert get_performance_remark(9.2) == 'Outstanding'
#     assert get_performance_remark(7.5) == 'Very Good'
#     assert get_performance_remark(4.5) == 'Needs Improvement'
#     print("get_performance_remark tests passed!")
# """
