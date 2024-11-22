from flask import Flask, render_template, Response
import cv2



app = Flask(__name__)

pi = False

if pi:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
    picam2.start()

else:
    cap = cv2.VideoCapture(0)

def gen_frames():
    while True:
        if pi:
            frame = picam2.capture_array()
        else:
            ret, frame = cap.read()
            if not ret:
                print('ERROR: Failed to read frame from camera')
                break
            
        ret, jpeg = cv2.imencode('.jpg', frame)
        
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, use_reloader=False)