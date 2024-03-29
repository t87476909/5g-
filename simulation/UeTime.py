from BeamPredict import PredictControlValue
from BeamTransmit import BeamUseFunction
from NetworkSettings import NetworkSettings,SystemInfo,Simulation

class TimeControlValue:
    bs_beam_ue = dict() #儲存該基地台beam下的ue
    ue_beam_allocated = dict() #儲存該ue在該beam的時間是否已經醒來(避免重複基地台計算到)

class UeTime:
    def __init__(self,bs_id):
        self.bs_beam_ue = TimeControlValue.bs_beam_ue #example: bs_id:{beam:[ue_id]}
        self.ue_beam_allocated = TimeControlValue.ue_beam_allocated #example ue_id:{beam:0 or 1}
        self.beam_transmit = BeamUseFunction.bs_transmit_beam #example: bs_id:[beam]
        self.beam_state = BeamUseFunction.bs_transmit_state 
        self.miss_beam = PredictControlValue.bs_miss_beam #example: bs_id:[miss_beam] (before的beam miss)
        self.ue_id = NetworkSettings.ue_id_list
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.mode = Simulation.mode
        self.bs_id = bs_id
        self.last_bs_id = NetworkSettings.bs_id_list[-1]
        
        if self.bs_id not in self.bs_beam_ue:
            self.bs_beam_ue.setdefault("{}".format(self.bs_id),dict())
            for i in range(self.beam_number):
                self.bs_beam_ue[self.bs_id][i] = list()

        for i in range(len(self.ue_id)):
            if self.ue_id[i] not in Simulation.ue_open_time:
                Simulation.ue_open_time[self.ue_id[i]] = 0 #宣告ue預測醒來的總時間
                self.ue_beam_allocated[self.ue_id[i]] = dict()
                for j in range(self.beam_number):
                    self.ue_beam_allocated[self.ue_id[i]][j] = 0 #0預設為該beam沒有醒過來
                

    def ue_time_calculate(self,current_ue_index):
        
        current_beam_index = (SystemInfo.system_time - 1) % self.beam_number
        need_beam = self.beam_transmit[self.bs_id][current_beam_index]
        #if Simulation.ue_move_control == True and NetworkSettings.UE_speed != 0:
        #	self.bs_beam_ue[self.bs_id][need_beam].clear()
        for i in range(len(current_ue_index)):
            if current_ue_index[i] not in self.bs_beam_ue[self.bs_id][need_beam]:
                self.bs_beam_ue[self.bs_id][need_beam].append(current_ue_index[i])

        if self.beam_index == 0:
            if self.beam_state == 'static': #靜態波束
                for beam,ue_id in self.bs_beam_ue[self.bs_id].items(): #beam = 0 ~ 7 ue_id = 該beam底下的ue_id
                    for static_i in range(len(ue_id)):
                        target_ue = "ue{}".format(ue_id[static_i])
                            #print("target_ue(要增加的ue) = ",target_ue)
                        if self.ue_beam_allocated[target_ue][beam] == 0:
                            self.ue_beam_allocated[target_ue][beam] = 1
                            Simulation.ue_open_time[target_ue] += 1 #靜態波束的ue每個都會輪到
            else: #動態波束
                for index in range(self.beam_number):
                    for beam,ue_id in self.bs_beam_ue[self.bs_id].items():
                        current_beam = self.beam_transmit[self.bs_id][index]
                        if beam == current_beam:
                            for dynamic_i in range(len(ue_id)):
                                target_ue = "ue{}".format(ue_id[dynamic_i])
                                if self.ue_beam_allocated[target_ue][index] == 0:
                                    if self.mode == 3:
                                        self.ue_beam_allocated[target_ue][index] = 1
                                        Simulation.ue_open_time[target_ue] += SystemInfo.ntu_T_time
                                    else:
                                        self.ue_beam_allocated[target_ue][index] = 1
                                        Simulation.ue_open_time[target_ue] += 1
                        else:
                            pass
            if self.bs_id == self.last_bs_id:
                for target_ue,beam_map in self.ue_beam_allocated.items():
                    for beam,allocated in beam_map.items():
                        self.ue_beam_allocated[target_ue][beam] = 0                    
        else:
            pass