from NetworkSettings import NetworkSettings
from NetworkSettings import SystemInfo
from NetworkSettings import Simulation
from sklearn import preprocessing 
import numpy as np
import math
import cmath

class ValueControlData:
    beam_throughput = dict() #儲存基地台波束的剩餘流量
    transmission_beam_throughput = dict() #儲存基地台波束的發射流量
    bs_throughput = dict() #儲存該基地台的流量大小
    beam_probability = dict() #儲存基地台波束的生成機率

class ValueCalculate: #基地台每打一次波束就會執行一次 (當執行beam_number次的時候就會進行統整)
    def __init__(self,bs_id,bs_beamforming_list,ue_data,allowed_data,current_rate_ue_index,bs_transmit_state):
        self.bs_id = bs_id
        self.beam_number = int(360 / NetworkSettings.beam_angle)
        self.beamforming_list = bs_beamforming_list #波束列表
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.need_beam = self.beamforming_list[self.beam_index] #當前時間輪到的波束
        self.ue_data_remaining = ue_data #example: ue_id:{data type:data_amount}
        self.ue_allowed_data = allowed_data
        self.ue_index = current_rate_ue_index
        self.mode = Simulation.mode
        self.state = bs_transmit_state

        if self.beam_index == 1 and SystemInfo.system_time !=0: #SystemInfo.system_time是從1開始
            for i in range(self.beam_number):
                ValueControlData.beam_throughput[self.bs_id][i] = 0 #將該基地台所有的波束流量都設為0(預設該波束底下沒有ue)
                if self.state == 'static': #mode3才會用到
                    ValueControlData.transmission_beam_throughput[self.bs_id][i] = 0
                #ValueControlData.transmission_beam_throughput[self.bs_id][i] = 0

            if self.bs_id not in ValueControlData.bs_throughput:
                ValueControlData.bs_throughput[self.bs_id] = {'time_before_last_time': None,'last_time': None} #將該基地台所有流量都設為0

    def execute(self):
        self.beam_throughput_calculate() #當前傳輸流量計算
        self.transmission_beam_throughput_calculate() #當前剩餘流量計算
        self.probability_calculate()

    def beam_throughput_calculate(self): #需要波束流量來得知優先度 所以需要將波束流量全部進行加總跟其他基地台做比較
        
        for ue_id,data_type in self.ue_data_remaining.items():
            ue = int(ue_id.lstrip('ue'))
            if ue in self.ue_index:
                for data_type,data_amount in data_type.items():
                    ValueControlData.beam_throughput[self.bs_id][self.need_beam] += data_amount
        #print("bs_id = {} ValueControlData.beam_throughput[self.bs_id] = {} needbeam = {} ".format(self.bs_id,ValueControlData.beam_throughput[self.bs_id],self.need_beam))
    def transmission_beam_throughput_calculate(self):
        if self.state == 'static':
            for ue_id,data_type in self.ue_allowed_data.items():
                ue = int(ue_id.lstrip('ue'))
                if ue in self.ue_index:
                    for data_type,data_amount in data_type.items():
                        ValueControlData.transmission_beam_throughput[self.bs_id][self.need_beam] += data_amount
        #print("ValueControlData.transmission_beam_throughput[self.bs_id] = ",ValueControlData.transmission_beam_throughput[self.bs_id])

    def probability_calculate(self):
        if self.beam_index == 0 and SystemInfo.system_time !=0: #波束輪過一輪才會執行一次 波束為 0~7
            if self.mode == 4:
                self.beam_aware_cross_probability_calculate()
            #假若流量為 0 則將他所生成的機率分給其他非0波束
            else:
                z_normalization_throughtput = preprocessing.scale(ValueControlData.beam_throughput[self.bs_id], axis=0, with_mean=True, with_std=True, copy=True)
                #z_transmission_normalization_throughtput = preprocessing.scale(ValueControlData.transmission_beam_throughput[self.bs_id], axis=0, with_mean=True, with_std=True, copy=True)
                probability = self.softmax(z_normalization_throughtput)
                #transmission_probability = self.softmax(z_transmission_normalization_throughtput)

                if 0 in ValueControlData.beam_throughput[self.bs_id]: #判斷是否有流量為0的波束
                    zero_throughput_probability = 0
                    throughput_probability = 0
                    for zero_probability_index in range(len(ValueControlData.beam_throughput[self.bs_id])): #紀錄beam流量為0的機率總和
                        if ValueControlData.beam_throughput[self.bs_id][zero_probability_index] == 0:
                            zero_throughput_probability += probability[zero_probability_index]
                            probability[zero_probability_index] = 0
                    for probability_index in range(len(ValueControlData.beam_throughput[self.bs_id])):
                        if ValueControlData.beam_throughput[self.bs_id][probability_index] != 0:
                            probability[probability_index] = probability[probability_index] / (1 - zero_throughput_probability)
                            throughput_probability += probability[probability_index]

                if sum(probability) == 0: #表示基地台底下完全沒有ue
                    for i in range(len(probability)):
                        probability[i] = 1 / self.beam_number
                '''
                if 0 in ValueControlData.transmission_beam_throughput[self.bs_id]: #判斷是否有流量為0的波束
                    zero_throughput_probability = 0
                    throughput_probability = 0
                    for zero_probability_index in range(len(ValueControlData.transmission_beam_throughput[self.bs_id])): #紀錄beam流量為0的機率總和
                        if ValueControlData.transmission_beam_throughput[self.bs_id][zero_probability_index] == 0:
                            zero_throughput_probability += transmission_probability[zero_probability_index]
                            transmission_probability[zero_probability_index] = 0
                    for probability_index in range(len(ValueControlData.transmission_beam_throughput[self.bs_id])):
                        if ValueControlData.transmission_beam_throughput[self.bs_id][probability_index] != 0:
                            transmission_probability[probability_index] = transmission_probability[probability_index] / (1 - zero_throughput_probability)
                            throughput_probability += transmission_probability[probability_index]
                if sum(transmission_probability) == 0: #表示基地台底下完全沒有ue
                    for j in range(len(transmission_probability)):
                        transmission_probability[i] = 1 / self.beam_number
                for index in range(len(probability)):
                    probability[index] = (probability[index] + transmission_probability[index])/2
                '''
                ValueControlData.beam_probability[self.bs_id] = probability
                #print("final probability = ",probability)

    def beam_aware_cross_probability_calculate(self):
        zero_count = 0
        probability = list()
        for beam_index in range(self.beam_number):
            probability.append(0) #機率預設為0
            if ValueControlData.transmission_beam_throughput[self.bs_id][beam_index] == 0:
                zero_count += 1 #計算有幾個流量為0的波束
                probability[beam_index] = 0
        total_transmission_throughput = sum(ValueControlData.transmission_beam_throughput[self.bs_id])
        multiply_proportions = 1 / total_transmission_throughput
        if self.beam_number != zero_count:
            for i in range(self.beam_number):
                if ValueControlData.transmission_beam_throughput[self.bs_id][i] != 0:
                    need_probability = ValueControlData.transmission_beam_throughput[self.bs_id][i] * multiply_proportions
                    probability[i] = need_probability
        else: #若靜態波束下沒有流量
            need_probability = 1 / self.beam_number
            for j in range(self.beam_number):
                probability[j] = need_probability
        ValueControlData.beam_probability[self.bs_id] = probability

    def softmax(self,throughtput): #區域總流量正規化
        throughtput = throughtput - np.max(throughtput)
        exp_throughtput = np.exp(throughtput)
        softmax_throughtput = exp_throughtput / np.sum(exp_throughtput)
        return softmax_throughtput


    '''
    def ntu_probability_calculate(self):
        zero_count = 0
        probability = list()
        for beam_index in range(self.beam_number):
            probability.append(0) #機率預設為0
            if ValueControlData.transmission_beam_throughput[self.bs_id][beam_index] == 0:
                zero_count += 1
                probability[beam_index] = 0
                if ValueControlData.transmission_beam_throughput[self.bs_id][beam_index] == 0

        if self.beam_number != zero_count:
            need_probability = 1 / (self.beam_number - zero_count)
            for i in range(self.beam_number):
                if ValueControlData.transmission_beam_throughput[self.bs_id][i] != 0:
                    probability[i] = need_probability
        else: #若靜態波束下沒有流量
            need_probability = 1 / self.beam_number
            for j in range(self.beam_number):
                probability[j] = need_probability
        ValueControlData.beam_probability[self.bs_id] = probability
    '''