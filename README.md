# SchoolManageMent

This is a personal project on which I am working part time to learn the core things of object oriented paradigm. This project is inteded to consist of APIs for different purposes of school management like student and staff data management, leave management, holiday management etc.
By any means, this project is not suggested to be used in production untill and unless you know what you are doing. Permissions have been handled but not very carefully. Some APIs rely on the frontend to send the right data, backend does not verify those details.

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
  
**Different Systems**
  
  1) **Authentication**: This application uses jwt authentication and stores specific data to the token and relies on that token data for authentication and permission management.
  
  2) **AppStaff Management**: AppStaff means the staff who are managing the system at the company level and do the work of onboarding new institutions. AppStaffs will have access to onboard new institutions and edit their details. AppStaff with app_admin designation will have access to all APIs in the system.
  
  3) **Institute Staff Management**: APIs related to institute staff management has been provided. Schools can create different type of staffs, store their personal and educational details in the database and give special designation and permissions like Class Teacher, Wing Co-ordinator etc.
  
  4) **Institute Configuration Mangement**: There are few things like what classes institute has, what subjects it provides in different classes etc to be saved at institute(admin) level. APIs for all that kind of stuff have been provided. Classes along with class group or level, subject groups and different types of levels in both cases of classes and subjects have been provided. So that persons with different level of permissions and designations can be created.
  
  5) **Student and Parent Management**: APIs related to student admission and saving details of students and parents have been provided. 
  
  6) **Holiday Management**: RestAPIs related to different type of holidays like weekly holidays, annual holidays and unusual holidays like summer vacation have been provided.
  
  7) **Leave Managemet**: Leave applications of student and institute staff both have been provided. Students can apply to Class Teacher, Vice Class Teacher, Principal etc while staff too can apply to the relevent designation. It has been left out to frontend that to whom those leaves can be applied should be permitted. Backend does not verify that leave can be applied of class teacher or not. Although this will be a matter of few lines of code to make those things configurable at backend.
  
  **Till now, Rest APIs for these features have been provides. Next in pipeline is Attendance management system for students and staff both.**
