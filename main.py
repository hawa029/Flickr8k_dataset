# Import des bibliothèques nécessaires
from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename
from  config import * 
from utils import *
from keras.models import load_model
import base64
import os

app = Flask(__name__)


# Définir la route pour la page d'accueil
@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        # Vérifier si un fichier a été soumis
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Vérifier si le fichier a un nom valide
        if file.filename == '':
            return redirect(request.url)
        # Vérifier si l'extension du fichier est valide
        if not allowed_file(file.filename):
            return redirect(request.url)
        # Enregistrer le fichier et rediriger vers la page d'annotation
    return render_template('home.html')

# Définir la route pour la page de chargement de l'image
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Vérifier si un fichier a été soumis
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Vérifier si le fichier a un nom valide
        if file.filename == '':
            return redirect(request.url)
        # Vérifier si l'extension du fichier est valide
        if not allowed_file(file.filename):
            return redirect(request.url)
        # Enregistrer le fichier et rediriger vers la page d'annotation
    
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return render_template('upload.html', filename=file.filename)

@app.route('/<path:filename>')
def send_file(filename):
      return send_from_directory('./static/uploads', filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_image(filename):
    # supprimer l'image
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # rediriger vers la page d'accueil
    return redirect(url_for('home'))

# Définir la route pour la page d'annotation de l'image
@app.route('/annotate/<filename>', methods=['GET', 'POST'])
def annotate(filename):
    if request.method == 'POST':
        # Traiter l'image avec le modèle de prédiction
        model = load_model('VGG19-model-ep004.h5')

        # Rediriger vers la page de visualisation de l'annotation
        return redirect(url_for('view_annotation', filename=filename))
    return render_template('annotate.html', filename=filename)

# Définir la route pour la visualisation de l'image annotée
@app.route('/view_annotation/<filename>', methods=['GET'])
def view_annotation(filename):

    # Récuperer le chemin de l'image
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Lecture de l'image binaire depuis le fichier
    with open(path, 'rb') as f:
        img_bytes = f.read()

    # Conversion du binaire en string
    img_data = base64.b64encode(img_bytes).decode()
    prediction = 'une description possible'

    return render_template('view_annotation.html', img_path=img_data, desc=prediction)


# Définir la route pour la page d'aide
@app.route('/help')
def help():
    return render_template('help.html')

# Vérifier si l'extension du fichier est autorisée
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Démarrer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)

