from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.profile import Profile
from app.schemas.address import AddressOut
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate, PatientDetail, PatientWithDoctor, \
    DoctorSummary
from app.core.security import get_current_user
from app.models.address import Address

router = APIRouter()

@router.post("/users/{user_id}/patients", response_model=PatientDetail)
def create_patient(
    user_id: int,
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "doctor":
        assigned_doctor_id = current_user.id
    elif current_user.role in ["assistant", "admin"]:
        doctor = db.query(User).filter(User.id == user_id, User.role == "doctor").first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        assigned_doctor_id = user_id
    else:
        raise HTTPException(status_code=403, detail="Not authorized to register patients")

    if db.query(Profile).filter(Profile.email == patient_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    profile = Profile(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        email=patient_data.email,
        phone_number=patient_data.phone_number,
    )
    db.add(profile)
    db.flush()

    if patient_data.address:
        address = Address(
            profile_id=profile.id,
            street=patient_data.address.street,
            postal_code=patient_data.address.postal_code,
            city=patient_data.address.city,
            country=patient_data.address.country
        )
        db.add(address)

    patient = Patient(
        profile_id=profile.id,
        assigned_user_id=assigned_doctor_id,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        allergies=patient_data.allergies,
        pre_diagnosis=patient_data.pre_diagnosis,
        current_diagnosis=patient_data.current_diagnosis,
        notes=patient_data.notes,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    address_obj = profile.addresses[0] if profile.addresses else None

    return PatientDetail(
        id=patient.id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        email=profile.email,
        phone_number=profile.phone_number,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        allergies=patient.allergies,
        pre_diagnosis=patient.pre_diagnosis,
        current_diagnosis=patient.current_diagnosis,
        notes=patient.notes,
        address=AddressOut.model_validate(address_obj) if address_obj else None
    )


@router.get("/users/{user_id}/patients", response_model=list[PatientOut])
def list_patients_for_doctor(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    doctor = db.query(User).filter(User.id == user_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    patients = (
        db.query(Patient)
        .filter(Patient.assigned_user_id == user_id)
        .join(Profile)
        .all()
    )

    result = []
    for patient in patients:
        profile = patient.profile
        address = profile.addresses[0] if profile.addresses else None

        result.append(PatientOut(
            id=patient.id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            email=profile.email,
            phone_number=profile.phone_number,
            address=AddressOut.model_validate(address) if address else None
        ))

    return result


@router.patch("/users/{user_id}/patients/{patient_id}", response_model=PatientDetail)
def update_patient(
    user_id: int,
    patient_id: int,
    updates: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(Patient).filter_by(id=patient_id, assigned_user_id=user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if updates.assigned_user_id:
        new_doctor = db.query(User).filter(User.id == updates.assigned_user_id, User.role == "doctor").first()
        if not new_doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        patient.assigned_user_id = updates.assigned_user_id

    # Update profile fields
    for field in ["first_name", "last_name", "email", "phone_number"]:
        value = getattr(updates, field)
        if value is not None:
            setattr(patient.profile, field, value)

    # Update or create address
    if updates.address:
        address = patient.profile.addresses[0] if patient.profile.addresses else None
        if not address:
            address = Address(profile_id=patient.profile.id)
            db.add(address)

        for field, value in updates.address.dict(exclude_unset=True).items():
            setattr(address, field, value)

    # Update patient fields
    for field in ["date_of_birth", "gender", "allergies", "pre_diagnosis", "current_diagnosis", "notes"]:
        value = getattr(updates, field)
        if value is not None:
            setattr(patient, field, value)

    db.commit()
    db.refresh(patient)

    address_obj = patient.profile.addresses[0] if patient.profile.addresses else None

    return PatientDetail(
        id=patient.id,
        first_name=patient.profile.first_name,
        last_name=patient.profile.last_name,
        email=patient.profile.email,
        phone_number=patient.profile.phone_number,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        allergies=patient.allergies,
        pre_diagnosis=patient.pre_diagnosis,
        current_diagnosis=patient.current_diagnosis,
        notes=patient.notes,
        address=AddressOut.model_validate(address_obj) if address_obj else None
    )

@router.delete("/users/{user_id}/patients/{patient_id}")
def delete_patient(
    user_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(Patient).filter_by(id=patient_id, assigned_user_id=user_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    profile = patient.profile

    db.delete(patient)
    if profile:
        db.delete(profile)

    db.commit()
    return {"message": f"Patient {patient_id} and profile deleted"}

@router.get("/patients", response_model=list[PatientWithDoctor])
def get_all_patients_with_doctors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patients = db.query(Patient).all()
    results = []

    for patient in patients:
        profile = patient.profile
        address = profile.addresses[0] if profile.addresses else None
        doctor = patient.doctor

        results.append(
            PatientWithDoctor(
                id=patient.id,
                first_name=profile.first_name,
                last_name=profile.last_name,
                email=profile.email,
                phone_number=profile.phone_number,
                date_of_birth=patient.date_of_birth,
                gender=patient.gender,
                allergies=patient.allergies,
                pre_diagnosis=patient.pre_diagnosis,
                current_diagnosis=patient.current_diagnosis,
                notes=patient.notes,
                address=AddressOut.model_validate(address) if address else None,
                assigned_doctor=DoctorSummary(
                    id=doctor.id,
                    title=doctor.title,
                    first_name=doctor.profile.first_name,
                    last_name=doctor.profile.last_name,
                    email=doctor.profile.email
                )
            )
        )

    return results

