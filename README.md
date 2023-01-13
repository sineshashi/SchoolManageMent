# SchoolManageMent

This is a personal project on which I am working part time to learn the core things of object oriented paradigm. This project is inteded to consist of APIs for different purposes of school management like student and staff data management, leave management, holiday management etc. 

**Understanding of Terminology**:
  
  0) Designation: This is the entity which consists of the data of user and its role and designation in the school. Role is also a special thing which decided what permissions a user can have.

  1) SuperAdmin: SuperAdmin, in the project means the owner of chain of schools. With this account, all the permissions for the schools under him are provided.
  
  2) Admin: Admin means a superadmin like account for a single school. For each school there will be one super admin and one admin account. In short, super admin represents the chain of schools while admin represent a single school.
  
  3) InstituteStaff: This is the school staff.
  
  4) ClassGroupDepartment: This represents a class group like primary, junior, highschool etc.
  
  5) SubjectGroupDepartment: This represents a subject group like science and arts.
  
  6) Class: Class is class level object which may have many sections.
  
  7) Section: Section is the entity representing a group of students.
  
  8) Subject: Subject represents a single subject.
  
  9) AcademicSession: Represents academic session details.
  
  10) Semester: Represents a semester of given academic session.
  
  11) WeeklyHolidays: Represents weekly holidays like sunday and saturday.
  
  12) AnnualHolidays: These are specially festival holidays like holi, diwali, christmas etc.
  
  13) IrregularHolidays: These are volatile holidays which are often not fixed in the start of the session like winter and summer vacation mandated of government due to extreme conditions.
  
  14) Meeting: Reperesents a single meeting considering two meetings in a working day.
  
  15) Leave: Represents an entilty for consisting of all the data for a leave.
