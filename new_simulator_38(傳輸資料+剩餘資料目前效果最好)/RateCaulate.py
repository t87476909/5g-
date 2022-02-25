import numpy as np
import math
import random
from NetworkSettings import NetworkSettings, Simulation,SystemInfo
from BeamForming import BeamFormingFunction
    
class RateCaulate:
    def __init__(self,bs_id,need_ue_index,bs_transmit_state):
        self.bs_id = bs_id
        self.mapping_table = NetworkSettings.ue_to_bs_mapping_table
        self.distance = NetworkSettings.bs_ue_distance #儲存距離
        self.frequency = NetworkSettings.BS_center_frequency #中心頻率
        self.BS_antenna_gain = NetworkSettings.BS_antenna_gain
        self.UE_antenna_gain = NetworkSettings.UE_antenna_gain
        self.Thermal_noise = NetworkSettings.Thermal_noise_dbm
        self.bandwidth = NetworkSettings.system_bandwidth
        self.BS_power = NetworkSettings.BS_transmission_power
        self.Number_resource_block = NetworkSettings.Number_resource_block
        self.need_ue_index = need_ue_index
        self.beam_angle = NetworkSettings.beam_angle
        self.beam_number = int(360 / self.beam_angle)
        self.beam_index = (SystemInfo.system_time - 1) % self.beam_number #系統時間從1開始
        self.state = bs_transmit_state
        self.beam_neighbor = NetworkSettings.bs_beam_neighbor
        self.mode = Simulation.mode
        self.bs_number = int(self.bs_id.lstrip('bs'))

    def sinr_rate_Caulate(self): #https://ir.nctu.edu.tw/bitstream/11536/72785/1/025601.pdf
        need_pathloss = list() #https://www.electronics-notes.com/articles/antennas-propagation/propagation-overview/free-space-path-loss.php
        interference_pathloss = list()
        need_received_power = list()
        interference_received_power = list()
        sinr = list()
        current_rate_ue_index = list()
        noise_power = self.Thermal_noise + 10 * np.log10(self.bandwidth * (10 ** 6)) #dbm thermal noise power
        noise_power = 10 ** ((noise_power-30)/10) #Watt thermal noise power
        #print("self.distance = ",self.distance)
        for ue_id,map_bs in self.mapping_table.items(): #這個pathloss已經生成該bs下所有ue的pathloss了
            for bs_index in range(len(map_bs)):
                if map_bs[bs_index] == self.bs_id:
                    ue_index = NetworkSettings.ue_id_list.index(ue_id)
                    need_pathloss.append(20 * np.log10(self.distance[ue_id][bs_index]/1000) + 20 * np.log10(self.frequency[self.bs_number]) + 32.44 - self.BS_antenna_gain - self.UE_antenna_gain)
                    current_rate_ue_index.append(ue_index)
                else:
                    interference_pathloss.append(20 * np.log10(self.distance[ue_id][bs_index]/1000) + 20 * np.log10(self.frequency[self.bs_number]) + 32.44 - self.BS_antenna_gain - self.UE_antenna_gain)

        #print("need_pathloss = ",need_pathloss) #這個pathloss包含 該bs下的ue所有連接到其餘bs的path loss
        #print("interference_pathloss = ",interference_pathloss)
        
        for i in range(len(need_pathloss)):
            need_received_power.append(self.BS_power - need_pathloss[i] - 2.15) #dbm = dbm + db
            need_received_power[i] = 10 **((need_received_power[i]-30)/10) # bs下ue的接收power Watt
        for j in range(len(interference_pathloss)):
            interference_received_power.append(self.BS_power - interference_pathloss[j] - 2.15) #dbm = dbm + db
            interference_received_power[j] = 10 **((interference_received_power[j]-30)/10) # bs下ue連接到不同基地台的接收power Watt

        need_index = 0
        interference_index = 0
        interference_or_not = False #判斷目標bs是否有干擾

        for ue_id,map_bs in self.mapping_table.items():
            if self.bs_id in map_bs and len(map_bs) > 1: #表示該ue有其餘連接基地台可能會有干擾
                if self.state == 'static': #假若系統發出靜態波束(必定不重疊)
                    sinr.append(need_received_power[need_index] / noise_power)
                    need_index = need_index + 1
                else: #假若系統發出動態波束(有機率重疊)
                    for target_bs,neighbor_bs_dict in self.beam_neighbor.items(): #bs0': {'bs1': {0: None, 1: None, 2: 5, 3: None, 4: None, 5: None, 6: None, 7: None}
                        if self.bs_id == target_bs: #當前目標bs
                            for neighbor_bs,beam_relation in neighbor_bs_dict.items():
                                target_bs_beam = BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'][self.beam_index] #當前基地台發出波束
                                neighbor_bs_beam = BeamFormingFunction.bs_generator_beam_list[neighbor_bs]['time_before_last_time'][self.beam_index] #鄰居基地台發出波束
                                interference_index = interference_index + 1
                                if beam_relation[target_bs_beam] != None and beam_relation[target_bs_beam] == neighbor_bs_beam:
                                    interference = interference_received_power[interference_index]
                                    sinr.append(need_received_power[need_index] / (noise_power + interference))
                                    interference_or_not = True
                                    #print("目標基地台相交波束 = {} 鄰居基地台相交波束 = {} 當前基地台波束位置 = {} ".format(BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'],BeamFormingFunction.bs_generator_beam_list[neighbor_bs]['time_before_last_time'],self.beam_index))
                            #print("目標基地台波束 = {} 鄰居基地台波束 = {} 當前基地台位置 = {} ".format(BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'],BeamFormingFunction.bs_generator_beam_list[neighbor_bs]['time_before_last_time'],self.beam_index))
                            #print("目標基地台 = {} 鄰居基地台 = {} 當前基地台波束 = {} 鄰居基地台波束 = {} ".format(self.bs_id,neighbor_bs,target_bs_beam,neighbor_bs_beam))
                    if interference_or_not == False: #若該目標bs檢測後沒有interference
                        sinr.append(need_received_power[need_index] / noise_power)
                        need_index = need_index + 1
                #print("interference_or_not = ",interference_or_not)
            if self.bs_id in map_bs and len(map_bs) == 1: #該ue沒有干擾
                sinr.append(need_received_power[need_index] / noise_power)
                need_index = need_index + 1 

        sinr_db = 10 * np.log10(sinr) #np.array
        sinr_numpy = np.asarray(sinr)
        all_rate = self.bandwidth* (10 ** 6) * np.log2(1 + sinr_numpy) #因為sinr為負值 沒有data rate 收不到訊號
        all_rate_mpbs_sec = all_rate * (10**-6)
        all_rb_rate_ms = all_rate_mpbs_sec / 1000 / self.Number_resource_block

        need_rb_rate_ms = list()
        need_current_rate_ue_index = list()
        for i in range(len(all_rb_rate_ms)):
            if i in self.need_ue_index:
                need_rb_rate_ms.append(all_rb_rate_ms[i])
                need_current_rate_ue_index.append(current_rate_ue_index[i])

        #print("all_ue_rate_Mbps = ",all_rate_mpbs_sec)
        #print("all_current_rate_ue_index = ",current_rate_ue_index)
        #print("all_sinr = ",sinr_numpy)
        #print("all_sinr_db = ",sinr_db)
        #print("all_rb_rate_Mbp_ms = ",all_rb_rate_ms)
        #print("need_rb_rate_ms = ",need_rb_rate_ms)
        #print("need_current_rate_ue_index = ",need_current_rate_ue_index)
        #print("bs_id = ",self.bs_id)
        #print("self.mapping_table",self.mapping_table)

        return need_rb_rate_ms,need_current_rate_ue_index
    
    def snr_rate_Caulate(self): #https://ir.nctu.edu.tw/bitstream/11536/72785/1/025601.pdf
        need_pathloss = list() #https://www.electronics-notes.com/articles/antennas-propagation/propagation-overview/free-space-path-loss.php
        need_received_power = list()
        snr = list()
        current_rate_ue_index = list()
        noise_power = self.Thermal_noise + 10 * np.log10(self.bandwidth * (10 ** 6)) #dbm thermal noise power
        noise_power = 10 ** ((noise_power-30)/10) #Watt thermal noise power
        #print("self.distance = ",self.distance)
        for ue_id,map_bs in self.mapping_table.items(): #這個pathloss已經生成該bs下所有ue的pathloss了
            for bs_index in range(len(map_bs)):
                if map_bs[bs_index] == self.bs_id:
                    ue_index = NetworkSettings.ue_id_list.index(ue_id)
                    need_pathloss.append(20 * np.log10(self.distance[ue_id][bs_index]/1000) + 20 * np.log10(self.frequency[self.bs_number]) + 32.44 - self.BS_antenna_gain - self.UE_antenna_gain)
                    current_rate_ue_index.append(ue_index)

        #print("need_pathloss = ",need_pathloss) #這個pathloss包含 該bs下的ue所有連接到其餘bs的path loss
        #print("interference_pathloss = ",interference_pathloss)
        
        for i in range(len(need_pathloss)):
            need_received_power.append(self.BS_power - need_pathloss[i] - 2.15) #dbm = dbm + db
            need_received_power[i] = 10 **((need_received_power[i]-30)/10) # bs下ue的接收power Watt

        need_index = 0
        for ue_id,map_bs in self.mapping_table.items():
            if self.bs_id in map_bs:
                snr.append(need_received_power[need_index] / noise_power)
                need_index = need_index + 1 

        snr_db = 10 * np.log10(snr) #np.array
        snr_numpy = np.asarray(snr)
        all_rate = self.bandwidth* (10 ** 6) * np.log2(1 + snr_numpy) #因為snr為負值 沒有data rate 收不到訊號
        all_rate_mpbs_sec = all_rate * (10**-6)
        all_rb_rate_ms = all_rate_mpbs_sec / 1000 / self.Number_resource_block
        need_rb_rate_ms = list()
        need_current_rate_ue_index = list()
        #print("self.need_ue_index = ",self.need_ue_index)
        #print("all_rb_rate_ms = ",all_rb_rate_ms)
        for i in range(len(all_rb_rate_ms)):
            if i in self.need_ue_index:
                need_rb_rate_ms.append(all_rb_rate_ms[i])
                need_current_rate_ue_index.append(current_rate_ue_index[i])
        #print("need_current_rate_ue_index = ",need_current_rate_ue_index)
        #print("current_rate_ue_index = ",current_rate_ue_index)
        return need_rb_rate_ms,need_current_rate_ue_index