from flask import Flask, render_template, request, flash, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret_key_for_development')

# Configuration SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get('GMAIL_USER')
EMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Récupération des données du formulaire
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        # Validation des champs
        if not all([name, email, subject, message]):
            flash('Tous les champs sont obligatoires', 'danger')
            return redirect(url_for('contact'))

        # Construction de l'email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = f"Nouveau message de contact: {subject}"
        
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
            
        except smtplib.SMTPException as e:
            app.logger.error(f"Erreur SMTP: {str(e)}")
            flash("Une erreur s'est produite lors de l'envoi du message. Veuillez réessayer plus tard.", 'danger')
            return redirect(url_for('contact'))
        except Exception as e:
            app.logger.error(f"Erreur inattendue: {str(e)}")
            flash("Une erreur inattendue s'est produite. Veuillez réessayer plus tard.", 'danger')
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
