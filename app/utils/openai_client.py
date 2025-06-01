import os

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
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
    # Determine gender-specific wording
    patient_term = "die Patientin" if gender.lower() == "weiblich" else "der Patient"

    # Compose prompt sections
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

    # Optional fields
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

    # Join prompt
    prompt = "\n\n".join(sections)

    # Make the API call
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
        max_tokens=800
    )

    return response.choices[0].message.content.strip()
