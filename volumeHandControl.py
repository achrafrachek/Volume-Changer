import cv2 
import mediapipe as mp
import numpy as np
import time
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
cap = cv2.VideoCapture(0)

wCam , hCam = 1080,720 

cap.set(3,wCam)
cap.set(4,hCam)

mpHands = mp.solutions.hands                         #initiating the variables according to mediapipe documentation
hands = mpHands.Hands() 
mpDraw = mp.solutions.drawing_utils
pTime = 0 
cTime = 0 


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
#volume.SetMasterVolumeLevel(-20.0, None)
minVol = volRange[0]
maxVol = volRange[1]
vol=0
volBar = 400
volpercentage = 0 

while True : 
    success, img = cap.read() 
    imgRGB= cv2.cvtColor(img, cv2.COLOR_BGR2RGB)                #project needs to be rgb img 
    results = hands.process(imgRGB)                             #checking if there is a hand or not

    xList=[]
    yList=[]
    bbox=[]

    draw  = True
    lmList=[]
    if results.multi_hand_landmarks :                           #displaying the landmarks and the connections between them
        for handLms in results.multi_hand_landmarks :           #displaying each landmark            
            for id, lm in enumerate(handLms.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)                
                #print(id, cx, cy)
                lmList.append([id, cx, cy])
                if len(lmList) > 15 :
                    #print(lmList[4] , lmList[8])
                    x1,y1 = lmList[4][1], lmList[4][2]
                    x2,y2 = lmList[8][1], lmList[8][2]
                    cenx,ceny = (x1+x2)//2 , (y1+y2)//2

                    cv2.circle(img, (x1,y1) , 13,(249,200,14) , cv2.FILLED)
                    cv2.circle(img, (x2,y2) , 13,(249,200,14) , cv2.FILLED)
                    cv2.line(img,(x1,y1),(x2,y2) , (45,226,230) , 3)
                    cv2.circle(img,(cenx,ceny) , 7 ,(45,226,230) ,cv2.FILLED ) 

                    length= math.hypot(x2-x1,y2-y1)

                    vol = np.interp(length , [50,300],[minVol, maxVol]) 
                    volBar = np.interp(length , [50,300],[400, 150]) 
                    volpercentage = np.interp(length , [50,300],[0, 100]) 
                    print(vol)
                    volume.SetMasterVolumeLevel(vol, None)
                    cv2.rectangle(img,(50,150),(85,400), (101,13,137), 3)
                    cv2.rectangle(img,(50,int(volBar)),(85,400), (101,13,137), cv2.FILLED)
                    cv2.putText(img,f"{int(volpercentage)}%" , (40,450) , cv2.FONT_HERSHEY_PLAIN, 1.5,(101,13,137),2 )



                    if length<50 :
                        cv2.circle(img,(cenx,ceny) , 15 ,(253,29,83) ,cv2.FILLED ) 

                xmin , xmax = min(xList) , min(xList)
                ymin , ymax = min(yList) , min(yList)
                bbox = xmin,ymin,xmax,ymax


 

                mpDraw.draw_landmarks(img , handLms , mpHands.HAND_CONNECTIONS)
                

                    #cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

    cTime = time.time()
    fps = 1/(cTime-pTime)    #calculating fps
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10,70) , (cv2.FONT_HERSHEY_COMPLEX_SMALL) , 2 ,(0,0,255), 2 )  #displaying fps 

    cv2.imshow("Image", img)            #basic cv2 to setup camera 
    if cv2.waitKey(1) == ord('q'):
        break