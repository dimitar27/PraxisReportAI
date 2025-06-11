import os

from dotenv import load_dotenv
from openai import OpenAI
import re

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
        previous_reports: list[str] = None
) -> str:
    """
    Generate a structured medical report in professional German using OpenAI.

    Args:
        title (str): Report title (not included in output).
        history (str): Patient history (Anamnese).
        exam (str): Physical examination results.
        gender (str, optional): Patient gender to guide phrasing.
        allergies (str, optional): Known allergies.
        past_illnesses (str, optional): past medical conditions.
        current_dx (str, optional): Current diagnoses.
        notes (str, optional): Additional notes.
        previous_reports (list[str], optional): Past reports to use as context.

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
        "- ICD-10: (Diagnose-Code)",
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
            "Zur besseren Einschätzung erhältst du zusätzliche Kontextinformationen, "
            "die **nicht direkt im Bericht erscheinen sollen**:\n\n" +
            "\n\n".join(context_parts)
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
                    "Füge keine rechtlichen Hinweise oder allgemeinen Disclaimer am Ende des Berichts hinzu."
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
        diagnosis["icd"] = icd_match.group(1).strip()
    if gva_match:
        diagnosis["gva"] = gva_match.group(1).strip()
    if z_match:
        diagnosis["z"] = z_match.group(1).strip()

    return diagnosis
