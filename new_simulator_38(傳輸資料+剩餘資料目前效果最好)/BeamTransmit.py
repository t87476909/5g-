from NetworkSettings import NetworkSettings,SystemInfo,Simulation
from BeamForming import BeamFormingFunction
import numpy as np
import math
import cmath
import time
#beamforming -> beamsearch -> beam
class BeamUseFunction:
    ue_location = list()
    ue_overlap_location = list()
    bs_location = list()
    bs_transmit_beam = dict() #儲存基地台要發射的波束
    bs_transmit_state = 0

class BeamTransmit:
    def __init__(self,bs_id):
        self.ue_location = BeamUseFunction.ue_location
        self.bs_location = BeamUseFunction.bs_location
        self.ue_overlap_location = BeamUseFunction.ue_overlap_location
        self.beamforming_list = list() #存取該基地台的波束排程
        self.ue_beam_list = list() #存取所有ue位於哪個beam底下
        self.num_bs = NetworkSettings.num_of_bs
        self.num_ue = NetworkSettings.num_of_ue
        self.num_overlap_ue = NetworkSettings.num_of_ue_overlap
        self.beam_angle = NetworkSettings.beam_angle
        self.bs_id = bs_id
        self.beam_number = int(360 / self.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.mapping_table = NetworkSettings.ue_to_bs_mapping_table
        self.mode = Simulation.mode

        if self.bs_id not in BeamUseFunction.bs_transmit_beam:
            BeamUseFunction.bs_transmit_beam.setdefault("{}".format(self.bs_id), [])
        #BeamUseFunction.bs_generator_beam_list["ue{}".format(i)].append("bs{}".format(j))

    def execute(self):
        if self.beam_index == 1 or SystemInfo.system_time == 1:
            self.transmit_beam() #發射波束
        need_beam_index = self.beamsearch()
        #print("之前產生的波束 = ",BeamFormingFunction.bs_generator_beam_list[self.bs_id])
        #print("bs_id = {} systme_time = {} beamtransmit = {} state = {} ".format(self.bs_id,SystemInfo.system_time, BeamUseFunction.bs_transmit_beam[self.bs_id],BeamUseFunction.bs_transmit_state))
        return BeamUseFunction.bs_transmit_beam[self.bs_id],need_beam_index,BeamUseFunction.bs_transmit_state
    
    def transmit_beam(self):
        if self.mode == 3 or self.mode == 4:
            if SystemInfo.system_time == 1: #系統最初始會打1次靜態波束
                for i in range(self.beam_number):
                    self.beamforming_list.append(i)
                BeamUseFunction.bs_transmit_beam[self.bs_id] = self.beamforming_list #存取所有基地台的beam
                BeamUseFunction.bs_transmit_state = 'static'
            else:
                BeamUseFunction.bs_transmit_beam[self.bs_id] = BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time']
                BeamUseFunction.bs_transmit_state = BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state']
        else:    
            if SystemInfo.system_time == 1 or SystemInfo.system_time == 1 + self.beam_number: #系統最初始會打2次靜態波束
                for i in range(self.beam_number):
                    self.beamforming_list.append(i)
                BeamUseFunction.bs_transmit_beam[self.bs_id] = self.beamforming_list #存取所有基地台的beam
                BeamUseFunction.bs_transmit_state = 'static'
            else:
                BeamUseFunction.bs_transmit_beam[self.bs_id] = BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time']
                BeamUseFunction.bs_transmit_state = BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state']
               
    def beamsearch(self): #基地台搜尋ue 每1ms執行一次
        location_index_list = list() #該基地台的底下ue的座標index
        overlap_ue_list = list()
        overlap_start_num = self.num_ue * self.num_bs #重疊區域位置起始
        bs_index = int(self.bs_id.lstrip('bs')) #取得該bs的座標位置
        #獲取該BS底下的ue位置
        bs_location = self.bs_location[bs_index]
        for i in range(self.num_ue): #非重疊區ue波束判別
            ue_location = self.ue_location[bs_index * self.num_ue + i]
            #print("第幾個ue = ",bs_index*self.num_ue+i)
            self.ue_beam_list.append(self.beamclassification(ue_location,bs_location))
        
        for ue_id,map_bs in self.mapping_table.items():
            for bs_index in range(len(map_bs)):
                if map_bs[bs_index] == self.bs_id: #若該bs_id 有在ue的關係內
                    ue_index = NetworkSettings.ue_id_list.index(ue_id) #所有ue的位置
                    location_index_list.append(ue_index - overlap_start_num) #
                    
        #print("overlap_ue_list = ",overlap_ue_list)
        #print("重疊區域的ue overlap ue = ",location_index_list)
        for j in range(len(location_index_list)):
            if location_index_list[j] >= 0:
                ue_location = self.ue_overlap_location[location_index_list[j]]
                #print("第幾個 overlap ue = ",j)
                self.ue_beam_list.append(self.beamclassification(ue_location,bs_location)) #

        beam_index = SystemInfo.system_time % self.beam_number #該輪的第幾次波束
        need_beam_index = [ i for i in range(len(self.ue_beam_list)) if self.ue_beam_list[i] == BeamUseFunction.bs_transmit_beam[self.bs_id][beam_index] ] #需要第幾個beam內的波束
        
        return need_beam_index

    def beamclassification(self,ue_location,bs_location): #判斷ue處於哪個基地台的beam底下
        #https://blog.csdn.net/qq_23055219/article/details/105184686
        #https://zhidao.baidu.com/question/324269714
        distance_x = ue_location[0] - bs_location[0] #x間距
        distance_y = ue_location[1] - bs_location[1] #y間距
        polar_location = complex(distance_x,distance_y)
        polar_location = cmath.polar(polar_location)
        angle = math.degrees(polar_location[1])
        if angle < 0:
            angle = 360 + angle
        beam = math.floor(angle / self.beam_angle) #判別在哪個波束下 
        return beam
        
        #for i in range(self.beam_number):
        #    if self.beam_angle * i <= angle and angle <= self.beam_angle * (i + 1):
                #print("ue_location = {} bs_location = {} angle = {} beam = {}".format(ue_location,bs_location,angle,i))
        #        return i 

