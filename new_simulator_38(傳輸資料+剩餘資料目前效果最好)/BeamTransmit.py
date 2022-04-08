from NetworkSettings import NetworkSettings,SystemInfo,Simulation
from BeamForming import BeamFormingFunction
import numpy as np
import math
import cmath
import time
#beamforming -> beamsearch -> beam
class BeamUseFunction:
    all_ue_location = list()
    bs_location = list()
    bs_transmit_beam = dict() #儲存基地台要發射的波束
    bs_transmit_state = 0

class BeamTransmit:
    def __init__(self,bs_id):

        self.all_ue_location = BeamUseFunction.all_ue_location
        self.bs_location = BeamUseFunction.bs_location
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
        need_beam_index,need_beam_ue_id = self.beam_search()
        #print("之前產生的波束 = ",BeamFormingFunction.bs_generator_beam_list[self.bs_id])
        #if self.bs_id == 'bs0': 
        #    print("bs_id = {} systme_time = {} beamtransmit = {} state = {} ".format(self.bs_id,SystemInfo.system_time, BeamUseFunction.bs_transmit_beam[self.bs_id],BeamUseFunction.bs_transmit_state))
        return BeamUseFunction.bs_transmit_beam[self.bs_id],need_beam_index,BeamUseFunction.bs_transmit_state,need_beam_ue_id
    
    def transmit_beam(self):
        #if self.mode == 3 or self.mode == 4:
        if self.mode == 3:
            if SystemInfo.system_time == 1: #系統最初始會打1次靜態波束
                for i in range(self.beam_number):
                    self.beamforming_list.append(i)
                BeamUseFunction.bs_transmit_beam[self.bs_id] = self.beamforming_list #存取所有基地台的beam
                BeamUseFunction.bs_transmit_state = 'static'
            else:
                BeamUseFunction.bs_transmit_beam[self.bs_id] = BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time']
                BeamUseFunction.bs_transmit_state = BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state']
        else: #self.mode == 0 1 2 4    
            if SystemInfo.system_time == 1 or SystemInfo.system_time == 1 + self.beam_number: #系統最初始會打2次靜態波束
                for i in range(self.beam_number):
                    self.beamforming_list.append(i)
                BeamUseFunction.bs_transmit_beam[self.bs_id] = self.beamforming_list #存取所有基地台的beam
                BeamUseFunction.bs_transmit_state = 'static'
            else:
                BeamUseFunction.bs_transmit_beam[self.bs_id] = BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time']
                BeamUseFunction.bs_transmit_state = BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state']

    def beam_search(self):

        bs_index = int(self.bs_id.lstrip('bs')) #取得該bs的座標位置
        bs_location = self.bs_location[bs_index]
        need_ue_id_list = list()
        need_beam_ue_id = list()

        for ue_id,map_bs in self.mapping_table.items():
            if self.bs_id in map_bs:
                ue_index = int(ue_id.lstrip('ue'))
                need_ue_id_list.append(ue_index)
        #if self.bs_id == 'bs0':
        #    print("need_ue_id_list = ",need_ue_id_list)
        need_ue_id_number = len(need_ue_id_list)
        for i in range(need_ue_id_number): #所有需要的ue_id遍歷
            ue_location = self.all_ue_location[need_ue_id_list[i]]
            self.ue_beam_list.append(self.beamclassification(ue_location,bs_location))

        beam_index = (SystemInfo.system_time - 1) % self.beam_number #該輪的第幾次波束
        ue_beam_number = len(self.ue_beam_list)
        need_beam_index = [ i for i in range(ue_beam_number) if self.ue_beam_list[i] == BeamUseFunction.bs_transmit_beam[self.bs_id][beam_index] ] #需要第幾個beam內的波束        
        
        need_beam_number = len(need_beam_index)
        for i in range(need_beam_number):
            need_beam_ue_id.append(need_ue_id_list[need_beam_index[i]]) #該波束需要的ue_id

        return need_beam_index,need_beam_ue_id

        
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

