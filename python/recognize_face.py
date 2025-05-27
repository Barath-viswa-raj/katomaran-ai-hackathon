from flask import Flask, request, jsonify
import sqlite3
import face_recognition
import numpy as np
import logging
import base64
import cv2
from io import BytesIO

app = Flask(__name__)

logging.basicConfig(filename='logs/python.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def decode_base64_image(image_data):
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

@app.route('/recognize', methods=['POST'])
def recognize_face():
    data = request.json
    image_data = data.get('image')

    if not image_data:
        logging.error('Missing image data')
        return jsonify({'message': 'Missing image data'}), 400

    try:
        # Decode the base64 image
        image = decode_base64_image(image_data)

        # Get face encodings
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            logging.info('No faces found in the image')
            return jsonify({'name': None})

        encoding = encodings[0]

        # Load known faces from database
        conn = sqlite3.connect('faces.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name, encoding FROM faces')
        known_faces = cursor.fetchall()
        conn.close()

        # Compare with known faces
        for name, known_encoding in known_faces:
            known_encoding = np.frombuffer(known_encoding, dtype=np.float64)
            match = face_recognition.compare_faces([known_encoding], encoding, tolerance=0.6)
            if match[0]:
                logging.info(f'Face recognized: {name}')
                return jsonify({'name': name})

        logging.info('No matching face found')
        return jsonify({'name': None})
    except Exception as e:
        logging.error(f'Error recognizing face: {str(e)}')
        return jsonify({'message': 'Error recognizing face'}), 500

if __name__ == '__main__':
    app.run(port=5001)