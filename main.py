# Import des bibliothèques nécessaires
from flask import Flask, render_template, request, redirect, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename
from keras.models import load_model, Model
from keras.applications.vgg19 import VGG19
from keras.utils import load_img
from keras.utils import img_to_array
from keras.applications.vgg19 import preprocess_input
from keras.utils import pad_sequences
from numpy import argmax
from joblib import load
import numpy as np

import base64
import os

app = Flask(__name__)

# Définir les extensions de fichier autorisées
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Créer une instance de l'application Flask
app = Flask(__name__)

# Chemin vers le dossier de stockage des images
UPLOAD_FOLDER = os.path.join('static','uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
      

        # Rediriger vers la page de visualisation de l'annotation
        return redirect(url_for('view_annotation', filename=filename))
    return render_template('annotate.html', filename=filename)


# chargement du model VGG19
model = load_model('VGG19-model-ep004.h5')
# load the tokenizer
tokenizer = load(open('tokenizer.joblib', 'rb'))
#path = os.path.join(app.config['UPLOAD_FOLDER'])

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
    
    # load the tokenizer
    tokenizer = load(open('tokenizer.joblib', 'rb'))
    # pre-define the max sequence length (from training)
    max_length = 30
    # load the model
    model = load_model('VGG19-model-ep004.h5')
    # load and prepare the photograph
    photo = extract_features(path)
    # generate description
    description = generate_desc(model, tokenizer, photo, max_length)

    description =  description.replace("startseq ", "").replace(" endseq", "")

    return render_template('view_annotation.html', img_path=img_data, desc=description)


# Définir la route pour la page d'aide
@app.route('/help')
def help():
    return render_template('help.html')

# Vérifier si l'extension du fichier est autorisée
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

##################################################################

# extract features from each photo in the directory
def extract_features(filename):
    # load the model
    model = VGG19()
     # re-structure the model
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    # load the photo
    image = load_img(filename, target_size=(224, 224))
    # convert the image pixels to a numpy array
    image = img_to_array(image)
    # reshape data for the model
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    # prepare the image for the VGG model
    image = preprocess_input(image)
    # get features
    feature = model.predict(image, verbose=0)
    return feature

# map an integer to a word
def word_for_id(integer, tokenizer):
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None

# generate a description for an image
def generate_desc(model, tokenizer, photo, max_length):
    # seed the generation process
    in_text = 'startseq'
    # iterate over the whole length of the sequence
    for i in range(max_length):
        # integer encode input sequence
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        # pad input
        sequence = pad_sequences([sequence], maxlen=max_length)
        # predict next word
        yhat = model.predict([photo,sequence], verbose=0)
        # convert probability to integer
        yhat = argmax(yhat)
        # map integer to word
        word = word_for_id(yhat, tokenizer)
        # stop if we cannot map the word
        if word is None:
            break
        # append as input for generating the next word
        in_text += ' ' + word
        # stop if we predict the end of the sequence
        if word == 'endseq':
            break
    return in_text




# Démarrage de l'application Flask
if __name__ == '__main__':
    app.run(debug=True)

