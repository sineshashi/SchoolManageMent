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