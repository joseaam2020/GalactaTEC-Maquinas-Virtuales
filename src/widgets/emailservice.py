import re
import random
import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def is_valid_email(email: str) -> bool:
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None

def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def send_verification_code(to_email: str) -> int | None:
    if not is_valid_email(to_email):
        print("Correo inválido")
        return None

    try:
        code = random.randint(100000, 999999)
        message = MIMEText(f"Tu código es: {code}", "plain")
        message['to'] = to_email
        message['from'] = "tecgalacta@gmail.com"
        message['subject'] = "Codigo Verificacion Galacta TEC"
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw_message}
        service = gmail_authenticate()
        service.users().messages().send(userId='me', body=message_body).execute()
        print("Correo enviado con OAuth2")
        return code
    except Exception as e:
        print("Error al enviar:", e)
        return None