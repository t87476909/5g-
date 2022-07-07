from NetworkSettings import NetworkSettings,SystemInfo
from BeamForming import BeamFormingFunction
import numpy as np
import random
from ValueCalculate import ValueControlData

class BeamChangeControl:
    beam_change_or_not = dict() #該基地台的波束是否可以修改

class BeamExchange:
    def __init__(self,bs_id):
        self.beam_list = BeamFormingFunction.bs_generator_beam_list #bs0:{'time_before_last_time':[],'last_time':[]}
        self.beam_state = BeamFormingFunction.bs_generator_beam_state[bs_id]['last_time_state']
        self.bs_id = bs_id
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.probilibty = ValueControlData.beam_probability #example: bs_id:[probility_list]
        self.sort_probility = list()

        if self.bs_id not in BeamChangeControl.beam_change_or_not:
            BeamChangeControl.beam_change_or_not[self.bs_id] = list()
            for i in range(self.beam_number):
                BeamChangeControl.beam_change_or_not[self.bs_id].append(0) #0為可以修改

    def execute(self,miss_beam,change_location): #需要替換的波束、原先要被替換的位置
        if self.beam_index == 0 and SystemInfo.system_time >= self.beam_number * 2 and self.beam_state == 'dymaic': #至少要出現第2個動態波束才能調換
            
            for i in range(self.beam_number):
                BeamChangeControl.beam_change_or_not[self.bs_id][i] = 0 #回歸初始值

            #print("system_time = {} bs_id = {} exchange_before = {} ".format(SystemInfo.system_time,self.bs_id,self.beam_list[self.bs_id]))
            #print("miss_beam = {} change_location = {} ".format(miss_beam,change_location))
            beam = list()
            unfinished_probilibty = list()

            for index in range(self.beam_number):
                beam.append(self.beam_list[self.bs_id]['last_time'][index])
            
            unfinished_num = len(miss_beam) #紀錄剩下尚未被扣完的
            for i in range(len(miss_beam)):
                if miss_beam[i] in beam:
                    beam.remove(miss_beam[i])
                    self.probilibty[self.bs_id][miss_beam[i]]
                    unfinished_num -= 1

            if unfinished_num > 0:
                unfinished_probilibty = self.probilibty[self.bs_id][beam].tolist()
                probilibty = self.probilibty[self.bs_id].tolist()
                
                #print("self.probilibty[self.bs_id] = ",self.probilibty[self.bs_id])
                
                while unfinished_num > 0:
                    min_probilibty = min(unfinished_probilibty) #找剩餘波束最小機率(不包含0 因為機率為0的波束不會出現)
                    remove_element = [i for i in range(len(probilibty)) if probilibty[i] == min_probilibty] #可能會有重複機率的波束出現
                    remove_element = random.choice(remove_element)
                    #print("unfinished_probilibty = ",unfinished_probilibty)
                    #print("min_probilibty = ",min_probilibty)
                    #print("remove_element = ",remove_element)
                    #print("beam = ",beam)
                    if remove_element in beam: 
                        unfinished_probilibty.remove(min_probilibty) #這個波束被剃除則下次不能再被剔除
                        beam.remove(remove_element)
                        unfinished_num -= 1 #剔除波束次數-1

            #波束替換成predict形式
            miss_index_count = 0
            other_index_count = 0
            for j in range(self.beam_number): #0~7
                if j in change_location:
                    self.beam_list[self.bs_id]['last_time'][j] = miss_beam[miss_index_count]
                    BeamChangeControl.beam_change_or_not[self.bs_id][j] = 1 #1為不可修改的波束
                    miss_index_count += 1
                else:
                    self.beam_list[self.bs_id]['last_time'][j] = beam[other_index_count]
                    other_index_count += 1
            #print("system_time = {} bs_id = {} exchange_final = {} ".format(SystemInfo.system_time,self.bs_id,self.beam_list[self.bs_id]))
