from flask import Flask
from main import *




# Définir les extensions de fichier autorisées
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Créer une instance de l'application Flask
app = Flask(__name__)

# Chemin vers le dossier de stockage des images
UPLOAD_FOLDER = os.path.join('static','uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
