import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_medical_report(
    title: str,
    history: str,
    exam: str,
    allergies: str = "",
    pre_dx: str = "",
    current_dx: str = "",
    notes: str = "",
    previous_reports: list[str] = None
) -> str:
    prompt = (
        f"Du bist ein medizinischer Assistent. Erstelle einen professionellen, strukturierten medizinischen Bericht auf Deutsch.\n\n"
        f"Titel: {title}\n\n"
        f"Anamnese:\n{history}\n\n"
        f"Körperliche Untersuchung:\n{exam}\n\n"
    )

    if allergies:
        prompt += f"Allergien: {allergies}\n\n"
    if pre_dx:
        prompt += f"Vordiagnose: {pre_dx}\n\n"
    if current_dx:
        prompt += f"Aktuelle Diagnose: {current_dx}\n\n"
    if notes:
        prompt += f"Zusätzliche Notizen: {notes}\n\n"

    if previous_reports:
        joined_reports = "\n---\n".join(previous_reports)
        prompt += f"Frühere Berichte zur Information:\n{joined_reports}\n\n"

    prompt += "Erstelle auf Basis dieser Informationen einen vollständigen Abschlussbericht."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein medizinischer Assistent und erstellst professionelle medizinische Berichte auf Deutsch."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

    return response.choices[0].message["content"]