import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from extensions import db
from models import User, Student, Company, Job, Application


# Load environment variables
load_dotenv()

# Create Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# MySQL database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/"
    f"{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# STUDENT REGISTRATION
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "An account with this email already exists.", 409

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="STUDENT",
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# ==========================================
# COMPANY REGISTRATION
# ==========================================

@app.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        company_name = request.form["company_name"]
        industry = request.form.get("industry")
        location = request.form.get("location")
        website = request.form.get("website")
        description = request.form.get("description")

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "An account with this email already exists.", 409

        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role="COMPANY",
        )

        db.session.add(new_user)
        db.session.commit()

        new_company = Company(
            user_id=new_user.id,
            company_name=company_name,
            industry=industry,
            location=location,
            website=website,
            description=description,
        )

        db.session.add(new_company)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("company_register.html")


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            if user.role == "ADMIN":
                return redirect(url_for("admin_dashboard"))

            elif user.role == "COMPANY":
                return redirect(url_for("company_dashboard"))

            else:
                return redirect(url_for("dashboard"))

        return "Invalid email or password", 401

    return render_template("login.html")


# ==========================================
# ADMIN DASHBOARD
# ==========================================






@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "ADMIN":
        return "Unauthorized: Admin access required", 403

    total_students = User.query.filter_by(role="STUDENT").count()
    total_companies = User.query.filter_by(role="COMPANY").count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()

    active_jobs = Job.query.filter_by(status="ACTIVE").count()

    pending_applications = Application.query.filter_by(
        status="APPLIED"
    ).count()

    # Recent applications
    recent_applications = (
        db.session.query(Application, Student, User, Job)
        .join(Student, Application.student_id == Student.id)
        .join(User, Student.user_id == User.id)
        .join(Job, Application.job_id == Job.id)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    # Recent jobs
    recent_jobs = (
        Job.query
        .order_by(Job.created_at.desc())
        .limit(5)
        .all()
    )

    # Student profile completion
    complete_profile_condition = db.and_(
        Student.phone.isnot(None),
        Student.phone != "",
        Student.college.isnot(None),
        Student.college != "",
        Student.branch.isnot(None),
        Student.branch != "",
        Student.semester.isnot(None),
        Student.cgpa.isnot(None),
        Student.graduation_year.isnot(None)
    )

    completed_profiles = (
        db.session.query(Student)
        .join(User, Student.user_id == User.id)
        .filter(User.role == "STUDENT")
        .filter(complete_profile_condition)
        .count()
    )

    incomplete_profiles = max(
        total_students - completed_profiles, 0
    )

    profile_completion_percentage = (
        round(completed_profiles / total_students * 100)
        if total_students else 0
    )

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_jobs=total_jobs,
        total_applications=total_applications,
        active_jobs=active_jobs,
        pending_applications=pending_applications,
        recent_applications=recent_applications,
        recent_jobs=recent_jobs,
        completed_profiles=completed_profiles,
        incomplete_profiles=incomplete_profiles,
        profile_completion_percentage=profile_completion_percentage
    )







@app.route("/admin/users")
@login_required
def admin_users():
    if current_user.role != "ADMIN":
        return "Unauthorized: Admin access required", 403

    users = User.query.order_by(User.id.desc()).all()

    return render_template("admin_users.html", users=users)



@app.route("/admin/students")
@login_required
def admin_students():
    if current_user.role != "ADMIN":
        return "Unauthorized: Admin access required", 403

    students = (
        db.session.query(User, Student)
        .outerjoin(Student, Student.user_id == User.id)
        .filter(User.role == "STUDENT")
        .order_by(User.id.desc())
        .all()
    )

    return render_template(
        "admin_students.html",
        students=students
    )




@app.route("/admin/companies")
@login_required
def admin_companies():
    if current_user.role != "ADMIN":
        return "Unauthorized: Admin access required", 403

    search = request.args.get("search", "").strip()
    verification = request.args.get("verification", "").strip().lower()

    query = (
        db.session.query(User, Company)
        .outerjoin(Company, Company.user_id == User.id)
        .filter(User.role == "COMPANY")
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term),
                Company.company_name.ilike(search_term),
                Company.location.ilike(search_term),
                Company.industry.ilike(search_term)
            )
        )

    if verification == "verified":
        query = query.filter(Company.is_verified.is_(True))
    elif verification == "unverified":
        query = query.filter(
            db.or_(
                Company.id.is_(None),
                Company.is_verified.is_(False)
            )
        )

    companies = query.order_by(User.id.desc()).all()

    return render_template(
        "admin_companies.html",
        companies=companies,
        search=search,
        verification=verification
    )



