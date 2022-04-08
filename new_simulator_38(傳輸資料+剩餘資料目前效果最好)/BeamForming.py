from NetworkSettings import NetworkSettings
from NetworkSettings import SystemInfo,Simulation
from ValueCalculate import ValueControlData
from ProportionalFair import ProportionalFairControlValue
import numpy as np
import math
import cmath
#beamforming -> beamsearch -> beam
class BeamFormingFunction:
    bs_generator_beam_list = dict() #儲存基地台所產生的波束
    control_variable = dict() #儲存系統控制的字典
    bs_generator_beam_state = dict() #產生的波束種類
    location_beam_list = dict() #儲存location方法的beam
    #ntu_control_variable = dict() #儲存台大系統控制的字典

class BeamForming:
    def __init__(self,bs_id):
        self.beamforming_list = list() #存取該基地台的波束排程
        self.beam_angle = NetworkSettings.beam_angle
        self.bs_id = bs_id
        self.beam_number = int(360 / self.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.location_beam_index = (SystemInfo.system_time - 1) % self.beam_number
        self.max_control_variable = SystemInfo.control_variable
        self.mode = Simulation.mode

        if self.bs_id not in BeamFormingFunction.control_variable:
            BeamFormingFunction.control_variable[self.bs_id] = 0
            BeamFormingFunction.location_beam_list[self.bs_id] = list()
            BeamFormingFunction.bs_generator_beam_list[self.bs_id] = {'time_before_last_time':[],'last_time':[]}
            BeamFormingFunction.bs_generator_beam_state[self.bs_id] = {'before_last_time_state':0,'last_time_state':0}

        
    def execute(self):

        if self.mode == 4:
            beam_priority_dict = ProportionalFairControlValue.location_beam_priority[self.bs_id]
            max_priority_beam = max(beam_priority_dict, key=beam_priority_dict.get)
            if len(BeamFormingFunction.location_beam_list[self.bs_id]) < self.beam_number:
                BeamFormingFunction.location_beam_list[self.bs_id].append(max_priority_beam)
            else: #波束更新
                BeamFormingFunction.location_beam_list[self.bs_id][self.location_beam_index] = max_priority_beam
            #if self.bs_id == 'bs0':
            #    print("ProportionalFairControlValue.location_beam_priority[self.bs_id] = ",ProportionalFairControlValue.location_beam_priority[self.bs_id])
            #    print("bs_id = {} BeamFormingFunction.location_beam_list[self.bs_id] = {}".format(self.bs_id,BeamFormingFunction.location_beam_list[self.bs_id]))

        if self.beam_index == 0:
            if self.mode <= 1: #為我的方法(靜態加動態)
                self.generator_dynamic_beam() #純動態
                '''
                if BeamFormingFunction.control_variable[self.bs_id] == 0: # V = 0 則指產生動態波束
                    BeamFormingFunction.control_variable[self.bs_id] += 1
                    self.generator_dynamic_beam() #產生動態波束

                elif BeamFormingFunction.control_variable[self.bs_id] < self.max_control_variable - 1: # V < max-1
                    BeamFormingFunction.control_variable[self.bs_id] += 1
                    self.generator_dynamic_beam() #產生動態波束

                #elif BeamFormingFunction.control_variable[self.bs_id] > self.max_control_variable - 1: # V > max-1 產生靜態波束
                else:
                    BeamFormingFunction.control_variable[self.bs_id] += 1
                    self.generator_static_beam() #產生靜態波束
                    if BeamFormingFunction.control_variable[self.bs_id] == self.max_control_variable + 1: #記得改加1
                        BeamFormingFunction.control_variable[self.bs_id] = 0
                '''
            elif self.mode == 2: #純靜態波束
                self.generator_static_beam() #產生靜態波束
            elif self.mode == 3: #台大論文參考波束
                self.generator_ntu_beam()
            elif self.mode == 4: #beam_Aware_cross layer DRX Design for 5G mmwave...
                self.generator_location_beam() 
                #self.generator_cross_beam()


    def generator_static_beam(self):
        for i in range(self.beam_number):
            self.beamforming_list.append(i)
        if self.mode == 0 or self.mode == 1 or self.mode == 2:
            BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'] = BeamFormingFunction.bs_generator_beam_list[self.bs_id]['last_time'] 
            BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state'] = BeamFormingFunction.bs_generator_beam_state[self.bs_id]['last_time_state']
            BeamFormingFunction.bs_generator_beam_list[self.bs_id]['last_time'] = self.beamforming_list
            BeamFormingFunction.bs_generator_beam_state[self.bs_id]['last_time_state'] = 'static'
        else:
            BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'] = self.beamforming_list 
            BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state'] = 'static'

    def generator_dynamic_beam(self):
        dynamic_beam_list = list()

        for i in range(self.beam_number):
            dynamic_beam_list.append(i) #建立動態波束用的列表範例 0 ~ 7

        #print("sum = {} ValueControlData.beam_probability[self.bs_id] = {} ".format(sum(ValueControlData.beam_probability[self.bs_id]),ValueControlData.beam_probability[self.bs_id]))
        for j in range(self.beam_number):
            self.beamforming_list.append(np.random.choice(dynamic_beam_list,p = ValueControlData.beam_probability[self.bs_id])) #生成動態隨機波束
        
        if self.mode == 0 or self.mode == 1 or self.mode == 2:
            if BeamFormingFunction.bs_generator_beam_list[self.bs_id]['last_time'] == None:
                BeamFormingFunction.bs_generator_beam_list[self.bs_id]['last_time'] = self.beamforming_list 
                BeamFormingFunction.bs_generator_beam_state[self.bs_id]['last_time_state'] = 'dymaic' 
            else:
                BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'] = BeamFormingFunction.bs_generator_beam_list[self.bs_id]['last_time'] 
                BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state'] = BeamFormingFunction.bs_generator_beam_state[self.bs_id]['last_time_state'] 
                BeamFormingFunction.bs_generator_beam_list[self.bs_id]['last_time'] = self.beamforming_list
                BeamFormingFunction.bs_generator_beam_state[self.bs_id]['last_time_state'] = 'dymaic' 
        else:
            BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'] = self.beamforming_list  
            BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state'] = 'dymaic' 

    def generator_ntu_beam(self):
        if BeamFormingFunction.control_variable[self.bs_id] < 9: #產生動態波束1個
            BeamFormingFunction.control_variable[self.bs_id] += 1
            self.generator_ntu_dynamic_beam()           
        else: #產生靜態波束2個
            BeamFormingFunction.control_variable[self.bs_id] += 1
            self.generator_static_beam()
            if BeamFormingFunction.control_variable[self.bs_id] == 10: #1靜1動都生產完了
                BeamFormingFunction.control_variable[self.bs_id] = 0

    def generator_location_beam(self):
        #self.generator_location_dynamic_beam()
        if BeamFormingFunction.control_variable[self.bs_id] < 9: #產生動態波束1個
            BeamFormingFunction.control_variable[self.bs_id] += 1
            self.generator_location_dynamic_beam()           
        else: #產生靜態波束2個
            BeamFormingFunction.control_variable[self.bs_id] += 1
            self.generator_static_beam()
            if BeamFormingFunction.control_variable[self.bs_id] == 10: #1靜1動都生產完了
                BeamFormingFunction.control_variable[self.bs_id] = 0

    def generator_location_dynamic_beam(self):
        location_beam_list_number = len(BeamFormingFunction.location_beam_list[self.bs_id])
        for i in range(location_beam_list_number):
            self.beamforming_list.append(BeamFormingFunction.location_beam_list[self.bs_id][i])
        BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'] = self.beamforming_list
        BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state'] = 'dymaic'

    def generator_ntu_dynamic_beam(self):
        dynamic_beam_dict = dict() #儲存該波束的前2個波束
        ntu_T_probability = list() #儲存該波束的前T個波束的機率

        for i in range(SystemInfo.ntu_T_time):
            ntu_T_probability.append(1 / SystemInfo.ntu_T_time)

        for beam_index in range(self.beam_number):
            dynamic_beam_dict[beam_index] = list()
            for j in range(1,self.beam_number):
                before_beam = beam_index - j #之前打過的波束
                if before_beam < 0:
                    need_beam = self.beam_number + before_beam #前2個波束
                    if ValueControlData.transmission_beam_throughput[self.bs_id][need_beam] != 0:
                        dynamic_beam_dict[beam_index].append(need_beam)
                else:
                    if ValueControlData.transmission_beam_throughput[self.bs_id][before_beam] != 0:
                        dynamic_beam_dict[beam_index].append(before_beam)
                if len(dynamic_beam_dict[beam_index]) == SystemInfo.ntu_T_time:
                    break
        
        for k in range(self.beam_number):
            if len(dynamic_beam_dict[k]) == SystemInfo.ntu_T_time:
                self.beamforming_list.append(np.random.choice(dynamic_beam_dict[k],p = ntu_T_probability))
            else:
                self.beamforming_list.append(dynamic_beam_dict[k])
        BeamFormingFunction.bs_generator_beam_list[self.bs_id]['time_before_last_time'] = self.beamforming_list  
        BeamFormingFunction.bs_generator_beam_state[self.bs_id]['before_last_time_state'] = 'dymaic'
        
    '''
    def generator_cross_beam(self):
        if BeamFormingFunction.control_variable[self.bs_id] < 1: #產生動態波束1個
            BeamFormingFunction.control_variable[self.bs_id] += 1
            self.generator_dynamic_beam()           
        else: #產生靜態波束1個
            BeamFormingFunction.control_variable[self.bs_id] += 1
            self.generator_static_beam()
            if BeamFormingFunction.control_variable[self.bs_id] == 2: #2靜2動都生產完了
                BeamFormingFunction.control_variable[self.bs_id] = 0
    '''