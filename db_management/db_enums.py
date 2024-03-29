from enum import Enum

class EducationLevelEnum(str, Enum):
    high_school = "High School Or Equivalent"
    intermediate = "Intermediate Or Equivalent"
    graduation = "Graduation"
    post_graduation = "Post Graduation"
    higher_education = "Higher Education"
    field_specific = "Specific Courses like B.Ed. etc."
    other = "Other"

class EducationStatusEnum(str, Enum):
    passed = "Passed"
    failed = "Failed"
    appearing = "Appearing"

class IdentityProofEnum(str, Enum):
    aadhar = "AADHAR CARD"
    pan_card = "PAN CARD"
    driving_licence = "Driving Licence"
    passport = "PASSPORT"

class GaurdianTypeEnum(str, Enum):
    father="father"
    mother="mother"
    other="other"

class DayEnum(int, Enum):
    monday = 0
    tuesday = 1
    wednesday = 2
    thursday = 3
    friday = 4
    saturday = 5
    sunday = 6

class LeaveTypeEnum(str, Enum):
    causal = "Causal leave"
    optional_holiday = "Optional Holiday"
    sick_leave = "Sick Leave"
    unpaid_leave = "Unpaid Leave"
    paternity_leave = "Paternity Leave"
    maternaity_leave = "Maternity Leave"
    privilege_leave = "Privilege Leave"

class LeaveStatusEnum(str, Enum):
    approved="Approved"
    pending="Pending"
    rejected="Rejected"

class MeetingEnum(int, Enum):
    first = 0
    second = 1

class StaffLeaveApproverTypeEnum(str, Enum):
    principal = "Principal"
    managing_director = "Managing Director"

class StudentLeaveApproverTypeEnum(str, Enum):
    class_teacher = "Class Teacher"
    vice_class_teacher = "Vice Class Teacher"
    principal = "Principal"
    managing_director = "Managing Director"

class ApproverTypeEnum(str, Enum):
    class_teacher = "Class Teacher"
    vice_class_teacher = "Vice Class Teacher"
    principal = "Principal"
    managing_director = "Managing Director"