from EventManager import EventManager
from BaseStation import BaseStation
from UserEquipment import UserEquipment
from NetworkSettings import NetworkSettings,SystemInfo,Simulation
from BeamTransmit import BeamUseFunction
from CellUser import CellUser
from BeamMapping import BeamMapping
import numpy as np
import random

ue_location_list = list() #UE座標 只有基地台需要
ue_overlap_location_list = list()
bs_location_list = list() #BS座標 只有基地台需要
all_ue_location_list = list()

def create_bs(event_manager):
    bs_x=0 #基地台初始位置設定
    bs_y=0
    frequency = 28000
    arrangement = int(round(np.sqrt(NetworkSettings.num_of_bs)))
    for i in range(NetworkSettings.num_of_bs):
        if(i % arrangement != 0 and i != 0): #基地台座標向上生成
            bs_y = bs_y + NetworkSettings.Neighbor_Distance
        if(i % arrangement == 0 and i != 0): #基地台座標向右生成
            bs_x = bs_x + NetworkSettings.Neighbor_Distance
            bs_y = bs_y - NetworkSettings.Neighbor_Distance * (arrangement-1)
        bs_location_list.append((bs_x,bs_y)) #記錄所有基地台座標

        bs = BaseStation(i, event_manager,bs_location_list)
        bs_id = "bs{}".format(i)
        NetworkSettings.object_info_dict[bs_id] = bs
        NetworkSettings.bs_id_list.append(bs_id)

        NetworkSettings.BS_center_frequency.append(frequency)
        frequency += (NetworkSettings.system_bandwidth / NetworkSettings.num_of_bs)
    BeamUseFunction.bs_location = bs_location_list
    #print("基地台座標 = ",bs_location_list)

def beam_clear(generate_user_point):
    if Simulation.beam_clear == True:
        if Simulation.beam_clear_mode == 0:
            generate_user_point.clear_beam()
        elif Simulation.beam_clear_mode == 1:
            generate_user_point.random_clear_beam()

def create_ue(event_manager,generate_user_point):
    for i in range(NetworkSettings.num_of_bs):
        for j in range(NetworkSettings.num_of_ue):
            location = generate_user_point.getRandomPointInrectangle(bs_location_list[i][0],bs_location_list[i][1],i) #丟入基地台x,y值
            ue_location_list.append(location) #記錄所有user座標
            all_ue_location_list.append(location)
            ue = UserEquipment(i*NetworkSettings.num_of_ue + j, event_manager)
            ue_id = "ue{}".format(i*NetworkSettings.num_of_ue + j)
            NetworkSettings.object_info_dict[ue_id] = ue
            NetworkSettings.ue_id_list.append(ue_id)
    #print("user不重疊區域座標 = ",ue_location_list)
def create_ue_overlap(event_manager,generate_user_point):
    overlap_start_num = NetworkSettings.num_of_bs * NetworkSettings.num_of_ue #重疊基地台ue_id的起始編號
    for i in range(NetworkSettings.num_of_bs):
        for j in range(NetworkSettings.num_of_ue_overlap):
            location = generate_user_point.getRandomPointInOverlap(bs_location_list[i][0],bs_location_list[i][1],i)
            ue_overlap_location_list.append(location)
            all_ue_location_list.append(location)
            ue = UserEquipment(overlap_start_num + i*NetworkSettings.num_of_ue_overlap + j, event_manager)
            ue_id = "ue{}".format(overlap_start_num + i*NetworkSettings.num_of_ue_overlap + j)
            NetworkSettings.object_info_dict[ue_id] = ue
            NetworkSettings.ue_id_list.append(ue_id)
    #print("NetworkSettings.ue_id_list = ",NetworkSettings.ue_id_list)
    #print("user重疊區域座標 = ",ue_overlap_location_list) 
def mapping_bs_and_ue(): #自動產生mapping關係
    overlap_start_num = NetworkSettings.num_of_bs * NetworkSettings.num_of_ue #重疊基地台ue_id的起始編號
    ue_id_number = len(NetworkSettings.ue_id_list)
    bs_id_number = len(NetworkSettings.bs_id_list)
    for i in range(ue_id_number): #所有UE
        BeamUseFunction.all_ue_location.append(all_ue_location_list[i])
        for j in range(bs_id_number): # 所有基地台
            if i < overlap_start_num: #小於overlap_start_num 不重疊UE座標
                bs_ue_x_distance = bs_location_list[j][0] - ue_location_list[i][0]
                bs_ue_y_distance = bs_location_list[j][1] - ue_location_list[i][1]
            else: #大於overlap_start_num 重疊UE座標
                bs_ue_x_distance = bs_location_list[j][0] - ue_overlap_location_list[i-overlap_start_num][0]
                bs_ue_y_distance = bs_location_list[j][1] - ue_overlap_location_list[i-overlap_start_num][1]
            #print("ue{}     bs{}".format(i,j))
            if np.sqrt(bs_ue_x_distance**2 + bs_ue_y_distance**2) < NetworkSettings.bs_range: #UE在基地台覆蓋範圍內
                NetworkSettings.ue_to_bs_mapping_table.setdefault("ue{}".format(i), [])
                NetworkSettings.bs_ue_distance.setdefault("ue{}".format(i), [])
                NetworkSettings.ue_to_bs_mapping_table["ue{}".format(i)].append("bs{}".format(j))
                NetworkSettings.bs_ue_distance['ue{}'.format(i)].append(np.sqrt(bs_ue_x_distance**2 + bs_ue_y_distance**2))
                
    #print("NetworkSettings.bs_ue_distance = ",NetworkSettings.bs_ue_distance)
    #print("NetworkSettings.ue_to_bs_mapping_table = ",NetworkSettings.ue_to_bs_mapping_table)
def bs_beam_neighbor(): #產生基地台之間的波束關係
    BeamMapping(bs_location_list,ue_overlap_location_list).execute()
    #print("NetworkSettings.bs_beam_neighbor = ",NetworkSettings.bs_beam_neighbor)
    #print("NetworkSettings.bs_neighbor = ",NetworkSettings.bs_neighbor)

def all_mode_data_clear():
    ue_location_list.clear()
    ue_overlap_location_list.clear()
    all_ue_location_list.clear()
    bs_location_list.clear()
    Simulation.mode += 1
    if Simulation.mode == 5: #記得要改成5
        Simulation.mode = 0

def main():
    event_manager = EventManager()
    generate_user_point = CellUser() #生成UE必要
    if 2*NetworkSettings.bs_range <= NetworkSettings.Neighbor_Distance: #判斷是否有dual-connected
        sys.exit("There is no base station that can be dual-connected")
    else:
        for system_round in range(SystemInfo.system_round):
            if Simulation.all_mode_test == True:
                Simulation.mode == 0 #系統方法從0開始跑
                for mode in range(5): #記得要改成5
                    create_bs(event_manager)
                    beam_clear(generate_user_point)
                    create_ue(event_manager,generate_user_point)
                    create_ue_overlap(event_manager,generate_user_point)
                    mapping_bs_and_ue()
                    bs_beam_neighbor()
                    event_manager.execute()
                    all_mode_data_clear()
            else:
                create_bs(event_manager)
                beam_clear(generate_user_point)
                create_ue(event_manager,generate_user_point)
                create_ue_overlap(event_manager,generate_user_point)
                mapping_bs_and_ue()
                bs_beam_neighbor()
                event_manager.execute()


if __name__ == '__main__':
    main()