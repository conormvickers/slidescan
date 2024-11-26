import mediapipe as mp
import cv2
import time
import requests
import threading


BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

last_fire_time = time.time()


playpause = "http://main.server:8123/api/webhook/YX7ptzJCNDcuvtfvmrxLMvW4mH0HUATj"
volumeup = "http://main.server:8123/api/webhook/ccHiaOkjUEi2qqT4oXmAic66tjGW2GwH"
volumedown = "http://main.server:8123/api/webhook/q0oX9549tRvZcvkV4Lq1Ri4CI96I7yrh"
url = playpause

timethresh = 2

def rate_limited_function(url):
    # Your function code here
    print("Function fired ", url)
    
    

    response = requests.get(url)

    print(response.text)
    

gestures = ["Victory", "ILoveYou", "Thumb_Down"]
def fire_rate_limited_function(gesture):
    global last_fire_time, gestures
    
    current_time = time.time()  
    if current_time - last_fire_time >= timethresh :
        
        url = ''
        if gesture == gestures[0]:
            url = playpause
        elif gesture == gestures[1]:
            url = volumeup
        elif gesture == gestures[2]:
            url = volumedown
        else:
            url = ''
            return
        
        rate_limited_function(url)
        last_fire_time = current_time
    else:
        print("Throttled")


urla = 'http://picam.local:8000/stream.mjpg'
urlb = 'http://picam.local:5000/video_feed'
urlc = 'http://localhost:5000/video_feed'
urlbertha = 'http://Bertha:5000/video_feed'
    
# options = GestureRecognizerOptions(
#     base_options=BaseOptions(model_asset_path='./gesture_recognizer.task'),
#     running_mode=VisionRunningMode.LIVE_STREAM,
#     result_callback=print_result)

cap = cv2.VideoCapture(urla)





options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path='./gesture_recognizer.task'),
   )

with GestureRecognizer.create_from_options(options) as recognizer:
    processing = False
    
    def process_frame(frame):
        global processing
        processing = True
        print('frame')
        frame_srgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_srgb)
                
                # recognizer.recognize_async(mp_image, int(time.time() * 1000))
                
                       

        result =  recognizer.recognize(mp_image)
        if result.gestures:
            gesture = result.gestures[0][0].category_name
            score = result.gestures[0][0].score
            print(result.gestures)

            if gesture in gestures and score > 0.7:
                print(result.gestures)
                fire_rate_limited_function(gesture=gesture)

        processing = False

    print("Started")
    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                print("Error reading frame")
                i = 0
                while not ret:
                    print('waiting 5 seconds  ...  ', i)
                    time.sleep(5)
                    print("trying again")
                    cap = cv2.VideoCapture(url)

                    ret, frame = cap.read()
                    i = i + 1
                    
                
            else:
            
                if not processing:
                    thread = threading.Thread(target=process_frame, args=(frame,))
                    thread.start()
                
                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(e)
            break

cap.release()
cv2.destroyAllWindows()