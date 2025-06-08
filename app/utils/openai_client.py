import os

from dotenv import load_dotenv
from openai import OpenAI

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
        pre_dx: str = "",
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
        pre_dx (str, optional): Preliminary diagnoses.
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
        f"Der Titel des Berichts lautet: {title.strip()}, aber verwende ihn bitte **nicht** im Text.",
        "Verwende folgende Abschnitte:",
        "- Befund",
        "- Diagnose",
        "- Therapie",
        "- Empfehlungen",
        f"Schreibe sachlich, klar und ohne Platzhalter wie Name, Datum oder Geschlecht.",
        f"Beziehe dich auf {patient_term} nur wenn nötig.",
        f"Anamnese:\n{history.strip()}",
        f"Körperliche Untersuchung:\n{exam.strip()}"
    ]

    # Add optional fields
    if allergies:
        sections.append(f"Allergien:\n{allergies.strip()}")
    if pre_dx:
        sections.append(f"Vordiagnose:\n{pre_dx.strip()}")
    if current_dx:
        sections.append(f"Aktuelle Diagnose:\n{current_dx.strip()}")
    if notes:
        sections.append(f"Zusätzliche Notizen:\n{notes.strip()}")
    if previous_reports:
        joined = "\n\n--- Frühere Berichte ---\n\n" + "\n\n---\n\n".join(previous_reports)
        sections.append(joined)

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
        max_tokens=1800
    )

    return response.choices[0].message.content.strip()
