from flask import Flask, render_template, Response, request, jsonify
import cv2
import subprocess

app = Flask(__name__)

# Variáveis globais para manter a câmera ativa e o estado de rotação
current_camera = 0
rotate_image = False

def get_available_cameras():
    try:
        result = subprocess.run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE, text=True)
        output = result.stdout
        cameras = []
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if '/dev/video' in line:
                camera = line.strip()
                cameras.append(camera)
        return cameras
    except Exception as e:
        print(f"Erro ao listar dispositivos: {e}")
        return []

def generate_frames():
    global current_camera, rotate_image
    video_capture = cv2.VideoCapture(current_camera)
    
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            # Aplica a rotação se a variável rotate_image estiver True
            if rotate_image:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    cameras = get_available_cameras()
    return render_template('index.html', cameras=cameras, current_camera=current_camera)

@app.route('/change_camera', methods=['POST'])
def change_camera():
    global current_camera
    data = request.get_json()
    camera_index = int(data.get('camera_index', 0))
    current_camera = camera_index
    return jsonify({"status": "success"})

@app.route('/rotate_image', methods=['POST'])
def rotate_image_toggle():
    global rotate_image, current_camera
    data = request.get_json()
    camera_index = data.get('camera_index', current_camera)  # Recebe o índice da câmera
    current_camera = camera_index  # Atualiza a câmera atual, caso tenha sido passado
    rotate_image = not rotate_image  # Inverte o estado de rotação
    return jsonify({"status": "success", "rotate": rotate_image})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, port=5501)
