from NetworkSettings import NetworkSettings,Simulation
from BeamTransmit import BeamUseFunction
from CellUser import CellUser
from collections import Counter
import numpy as np
import math
import cmath
import random
import copy

class UeMove:
    def __init__(self):
        self.mapping_table = NetworkSettings.ue_to_bs_mapping_table
        self.bs_beam_neighbor = NetworkSettings.bs_beam_neighbor #bs_id:{bs_id:{beam:{beam}}}
        self.distance = NetworkSettings.bs_ue_distance #ue:bs0 distance 、 bs1 distance
        self.move_speed = NetworkSettings.UE_speed
        self.all_ue_location = BeamUseFunction.all_ue_location #location..overlap --> 依照ue_id的順序
        self.bs_location = BeamUseFunction.bs_location
        self.ue_id_list = NetworkSettings.ue_id_list
        self.bs_id_list = NetworkSettings.bs_id_list
        self.bs_number = NetworkSettings.num_of_bs
        self.bs_range = NetworkSettings.bs_range
        self.bs = NetworkSettings.object_info_dict
        self.CellUser = CellUser()
        self.mode = Simulation.mode
        self.overlap_ue_id_list = list()
        self.beam_angle = NetworkSettings.beam_angle

    def execute(self):
        NetworkSettings.record_ue_connect_bs = copy.deepcopy(self.mapping_table) #進行前一次的ue connect bs的複製動作
        self.ue_location_move()
        self.mapping_ue_to_bs()
        self.bs_data_change()
        if self.mode == 0 or self.mode == 1:
            self.beam_neighbor_change()

    def ue_location_move(self): #移動時要省視是否在邊界(不然超出會造成事件錯誤)
        for i in range(len(self.all_ue_location)): #所有ue座標移動
            Distribution_direction = np.random.randint(1,4) # 移動方向 1 ~ 4(上下左右)
            Distribution_speed_km = np.random.randint(0,self.move_speed) #
            Distribution_speed_m = Distribution_speed_km * 1000 / 60 / 60 # km/hr -> m / sec
            if Distribution_direction == 1: #上
                self.all_ue_location[i][1] += Distribution_speed_m
            elif Distribution_direction == 2: #下
                self.all_ue_location[i][1] -= Distribution_speed_m
            elif Distribution_direction == 3: #左
                self.all_ue_location[i][0] -= Distribution_speed_m
            else: #右
                self.all_ue_location[i][0] += Distribution_speed_m

    def mapping_ue_to_bs(self): #mapping關係重新梳理
        for i in range(len(self.ue_id_list)): #所有UE遍立
            self.mapping_table["ue{}".format(i)].clear() #要把舊資料刪除
            self.distance['ue{}'.format(i)].clear() #要把舊資料刪除
            for j in range(len(self.bs_id_list)): # 所有基地台
                bs_ue_x_distance = self.bs_location[j][0] - self.all_ue_location[i][0]
                bs_ue_y_distance = self.bs_location[j][1] - self.all_ue_location[i][1]
                if math.sqrt(bs_ue_x_distance**2 + bs_ue_y_distance**2) < self.bs_range: #UE在基地台覆蓋範圍內
                    self.mapping_table["ue{}".format(i)].append("bs{}".format(j))
                    self.distance['ue{}'.format(i)].append(math.sqrt(bs_ue_x_distance**2 + bs_ue_y_distance**2))
            if len(self.mapping_table["ue{}".format(i)]) == 0: #表示該ue沒有在任何基地台的範圍內
                self.check_ue_in_bs(i)
            elif len(self.mapping_table["ue{}".format(i)]) >= 2: #表示該ue在overlapping的ue_list內
                self.overlap_ue_id_list.append(i)
                    
    def check_ue_in_bs(self,ue):
        #Distribution_type = np.random.randint(1,3) # 1~2(1為not overlap 2為overlap)
        Distribution_bs = np.random.randint(0,self.bs_number) #隨機分配基地台 bs0~ bs_number-1
        bs_x_location = self.bs_location[Distribution_bs][0]
        bs_y_location = self.bs_location[Distribution_bs][1]
        ue_location = self.CellUser.getRandomPointInrectangle(bs_x_location,bs_y_location,Distribution_bs) #重新生成一個新的座標給他(還是會依照beam_clear的規則走)
        #ue_location = self.CellUser.getRandomPointInOverlap(bs_x_location,bs_y_location,Distribution_bs) #重新生成一個新的座標給他(還是會依照beam_clear的規則走)
        self.mapping_table["ue{}".format(ue)].append("bs{}".format(Distribution_bs)) #為了省麻煩ue一律生成在不重疊的區域
        self.all_ue_location[ue] = ue_location #座標更新

        distance_x = bs_x_location - ue_location[0]
        distance_y = bs_y_location - ue_location[1]
        self.distance['ue{}'.format(ue)].append(math.sqrt(distance_x**2 + distance_y**2)) #距離更新

    def beam_neighbor_change(self):

        for i in range(len(self.overlap_ue_id_list)):
            overlap_ue_location = self.all_ue_location[self.overlap_ue_id_list[i]]            
            overlap_ue_id = "ue{}".format(self.overlap_ue_id_list[i])
            overlap_bs_list = self.mapping_table[overlap_ue_id] #
            target_bs = int(overlap_bs_list[0].lstrip('bs'))
            neighbor_bs = int(overlap_bs_list[1].lstrip('bs'))

            target_bs_location = self.bs_location[target_bs]
            neighbor_bs_location = self.bs_location[neighbor_bs]

            target_beam = self.beamclassification(overlap_ue_location,target_bs_location)
            neighbor_beam = self.beamclassification(overlap_ue_location,neighbor_bs_location)
            if target_beam and neighbor_beam != None:
                NetworkSettings.bs_beam_neighbor["bs{}".format(target_bs)]["bs{}".format(neighbor_bs)][target_beam] = neighbor_beam
                NetworkSettings.bs_beam_neighbor["bs{}".format(neighbor_bs)]["bs{}".format(target_bs)][neighbor_beam] = target_beam

    def beamclassification(self,ue_location,bs_location): #判斷ue處於哪個基地台的beam底下
        distance_x = ue_location[0] - bs_location[0] #x間距
        distance_y = ue_location[1] - bs_location[1] #y間距
        polar_location = complex(distance_x,distance_y)
        polar_location = cmath.polar(polar_location)
        angle = math.degrees(polar_location[1])
        if angle < 0:
            angle = 360 + angle
        beam = math.floor(angle / self.beam_angle) #判別在哪個波束下 
        return beam

    def bs_data_change(self):
        change_ue_list = list() #紀錄有更動的ue
        for ue_id_key,value in self.mapping_table.items():
            if self.mapping_table[ue_id_key] != NetworkSettings.record_ue_connect_bs[ue_id_key]: #舊bs ue資料丟給新bs
                change_ue_list.append(ue_id_key)
                send_bs_id = NetworkSettings.record_ue_connect_bs[ue_id_key] #這是舊的
                receive_bs_id = self.mapping_table[ue_id_key] #這是新的
                for i in range(len(send_bs_id)):
                    for j in range(len(receive_bs_id)):
                        #print("send_bs_id = ",send_bs_id[i])
                        #print("receive_bs_id = ",receive_bs_id[j])
                        if send_bs_id[i] != receive_bs_id[j]: # 避免重複送給重複
                            if ue_id_key in self.bs[receive_bs_id[j]].queue_for_ue: #新的bs已經有該ue_id了就會疊加
                                send_ue_id_data = Counter(self.bs[send_bs_id[i]].queue_for_ue[ue_id_key])
                                receive_ue_id_data = Counter(self.bs[receive_bs_id[j]].queue_for_ue[ue_id_key])
                                #print("send_ue_id_data = ",send_ue_id_data)
                                #print("receive_ue_id_data = ",receive_ue_id_data)
                                receive_ue_id_data = dict(receive_ue_id_data + send_ue_id_data) #舊的疊加新的
                                #send_ue_id_trigger_time = Counter(self.bs[send_bs_id[i]].queue_trigger_time[ue_id_key])
                                #receive_ue_id_trigger_time = Counter(self.bs[receive_bs_id[i]].queue_trigger_time[ue_id_key])
                                #print("send_ue_id_trigger_time = ",send_ue_id_trigger_time)
                                #print("receive_ue_id_trigger_time = ",receive_ue_id_trigger_time)
                                #receive_ue_id_trigger_time = dict(receive_ue_id_trigger_time + send_ue_id_trigger_time)

                            else: #新的bs沒有該ue_id了更新
                                #print("ue_id_key = ",ue_id_key)
                                #print("self.bs[receive_bs_id[j]].queue_for_ue = ",self.bs[receive_bs_id[j]].queue_for_ue)
                                #print("self.bs[send_bs_id[i]].queue_for_ue = ",self.bs[send_bs_id[i]].queue_for_ue)
                                self.bs[receive_bs_id[j]].queue_for_ue[ue_id_key] = self.bs[send_bs_id[i]].queue_for_ue[ue_id_key] #舊的丟給新的
                                self.bs[receive_bs_id[j]].queue_trigger_time[ue_id_key] = self.bs[send_bs_id[i]].queue_trigger_time[ue_id_key] #舊的丟給新的
                    if send_bs_id[i] not in receive_bs_id: #不重複的bs
                        del self.bs[send_bs_id[i]].queue_for_ue[ue_id_key] #舊bs ue資料刪除)
                        del self.bs[send_bs_id[i]].queue_trigger_time[ue_id_key] #舊bs ue資料刪除
        #print("change_ue_list = ",change_ue_list)