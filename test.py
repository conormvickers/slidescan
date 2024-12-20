import cv2
import time

espurl = 'http://192.168.1.146/mjpeg/1'
    
# options = GestureRecognizerOptions(
#     base_options=BaseOptions(model_asset_path='./gesture_recognizer.task'),
#     running_mode=VisionRunningMode.LIVE_STREAM,
#     result_callback=print_result)
streamurl = espurl
cap = cv2.VideoCapture(streamurl)



while True:
        try:
            ret, frame = cap.read()
            print(ret)
            if not ret:
                print("Error reading frame:", cap.get(cv2.CAP_PROP_FRAME_COUNT))
                i = 0
                while not ret:
                    print('waiting 5 seconds  ...  ', i)
                    time.sleep(5)
                    print("trying again")
                    cap = cv2.VideoCapture(streamurl)

                    ret, frame = cap.read()
                    i = i + 1
                    
                
            else:
            
         
                
                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(e)
            break
