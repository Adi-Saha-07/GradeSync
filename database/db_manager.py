import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG

class DBManager:
    def __init__(self):
        self.config = DB_CONFIG.copy()
        self.database_name = self.config.pop('database')
        self._ensure_database_exists()
        self.config['database'] = self.database_name
        self.initialize()

    def _ensure_database_exists(self):
        """Creates the database if it doesn't exist."""
        try:
            with mysql.connector.connect(**self.config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")
        except Error as e:
            print(f"Error ensuring database exists: {e}")

    @contextmanager
    def connect(self):
        """Context manager for yielding a database connection and cursor."""
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor(dictionary=True)
            yield connection, cursor
        except Error as e:
            print(f"Database connection error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def initialize(self):
        """Creates all necessary tables if they don't exist."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                roll_number VARCHAR(100) UNIQUE NOT NULL,
                branch VARCHAR(100) NOT NULL,
                year_of_joining INT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS semesters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                semester_number INT NOT NULL,
                academic_year VARCHAR(20) NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                semester_id INT NOT NULL,
                subject_name VARCHAR(255) NOT NULL,
                subject_code VARCHAR(50) NOT NULL,
                credits INT NOT NULL,
                FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS marks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subject_id INT NOT NULL,
                internal_marks FLOAT,
                external_marks FLOAT,
                total_marks FLOAT,
                grade VARCHAR(5) NOT NULL,
                grade_points FLOAT NOT NULL,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            )
            """
        ]
        
        try:
            with self.connect() as (conn, cursor):
                for query in queries:
                    cursor.execute(query)
                conn.commit()
        except Error as e:
            print(f"Error initializing tables: {e}")

    def add_student(self, name, roll_number, branch, year_of_joining):
        query = "INSERT INTO students (name, roll_number, branch, year_of_joining) VALUES (%s, %s, %s, %s)"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (name, roll_number, branch, year_of_joining))
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Error adding student: {e}")
            return None

    def get_student(self, student_id):
        query = "SELECT * FROM students WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (student_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"Error getting student: {e}")
            return None

    def update_student(self, student_id, name, roll_number, branch, year_of_joining):
        query = """
            UPDATE students 
            SET name = %s, roll_number = %s, branch = %s, year_of_joining = %s 
            WHERE id = %s
        """
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (name, roll_number, branch, year_of_joining, student_id))
                conn.commit()
                return True
        except Error as e:
            print(f"Error updating student: {e}")
            return False

    def delete_student(self, student_id):
        query = "DELETE FROM students WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (student_id,))
                conn.commit()
                return True
        except Error as e:
            print(f"Error deleting student: {e}")
            return False


    def add_semester(self, student_id, semester_number, academic_year):
        query = "INSERT INTO semesters (student_id, semester_number, academic_year) VALUES (%s, %s, %s)"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (student_id, semester_number, academic_year))
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Error adding semester: {e}")
            return None

    def get_semester(self, semester_id):
        query = "SELECT * FROM semesters WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (semester_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"Error getting semester: {e}")
            return None

    def update_semester(self, semester_id, semester_number, academic_year):
        query = "UPDATE semesters SET semester_number = %s, academic_year = %s WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (semester_number, academic_year, semester_id))
                conn.commit()
                return True
        except Error as e:
            print(f"Error updating semester: {e}")
            return False

    def delete_semester(self, semester_id):
        query = "DELETE FROM semesters WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (semester_id,))
                conn.commit()
                return True
        except Error as e:
            print(f"Error deleting semester: {e}")
            return False

    def add_subject(self, semester_id, subject_name, subject_code, credits):
        query = "INSERT INTO subjects (semester_id, subject_name, subject_code, credits) VALUES (%s, %s, %s, %s)"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (semester_id, subject_name, subject_code, credits))
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Error adding subject: {e}")
            return None

    def get_subject(self, subject_id):
        query = "SELECT * FROM subjects WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (subject_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"Error getting subject: {e}")
            return None

    def update_subject(self, subject_id, subject_name, subject_code, credits):
        query = "UPDATE subjects SET subject_name = %s, subject_code = %s, credits = %s WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (subject_name, subject_code, credits, subject_id))
                conn.commit()
                return True
        except Error as e:
            print(f"Error updating subject: {e}")
            return False

    def delete_subject(self, subject_id):
        query = "DELETE FROM subjects WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (subject_id,))
                conn.commit()
                return True
        except Error as e:
            print(f"Error deleting subject: {e}")
            return False

    def add_mark(self, subject_id, internal_marks, external_marks, total_marks, grade, grade_points):
        query = """
            INSERT INTO marks (subject_id, internal_marks, external_marks, total_marks, grade, grade_points) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (subject_id, internal_marks, external_marks, total_marks, grade, grade_points))
                conn.commit()
                return cursor.lastrowid
        except Error as e:
            print(f"Error adding marks: {e}")
            return None

    def get_mark(self, mark_id):
        query = "SELECT * FROM marks WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (mark_id,))
                return cursor.fetchone()
        except Error as e:
            print(f"Error getting mark: {e}")
            return None

    def update_mark(self, mark_id, internal_marks, external_marks, total_marks, grade, grade_points):
        query = """
            UPDATE marks 
            SET internal_marks = %s, external_marks = %s, total_marks = %s, grade = %s, grade_points = %s 
            WHERE id = %s
        """
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (internal_marks, external_marks, total_marks, grade, grade_points, mark_id))
                conn.commit()
                return True
        except Error as e:
            print(f"Error updating mark: {e}")
            return False

    def delete_mark(self, mark_id):
        query = "DELETE FROM marks WHERE id = %s"
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (mark_id,))
                conn.commit()
                return True
        except Error as e:
            print(f"Error deleting mark: {e}")
            return False

    def get_all_semesters_with_sgpa(self, student_id):
        """
        Calculates and returns SGPA for all semesters of a specific student.
        SGPA = sum(credits * grade_points) / sum(credits)
        """
        query = """
            SELECT 
                sem.id as semester_id,
                sem.semester_number,
                sem.academic_year,
                SUM(sub.credits) as total_credits,
                SUM(sub.credits * m.grade_points) as total_grade_points,
                IFNULL(SUM(sub.credits * m.grade_points) / NULLIF(SUM(sub.credits), 0), 0) as sgpa
            FROM semesters sem
            LEFT JOIN subjects sub ON sem.id = sub.semester_id
            LEFT JOIN marks m ON sub.id = m.subject_id
            WHERE sem.student_id = %s
            GROUP BY sem.id, sem.semester_number, sem.academic_year
            ORDER BY sem.semester_number ASC
        """
        try:
            with self.connect() as (conn, cursor):
                cursor.execute(query, (student_id,))
                return cursor.fetchall()
        except Error as e:
            print(f"Error fetching SGPA for semesters: {e}")
            return []
