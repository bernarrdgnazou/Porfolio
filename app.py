from flask import Flask, render_template, request, flash, redirect, url_for, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from datetime import datetime

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key_for_development')

# Configuration SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get('GMAIL_USER')
EMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')

# Dictionnaire de traductions
TRANSLATIONS = {
    'en': {
        'home': 'Home',
        'about': 'About',
        'projects': 'Projects',
        'services': 'Services',
        'contact': 'Contact',
        'fields_required': 'All fields are required',
        'send_success': 'Message sent successfully!',
        'send_error': 'Error sending message'
    },
    'fr': {
        'home': 'Accueil',
        'about': 'À propos',
        'projects': 'Projets',
        'services': 'Services',
        'contact': 'Contact',
        'fields_required': 'Tous les champs sont obligatoires',
        'send_success': 'Message envoyé avec succès!',
        'send_error': "Erreur lors de l'envoi du message"
    }
}

@app.context_processor
def inject_global_vars():
    lang = session.get('lang', 'en')
    return {
        'now': datetime.utcnow(),
        'lang': lang,
        't': TRANSLATIONS[lang],  # t.home, t.about, etc.
        'current_endpoint': request.endpoint,
        'is_active': lambda endpoint: 'active' if request.endpoint == endpoint else ''
    }

def get_active_lang():
    return session.get('lang', 'en')

@app.route('/')
def portal():
    return render_template('portal.html')

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['fr', 'en']:
        session['lang'] = lang
    return redirect(url_for('home'))

@app.route('/home')
def home():
    lang = get_active_lang()
    return redirect(url_for(f'{lang}_home'))

def render_lang_template(template_name, lang):
    return render_template(f'{lang}/{template_name}', lang=lang)

# Routes françaises
@app.route('/fr/')
def fr_home():
    return render_lang_template('index.html', 'fr')

@app.route('/fr/about')
def fr_about():
    return render_lang_template('about.html', 'fr')

@app.route('/fr/projects')
def fr_projects():
    return render_lang_template('projects.html', 'fr')

@app.route('/fr/services')
def fr_services():
    return render_lang_template('services.html', 'fr')

@app.route('/fr/contact', methods=['GET', 'POST'])
def fr_contact():
    if request.method == 'POST':
        return handle_contact_form('fr')
    return render_lang_template('contact.html', 'fr')

# Routes anglaises
@app.route('/en/')
def en_home():
    return render_lang_template('index.html', 'en')

@app.route('/en/about')
def en_about():
    return render_lang_template('about.html', 'en')

@app.route('/en/projects')
def en_projects():
    return render_lang_template('projects.html', 'en')

@app.route('/en/services')
def en_services():
    return render_lang_template('services.html', 'en')

@app.route('/en/contact', methods=['GET', 'POST'])
def en_contact():
    if request.method == 'POST':
        return handle_contact_form('en')
    return render_lang_template('contact.html', 'en')

def handle_contact_form(lang):
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()

    if not all([name, email, subject, message]):
        flash(TRANSLATIONS[lang]['fields_required'], 'danger')
        return redirect(url_for(f'{lang}_contact'))

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    
    if lang == 'fr':
        msg['Subject'] = f"Nouveau message de contact: {subject}"
        email_body = f"""Nom: {name}
Email: {email}
Sujet: {subject}

Message:
{message}"""
    else:
        msg['Subject'] = f"New contact message: {subject}"
        email_body = f"""Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}"""

    if send_email(msg, email_body):
        flash(TRANSLATIONS[lang]['send_success'], 'success')
    else:
        flash(TRANSLATIONS[lang]['send_error'], 'danger')
    
    return redirect(url_for(f'{lang}_contact'))

def send_email(msg, body):
    try:
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        app.logger.error(f"Email error: {str(e)}")
        return False

if __name__ == '__main__':
    app.run(debug=True)