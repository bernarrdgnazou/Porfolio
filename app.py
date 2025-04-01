from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)
app.secret_key = 'ton_secret_key_ici'  # Nécessaire pour les messages flash

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get('GMAIL_USER')
EMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')
RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Vérification reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        recaptcha_data = {
            'secret': RECAPTCHA_SECRET,
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=recaptcha_data)
        result = r.json()
        
        if not result.get('success'):
            flash('Veuillez compléter le CAPTCHA correctement', 'danger')
            return redirect(url_for('contact'))

        # Récupération des données
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        # Validation supplémentaire
        if not all([name, email, subject, message]):
            flash('Tous les champs sont obligatoires', 'danger')
            return redirect(url_for('contact'))

        # Construction de l'email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = f"New Contact: {subject}"
        
        email_body = f"""
        Nom: {name}
        Email: {email}
        Sujet: {subject}
        
        Message:
        {message}
        """
        msg.attach(MIMEText(email_body, 'plain'))

        # Envoi de l'email
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            
            flash('Votre message a été envoyé avec succès! Je vous répondrai dès que possible.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            flash(f"Une erreur s'est produite lors de l'envoi: {str(e)}", 'danger')
            return redirect(url_for('contact'))

    return render_template('contact.html')


# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('index.html')


# Route pour la page À propos
@app.route('/about')
def about():
    return render_template('about.html')


# Route pour la page Projets
@app.route('/projects')
def projects():
    return render_template('projects.html')


# Route pour la page Services
@app.route('/services')
def services():
    return render_template('services.html')




# Lancer l'application
if __name__ == '__main__':
    app.run(debug=False)
