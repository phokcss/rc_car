from socket import *
import cv2
import time
import RPi.GPIO as GPIO
from gpiozero import Motor
global color 					
import math
import os
from PIL import Image
import numpy as np
import time
import picamera
set_color='none'				#따라가는 화살표 색 'none으로 초기화'
detect=0		#따라가는 색이 있는지 확인하는 변수
angle=0			#현재 rc카의 각도를 저장하는 함수

GPIO.setmode(GPIO.BCM)			#BCM 모드:핀 번호를 GPIO모듈 번호로 사용

right_up_motor = Motor(forward=20,backward=21)			#오른쪽 위 모터 설정
left_down_motor= Motor(forward=16,backward=17)			#왼쪽 아래 모터 설정
right_down_motor = Motor(forward=26,backward=19)		#오른쪽 아래 모터 설정
left_up_motor= Motor(forward=6,backward=5)				#왼쪽 위 모터 설정

GPIO.setup(23,GPIO.OUT)						#출발을 알려주는 led를 설정
GPIO.setup(24,GPIO.OUT)						#출발을 알려주는 led를 설정
GPIO.setup(25,GPIO.OUT)						#출발을 알려주는 led를 설정
servo_left_pin=12							#서보모터 2개 핀 설정
servo_right_pin=13							#서보모터 2개 핀 설정

GPIO.setup(servo_right_pin,GPIO.OUT)		#서보모터 2개 제어 설정
GPIO.setup(servo_left_pin,GPIO.OUT)			#서보모터 2개 제어 설정

servo_right=GPIO.PWM(servo_right_pin,50)	#서보모터 2개pwm 설정
servo_left=GPIO.PWM(servo_left_pin,50)		#서보모터 2개pwm 설정

servo_right.start(12.5)						#서보모터 2개 각도 초기화 설정 				
servo_left.start(7.5) 						#서보모터 2개 각도 초기화 설정

time.sleep(3)
									

GPIO.setup(servo_right_pin,GPIO.IN)			#떨림 방지를 위해 서보모터 입력핀으로 전환
GPIO.setup(servo_left_pin,GPIO.IN)			#떨림 방지를 위해 서보모터 입력핀으로 전환

def color_detect(test_image,what):     					#hsv를 사용해 색깔 감지하는 함수		h:색상 s:채도 v:명도
		if(what=='col'):       	#화살표 색깔 감지 부분(따라가는 화살 색)     					
			green = cv2.inRange(test_image, (50,150,0)  , (90,300,255))      		#h:50~90,s:150~300, v:0~255인 부분을 색칠
			img_result_green = cv2.bitwise_and(test_image, test_image, mask=green) 

			pos_green = np.where((img_result_green[:,:,0] != 0)&
								 (img_result_green[:,:,1] != 0)& 
								 (img_result_green[:,:,2] != 0))	#색칠된 부분을 감지해서 크기로 저장

			if(len(pos_green[0])>2000):               #크기가 일정 부분이 넘으면 색깔이 감지됬다고 판단 
				print("green", len(pos_green[0]))
				return 'green'  #green 리턴
			else:
				dst= cv2.inRange(test_image, (100,200,0) , (120,255,255))           
				img_result2 = cv2.bitwise_and(test_image, test_image, mask = dst)    

				pos_blue = np.where((img_result2[:,:,0] != 0) &               
									(img_result2[:,:,1] != 0) &
									(img_result2[:,:,2] != 0))
				print('blue',len(pos_blue[0]))
				if(len(pos_blue[0])>2000):  
					return 'blue'      
				else:
					return 'none'      
		elif(what=='dire'):			#마크 배경 감지 부분(방향)
			dst = cv2.inRange(test_image, (0,100,0) , (75,220,255)  )      
			img_result_yellow= cv2.bitwise_and(test_image, test_image, mask=dst)   
			pos_yellow = np.where(                                          
				(img_result_yellow[:, :, 0] != 0)
				& (img_result_yellow[:, :, 1] != 0)
				& (img_result_yellow[:, :, 2] != 0))
			print('yellow',len(pos_yellow[0]))

			if (len(pos_yellow[0]) > 2000):       
				return 'yellow'     
			else:
				dst = cv2.inRange(test_image, (120,100,0), (150,250,255))     
				img_result2 = cv2.bitwise_and(test_image, test_image, mask=dst)   

				pos_puple = np.where((img_result2[:, :, 0] != 254) &        
									 (img_result2[:, :, 1] != 0) &
									 (img_result2[:, :, 2] != 0))

				print('purple',len(pos_puple[0]))
				if (len(pos_puple[0]) > 2000):          
					print("크기",len(pos_puple[0]))
					return 'purple'     
				
				else:
					dst = cv2.inRange(test_image, (85, 240, 0), (100, 260, 255))   
					img_result2 = cv2.bitwise_and(test_image, test_image, mask=dst) 
					pos_mint = np.where(                                       
						(img_result2[:, :, 0] != 254) &
						(img_result2[:, :, 1] != 0) &
						(img_result2[:, :, 2] != 0))
					print('mint',len(pos_mint[0]))
		

					if (len(pos_mint[0]) > 2000):        
						return 'mint'      
					else:
						return 'none'       
		else:
			return 'error'
