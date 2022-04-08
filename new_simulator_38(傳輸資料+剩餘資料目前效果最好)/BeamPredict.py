from NetworkSettings import NetworkSettings,SystemInfo
from BeamForming import BeamFormingFunction
from collections import Counter
import numpy as np

class PredictControlValue:
    bs_miss_beam = dict() #example: bs0:{[0,1,2,3,4,5]}
    
class BeamPredict:
    def __init__(self):
        self.beam_number = int(360 / NetworkSettings.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.bs_number = NetworkSettings.num_of_bs
        self.bs_list = NetworkSettings.bs_id_list
        self.bs_beam_list = BeamFormingFunction.bs_generator_beam_list

    def bs_execute(self,bs_id,need_ue_index):
        if self.beam_index == 0 and self.bs_beam_list[bs_id]['time_before_last_time'] != None:
            classify = 1 #bs = 1
            miss_beam,change_location = self.predict(self.bs_beam_list[bs_id]['time_before_last_time'],classify) #預測的波束
            PredictControlValue.bs_miss_beam[bs_id] = miss_beam
            
            #print("BeamFormingFunction.bs_generator_beam_list[bs_id]",BeamFormingFunction.bs_generator_beam_list[bs_id])
            #print("system_time = ",SystemInfo.system_time)
            #print("miss_beam = ",miss_beam)
            #print("change_location = ",change_location)
            return miss_beam,change_location
        else: #因為回傳默認是一個none直 需要回傳2個不然會報錯
            return None,None
            #BeamFormingFunction.bs_generator_beam_list[bs_id]['time_before_last_time'] = predict_beam #生成的波束要更改成預測結果
    
    #https://www.codeleading.com/article/99535617560/       
    #https://blog.csdn.net/sinat_29957455/article/details/103886088
    def predict(self,beam,classify):
        miss_beam = list() #該基地台缺少的波束
        change_location = list() #需要替換成miss的位置
        miss_beam_index = 0
        for i in range(self.beam_number):
            if i not in beam:
                miss_beam.append(i)

        miss_beam_number = len(miss_beam)
        for j in range(miss_beam_number):
            change_location.append(j)
        
        if classify == 0:
            change_location_number = len(change_location)
            for index in range(change_location_number):
                beam[index] = miss_beam[miss_beam_index]
                miss_beam_index += 1
            return beam
        else:
            return miss_beam,change_location



