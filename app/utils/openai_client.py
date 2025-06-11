import os

from dotenv import load_dotenv
from openai import OpenAI
import re
from datetime import date

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_medical_report(
        title: str,
        history: str,
        exam: str,
        gender: str = "",  # "weiblich" or "männlich"
        allergies: str = "",
        past_illnesses: str = "",
        current_dx: str = "",
        notes: str = "",
        previous_reports: list[str] = None,
        patient_dob: date = None
) -> str:
    """
    Generate a structured medical report in professional German using OpenAI.

    Args:
        title (str): Report title (not included in output).
        history (str): Patient history (Anamnese).
        exam (str): Physical examination results (Körperliche Untersuchung).
        gender (str, optional): Patient gender to guide phrasing.
        allergies (str, optional): Known allergies.
        past_illnesses (str, optional): past medical conditions.
        current_dx (str, optional): Current diagnoses.
        notes (str, optional): Additional notes.
        previous_reports (list[str], optional): Past reports to use as context.
        patient_dob (date, optional): Date of birth to calculate and include patient’s age.

    Returns:
        str: Generated medical report in German.
    """
    # Determine gender-specific wording
    is_female = gender.lower() == "weiblich"
    patient_term = "die Patientin" if is_female else "der Patient"

    # Base instruction
    sections = [
        "Du bist ein erfahrener Neurologe. Erstelle einen strukturierten medizinischen Bericht "
        "in professionellem Deutsch auf Basis folgender Informationen.",
        # Uncomment this line to generate in English for demo purposes
        # "Please create the report in English.",
        f"Der Titel des Berichts lautet: {title.strip()}, aber verwende ihn bitte **nicht** im Text.",
        #"Verwende folgende Abschnitte und **fülle sie sehr ausführlich aus**:",
        "Verwende folgende Abschnitte:",
        "**Zusammenfassung:**",
        "Enthält eine kurze fachliche Zusammenfassung der Anamnese und Befunde.",
        "Schließe am Ende der Zusammenfassung eine strukturierte Diagnose mit folgenden Punkten ein:",
        "- ICD-10: (Diagnose-Code und Bezeichnung, z. B. G45.9 – Transitorische zerebrale Ischämie)",
        "- GVA: (Was ausgeschlossen wurde)",
        "- Z: (Zustand nach ...)",
        "**Therapie:**",
        "Beschreibe die durchgeführte oder empfohlene Therapie.",
        "**Empfohlene Medikation:**",
        "Liste Medikamente auf, inklusive Dosierung und Häufigkeit, wenn verfügbar.",
        f"Schreibe sachlich, klar und ohne Platzhalter wie Name, Datum oder Geschlecht.",
        f"Beziehe dich auf {patient_term} nur wenn nötig.",
        f"Anamnese:\n{history.strip()}",
        f"Körperliche Untersuchung:\n{exam.strip()}"
    ]

    context_parts = []
    if patient_dob:
        age = calculate_age(patient_dob)
        context_parts.append(f"Alter: {age} Jahre")
    if allergies:
        context_parts.append(f"Allergien:\n{allergies.strip()}")
    if past_illnesses:
        context_parts.append(f"Vorerkrankungen:\n{past_illnesses.strip()}")
    if current_dx:
        context_parts.append(f"Aktuelle Diagnose:\n{current_dx.strip()}")
    if notes:
        context_parts.append(f"Zusätzliche Notizen:\n{notes.strip()}")
    if previous_reports:
        joined = "\n\n--- Frühere Berichte ---\n\n" + "\n\n---\n\n".join(previous_reports)
        context_parts.append(joined)

    if context_parts:
        sections.append(
            "Die folgenden Informationen dienen **ausschließlich als Kontext**, "
            "um dir ein besseres medizinisches Gesamtbild zu vermitteln. "
            "Bitte **vermeide es, Textstellen direkt zu übernehmen**. "
            "Du darfst jedoch relevante Inhalte sinngemäß berücksichtigen, "
            "wenn sie für die Beurteilung medizinisch wichtig sind:\n\n"
            + "\n\n".join(context_parts)
        )

    # Final instruction
    sections.append("Erstelle jetzt den Abschlussbericht mit medizinischer Fachsprache.")

    # Combine into full prompt
    prompt = "\n\n".join(sections)

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "Du bist ein medizinischer Experte und erstellst präzise medizinische Berichte auf Deutsch. "
                    "Füge keine rechtlichen Hinweise oder allgemeinen Disclaimer am Ende des Berichts hinzu. "
                    "Vermeide am Ende des Berichts pauschale Empfehlungen wie 'regelmäßige Verlaufskontrollen' "
                    "oder allgemeine Formulierungen, es sei denn, sie ergeben sich konkret aus den vorliegenden Befunden."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.6,
        max_tokens=3000
    )

    return response.choices[0].message.content.strip()


def extract_diagnosis_block(final_report: str) -> dict:
    """
    Extracts ICD-10, GVA, and Z lines from the AI-generated report.

    Returns:
        dict: {
            "icd": "...",
            "gva": "...",
            "z": "..."
        }
    """
    diagnosis = {
        "icd": "",
        "gva": "",
        "z": ""
    }

    icd_match = re.search(r"[-–•]?\s*ICD-10:\s*(.+)", final_report)
    gva_match = re.search(r"[-–•]?\s*GVA:\s*(.+)", final_report)
    z_match = re.search(r"[-–•]?\s*Z:\s*(.+)", final_report)

    if icd_match:
        diagnosis["icd"] = clean_markdown(icd_match.group(1))
    if gva_match:
        diagnosis["gva"] = clean_markdown(gva_match.group(1))
    if z_match:
        diagnosis["z"] = clean_markdown(z_match.group(1))

    return diagnosis


def clean_markdown(text: str) -> str:
    """
    Removes Markdown-style bold markers (**...**) from the given text.
    """
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text).strip()


def calculate_age(dob: date) -> int:
    """
    Calculate the current age of a person based on their date of birth.

    Args:
        dob (date): The person's date of birth.

    Returns:
        int: The person's age in full years.
    """
    # Get today’s date
    today = date.today()

    # Start with the difference in years
    age = today.year - dob.year

    # If the birthday hasn't happened yet this year, subtract 1
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age



