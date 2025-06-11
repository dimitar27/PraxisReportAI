from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from datetime import datetime
import os
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from app.db import get_db
from app.models.medical_report import MedicalReport
from app.models.patient import Patient
from app.models.profile import Profile
from app.models.user import User
from app.schemas.medical_report import (
    MedicalReportCreate,
    MedicalReportUpdate,
    MedicalReportOut,
)
from app.core.security import get_current_user, require_doctor_or_admin
from app.utils.openai_client import generate_medical_report

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = os.path.abspath(BASE_DIR / "static")

env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

def format_report_sections(text: str) -> str:
    """
    Converts markdown-like **section** formatting into HTML
    and replaces newlines with <br>.
    """
    if not text:
        return ""

    # Convert **Section:** to <p><strong>Section:</strong></p>
    formatted = re.sub(r"\*\*(.+?):\*\*", r"<strong>\1:</strong>", text)

    # Convert remaining newlines into <br> for HTML formatting
    formatted = formatted.replace("\n\n", "<br><br>")
    formatted = formatted.replace("\n", "<br>")

    return formatted.strip()


@router.post("/patients/{patient_id}/reports", response_model=MedicalReportOut, status_code=201)
def create_report(
    patient_id: int,
    report_data: MedicalReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and store a medical report for a given patient using OpenAI.

    - Retrieves previous reports for context.
    - Calls AI to generate a new final report.
    - Saves the complete report to the database.
    """
    patient = db.query(Patient).filter_by(id=patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get previous reports (if any) to provide context
    # for generating the new medical report
    previous_reports = []
    for report in patient.reports:
        if report.final_report:
            previous_reports.append(report.final_report)

    # Call OpenAI to generate the final report
    final_report = generate_medical_report(
        title=report_data.title,
        history=report_data.patient_history,
        exam=report_data.physical_exam,
        gender=patient.gender,
        allergies=patient.allergies or "",
        past_illnesses=patient.past_illnesses or "",
        current_dx=patient.current_diagnosis or "",
        notes=patient.notes or "",
        previous_reports=previous_reports
    )

    # Save to DB
    report = MedicalReport(
        patient_id=patient_id,
        title=report_data.title,
        patient_history=report_data.patient_history,
        physical_exam=report_data.physical_exam,
        final_report=final_report
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/patients/{patient_id}/reports", response_model=list[MedicalReportOut])
def list_reports_for_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all medical reports for a given patient.
    Accessible to all authenticated users.
    """
    return db.query(MedicalReport).filter_by(patient_id=patient_id).all()

@router.get("/reports/{report_id}", response_model=MedicalReportOut)
def get_report_by_id(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific medical report by its ID.
    Accessible to all authenticated users.
    """
    report = db.query(MedicalReport).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.patch("/reports/{report_id}", response_model=MedicalReportOut)
def update_report(
    report_id: int,
    updates: MedicalReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Update a medical report by its ID.
    Only accessible to doctors and administrators.
    """
    report = db.query(MedicalReport).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # update only the fields that were provided in the request
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)
    return report


@router.delete("/reports/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    """
    Delete a specific medical report by ID.
    Accessible to doctors and admins only.
    """
    report = db.query(MedicalReport).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()
    return {"message": f"Report {report_id} deleted"}


@router.get("/reports/{report_id}/pdf")
def generate_report_pdf(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and return a PDF version of a medical report.

    - Retrieves the medical report, patient, and doctor data.
    - Loads and fills an HTML template with the relevant information.
    - Converts the rendered HTML to a PDF and returns it as a downloadable file.

    Accessible to all authenticated users.
    """
    # Load report with related patient and doctor data
    # (including their profiles and addresses)
    report = (
        db.query(MedicalReport)
        .options(
            joinedload(MedicalReport.patient)
            .joinedload(Patient.profile)
            .joinedload(Profile.addresses),
            joinedload(MedicalReport.patient)
            .joinedload(Patient.doctor)
            .joinedload(User.profile)
            .joinedload(Profile.addresses)
        )
        .filter(MedicalReport.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    patient = report.patient
    if not patient or not patient.profile or not patient.doctor:
        raise HTTPException(status_code=400,
                            detail="Missing patient, profile, or doctor info"
        )

    doctor_user = patient.doctor
    doctor_profile = doctor_user.profile
    if not doctor_profile or not doctor_profile.addresses:
        raise HTTPException(status_code=400, detail="Doctor's address missing")
    # Use the first address associated with the doctor
    doctor_address = doctor_profile.addresses[0]

    patient_profile = patient.profile
    patient_address = patient_profile.addresses[0] if patient_profile and patient_profile.addresses else None

    # Convert formatted sections (like **Diagnosis**) into styled HTML
    formatted_report = format_report_sections(report.final_report)

    #Prepare logo path before rendering
    logo_file = os.path.join(STATIC_DIR, "logo.png")
    logo_path = f"file://{logo_file}" if os.path.exists(logo_file) else None

    # Load the HTML template
    # and populate it with report, patient, and doctor data
    template = env.get_template("report_template.html")
    rendered_html = template.render(
        # Doctor Info
        practice_name=doctor_user.practice_name or "Praxis",
        specialization=doctor_user.specialization or "Facharzt",
        phone=doctor_profile.phone_number,
        email=doctor_profile.email,
        street=doctor_address.street,
        postal_code=doctor_address.postal_code,
        city=doctor_address.city,
        logo_path=logo_path,

        # Patient info
        patient_name=f"{patient_profile.first_name} {patient_profile.last_name}",
        birth_date=patient.date_of_birth.strftime("%d.%m.%Y"),
        patient_gender=patient.gender.capitalize(),
        gendered_prefix="Herr" if patient.gender.lower() == "männlich" else "Frau",

        patient_street=patient_address.street if patient_address else "",
        patient_postal_code=patient_address.postal_code if patient_address else "",
        patient_city=patient_address.city if patient_address else "",
        patient_country=patient_address.country if patient_address else "",

        # Report content
        date=datetime.now().strftime("%d. %B %Y"),
        allergies=patient.allergies,
        past_illnesses=patient.past_illnesses,
        current_dx=patient.current_diagnosis,
        history=report.patient_history,
        exam=report.physical_exam,
        final_report=formatted_report,
        report_main_heading=report.title,

        doctor_name=f"{doctor_profile.first_name} {doctor_profile.last_name}",
        doctor_title=doctor_user.title
    )

    # Generate PDF from rendered HTML
    pdf = HTML(string=rendered_html).write_pdf()

    filename = f'attachment; filename="arztbrief_{report_id}.pdf"'

    # Return the PDF as a downloadable HTTP response
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": filename}
    )

