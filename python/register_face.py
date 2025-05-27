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

@app.route('/register', methods=['POST'])
def register_face():
    data = request.json
    name = data.get('name')
    image_data = data.get('image')

    if not name or not image_data:
        logging.error('Missing name or image data')
        return jsonify({'message': 'Missing name or image data'}), 400

    try:
        # Decode the base64 image
        image = decode_base64_image(image_data)

        # Get face encodings
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            logging.error('No face detected in the image')
            return jsonify({'message': 'No face detected in the image'}), 400

        encoding = encodings[0]

        # Store in database
        conn = sqlite3.connect('faces.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO faces (name, encoding, timestamp) VALUES (?, ?, datetime("now"))',
                       (name, encoding.tobytes()))
        conn.commit()
        conn.close()

        logging.info(f'Face registered successfully: {name}')
        return jsonify({'message': 'Face registered successfully'})
    except Exception as e:
        logging.error(f'Error registering face: {str(e)}')
        return jsonify({'message': 'Error registering face'}), 500

if __name__ == '__main__':
    app.run(port=5000)