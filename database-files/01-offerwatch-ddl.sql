DROP DATABASE IF EXISTS `OfferWatchDB`;
CREATE DATABASE IF NOT EXISTS `OfferWatchDB`;
USE `OfferWatchDB`;

CREATE TABLE Institution (
   InstitutionID INT AUTO_INCREMENT PRIMARY KEY,
   InstitutionName VARCHAR(100) NOT NULL,
   InstitutionType VARCHAR(50) NOT NULL,
   Status VARCHAR(20) NOT NULL
);

CREATE TABLE Role (
   RoleID INT AUTO_INCREMENT PRIMARY KEY,
   RoleName VARCHAR(75) NOT NULL UNIQUE,
   RoleDescription TEXT
);

CREATE TABLE Permission (
   PermissionID INT AUTO_INCREMENT PRIMARY KEY,
   PermissionName VARCHAR(100) NOT NULL UNIQUE,
   PermissionDescription TEXT
);

CREATE TABLE Role_Permission (
   RoleID INT NOT NULL,
   PermissionID INT NOT NULL,
   PRIMARY KEY (RoleID, PermissionID),
   CONSTRAINT fk_rp_role
       FOREIGN KEY (RoleID) REFERENCES Role(RoleID),
   CONSTRAINT fk_rp_permission
       FOREIGN KEY (PermissionID) REFERENCES Permission(PermissionID)
);

