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
        self.beam_number = round(360 / self.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.mapping_table = NetworkSettings.ue_to_bs_mapping_table
        self.mode = Simulation.mode
        self.bs_beam_neighbor = NetworkSettings.bs_beam_neighbor #format [target_bs][neighbor_bs][current_target_beam]
        self.bs_ue_distance = NetworkSettings.bs_ue_distance

        if self.bs_id not in BeamUseFunction.bs_transmit_beam:
            BeamUseFunction.bs_transmit_beam.setdefault("{}".format(self.bs_id), [])

    def execute(self):
        #print("----------------------------------------------------------------------")
        if self.beam_index == 1 or SystemInfo.system_time == 1:
            self.transmit_beam() #發射波束
        need_ue_index,need_beam_ue_id = self.beam_search()
        if self.mode > 1 and SystemInfo.system_time != 1: #不使用雙連接系統
            need_index,need_ue_id = self.receiver_one(need_ue_index,need_beam_ue_id) #0.007            
            return BeamUseFunction.bs_transmit_beam[self.bs_id],need_index,BeamUseFunction.bs_transmit_state,need_ue_id,need_beam_ue_id
        else:
            return BeamUseFunction.bs_transmit_beam[self.bs_id],need_ue_index,BeamUseFunction.bs_transmit_state,need_beam_ue_id,need_beam_ue_id
    
    def transmit_beam(self):
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

        for i in range(len(need_ue_id_list)): #所有需要的ue_id遍歷
            ue_location = self.all_ue_location[need_ue_id_list[i]]
            self.ue_beam_list.append(self.beamclassification(ue_location,bs_location))

        beam_index = (SystemInfo.system_time - 1) % self.beam_number #該輪的第幾次波束
        need_ue_index = [ i for i in range(len(self.ue_beam_list)) if self.ue_beam_list[i] == BeamUseFunction.bs_transmit_beam[self.bs_id][beam_index] ] #求需要在ue_id_list內的第幾個ue位置
        
        for i in range(len(need_ue_index)):
            need_beam_ue_id.append(need_ue_id_list[need_ue_index[i]]) #該波束需要的ue_id
            
        #print("self.bs_beam_neighbor[slef.bs_id] = ",self.bs_beam_neighbor[self.bs_id])
        #print("bs_id = {} BeamUseFunction.bs_transmit_beam[self.bs_id] = {}".format(self.bs_id,BeamUseFunction.bs_transmit_beam[self.bs_id]))
        #print("beam_index = {} need_ue_index = {} ".format(beam_index,need_ue_index))
        #print("need_beam_ue_id = ",need_beam_ue_id)

        return need_ue_index,need_beam_ue_id
    
    def receiver_one(self,need_ue_index,need_beam_ue_id): #判斷該方法的UE只能使用一個接收器
        #1. 判斷波束是否可能為雙連接波束 2.判斷該ue是否在雙連接範圍下 -> 3.是的話要判斷該ue在同一個波束時槽中是否有雙連接 4.
        #beam_index = (SystemInfo.system_time - 1) % self.beam_number #該輪的第幾次波束
        #current_beam = BeamUseFunction.bs_transmit_beam[self.bs_id][beam_index] #當前基地台打出來的波束        
        bs_index = int(self.bs_id.lstrip('bs')) #取得該bs的座標位置
        bs_location = self.bs_location[bs_index]
        need_remove_index_list = list()
        need_remove_ue_id_list = list()
        
        
        for i in range(len(need_beam_ue_id)):
            ue_id = "ue" + str(need_beam_ue_id[i])
            min_distance = min(self.bs_ue_distance[ue_id])
            ue_location = self.all_ue_location[need_beam_ue_id[i]] #當前ue的位置
            x_distance = bs_location[0] - ue_location[0] #當前ue與基地台的x距離
            y_distance = bs_location[1] - ue_location[1] #當前ue與基地台的y距離
            current_bs_ue_distance = math.sqrt(x_distance**2 + y_distance**2)
            if current_bs_ue_distance != min_distance: #若是該基地台對於ue而言並非最佳選擇
                need_remove_index_list.append(need_ue_index[i])
                need_remove_ue_id_list.append(need_beam_ue_id[i])

        if len(need_remove_index_list) > 0 and len(need_remove_ue_id_list) > 0:
            new_need_ue_index = list(set(need_ue_index) - set(need_remove_index_list))
            new_need_beam_ue_id = list(set(need_beam_ue_id) - set(need_remove_ue_id_list))
            #print("need_remove_index_list = {} need_remove_ue_id_list = {}".format(need_remove_index_list,need_remove_ue_id_list))
            #print("new_need_ue_index = {} new_need_beam_ue_id = {}".format(new_need_ue_index,new_need_beam_ue_id))
            return new_need_ue_index,new_need_beam_ue_id
        else:
            return need_ue_index,need_beam_ue_id
        
        
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
        