@app.route("/admin/companies/<int:company_id>/toggle-verification",
           methods=["POST"])
@login_required
def admin_toggle_company_verification(company_id):
    if current_user.role != "ADMIN":
        return "Unauthorized: Admin access required", 403

    company = db.session.get(Company, company_id)

    if company is None:
        return "Company not found", 404

    company.is_verified = not bool(company.is_verified)
    db.session.commit()

    return redirect(url_for("admin_companies"))





@app.route("/admin/jobs")
@login_required
def admin_jobs():
    if current_user.role != "ADMIN":
        return "Unauthorized: Admin access required", 403

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip().upper()

    query = db.session.query(Job)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Job.title.ilike(search_term),
                Job.company_name.ilike(search_term)
            )
        )

    if status in ["ACTIVE", "CLOSED", "INACTIVE"]:
        query = query.filter(Job.status == status)

    jobs = query.order_by(Job.created_at.desc()).all()

    return render_template(
        "admin_jobs.html",
        jobs=jobs,
        search=search,
        status=status
    )

    
    
    


@app.route("/admin/applications")
@login_required
def admin_applications():
    if current_user.role != "ADMIN":
        return "Unauthorized: Admin access required", 403

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip().upper()

    query = (
        db.session.query(Application, Student, User, Job)
        .join(Student, Application.student_id == Student.id)
        .join(User, Student.user_id == User.id)
        .join(Job, Application.job_id == Job.id)
    )

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term),
                Job.title.ilike(search_term),
                Job.company_name.ilike(search_term)
            )
        )

    if status in ["APPLIED", "SHORTLISTED", "REJECTED", "SELECTED"]:
        query = query.filter(Application.status == status)

    applications = query.order_by(
        Application.applied_at.desc()
    ).all()

    return render_template(
        "admin_applications.html",
        applications=applications,
        search=search,
        status=status
    )
    
    
    
@app.route("/company/application/<int:application_id>/status", methods=["POST"])
@login_required
def company_update_application_status(application_id):
    if current_user.role != "COMPANY":
        return "Unauthorized: Company access required", 403

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    if company is None:
        return "Company profile not found.", 404

    application = db.session.get(Application, application_id)

    if application is None:
        return "Application not found.", 404

    job = db.session.get(Job, application.job_id)

    if job is None or job.company_name != company.company_name:
        return "Unauthorized access to this application.", 403

    new_status = request.form.get("status", "").strip().upper()

    if new_status not in ["SHORTLISTED", "REJECTED", "SELECTED"]:
        return "Invalid application status.", 400

    application.status = new_status
    db.session.commit()

    return redirect(url_for("company_applicants"))





# ==========================================
# COMPANY DASHBOARD
# ==========================================

@app.route("/company/dashboard")
@login_required
def company_dashboard():
    if current_user.role != "COMPANY":
        if current_user.role == "ADMIN":
            return redirect(url_for("admin_dashboard"))

        return redirect(url_for("dashboard"))

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    return render_template(
        "company_dashboard.html",
        company=company,
    )


# ==========================================
# CREATE JOB
# ==========================================

@app.route("/company/job/create", methods=["GET", "POST"])
@login_required
def create_job():
    if current_user.role != "COMPANY":
        return "Unauthorized: Company access required", 403

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    if company is None:
        return "Company profile not found.", 404

    if request.method == "POST":
        deadline = datetime.strptime(
            request.form["deadline"],
            "%Y-%m-%d",
        ).date()

        job = Job(
            company_name=company.company_name,
            title=request.form["title"],
            description=request.form["description"],
            job_type=request.form["job_type"],
            location=request.form["location"],
            min_cgpa=float(request.form.get("min_cgpa") or 0),
            max_backlogs=int(request.form.get("max_backlogs") or 0),
            salary=request.form.get("salary"),
            deadline=deadline,
            status="ACTIVE",
        )

        db.session.add(job)
        db.session.commit()

        return redirect(url_for("company_jobs"))

    return render_template("company_job_form.html", job=None)


# ==========================================
# VIEW COMPANY JOBS
# ==========================================

