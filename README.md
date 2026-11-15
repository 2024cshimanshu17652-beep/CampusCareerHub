# Campus Career Hub

Campus Career Hub is a role-based college placement and recruitment web application developed using Flask and MySQL.

The platform provides separate functionality for Students, Companies, and Administrators.

## Features

### Student
- Student registration and login
- Student profile management
- View available jobs
- Job eligibility based on minimum CGPA and maximum backlogs
- Apply for eligible jobs
- Prevent duplicate applications
- Track application status

### Company
- Company registration and login
- Company profile management
- Create and manage job postings
- Set minimum CGPA and maximum backlog requirements
- View student applicants
- Shortlist applicants
- Reject applicants
- Select applicants

### Admin
- Admin dashboard
- Manage students
- Manage companies
- Verify companies
- Manage job postings
- Manage applications
- Search and filter records
- View placement statistics

## Technology Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- MySQL
- PyMySQL
- HTML
- CSS
- Jinja2

## Database

MySQL is used for storing users, student profiles, company profiles, job postings, and applications.

## Application Workflow

**Student:**  
Register → Complete Profile → View Jobs → Check Eligibility → Apply → Track Application

**Company:**  
Register → Complete Profile → Create Job → Set Eligibility → View Applicants → Shortlist/Reject/Select

**Admin:**  
Login → Dashboard → Manage Students/Companies/Jobs/Applications → Verify Companies

## Project Purpose

This project was developed as a BTech Computer Science portfolio project to demonstrate full-stack web development, database integration, authentication, role-based access control, and recruitment workflow implementation.
