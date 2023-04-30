import tensorflow as tf
from PIL import Image, ImageDraw






# Charger le modèle
model = tf.keras.models.load_model('path/to/model.h5')

# Définir une fonction pour annoter une image
def annotate_image(image_path):
    # Charger l'image
    img = Image.open(image_path)
    
    # Prétraitement de l'image
    img = img.resize((224, 224))
    img = tf.keras.preprocessing.image.img_to_array(img)
    img = tf.keras.applications.mobilenet_v2.preprocess_input(img)
    img = tf.expand_dims(img, axis=0)
    
    # Faire une prédiction sur l'image
    pred = model.predict(img)
    
    # Récupérer la classe prédite
    class_idx = tf.argmax(pred, axis=1)[0]
    
    # Retourner la classe prédite (ici, on suppose qu'on a un dictionnaire qui associe les classes à des descriptions)
    return class_idx

# Définir une fonction pour enregistrer l'image avec la description
def save_annotated_image(image_path, description):
    # Charger l'image
    img = Image.open(image_path)
    
    # Dessiner la description sur l'image
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), description)
    
    # Enregistrer l'image
    img.save(image_path)