@app.route("/company/jobs")
@login_required
def company_jobs():
    if current_user.role != "COMPANY":
        return "Unauthorized: Company access required", 403

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    if company is None:
        return "Company profile not found.", 404

    jobs = Job.query.filter_by(
        company_name=company.company_name
    ).order_by(
        Job.created_at.desc()
    ).all()

    return render_template("company_jobs.html", jobs=jobs)


# ==========================================
# EDIT JOB
# ==========================================

@app.route(
    "/company/job/<int:job_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_job(job_id):
    if current_user.role != "COMPANY":
        return "Unauthorized: Company access required", 403

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    job = Job.query.get_or_404(job_id)

    if company is None or job.company_name != company.company_name:
        return "Unauthorized", 403

    if request.method == "POST":
        job.title = request.form["title"]
        job.description = request.form["description"]
        job.job_type = request.form["job_type"]
        job.location = request.form["location"]

        job.min_cgpa = float(request.form.get("min_cgpa") or 0)
        job.max_backlogs = int(request.form.get("max_backlogs") or 0)
        job.salary = request.form.get("salary")

        job.deadline = datetime.strptime(
            request.form["deadline"],
            "%Y-%m-%d",
        ).date()

        db.session.commit()

        return redirect(url_for("company_jobs"))

    return render_template("company_job_form.html", job=job)


# ==========================================
# DELETE OR CLOSE JOB
# ==========================================

@app.route(
    "/company/job/<int:job_id>/delete",
    methods=["POST"],
)
@login_required
def delete_job(job_id):
    if current_user.role != "COMPANY":
        return "Unauthorized: Company access required", 403

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    job = Job.query.get_or_404(job_id)

    if company is None or job.company_name != company.company_name:
        return "Unauthorized", 403

    # Preserve application history
    existing_application = Application.query.filter_by(
        job_id=job.id
    ).first()

    if existing_application:
        job.status = "CLOSED"
    else:
        db.session.delete(job)

    db.session.commit()

    return redirect(url_for("company_jobs"))


# ==========================================
# COMPANY APPLICANTS
# ==========================================

@app.route("/company/applicants")
@login_required
def company_applicants():
    if current_user.role != "COMPANY":
        return "Unauthorized: Company access required", 403

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    if company is None:
        return "Company profile not found.", 404

    company_jobs_list = Job.query.filter_by(
        company_name=company.company_name
    ).all()

    job_ids = [job.id for job in company_jobs_list]

    applicants = []

    if job_ids:
        applications_list = Application.query.filter(
            Application.job_id.in_(job_ids)
        ).order_by(
            Application.applied_at.desc()
        ).all()

        for application in applications_list:
            student = db.session.get(
                Student,
                application.student_id,
            )

            if student is None:
                continue

            student_user = db.session.get(
                User,
                student.user_id,
            )

            job = db.session.get(
                Job,
                application.job_id,
            )

            applicants.append({
                "application": application,
                "student": student,
                "student_user": student_user,
                "job": job,
            })

    return render_template(
        "company_applicants.html",
        applicants=applicants,
    )


# ==========================================
# UPDATE APPLICATION STATUS
# ==========================================

@app.route(
    "/company/application/<int:application_id>/status",
    methods=["POST"],
)
@login_required
def update_application_status(application_id):
    if current_user.role != "COMPANY":
        return "Unauthorized: Company access required", 403

    application = Application.query.get_or_404(application_id)
    job = Job.query.get_or_404(application.job_id)

    company = Company.query.filter_by(
        user_id=current_user.id
    ).first()

    if company is None or job.company_name != company.company_name:
        return "Unauthorized", 403

    new_status = request.form.get("status")

    allowed_statuses = [
        "APPLIED",
        "SHORTLISTED",
        "INTERVIEW",
        "SELECTED",
        "REJECTED",
    ]

    if new_status not in allowed_statuses:
        return "Invalid application status", 400

    application.status = new_status
    db.session.commit()

    return redirect(url_for("company_applicants"))


# ==========================================
# STUDENT DASHBOARD
# ==========================================

@app.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "ADMIN":
        return redirect(url_for("admin_dashboard"))

    if current_user.role == "COMPANY":
        return redirect(url_for("company_dashboard"))

    return render_template("dashboard.html")


# ==========================================
# STUDENT PROFILE
# ==========================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if current_user.role != "STUDENT":
        return "Unauthorized: Student access required", 403

    student = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    if request.method == "POST":
        phone = request.form.get("phone")
        college = request.form.get("college")
        branch = request.form.get("branch")
        semester = request.form.get("semester")
        cgpa = request.form.get("cgpa")
        backlogs = request.form.get("backlogs")
        graduation_year = request.form.get("graduation_year")
        github_url = request.form.get("github_url")
        linkedin_url = request.form.get("linkedin_url")

        if student is None:
            student = Student(user_id=current_user.id)
            db.session.add(student)

        student.phone = phone
        student.college = college
        student.branch = branch

        student.semester = int(semester) if semester else None
        student.cgpa = float(cgpa) if cgpa else None
        student.backlogs = int(backlogs) if backlogs else 0

        student.graduation_year = (
            int(graduation_year) if graduation_year else None
        )

        student.github_url = github_url
        student.linkedin_url = linkedin_url

        db.session.commit()

        return redirect(url_for("profile"))

    return render_template("profile.html", student=student)


# ==========================================
# BROWSE JOBS
# ==========================================

@app.route("/jobs")
@login_required
def jobs():
    if current_user.role != "STUDENT":
        return "Unauthorized: Student access required", 403

    jobs_list = Job.query.filter_by(
        status="ACTIVE"
    ).order_by(
        Job.created_at.desc()
    ).all()

    return render_template("jobs.html", jobs=jobs_list)


# ==========================================
# JOB DETAILS
# ==========================================

@app.route("/job/<int:job_id>")
@login_required
def job_details(job_id):
    if current_user.role != "STUDENT":
        return "Unauthorized: Student access required", 403

    job = Job.query.get_or_404(job_id)

    student = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    already_applied = False

    if student:
        existing_application = Application.query.filter_by(
            student_id=student.id,
            job_id=job.id,
        ).first()

        already_applied = existing_application is not None

    return render_template(
        "job_details.html",
        job=job,
        already_applied=already_applied,
    )


# ==========================================
# APPLY FOR A JOB
# ==========================================


@app.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply_job(job_id):
    if current_user.role != "STUDENT":
        return "Unauthorized: Student access required", 403

    job = Job.query.get_or_404(job_id)

    if job.status != "ACTIVE":
        return "This job is no longer accepting applications.", 400

    student = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    if student is None:
        return "Please complete your student profile before applying.", 400

    # Check whether eligibility information is available
    if student.cgpa is None or student.backlogs is None:
        return (
            "Please update your CGPA and backlog details "
            "in your student profile before applying."
        ), 400

    # Check minimum CGPA
    minimum_cgpa = job.min_cgpa if job.min_cgpa is not None else 0

    if student.cgpa < minimum_cgpa:
        return (
            f"You are not eligible for this job. "
            f"Minimum required CGPA is {minimum_cgpa}; "
            f"your CGPA is {student.cgpa}."
        ), 400

    # Check maximum allowed backlogs
    maximum_backlogs = (
        job.max_backlogs if job.max_backlogs is not None else 0
    )

    if student.backlogs > maximum_backlogs:
        return (
            f"You are not eligible for this job. "
            f"Maximum allowed backlogs: {maximum_backlogs}; "
            f"your backlogs: {student.backlogs}."
        ), 400

    # Prevent duplicate applications
    existing_application = Application.query.filter_by(
        student_id=student.id,
        job_id=job.id,
    ).first()

    if existing_application:
        return "You have already applied for this job.", 409

    # Create application only after eligibility checks pass
    application = Application(
        student_id=student.id,
        job_id=job.id,
        status="APPLIED",
    )

    db.session.add(application)
    db.session.commit()

    return redirect(url_for("applications"))



# ==========================================
# MY APPLICATIONS
# ==========================================


@app.route("/applications")
@login_required
def applications():
    if current_user.role != "STUDENT":
        return "Unauthorized: Student access required", 403

    student = Student.query.filter_by(
        user_id=current_user.id
    ).first()

    applications_list = []

    if student is not None:
        records = Application.query.filter_by(
            student_id=student.id
        ).order_by(
            Application.applied_at.desc()
        ).all()

        for application in records:
            job = db.session.get(Job, application.job_id)

            applications_list.append({
                "application": application,
                "job": job,
            })

    return render_template(
        "applications.html",
        applications=applications_list,
    )



# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)