def start():									#led로 rc카가 언제 출발하는지 알려주는 코드
	print('start')							
	GPIO.output(23,False)
	GPIO.output(24,False)
	GPIO.output(25,False)
	
	GPIO.output(23,True)
	time.sleep(2)
	GPIO.output(24,True)
	time.sleep(2)
	GPIO.output(25,True)
	time.sleep(2)
	
	GPIO.output(23,False)
	GPIO.output(24,False)
	GPIO.output(25,False)
	
	
def stop_rc():										
	print('stop_rc')					#rc카가 정지하는 코드
	left_up_motor.stop()			
	left_down_motor.stop()
	right_down_motor.stop()
	right_up_motor.stop()
					
def motor(angle):						#rc카가 angle에따라 방향변경을 하는 코드
	print('motor')
	
	GPIO.setup(servo_right_pin,GPIO.OUT)		#서보모터 출력핀으로 전환
	GPIO.setup(servo_left_pin,GPIO.OUT)
	print('angle',angle)
	if(angle==0):
		servo_right.ChangeDutyCycle(12.5)		#서보모터 방향전환
		servo_left.ChangeDutyCycle(7.5)
		time.sleep(3)		
		GPIO.setup(servo_right_pin,GPIO.IN)		#서보모터 다시 입력핀으로 전환
		GPIO.setup(servo_left_pin,GPIO.IN)		
		left_up_motor.forward(1)				#모터 전진
		left_down_motor.forward(1)
		right_down_motor.forward(1)
		right_up_motor.forward(1)
		
	
	elif(angle==90):
		servo_right.ChangeDutyCycle(7.5)
		servo_left.ChangeDutyCycle(12.5)
		time.sleep(3)
		GPIO.setup(servo_right_pin,GPIO.IN)
		GPIO.setup(servo_left_pin,GPIO.IN)
		left_up_motor.backward(1)			
		left_down_motor.forward(1)
		right_down_motor.backward(1)
		right_up_motor.forward(1)
		
		

	elif(angle==180):
		servo_right.ChangeDutyCycle(12.5)
		servo_left.ChangeDutyCycle(7.5)
		time.sleep(3)	
		GPIO.setup(servo_right_pin,GPIO.IN)
		GPIO.setup(servo_left_pin,GPIO.IN)			
		left_up_motor.backward(1)			
		left_down_motor.backward(1)
		right_down_motor.backward(1)
		right_up_motor.backward(1)
		
		

	else:
		servo_right.ChangeDutyCycle(7.5)
		servo_left.ChangeDutyCycle(12.5)
		time.sleep(3)
		GPIO.setup(servo_right_pin,GPIO.IN)
		GPIO.setup(servo_left_pin,GPIO.IN)
		left_up_motor.forward(1)			
		left_down_motor.backward(1)
		right_down_motor.forward(1)
		right_up_motor.backward(1)

camera= picamera.PiCamera()				#카메라 설정
camera.start_preview					
camera.resolution = (150, 150)			#카메라 해상도 설정

count=0					#쫒아갈 화살표 색 설정 변수	
while True:
	try:
		try:									

			camera.capture('img.png')			#사진 저장
			frame=cv2.imread('img.png')			#사진 읽기
			try:
				 frame= frame[ 0:150,0:150] 
			except TypeError: 
				camera.stop_preview()			#error시 종료
				camera.close()	
				cv2.destroyAllWindows()
				break
			time.sleep(0.1)
			hsv= cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)		#사진 hsv로 변환
			start_time = time.time()
			color=color_detect(hsv,'col')			#색감지
			count=count+1
			end = time.time()
			print(f"{end - start_time:.5f} sec")
			if(count<5):
				color=color_detect(frame,'col')			#5번 동안 색 설정
				
			elif((detect==0) and ((color=='green')or(color=='blue'))):		#설정 완료시					
				detect=1
				print('_______________________color_set______________________')
				motor(angle)
				set_color=color
				print("set_color",set_color)
				print("set_color",set_color)
				print("set_color",set_color)
				print("set_color",set_color)

				color='none'
				time.sleep(1)	
				time.sleep(1)	

				continue	
			elif(detect==0 and color=='none'):
				print('______________________color_not_set_________________________')					
				break
			elif(color==set_color):
				print('_______________________color_detect______________________')
				stop_rc()									#color detect함수에서 감지된 색과 설정 색이 같다면 정지
				color=color_detect(frame,'dire')			
				if (color=='yellow'):		#좌회전
					angle=angle-90		
					if(angle==-90):
						angle=270
					motor(angle)			#서보모터 변경후 전진
					time.sleep(1.5)
					color='none'
					continue
				elif (color=='purple'):		#우회전
					angle=angle+90
					print('6')
					if(angle==360):
						angle=0
					motor(angle)			#서보모터 변경후 전진
					time.sleep(1.5)
					color='none'
					continue
				elif (color=='mint'):		#정지
					color='none'
					print('stop')
					break
				else:
					motor(angle)
					time.sleep(0.5)
					stop_rc()
					color=color_detect(frame,'dire')
			else:
				continue
		except BrokenPipeError:
			continue
	except KeyboardInterrupt:
		camera.stop_preview()	
		camera.close()	
		cv2.destroyAllWindows()
camera.stop_preview()	
camera.close()	
cv2.destroyAllWindows()
