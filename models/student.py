from dataclasses import dataclass

@dataclass
class MarkEntry:
    id: int
    semester: int
    subject: str
    credits: int
    grade: str
    
    @property
    def grade_point(self) -> int:
        mapping = {'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'C': 5, 'F': 0}
        return mapping.get(self.grade.upper(), 0)

@dataclass
class SemesterRecord:
    semester: int
    marks: list[MarkEntry]
    sgpa: float

@dataclass
class StudentRecord:
    semesters: dict[int, SemesterRecord]
    cgpa: float