CREATE TABLE Major (
   MajorID INT AUTO_INCREMENT PRIMARY KEY,
   MajorName VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Industry (
   IndustryID INT AUTO_INCREMENT PRIMARY KEY,
   Title VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE `User` (
   UserID INT AUTO_INCREMENT PRIMARY KEY,
   FirstName VARCHAR(50) NOT NULL,
   LastName VARCHAR(50) NOT NULL,
   Email VARCHAR(100) NOT NULL UNIQUE,
   RoleID INT NOT NULL,
   InstitutionID INT NOT NULL,
   Created_At DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
   Deactivated_At DATETIME NULL,
   Account_Status VARCHAR(20) NOT NULL,
   CONSTRAINT fk_user_role
       FOREIGN KEY (RoleID) REFERENCES Role(RoleID),
   CONSTRAINT fk_user_institution
       FOREIGN KEY (InstitutionID) REFERENCES Institution(InstitutionID),
   INDEX idx_user_role (RoleID),
   INDEX idx_user_institution (InstitutionID)
);

CREATE TABLE Advisor (
   AdvisorID INT AUTO_INCREMENT PRIMARY KEY,
   UserID INT NOT NULL UNIQUE,
   CONSTRAINT fk_advisor_user
       FOREIGN KEY (UserID) REFERENCES `User`(UserID),
   INDEX idx_advisor_user (UserID)
);

CREATE TABLE Recruiter (
   RecruiterID INT AUTO_INCREMENT PRIMARY KEY,
   UserID INT NOT NULL UNIQUE,
   CONSTRAINT fk_recruiter_user
       FOREIGN KEY (UserID) REFERENCES `User`(UserID),
   INDEX idx_recruiter_user (UserID)
);

CREATE TABLE Student (
   StudentID INT AUTO_INCREMENT PRIMARY KEY,
   UserID INT NOT NULL UNIQUE,
   Year INT NOT NULL,
   MajorID INT NULL,
   GPA DECIMAL(3,2) NULL,
   NumApplications INT NOT NULL DEFAULT 0,
   LastActivityDate DATETIME NULL,
   AdvisorID INT NULL,
   CONSTRAINT fk_student_user
       FOREIGN KEY (UserID) REFERENCES `User`(UserID),
   CONSTRAINT fk_student_major
       FOREIGN KEY (MajorID) REFERENCES Major(MajorID),
   CONSTRAINT fk_student_advisor
       FOREIGN KEY (AdvisorID) REFERENCES Advisor(AdvisorID),
   INDEX idx_student_user (UserID),
   INDEX idx_student_major (MajorID),
   INDEX idx_student_advisor (AdvisorID),
   INDEX idx_student_last_activity (LastActivityDate)
);

CREATE TABLE Student_Industry (
   StudentIndustryID INT AUTO_INCREMENT PRIMARY KEY,
   StudentID INT NOT NULL,
   IndustryID INT NOT NULL,
   PreferenceRank INT NULL,
   CONSTRAINT fk_studentindustry_student
       FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
   CONSTRAINT fk_studentindustry_industry
       FOREIGN KEY (IndustryID) REFERENCES Industry(IndustryID),
   CONSTRAINT uq_student_industry UNIQUE (StudentID, IndustryID),
   INDEX idx_studentindustry_student (StudentID),
   INDEX idx_studentindustry_industry (IndustryID)
);

CREATE TABLE Employer (
   EmployerID INT AUTO_INCREMENT PRIMARY KEY,
   IndustryID INT NOT NULL,
   Name VARCHAR(100) NOT NULL,
   Location VARCHAR(100) NULL,
   Size VARCHAR(50) NULL,
   RecruitingStatus VARCHAR(50) NULL,
   MinGPA DECIMAL(3,2) NULL,
   CONSTRAINT fk_employer_industry
       FOREIGN KEY (IndustryID) REFERENCES Industry(IndustryID),
   INDEX idx_employer_industry (IndustryID),
   INDEX idx_employer_name (Name)
);

CREATE TABLE `Position` (
   PositionID INT AUTO_INCREMENT PRIMARY KEY,
   EmployerID INT NOT NULL,
   Title VARCHAR(100) NOT NULL,
   CONSTRAINT fk_position_employer
       FOREIGN KEY (EmployerID) REFERENCES Employer(EmployerID),
   INDEX idx_position_employer (EmployerID),
   INDEX idx_position_title (Title)
);

CREATE TABLE Resume (
   ResumeID INT AUTO_INCREMENT PRIMARY KEY,
   StudentID INT NOT NULL,
   Version INT NOT NULL,
   InterviewConversionRate DECIMAL(5,2) NULL,
   DateSubmitted DATETIME NOT NULL,
   CONSTRAINT fk_resume_student
       FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
   CONSTRAINT uq_resume_version UNIQUE (StudentID, Version),
   INDEX idx_resume_student (StudentID)
);

CREATE TABLE Job_Application (
   ApplicationID INT AUTO_INCREMENT PRIMARY KEY,
   StudentID INT NOT NULL,
   PositionID INT NOT NULL,
   ResumeID INT NULL,
   Application_Date DATETIME NOT NULL,
   Status VARCHAR(50) NOT NULL,
   Notes TEXT NULL,
   IsArchived BOOLEAN NOT NULL DEFAULT FALSE,
   CONSTRAINT fk_application_student
       FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
   CONSTRAINT fk_application_position
       FOREIGN KEY (PositionID) REFERENCES `Position`(PositionID),
   CONSTRAINT fk_application_resume
       FOREIGN KEY (ResumeID) REFERENCES Resume(ResumeID),
   INDEX idx_application_student (StudentID),
   INDEX idx_application_position (PositionID),
   INDEX idx_application_status (Status),
   INDEX idx_application_archived (IsArchived),
   INDEX idx_application_date (Application_Date)
);

CREATE TABLE Interview (
   InterviewID INT AUTO_INCREMENT PRIMARY KEY,
   ApplicationID INT NOT NULL,
   Date_Time DATETIME NOT NULL,
   Type VARCHAR(50) NULL,
   WeekReported DATETIME NULL,
   RecruiterFeedback TEXT NULL,
   CONSTRAINT fk_interview_application
       FOREIGN KEY (ApplicationID) REFERENCES Job_Application(ApplicationID),
   INDEX idx_interview_application (ApplicationID),
   INDEX idx_interview_date (Date_Time)
);

CREATE TABLE Job_Offer (
   OfferID INT AUTO_INCREMENT PRIMARY KEY,
   ApplicationID INT NOT NULL UNIQUE,
   Salary DECIMAL(10,2) NULL,
   Deadline DATETIME NULL,
   Location VARCHAR(100) NULL,
   Benefits TEXT NULL,
   StartDate DATETIME NULL,
   DateExtended DATETIME NULL,
   DateAccepted DATETIME NULL,
   TimeToOfferWeeks INT NULL,
   OfferAccepted BOOLEAN NULL,
   CONSTRAINT fk_joboffer_application
       FOREIGN KEY (ApplicationID) REFERENCES Job_Application(ApplicationID),
   INDEX idx_joboffer_deadline (Deadline)
);

CREATE TABLE Reminder (
   ReminderID INT AUTO_INCREMENT PRIMARY KEY,
   ApplicationID INT NOT NULL,
   Description TEXT NOT NULL,
   DueDate DATETIME NOT NULL,
   CONSTRAINT fk_reminder_application
       FOREIGN KEY (ApplicationID) REFERENCES Job_Application(ApplicationID),
   INDEX idx_reminder_application (ApplicationID),
   INDEX idx_reminder_duedate (DueDate)
);

CREATE TABLE Note (
   NoteID INT AUTO_INCREMENT PRIMARY KEY,
   ApplicationID INT NOT NULL,
   Note_Text TEXT NOT NULL,
   Created_At DATETIME NOT NULL,
   CONSTRAINT fk_note_application
       FOREIGN KEY (ApplicationID) REFERENCES Job_Application(ApplicationID),
   INDEX idx_note_application (ApplicationID),
   INDEX idx_note_created (Created_At)
);

CREATE TABLE Service_Component (
   ComponentID INT AUTO_INCREMENT PRIMARY KEY,
   Component_Name VARCHAR(100) NOT NULL,
   Component_Type VARCHAR(50) NOT NULL,
   Current_Status VARCHAR(20) NOT NULL,
   Last_Checked_At DATETIME NOT NULL
);

CREATE TABLE Error_Log (
   ErrorID INT AUTO_INCREMENT PRIMARY KEY,
   Error_Type VARCHAR(50) NOT NULL,
   Occurred_At DATETIME NOT NULL,
   Status VARCHAR(20) NOT NULL,
   Severity VARCHAR(20) NOT NULL,
   Message TEXT NOT NULL,
   ComponentID INT NOT NULL,
   CONSTRAINT fk_errorlog_component
       FOREIGN KEY (ComponentID) REFERENCES Service_Component(ComponentID),
   INDEX idx_errorlog_component (ComponentID),
   INDEX idx_errorlog_occurred (Occurred_At),
   INDEX idx_errorlog_status (Status)
);

CREATE TABLE Health_Metric (
   MetricID INT AUTO_INCREMENT PRIMARY KEY,
   Metric_Name VARCHAR(100) NOT NULL,
   Metric_Value DECIMAL(10,2) NOT NULL,
   Metric_Unit VARCHAR(30) NULL,
   Recorded_At DATETIME NOT NULL,
   ComponentID INT NOT NULL,
   CONSTRAINT fk_healthmetric_component
       FOREIGN KEY (ComponentID) REFERENCES Service_Component(ComponentID),
   INDEX idx_healthmetric_component (ComponentID),
   INDEX idx_healthmetric_recorded (Recorded_At)
);

CREATE TABLE Data_Correction (
   CorrectionID INT AUTO_INCREMENT PRIMARY KEY,
   UserID INT NOT NULL,
   Correction_Type VARCHAR(50) NOT NULL,
   Correction_Date DATETIME NOT NULL,
   Old_Value TEXT NULL,
   New_Value TEXT NULL,
   CorrectedByUserID INT NOT NULL,
   CONSTRAINT fk_datacorrection_user
       FOREIGN KEY (UserID) REFERENCES `User`(UserID),
   CONSTRAINT fk_datacorrection_correctedby
       FOREIGN KEY (CorrectedByUserID) REFERENCES `User`(UserID),
   INDEX idx_datacorrection_user (UserID),
   INDEX idx_datacorrection_correctedby (CorrectedByUserID),
   INDEX idx_datacorrection_date (Correction_Date)
);