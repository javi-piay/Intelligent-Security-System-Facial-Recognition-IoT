##
import cv2
import time
import tensorflow as tf
import numpy as np
from keras_facenet import FaceNet
import os
import logging
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
##
YOUR_CLIENT_ID = 'KZAxBVHc2Tse2wnK7SUeYYEVXAX9rFNA'
YOUR_CLIENT_SECRET = 'xQCcQ5bsrQTuXd3GWfcOOdcS67jUH7ZRwK7ZaGgMpgaLYRaI34eJUmaQelAO65F6'
oauth_client = BackendApplicationClient(client_id=YOUR_CLIENT_ID)
token_url = "https://api2.arduino.cc/iot/v1/clients/token"

oauth = OAuth2Session(client=oauth_client)
token = oauth.fetch_token(
    token_url=token_url,
    client_id=YOUR_CLIENT_ID,
    client_secret=YOUR_CLIENT_SECRET,
    include_client_id=True,
    audience="https://api2.arduino.cc/iot",
)

print(token.get("access_token"))

import iot_api_client as iot
from iot_api_client.rest import ApiException
from iot_api_client.configuration import Configuration

# configure and instance the API client
client_config = Configuration(host="https://api2.arduino.cc/iot")
client_config.access_token = token.get("access_token")
client = iot.ApiClient(client_config)

# as an example, interact with the devices API
devices_api = iot.DevicesV2Api(client)
things_api = iot.ThingsV2Api(client)
properties_api = iot.PropertiesV2Api(client)
# Your thing ID and property ID
THING_ID = '8dd73b08-b8dc-41db-90b3-f3a458036142'  # Replace with your thing ID
PROPERTY_ID = 'a39b54ac-f227-4841-b00f-63b5844703e8'  # Replace with your property ID

# Configurar Arduino IoT Cloud Client
def logging_func():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )

def renew_token_if_needed(oauth, token_url, client_id, client_secret):
    current_time = time.time()
    expires_at = oauth.token.get('expires_at', 0)

    # Renueva el token si está a punto de expirar (por ejemplo, en 60 segundos)
    if current_time >= expires_at - 20:
        new_token = oauth.fetch_token(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
            include_client_id=True,
            audience="https://api2.arduino.cc/iot",
        )
        oauth.token = new_token
        client_config.access_token = new_token.get("access_token")
        client = iot.ApiClient(client_config)
        return client
    return None



def send_face_data_to_cloud(value):
    global last_sent_time, MIN_TIME_INTERVAL

    current_time = time.time()

    # Verificar si ha pasado suficiente tiempo desde el último envío
    if current_time - last_sent_time >= MIN_TIME_INTERVAL:
        try:
            properties_api.properties_v2_publish(
                THING_ID,
                PROPERTY_ID,
                {"value": value}
            )
            print(f"Sent value '{value}' to Arduino IoT Cloud.")

            # Actualizar el tiempo del último envío
            last_sent_time = current_time

        except ApiException as e:
            print(f"Exception when sending data to Arduino IoT Cloud: {e}")



##

DIR_KNOWNS = r"C:\Users\javie\pythonOpenCV\TFM\CONOCIDOS"

#CARGAR IMAGEN
def load_image(DIR, NAME):
    return cv2.cvtColor(cv2.imread(f'{DIR}/{NAME}'), cv2.COLOR_BGR2RGB)


with tf.io.gfile.GFile(r'C:\Users\javie\pythonOpenCV\TFM\frozen_inference_graph_face.pb','rb') as f:
    graph_def = tf.compat.v1.GraphDef()
    graph_def.ParseFromString(f.read())

with tf.Graph().as_default() as mobilenet:
    tf.import_graph_def(graph_def,name='')

# Inicializar mobilenet
    sess = tf.compat.v1.Session(graph=mobilenet)
    image_tensor = mobilenet.get_tensor_by_name('image_tensor:0')
    boxes = mobilenet.get_tensor_by_name('detection_boxes:0')
    scores = mobilenet.get_tensor_by_name('detection_scores:0')

#DETECTAR CARAS
def detect_faces(image, sess, image_tensor, boxes, scores, score_threshold=0.85):
    #global boxes, scores
    (imh, imw) = image.shape[:-1]
    img = np.expand_dims(image, axis=0)

    # Predicción (detección)
    (boxes, scores) = sess.run([boxes, scores], feed_dict={image_tensor: img})

    # Reajustar tamaños boxes, scores
    boxes = np.squeeze(boxes, axis=0)
    scores = np.squeeze(scores, axis=0)

    # Depurar bounding boxes
    idx = np.where(scores >= score_threshold)[0]

    # Crear bounding boxes
    bboxes = []
    for index in idx:
        ymin, xmin, ymax, xmax = boxes[index, :]
        (left, right, top, bottom) = (xmin * imw, xmax * imw, ymin * imh, ymax * imh)
        left, right, top, bottom = int(left), int(right), int(top), int(bottom)
        bboxes.append([left, right, top, bottom])

    return bboxes

#DIBUJAR RECUADRO
def draw_box(image,box,color,line_width=6):
    if box==[]:
        return image
    else:
        cv2.rectangle(image,(box[0],box[2]),(box[1],box[3]),color,line_width)
    return image

