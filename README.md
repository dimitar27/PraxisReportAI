# PraxisReportAI

**PraxisReportAI** is a medical web application designed for small medical practices, specifically tailored for German-speaking neurologists. The app provides tools to manage patient data and streamline the creation of medical reports using AI assistance.

---

## 🧠 Project Concept

This project was inspired by a real-world use case from a practicing neurologist. The goal is to reduce the administrative burden of report writing through automation while maintaining high standards of professionalism and accuracy.

The app allows:
- Secure login for doctors
- Patient registration and management
- Creation and viewing of medical reports
- AI-assisted generation of reports based on:
  - Patient History
  - Physical Examination
- PDF export of finalized reports
- Full support in German, with future plans for English translation

---

## ⚙️ Features

- **Authentication:** Secure doctor login using JWT
- **Database:** PostgreSQL with SQLAlchemy ORM for managing users, patients, and reports
- **REST API:** Built with FastAPI, includes CRUD operations
- **AI Integration:** Uses OpenAI to generate medical reports from structured input
- **PDF Export:** Reports are styled and exported using WeasyPrint
- **Data Validation:** Strong input validation using Pydantic schemas
- **Role Management:** Admin, Doctor, Assistant roles with appropriate access control
- **Report Customization:** Doctors can edit AI-generated reports before saving

---

## 🛠️ Tech Stack

- **Back-end:** Python, FastAPI
- **Database:** PostgreSQL, SQLAlchemy
- **PDF Generation:** WeasyPrint
- **AI:** OpenAI API
- **Templating:** Jinja2
- **Authentication:** JWT (OAuth2PasswordBearer)
- **Environment Config:** dotenv

---

## 📂 Project Structure

```
PraxisReportAI/
├── .venv/                         # Python virtual environment
├── alembic/                       # Alembic database migration tools
├── app/
│   ├── api/
│   │   └── routes/                # API Endpoints
│   │       ├── auth.py            # Authentication routes (e.g., login)
│   │       ├── patients.py        # Patient management routes (CRUD)
│   │       ├── reports.py         # Medical report routes (CRUD, AI integration, PDF generation)
│   │       └── users.py           # User management routes
│   ├── core/
│   │   └── security.py            # Security utilities (password hashing, JWT handling)
│   ├── models/                    # SQLAlchemy ORM database models
│   │   ├── __init__.py            # Initializes models module
│   │   ├── address.py             # Address model
│   │   ├── base.py                # Base for SQLAlchemy models and TimestampMixin
│   │   ├── medical_report.py      # MedicalReport model
│   │   ├── patient.py             # Patient model
│   │   ├── profile.py             # User and Patient profile details
│   │   └── user.py                # User account model (doctor, assistant, admin)
│   ├── schemas/                   # Pydantic schemas for data validation and serialization
│   │   ├── address.py             # Address schemas
│   │   ├── medical_report.py      # Medical report schemas
│   │   ├── patient.py             # Patient schemas
│   │   └── user.py                # User schemas
│   ├── static/                    # Static files (e.g., images for templates)
│   │   └── logo.png               # Practice logo
│   ├── templates/                 # HTML templates for PDF generation
│   │   └── report_template.html   # Template for medical reports PDF
│   ├── utils/                     # Utility functions and services
│   │   ├── openai_client.py       # OpenAI API interaction logic
│   │   └── pdf_generator.py       # PDF generation logic (using WeasyPrint)
│   ├── db.py                      # Database connection and session management
│   └── main.py                    # Main FastAPI application entry point
├── tests/                         # Test files
├── .env                           # Environment variables (e.g., DB URL, OpenAI API Key)
├── .gitignore                     # Files/directories to be ignored by Git
└── alembic.ini                    # Alembic configuration file
```

---

## 🚀 Setup and Installation

To run the project locally, follow these steps:

### 1. Clone the Repository

```bash
git clone https://github.com/dimitar27/PraxisReportAI.git
cd PraxisReportAI
```

### 2. Set up Virtual Environment

It is highly recommended to use a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

Install all required Python packages. If you don’t have a `requirements.txt`, generate one with:

```bash
pip freeze > requirements.txt
```

Example requirements.txt:

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-jose[cryptography]
passlib[bcrypt]
python-dotenv
openai
weasyprint
jinja2
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory with the following:

```
DATABASE_URL="postgresql+psycopg2://user:password@localhost/praxisreportai_db"
OPENAI_API_KEY="your_openai_api_key_here"
SECRET_KEY="a_very_secret_and_long_key_for_jwt_signing"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Database Migrations

Use Alembic to initialize and upgrade the database:

```bash
# First time
alembic stamp head

# Then:
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

App available at: http://127.0.0.1:8000  
Swagger Docs: http://127.0.0.1:8000/docs

---
