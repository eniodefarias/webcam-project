from flask import Flask, render_template, Response, request, jsonify
import cv2

app = Flask(__name__)

# Inicia com a primeira câmera (índice 0)
camera_index = 0
video_capture = cv2.VideoCapture(camera_index)

def generate_frames():
    global video_capture
    while True:
        # Capture frame-by-frame
        success, frame = video_capture.read()
        if not success:
            break
        else:
            # Converta o frame para o formato JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            # Use o formato MJPEG para transmissão contínua
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/change_camera', methods=['POST'])
def change_camera():
    global camera_index, video_capture
    
    # Recebe o novo índice da câmera do frontend
    data = request.get_json()
    new_camera_index = data.get('camera_index')
    
    # Atualiza o índice da câmera
    if new_camera_index is not None:
        camera_index = new_camera_index
        # Reinicia a captura de vídeo com a nova câmera
        video_capture.release()
        video_capture = cv2.VideoCapture(camera_index)
        return jsonify({"status": "success", "camera_index": camera_index})
    return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5501)
