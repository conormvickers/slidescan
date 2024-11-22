import mediapipe as mp
import cv2
import time
import requests


BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

last_fire_time = time.time()


playpause = "https://homeassistant.docdrive.link/api/webhook/YX7ptzJCNDcuvtfvmrxLMvW4mH0HUATj"
volumeup = "https://homeassistant.docdrive.link/api/webhook/ccHiaOkjUEi2qqT4oXmAic66tjGW2GwH"
volumedown = "https://homeassistant.docdrive.link/api/webhook/q0oX9549tRvZcvkV4Lq1Ri4CI96I7yrh"
url = playpause

timethresh = 2

def rate_limited_function(url):
    # Your function code here
    print("Function fired ", url)
    
    

    response = requests.get(url)

    print(response.text)
    
    
def fire_rate_limited_function(gesture):
    global last_fire_time
    
    current_time = time.time()  
    if current_time - last_fire_time >= timethresh:
        
        url = ''
        match gesture:
            case 'Victory':
                url = playpause
            case 'Thumb_Up':
                url = volumeup
            case 'Thumb_Down':
                url = volumedown
            case _:
                url = ''
                return
        
        rate_limited_function(url)
        last_fire_time = current_time
    else:
        print("Throttled")


cap = cv2.VideoCapture('http://picam.local:8000/stream.mjpg')

    
# options = GestureRecognizerOptions(
#     base_options=BaseOptions(model_asset_path='./gesture_recognizer.task'),
#     running_mode=VisionRunningMode.LIVE_STREAM,
#     result_callback=print_result)

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='./gesture_recognizer.task'),
   )

with GestureRecognizer.create_from_options(options) as recognizer:

    print("Started")
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                print("Error reading frame")
                break
            
            
            # frame_srgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            # recognizer.recognize_async(mp_image, int(time.time() * 1000))
            result =  recognizer.recognize(mp_image)
            if result.gestures:
                gesture = result.gestures[0][0].category_name
                fire_rate_limited_function(gesture=gesture)
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(e)
            break

cap.release()
cv2.destroyAllWindows()