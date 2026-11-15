from datetime import datetime

from extensions import db
from flask_login import UserMixin


# ==========================================
# USER MODEL
# ==========================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="STUDENT"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================================
# STUDENT MODEL
# ==========================================

class Student(db.Model):

    __tablename__ = "students"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(15)
    )

    college = db.Column(
        db.String(150)
    )

    branch = db.Column(
        db.String(100)
    )

    semester = db.Column(
        db.Integer
    )

    cgpa = db.Column(
        db.Float
    )

    backlogs = db.Column(
        db.Integer,
        default=0
    )

    graduation_year = db.Column(
        db.Integer
    )

    github_url = db.Column(
        db.String(255)
    )

    linkedin_url = db.Column(
        db.String(255)
    )


# ==========================================
# COMPANY MODEL
# ==========================================

class Company(db.Model):

    __tablename__ = "companies"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    company_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    website = db.Column(
        db.String(255)
    )

    location = db.Column(
        db.String(100)
    )

    industry = db.Column(
        db.String(100)
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )


# ==========================================
# JOB MODEL
# ==========================================

class Job(db.Model):

    __tablename__ = "jobs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    company_name = db.Column(
        db.String(150),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    job_type = db.Column(
        db.String(50),
        nullable=False
    )

    location = db.Column(
        db.String(100),
        nullable=False
    )

    min_cgpa = db.Column(
        db.Float,
        default=0
    )

    max_backlogs = db.Column(
        db.Integer,
        default=0
    )

    salary = db.Column(
        db.String(100)
    )

    deadline = db.Column(
        db.Date
    )

    status = db.Column(
        db.String(30),
        default="ACTIVE"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# ==========================================
# APPLICATION MODEL
# ==========================================

class Application(db.Model):

    __tablename__ = "applications"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="APPLIED"
    )

    applied_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint(
            "student_id",
            "job_id",
            name="unique_student_job"
        ),
    )