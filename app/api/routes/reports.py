from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.medical_report import MedicalReport
from app.models.patient import Patient
from app.models.user import User
from app.schemas.medical_report import MedicalReportCreate, MedicalReportUpdate, MedicalReportOut
from app.core.security import get_current_user, require_doctor_or_admin
from app.utils.openai_client import generate_medical_report

router = APIRouter()

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