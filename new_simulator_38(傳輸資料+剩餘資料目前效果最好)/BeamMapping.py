from NetworkSettings import NetworkSettings
import numpy as np
import math
import cmath

class BeamMapping:
    def __init__(self,bs_location,ue_overlap_location_list):
        self.beam_angle = NetworkSettings.beam_angle
        self.beam_number = round(360 / self.beam_angle)
        self.bs_list = NetworkSettings.bs_id_list
        self.bs_location = bs_location
        self.ue_overlap_location = ue_overlap_location_list
        self.neighbor_distance = NetworkSettings.Neighbor_Distance

        self.num_bs = NetworkSettings.num_of_bs
        self.num_ue = NetworkSettings.num_of_ue
        self.num_overlap_ue = NetworkSettings.num_of_ue_overlap
        self.mapping_table = NetworkSettings.ue_to_bs_mapping_table
        self.beam_number = round(360 / NetworkSettings.beam_angle)

    def execute(self):
        self.mapping()

    def mapping(self):
        for i in range(len(self.bs_location)):
            NetworkSettings.bs_neighbor.setdefault("bs{}".format(i),list())
            NetworkSettings.bs_neighbor["bs{}".format(i)].append("bs{}".format(i))
            for j in range(len(self.bs_location)):
                if self.bs_location[i][0] == self.bs_location[j][0]: #bs間的x相同
                    if (self.bs_location[i][1] + self.neighbor_distance) == self.bs_location[j][1]: #y往上一個distance單位
                        #position = 1
                        self.neighbor_add(i,j)
                    if (self.bs_location[i][1] - self.neighbor_distance) == self.bs_location[j][1]: #y往下一個distance單位
                        #position = 2
                        self.neighbor_add(i,j)
                if self.bs_location[i][1] == self.bs_location[j][1]: #bs間的y相同
                    if (self.bs_location[i][0] + self.neighbor_distance) == self.bs_location[j][0]: #x往右一個distance單位
                        #position = 3
                        self.neighbor_add(i,j)
                    if (self.bs_location[i][0] - self.neighbor_distance) == self.bs_location[j][0]: #x往左一個distance單位
                        #position = 4
                        self.neighbor_add(i,j)
    
    def neighbor_add(self,i,j):

        NetworkSettings.bs_neighbor.setdefault("bs{}".format(i),list())
        NetworkSettings.bs_neighbor["bs{}".format(i)].append("bs{}".format(j))

        NetworkSettings.bs_beam_neighbor.setdefault("bs{}".format(i),dict())
        NetworkSettings.bs_beam_neighbor["bs{}".format(i)]["bs{}".format(j)] = dict()
        for target_bs in range(self.beam_number):
            NetworkSettings.bs_beam_neighbor["bs{}".format(i)]["bs{}".format(j)][target_bs] = None
        
        target_ue_beam_list,neighbor_ue_beam_list = self.beam_neighbor(i,j) #該基地台的波束連接關係
        #target_ue_beam_list = list(set(target_ue_beam_list)) #刪除重複元素 我們僅需要其中連結的關係
        #neighbor_ue_beam_list = list(set(neighbor_ue_beam_list))
        #print("target_ue_beam_list = ",target_ue_beam_list)
        #print("neighbor_ue_beam_list = ",neighbor_ue_beam_list)
        for beam_neighbor_index in range(len(target_ue_beam_list)):
            NetworkSettings.bs_beam_neighbor["bs{}".format(i)]["bs{}".format(j)][target_ue_beam_list[beam_neighbor_index]] = neighbor_ue_beam_list[beam_neighbor_index]

    def beam_neighbor(self,target_bs,neighbor_bs):    
        location_index_list = list() #該基地台的底下ue的座標index
        target_ue_beam_list = list()
        neighbor_ue_beam_list = list()
        
        overlap_start_num = self.num_ue * self.num_bs #重疊區域位置起始

        target_bs_location = self.bs_location[target_bs]
        neighbor_bs_location = self.bs_location[neighbor_bs]
        
        target_bs_id = "bs" + str(target_bs)
        neighbor_bs_id = "bs" + str(neighbor_bs)

        for ue_id,map_bs in self.mapping_table.items():
            if target_bs_id in map_bs and neighbor_bs_id in map_bs:
                ue_index = NetworkSettings.ue_id_list.index(ue_id) #所有ue的位置
                location_index_list.append(ue_index - overlap_start_num) #求重疊區域的ue位置

        for j in range(len(location_index_list)):
            if location_index_list[j] >= 0:
                ue_location = self.ue_overlap_location[location_index_list[j]]
                target_ue_beam_list.append(self.beamclassification(ue_location,target_bs_location)) #目標與鄰居基地台的ue在哪個波束底下
                neighbor_ue_beam_list.append(self.beamclassification(ue_location,neighbor_bs_location)) #目標與鄰居基地台的ue在哪個波束底下        
        #print("target_bs_id = {} target_beam_list = {}".format(target_bs_id,target_ue_beam_list))
        #print("neighbor_bs_id = {} neighbor_beam_list = {}".format(neighbor_bs_id,neighbor_ue_beam_list))
        
        return target_ue_beam_list,neighbor_ue_beam_list       

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