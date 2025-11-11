from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class OrdinarySubjectGrade(BaseModel):
    subject: Optional[str] = None
    grade: Optional[str] = Field(None, description="Letters A-F or numbers 1-9 make corrections closely resembling characters ensure you stick to the range")


# Enum for grade values (letters A-F and numbers 1-9)
class Grade(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = '1'
    H = "2"
    I = "3"
    J = "4"
    K = "5"
    L = "6"
    M = "7"
    N = "8"
    O = "9"
    P = "A+"

    # You can add more values if necessary (e.g., 1-9)
    # If the range is expected to be numerical (1-9), you can include numbers as well
    # For example: G = 7, H = 8, I = 9, etc.


# Enum for level values
class Level(Enum):
    PRINCIPAL = 'AL'  # Advanced Level
    ADVANCED_SUBSIDIARY = 'AS'  # Advanced Subsidiary


# Updated AdvancedSubjectGrade model
class AdvancedSubjectGrade(BaseModel):
    subject: Optional[str] = None
    grade: Optional[Grade] = Field(None,
                                   description="Either A+ or Single letters in uppercase A-F or numbers 1-9 make corrections closely resembling characters ensure you stick to the range")
    level: Optional[Level] = Field(None,
                                   description="One of these: Principal (AL), or Advanced Subsidiary (AS) make estimated correction to ensure you stick to the range")

    class Config:
        use_enum_values = True  # This automatically uses the enum value for serialization


class OrdinaryExamResult(BaseModel):
    exam_type: Optional[str] = None  # "Cambridge S.C." or "Cambridge G.C.E." etc.
    month_year: Optional[str] = None
    index_no: Optional[str] = None
    exam_centre_no: Optional[str] = None
    subjects: Optional[List[OrdinarySubjectGrade]] = None
    result: Optional[str] = None
    aggregate: Optional[str] = None


class AdvancedExamResult(BaseModel):
    exam_type: Optional[str] = None  # "Cambridge S.C." or "Cambridge G.C.E." etc.
    month_year: Optional[str] = None
    index_no: Optional[str] = None
    exam_centre_no: Optional[str] = None
    subjects: Optional[List[AdvancedSubjectGrade]] = None
    result: Optional[str] = None
    aggregate: Optional[str] = None


class QualificationLevel(str, Enum):
    SECONDARY = "secondary"
    TECHNICAL = "technical"
    DIPLOMA = "diploma"
    DEGREE = "degree"
    POST_DEGREE = "post_degree"


class CourseType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    DISTANCE = "distance_education"


class Qualification(BaseModel):
    level: Optional[QualificationLevel] = None
    institution: Optional[str] = None
    country: Optional[str] = None
    qualification_name: Optional[str] = None
    class_division_level: Optional[str] = None
    date_of_result: Optional[str] = None
    course_type: Optional[CourseType] = None
    duration_from: Optional[str] = None
    duration_to: Optional[str] = None
    subjects: Optional[List[str]] = None


class SecondaryQualificationsSubjectGrade(BaseModel):
    marks: Optional[int] = None
    grade: Optional[str] = None
    subject: Optional[str] = None
    percentage: Optional[int] = None


class SecondaryQualificationsExamResult(BaseModel):
    subjects: Optional[List[SecondaryQualificationsSubjectGrade]] = None
    result: Optional[str] = None
    aggregate: Optional[str] = None


class SecondaryQualifications(BaseModel):
    examining_body: Optional[str] = Field(None, description="")
    country: Optional[str] = Field(None, description="")
    certificate: Optional[str] = Field(None, description="")
    year: Optional[str] = Field(None, description="Date acquired in YYYY-MM-DD format")
    ExamResult: Optional[List[SecondaryQualificationsExamResult]]


class Employment(BaseModel):
    post_held: Optional[str] = None
    temporary_substantive: Optional[str] = None
    ministry_department: Optional[str] = None
    date_of_appointment: Optional[str] = None
    date_of_confirmation: Optional[str] = None
    present_salary: Optional[float] = None


class PSCApplication(BaseModel):
    # Personal Information
    post_applied_for: Optional[str] = None
    ministry_department: Optional[str] = None
    date_of_advertisement: Optional[str] = Field(None, description="Date of advertisement in yyyy-mm-dd format")
    national_identity_no: Optional[str] = Field(None, description="XXXXXXXXXXXXXX must be 14 characters long")
    surname: Optional[str] = None
    other_names: Optional[str] = None
    maiden_name: Optional[str] = None
    residential_address: Optional[str] = None
    date_of_birth: Optional[str] = Field(None, description="Date of birth in yyyy-mm-dd format")
    age: Optional[int] = None
    place_of_birth: Optional[str] = None
    nationality: Optional[str] = None

    # Contact Information
    phone_office: Optional[str] = None
    phone_home: Optional[str] = None
    phone_mobile: Optional[str] = None
    email: Optional[str] = None

    # Physical Attributes (sometimes required)
    height: Optional[float] = None
    chest: Optional[float] = None
    weight: Optional[float] = None

    # Qualifications
    ordinary_level_exams: Optional[List[OrdinaryExamResult]] = None
    advanced_level_exams: Optional[List[AdvancedExamResult]] = None
    other_secondary_qualifications: Optional[List[SecondaryQualificationsExamResult]] = None
    technical_vocational_qualifications: Optional[List[Qualification]] = None
    diploma_qualifications: Optional[List[Qualification]] = None
    degree_qualifications: Optional[List[Qualification]] = None
    post_degree_qualifications: Optional[List[Qualification]] = None
    other_qualifications: Optional[List[str]] = None

    # Employment History
    current_government_employment: Optional[Employment] = None
    previous_government_employment: Optional[List[Employment]] = None
    other_employment: Optional[List[Employment]] = None

    # Legal Information
    investigation_enquiry: Optional[bool] = None
    investigation_details: Optional[str] = None
    court_conviction: Optional[bool] = None
    conviction_details: Optional[str] = None
    resigned_retired_dismissed: Optional[bool] = None
    resignation_details: Optional[str] = None
