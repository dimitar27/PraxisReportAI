from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session, joinedload
from app.db import get_db
from app.models.medical_report import MedicalReport
from app.models.patient import Patient
from app.models.user import User
from app.schemas.medical_report import MedicalReportCreate, MedicalReportUpdate, MedicalReportOut
from app.core.security import get_current_user, require_doctor_or_admin
from app.utils.openai_client import generate_medical_report
from fastapi.responses import FileResponse
from app.utils.pdf_generator import generate_pdf
from app.models.profile import Profile
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import re


router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = os.path.abspath(BASE_DIR / "static")

env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

def format_report_sections(text: str) -> str:
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
    patient = db.query(Patient).filter_by(id=patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get historical reports if any
    previous_reports = [
        r.final_report for r in patient.reports
        if r.final_report
    ]

    # Call OpenAI to generate the final report
    final_report = generate_medical_report(
        title=report_data.title,
        history=report_data.patient_history,
        exam=report_data.physical_exam,
        gender=patient.gender,
        allergies=patient.allergies or "",
        pre_dx=patient.pre_diagnosis or "",
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
    return db.query(MedicalReport).filter_by(patient_id=patient_id).all()

@router.get("/reports/{report_id}", response_model=MedicalReportOut)
def get_report_by_id(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    report = db.query(MedicalReport).filter_by(id=report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

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
    report = (
        db.query(MedicalReport)
        .options(
            joinedload(MedicalReport.patient).joinedload(Patient.profile),
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
        raise HTTPException(status_code=400, detail="Missing patient, profile, or doctor info")

    doctor_user = patient.doctor
    profile = doctor_user.profile
    if not profile or not profile.addresses:
        raise HTTPException(status_code=400, detail="Doctor's address missing")

    address = profile.addresses[0]

    formatted_report = format_report_sections(report.final_report)

    #Prepare logo path before rendering
    logo_file = os.path.join(STATIC_DIR, "logo.png")
    logo_path = f"file://{logo_file}" if os.path.exists(logo_file) else None

    template = env.get_template("report_template.html")
    rendered_html = template.render(
        practice_name=doctor_user.practice_name or "Praxis",
        specialization=doctor_user.specialization or "Facharzt",
        phone=profile.phone_number,
        email=profile.email,
        street=address.street,
        postal_code=address.postal_code,
        city=address.city,
        logo_path=logo_path,

        date=datetime.now().strftime("%d. %B %Y"),

        patient_name=f"{patient.profile.first_name} {patient.profile.last_name}",
        birth_date=patient.date_of_birth.strftime("%d.%m.%Y"),
        patient_gender=patient.gender.capitalize(),
        gendered_prefix="Herr" if patient.gender.lower() == "männlich" else "Frau",

        allergies=patient.allergies,
        pre_dx=patient.pre_diagnosis,
        current_dx=patient.current_diagnosis,
        history=report.patient_history,
        exam=report.physical_exam,
        final_report=formatted_report,

        doctor_name=f"{profile.first_name} {profile.last_name}",
        doctor_title=doctor_user.title
    )

    pdf = HTML(string=rendered_html).write_pdf()

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="arztbrief_{report_id}.pdf"'
        }
    )