#CARGAR FACENET
facenet = FaceNet()

#EXTRAER ROSTROS
def extract_faces(image,bboxes,new_size=(160,160)):
    cropped_faces = []
    for box in bboxes:
        left, right, top, bottom = box
        face = image[top:bottom,left:right]
        cropped_faces.append(cv2.resize(face,dsize=new_size))
    return cropped_faces
def compute_embeddings(model, faces):
    # Si solo se proporciona un rostro, convertirlo en una lista de un solo elemento
    if not isinstance(faces, list):
        faces = [faces]

    embeddings = []
    for face in faces:
        face = np.expand_dims(face, axis=0)  # Asegúrate de que sea una matriz de forma (1, alto, ancho, canales)
        signature = model.embeddings(face)
        embeddings.append(signature)

    # Si solo se proporcionó un rostro, devolver la incrustación en lugar de una lista
    if len(embeddings) == 1:
        embeddings = embeddings[0]

    return embeddings

known_faces = dict()
cont = 0
print('Procesando rostros conocidos...')
for label in os.listdir(DIR_KNOWNS):
    # Se crea una lista que será el valor de cada carpeta en el diccionario
    known_embeddings = []
    image_path = os.path.join(DIR_KNOWNS, label)
    cont = cont+1
    print('Procesando carpeta número '+str(cont)+'. Nombre:' + label)
    image_files = os.listdir(image_path)
    if not image_files:  # Verificar si la carpeta está vacía
        print(f'La carpeta {label} está vacía. Se omitirá.')
        continue
    for image_name in os.listdir(os.path.join(DIR_KNOWNS, label)):
        image = load_image(image_path,image_name)

        bboxes = detect_faces(image, sess, image_tensor, boxes, scores,score_threshold=0.85)

        # condicional para que se guarde solo si puedo identificar la imagen
        if bboxes != []:
            face = extract_faces(image,bboxes)

            known_embeddings.append(compute_embeddings(facenet,face[0]))
    known_faces[label] = known_embeddings

def compare_faces(embs_ref, emb_desc, umbral=1):
    Claves = embs_ref.keys()
    reconocimiento = []
    minimo = []
    nombre_reconocido =None
    for clave in Claves:
        persona = embs_ref[clave]
        distancias = []
        for i in persona:
            distancias.append(np.linalg.norm(i-emb_desc))

        distancias = np.array(distancias)
        if any(distancias<=umbral):
            reconocimiento.append(True)
            minimo.append(min(distancias))
            nombre_reconocido = clave
        else:
            reconocimiento.append(False)
            minimo.append(min(distancias))

    return nombre_reconocido, reconocimiento

def draw_text(image,text,box,line_width,color,grueso):
    if box==[]:
        return image
    else:
        cv2.putText(image,text,(box[0],box[2]-15),cv2.FONT_ITALIC,line_width,color,grueso)
    return image

##
 #Crear la ventana con un nombre específico y redimensionarla
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.resizeWindow('frame', 600, 480)  # Ajusta estos valores a las dimensiones deseadas

frame_interval = 5  # Capturar un frame de cada 4 frames

stream_url = 'rtsp://ghY01MEh:DKgcKDku5HPUXE71@192.168.66.46:554/live/ch0'

# Intentar abrir la conexión con la cámara IP
cap = cv2.VideoCapture(stream_url)
if not cap.isOpened():
    print("No se pudo conectar a la cámara IP")
else:
    print("Conexión exitosa a la cámara IP")

    last_sent_time = 0  # Tiempo del último envío
    MIN_TIME_INTERVAL = 20  # Intervalo mínimo de tiempo entre envíos (en segundos)
    frame_count = 0
    while True:
        ret,frame = cap.read()
        if not ret:
            print("No se pudo conectar a la cámara IP.")
            break
        frame_count += 1
        if frame_count % frame_interval != 0:
            continue  # Saltar este frame

        # Renovar el token si es necesario
        client = renew_token_if_needed(oauth, token_url, YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)


        img_with_boxes = frame.copy()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        bboxes = detect_faces(image, sess, image_tensor, boxes, scores)
        faces = extract_faces(image,bboxes)

        for face, box in zip(faces,bboxes):
                emb = compute_embeddings(facenet,face)
                nombre_reconocido, reconocimiento = compare_faces(known_faces,emb)

                if not any(reconocimiento):
                    img_with_boxes = draw_box(img_with_boxes,box,(0,0,255),5)
                    img_with_boxes = draw_text(img_with_boxes,"Desconocido",box,1,(0,0,255),2)
                    send_face_data_to_cloud("Desconocido")

                else:
                    img_with_boxes = draw_box(img_with_boxes,box,(0,255,0),5)
                    img_with_boxes = draw_text(img_with_boxes,nombre_reconocido,box,1,(0,255,0),2)
                    send_face_data_to_cloud(nombre_reconocido)

        cv2.imshow('frame',img_with_boxes)
        k = cv2.waitKey(1)
        if k == 27:
            break
cap.release()
cv2.destroyAllWindows()
