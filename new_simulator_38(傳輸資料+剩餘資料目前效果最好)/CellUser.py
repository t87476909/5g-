import numpy as np
import math
import cmath
import random
from NetworkSettings import NetworkSettings,Simulation

class CellUser:
    def __init__(self):
        self.overlap_width = (2 * NetworkSettings.bs_range - NetworkSettings.Neighbor_Distance)/2
        self.overlap_length = NetworkSettings.Neighbor_Distance - NetworkSettings.bs_range
        self.beam_eliminate = NetworkSettings.beam_eliminate #每個基地台被清除的波束
        self.beam_angle = NetworkSettings.beam_angle
        self.beam_number = int(360 / self.beam_angle)
        self.clear_number = Simulation.random_beam_clear_number + 1
    
    def random_clear_beam(self):
        for i in range(NetworkSettings.num_of_bs):
            self.beam_eliminate[i] = list()
            clear_count = random.randrange(1,self.clear_number) #沒有ue的beam
            for j in range(clear_count):
                clear_beam = random.randrange(0,7)
                self.beam_eliminate[i].append(clear_beam)
        #print("被清除的波束 = ",self.beam_eliminate)
    def clear_beam(self):
        for i in range(NetworkSettings.num_of_bs):
            self.beam_eliminate[i] = list()
            for j in range(len(NetworkSettings.beam_clear_index)):
                self.beam_eliminate[i].append(NetworkSettings.beam_clear_index[j])
        #print("被清除的波束 = ",self.beam_eliminate)
    def getRandomPointInrectangle(self,x,y,i): #if (2*NetworkSettings.bs_range > NetworkSettings.Neighbor_Distance) (基地台範圍有重疊)
        while True:
            precision = 3
            pr_x = np.sqrt(self.overlap_length * self.overlap_length * random.randint(0, 10 ** precision) / float(10 ** precision)) #pr生成為 0 ~ self.overlap_length
            pr_y = np.sqrt(self.overlap_length * self.overlap_length * random.randint(0, 10 ** precision) / float(10 ** precision))
            theta_x = random.uniform(-1, 1)
            theta_y = random.uniform(-1, 1)
            thePoint = (x + pr_x * theta_x , y + pr_y * theta_y)
            distance_x = thePoint[0] - x #x間距
            distance_y = thePoint[1] - y #y間距
            polar_location = complex(distance_x,distance_y)
            polar_location = cmath.polar(polar_location)
            angle = math.degrees(polar_location[1])
            if angle < 0:
                angle = 360 + angle
            beam = math.floor(angle / self.beam_angle) #判別在哪個波束下
            if Simulation.beam_clear == False:
                break
            elif beam not in self.beam_eliminate[i]: #判斷生成的隨機座標點在不在需要被清除的座標內、#判斷是否要進行波束內座標清除的動作
                break
        return thePoint

    def getRandomPointInOverlap(self,x,y,i): #重複覆蓋範圍
        while True:
            if x == 0 and y == 0: #分配1、2、3、4(上右下左)
                Distribution_direction = np.random.randint(1,5)
            elif x == 0: #分配1、2、4(上右左)
                Distribution_direction = np.random.randint(1,4)
                if Distribution_direction == 3:
                    Distribution_direction = Distribution_direction + 1
            elif y == 0: #分配1、2、3(上右下)
                Distribution_direction = np.random.randint(1,4)
            else: #分配1、2(上右)
                Distribution_direction = np.random.randint(1,3)
            
            thePoint = self.getRandomdirection(Distribution_direction,x,y,i)
            distance_x = thePoint[0] - x #x間距
            distance_y = thePoint[1] - y #y間距
            polar_location = complex(distance_x,distance_y)
            polar_location = cmath.polar(polar_location)
            angle = math.degrees(polar_location[1])

            if angle < 0:
                angle = 360 + angle
            beam = math.floor(angle / self.beam_angle) #判別在哪個波束下
            if Simulation.beam_clear == False:
                break
            elif beam not in self.beam_eliminate[i]: #判斷生成的隨機座標點在不在需要被清除的座標內、#判斷是否要進行波束內座標清除的動作
                break
        #print("bs_id = {} beam = {} Overlappoint = {} ".format(i,beam,thePoint))
        return thePoint

    def getRandomdirection(self,Distribution_direction,x,y,i):
        precision = 3
        theta = random.uniform(-1, 1)
        pr = np.sqrt(self.overlap_width * self.overlap_width * random.randint(0, 10 ** precision) / float(10 ** precision))
        length = self.overlap_length + pr
        limit = np.sqrt(abs(NetworkSettings.bs_range **2 - length**2))
        if Distribution_direction == 1: #生成上方向
            final_y = y + length
            final_x = x + limit * theta
        if Distribution_direction == 2: #生成右方向
            final_y = y + limit * theta
            final_x = x + length
        if Distribution_direction == 3: #生成下方向
            final_y = y - length
            final_x = x + limit * theta
        if Distribution_direction == 4: #生成左方向
            final_y = y + limit * theta
            final_x = x - length
        UE_generator_location = (final_x ,final_y)
            
        return UE_generator_location

    def getRandomPointInCircle(self,x,y): #if (2*NetworkSettings.bs_range <= NetworkSettings.Neighbor_Distance) (基地台範圍沒有重疊)
        precision = 3
        pr = np.sqrt(NetworkSettings.bs_range * NetworkSettings.bs_range * random.randint(0, 10 ** precision) / float(10 ** precision))
        theta = 2 * np.pi * random.random()
        thePoint = ( x + pr * np.cos(theta), y + pr * np.sin(theta))
        #print(thePoint)
        return thePoint
        