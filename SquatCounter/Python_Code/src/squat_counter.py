import cv2
import mediapipe as mp
from bleak import BleakScanner
from bleak import BleakClient
import struct
import asyncio
import threading
import time


#rep counter
rep = 0

#state of setup (top,bottom,start, or end)
state  = 0

#variable for button 
btn = [0,]

#top displacement value
top = 0

#bottom displacement value
bottom = 1

#variable for rep rate
rate = 0

#variable for next position
pos = "N/A"

# Bluetooth function (in a separate thread)
def async_thread():
  async def run():
        
          scanner = BleakScanner()
          devices = await scanner.discover(5,return_adv = True)
          
          def notification_callback(sender,payload):
            global btn
            
            btn = struct.unpack('<b',payload)  #btn stores whether button is pressed or not
            
          
          async with BleakClient("E8:9F:6D:00:A2:B2") as client:
              running = 1
              while running:
                  global btn
                  await client.start_notify("121eae50-5f0a-4780-843a-ad2c04997dd8",notification_callback)
                  
                  while True:
                    await asyncio.sleep(1)
        
  asyncio.run(run())



t1 = threading.Thread(target = async_thread) #starts thread
t1.start()
time.sleep(5)  #this gives the bluetooth thread time to connect before mediapipe starts


#mediapipe setup variables
mp_drawing = mp.solutions.drawing_utils

mp_drawing_styles = mp.solutions.drawing_styles

mp_pose = mp.solutions.pose

#beginning of opencv code
cap = cv2.VideoCapture(0)
with mp_pose.Pose(min_detection_confidence=.5,
min_tracking_confidence=.5) as pose:
    
    while cap.isOpened():
        
        works, image = cap.read() #reads webcam feed into variables
        if not works:
            print("No Video; Ignoring") 
            continue

      # converts frame to RGB for pose Processing  
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
   
        # Reconverts frame to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        image = cv2.flip(image,1)

        #writes the rep, rep rate, and next position up in the corner of the screen
        cv2.putText(image,f"Reps: {rep}",(0,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(image,f"Rep Rate: {rate}",(0,60),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),1,cv2.LINE_AA)
        cv2.putText(image,f"Next Position: {pos}",(0,90),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),1,cv2.LINE_AA)
        cv2.imshow('My Window', image)
       
        #calculates the difference between the nose landmark and right knee landmark. this is used to measure squats
        diff = (results.pose_world_landmarks.landmark[mp_pose.PoseLandmark.NOSE].y)-(results.pose_world_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y)
        
        # if button is pressed, it will check what the state is, it goes from logging the top difference,
        # logging the bottom difference, starting, and ending. If pressed after this, the cycle continues
        if btn[0] == 1:        
            match state:
                case 0:
                  top = diff
                  state = 1
                  print("Top Logged")
                    
                case 1:
                  bottom = diff
                  state = 2
                  print("Bottom Logged")
                    
                case 2:
                   
                  state = 3
                  rep = 0
                  prev = 1
                  pos = "DOWN"
                  print("Start!")
                  t1 = time.perf_counter()
                  
                    
                case 3:
                
                  state = 0
                  print("End!")
                
                case _:
                   print("ERROR - INVALID STATE")
                    

           # once in the start state, you are prompted to go down. once you reach the bottom difference, you are told
           # to go up. Once you reach the top difference, you have completed a rep. The rate is computed by subtracting 
           # the time from the latest rep from the time at the last rep and then dividing 1 by this difference
        if state == 3:
           
          if  diff <= top :
             if prev == 0:
                prev = 1
                rep +=1
                t2 = time.perf_counter()
                dt = t1-t2
                rate = 1/dt
                t1 = time.perf_counter()
                pos = "DOWN"
                
          if diff >= bottom:
             if prev == 1:
                prev = 0
                pos = "UP"
        
        
          
          
                
                
      
           
        # this breaks out of the loop if x is pressed
        if cv2.waitKey(1) == ord('q'):
          break
        time.sleep(.05)  # this is used to help make sure one button press is not counted as multiple
    
    cap.release()
    cv2.destroyAllWindows()
    t1.join            
        


