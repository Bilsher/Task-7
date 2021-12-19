import cv2
from PIL import ImageGrab
import numpy as np
import pyautogui as pag
import time

class Object:
    #Конструктор объекта
	def __init__(self, path):
        
        # 0 в imread означает что мы считываем изображение через grayscale 
        #Изображение в градациях серого - это изображение, в котором один пиксель представляет
        #количество света или содержит только информацию об интенсивности света. Это одномерное 
        #изображение, имеющее только разные оттенки серого цвета. Что позволит упростить считывание.
		img = cv2.imread(path, 0)
		self.img = img
		self.width = img.shape[1]
		self.height = img.shape[0]
		self.location = None
		
    #функция совпадения,она ищет наличие спрайта на изображении.
    #Она находит, насколько каждый участок изображения подходит под шаблон. Там, где это 
    #число максимальное и где оно больше чем 80% мы считаем, что там шаблон подошёл.
    #За динозавром может быть намешано куча лишних пиксеоей, но на 80% динозавр подошёл,  
    #поэтому мы считаем, что мы нашли его
	def match(self, scr):
		res = cv2.matchTemplate(scr, self.img, cv2.TM_CCOEFF_NORMED)
		minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
		startLoc = maxLoc
		endLoc = (startLoc[0]+self.width, startLoc[1]+self.height)

		if maxVal>0.8:
			self.location = (startLoc, endLoc)
			return True 
		else:
			self.location = None
			return False

#Функция для захвата экрана
def grabScreen(bbox=None):
	img = ImageGrab.grab(bbox=bbox)
	img = np.array(img)
    #Конвертируем RGB в BGR, что бы правильно отображались цвета. 
    #Pillow работает в формате [R, G, B]
    #OpenCV работает в формате [B, G, R]
	img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
	return img

startTime = time.time()
prevTime = time.time()

#Постепенное увелечение расстояние
speedRate = 1.5

#Расстояние на котором нужно прыгнуть
distanceThreshold = 80
#Зарезервированое расстояние что бы вернуть скорость, после Gameover
dtdef = 80  

#Картинки png которые считываются из папки object, а дальше преобразуются через функцию object(path)
player = Object('objects/dino.png')
obstacle = [Object('objects/cact1.png'), Object('objects/cact2.png'), Object('objects/bird.png')]
gmover = Object('objects/go.png')

#Блок отвечающий за захват экрана, если динозавр найден, то программа начинает игру и переходит 
#ко второму циклу
while 1:
	img = grabScreen()
    
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #Функция которая ищет крайние точки относительно location самого динозавра, 
    #считает по размеру самого объекта динозвар
	if player.match(img):
        #Крайняя левая-верхняя точка: 1 влево
		topleft_x = int(player.location[0][0]- player.width)
        #3 наверх
		topleft_y = int(player.location[0][1] - 3*player.height)
        
        # 14 справа
		bottomRight_x = int(player.location[1][0]+14*player.width)
        #0,5 так как пол это примерно половина модели динозавра
		bottomRight_y = int(player.location[1][1] + 0.5*player.height)
        #Точки захвата экрана
		screenStart = (topleft_x, topleft_y)
		screenEnd = (bottomRight_x, bottomRight_y)
		break
		
pag.press('space')

#Блок отвечающий за онсновую функцию прыжка
while 1:
   
	img_o = grabScreen(bbox=(*screenStart, *screenEnd))
	img = cv2.cvtColor(img_o, cv2.COLOR_BGR2GRAY)
	
	player.match(img)
    
    #Прибавка расстояния со временем, если скорость прохождения кактуса стала больше ожидаемой,
    #distancethrashhold += speedrait
	if time.time() - prevTime > 1:
		if time.time() - startTime < 180 and player.location:
			distanceThreshold += speedRate
		
		prevTime = time.time()
	
    #Подсветка модели для игрока
	if player.location:
		cv2.rectangle(img_o, player.location[0], player.location[1], (255,0,0), 2)

   #обновление distanceThreshold при пройгрыше + завхат экрана пройгрыша
	if gmover.match(img):
		distanceThreshold = dtdef
		print("GameOver")
		pag.press('space')
	
    #Подсветка для динозавра + функция прыжка при распознанни припядствия на расстоянии
	for obstact in obstacle:
		if obstact.match(img):
			cv2.rectangle(img_o, obstact.location[0], obstact.location[1], (0,0,255), 2)


            #проверка не равен ли location, значению null, дабы избежать возможных ошибок
			if player.location:
                #horizontalDistance - это расстояние от динозавра до кактуса
                #verticalDistance - это расстояние до птицы. 
                #Если дистанция до кактуса маленькая, то динозвар прыгатет  
                #Но если вдру вверху птица, то прыжок не произойдёт
				horizontalDistance = obstact.location[0][0]-player.location[1][0]
				verticalDistance = player.location[0][1] - obstact.location[1][1]

				if horizontalDistance < distanceThreshold and verticalDistance < 2:
					pag.press('space')
					print("SPACE")
					break

				
	cv2.imshow("Screen2", img_o)
	
	if cv2.waitKey(1) == ord('q'):
		break
	

cv2.destroyAllWindows()
