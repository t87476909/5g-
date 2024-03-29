from NetworkSettings import NetworkSettings,SystemInfo,Simulation
from RateCaulate import RateCaulate
from ProportionalFair import ProportionalFair
from BeamTransmit import BeamTransmit
from BeamForming import BeamForming
from BeamPredict import BeamPredict
from BeamExchange import BeamExchange
from Dominate import Dominate
from UeTime import UeTime
from ValueCalculate import ValueCalculate,ValueControlData
from DelayCalculate import DelayCalculate,DelayCalculateData
import math
import numpy as np
import random
import time

class BsProcessData:
    def __init__(self, event_details, event_trigger_time,event_manager, bs_id):
        self.event_details = event_details
        self.event_manager = event_manager
        self.event_trigger_time = event_trigger_time
        self.bs = NetworkSettings.object_info_dict[bs_id]

    def execute(self):
        target_ue = self.event_details['target_ue']
        data_amount = self.event_details['data_amount']
        self.bs.add_data_for_ue(target_ue, data_amount,self.event_trigger_time)

class BsSched:
    def __init__(self, event_details, event_manager, bs_id, history_rate):
        self.event_details = event_details
        self.event_manager = event_manager
        self.bs_id = bs_id
        self.bs = NetworkSettings.object_info_dict[bs_id]
        self.current_rate = list()
        self.current_rate_ue_index = list()
        self.bs_beamforming_list = list()
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.history_rate = history_rate
        self.BeamTransmit = BeamTransmit(bs_id) #波束用schedule
        self.BeamForming = BeamForming(bs_id)
        self.Dominate = Dominate(bs_id)
        self.BeamPredict = BeamPredict()
        self.BeamExchange = BeamExchange(bs_id)
        self.bs_number = NetworkSettings.num_of_bs
        self.UeTime = UeTime(bs_id)
        self.mode = Simulation.mode
        self.ue_move_count = 0

    def execute(self): #從1開始
        #print("-----------------------------------------------------------------------")
        self.generate_event_to_self()
        #start = time.time()
        self.bs_beamforming_list,need_ue_index,bs_transmit_state,need_beam_ue_id,time_need_ue_index = self.BeamTransmit.execute() #基地台波束、該ue_id所對應 需要的波束 #1.65s --> 0.15
        #print("bs_id = {} transbeam = {} bs_beam_state = {}".format(self.bs_id,self.bs_beamforming_list,bs_transmit_state))
        self.current_rate,self.current_rate_ue_index = RateCaulate(self.bs_id,need_ue_index,bs_transmit_state,need_beam_ue_id).snr_rate_Caulate() #當前波束速度 與 當前要被分配的UE #0.5s
        self.perform_resource_assignment(bs_transmit_state) #11.19s
        self.BeamForming.execute(bs_transmit_state) #0.103s
        miss_beam,change_location = self.BeamPredict.bs_execute(self.bs_id,need_ue_index) #0.004s
        if self.mode <= 1 or self.mode == 5: #我的方法 0.09s
            self.BeamExchange.execute(miss_beam,change_location)
            if self.mode != 5:
                self.Dominate.execute() #多基地台協調方法
        self.UeTime.ue_time_calculate(time_need_ue_index) #計算ue開啟時間(我的方法的) #0.116
        return self.history_rate

    def perform_resource_assignment(self,bs_transmit_state): #RB分配
        ue_data = self.bs.queue_for_ue #儲存該bs的ue 佇列data量
        allowed_data, self.history_rate = ProportionalFair(self.history_rate,self.current_rate,self.bs_id,ue_data,self.current_rate_ue_index,self.bs_beamforming_list).execute() #allow 該bs的所有分配 6.9s
        #print("allowed_data = ",allowed_data)
        for ue_id, ue_type_data in allowed_data.items():
            for data_type,data_amount in ue_type_data.items():
                if data_amount > 0:
                    #print("ue_id = {} data_type = {} data_amount = {}".format(ue_id,data_type,data_amount))
                    self.bs.dec_data_for_ue(ue_id,data_type,data_amount)
                    self.generate_event_to_ue(ue_id, data_amount) #原本要往後一格
                self.bs.drop_data_for_ue(ue_id, data_type)
        if self.mode != 4:
            ValueCalculate(self.bs_id,self.bs_beamforming_list, ue_data,allowed_data, self.current_rate_ue_index,bs_transmit_state).execute() #該基地台的參數計算 0.6s

    def generate_event_to_ue(self, target_ue, data_amount): #傳給UE的data
        event = {
            "event_target": target_ue,
            "event_name": "incoming_downlink_data",
            "event_trigger_time": SystemInfo.system_time + 1,
            "event_details": {
                "data_amount": data_amount
            }
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def generate_event_to_self(self): #執行schedule
        event = {
            "event_target": self.bs_id,
            "event_name": "schedule",
            "event_trigger_time": SystemInfo.system_time + 1,
            "event_details": {}
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

class BaseStation:
    event_handler_dict = {
        "incoming_video_data": BsProcessData, #有接收到TrafficGenetator的incoming_data才會觸發
        "incoming_voice_data": BsProcessData,
        "incoming_CBR_data": BsProcessData,
        "schedule": BsSched
    }

    def __init__(self, bs_id, event_manager,bs_location_list):
        self.bs_id = "bs{}".format(bs_id)
        self.event_manager = event_manager
        self.queue_for_ue = dict() #queue_for_ue的每個ue都要再放一個dict
        self.neighbor_distance = NetworkSettings.Neighbor_Distance
        self.ue_number = NetworkSettings.num_of_bs * (NetworkSettings.num_of_ue + NetworkSettings.num_of_ue_overlap)
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.queue_trigger_time = dict()
        self.history_rate = [(10 ** -6) for _ in range(self.ue_number)] #創建儲存過去資料的rate
        

        ValueControlData.beam_throughput.setdefault(self.bs_id, [])
        ValueControlData.transmission_beam_throughput.setdefault(self.bs_id, [])
        for i in range(self.beam_number):
            ValueControlData.beam_throughput[self.bs_id].append(0) #先將該基地台所有的波束流量都設為0(預設該波束底下沒有ue)
            ValueControlData.transmission_beam_throughput[self.bs_id].append(0)
        
        self.generate_first_event()
        if bs_id == NetworkSettings.num_of_bs -1: #所有基地台座標輸入完畢 bs是從0開始
            self.bs_location = bs_location_list
    
    def generate_first_event(self):
        event = {
            "event_target": self.bs_id,
            "event_name": "schedule",
            "event_trigger_time": 1,
            "event_details": {}
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def event_handler(self, event_content):
        event_name = event_content['event_name']
        if event_name in self.event_handler_dict:
            if event_name == "schedule":
                self.history_rate = self.event_handler_dict[event_name](event_content['event_details'], self.event_manager, self.bs_id,self.history_rate).execute()
            else:
                self.event_handler_dict[event_name](event_content['event_details'],event_content['event_trigger_time'], self.event_manager, self.bs_id).execute()
        else:
            print("BaseStation: The {} cannot handle this event {}".format(self.bs_id, event_name))

    def add_data_for_ue(self,ue_id, data_amount, event_trigger_time):
        if ue_id not in self.queue_for_ue:
            self.queue_for_ue[ue_id] = {"CBR":0,"voice":0,"video":0} #這邊要改成CBR、video、voice
        if ue_id not in self.queue_trigger_time:
            self.queue_trigger_time[ue_id] = {"CBR":[],"voice":[],"video":[]}
        if data_amount == 1460 * 8 : #1460 * 8 = 11680
            self.queue_for_ue[ue_id]['CBR'] += data_amount
            self.queue_trigger_time[ue_id]["CBR"].append(event_trigger_time)
        elif data_amount == 10 * 8: #10 * 8 = 80
            self.queue_for_ue[ue_id]['voice'] += data_amount
            self.queue_trigger_time[ue_id]["voice"].append(event_trigger_time)
        elif data_amount == 1000 * 8:
            self.queue_for_ue[ue_id]['video'] += data_amount
            self.queue_trigger_time[ue_id]["video"].append(event_trigger_time)

    def dec_data_for_ue(self, ue_id, data_type, data_amount):
        type_data_amount_dict = {
            "CBR": (1460 * 8),
            "voice": (10 * 8),
            "video": (1000 * 8)
        }

        self.queue_for_ue[ue_id][data_type] -= data_amount
        DelayCalculate.add_data_amount(ue_id, data_amount)
        DelayCalculate.add_loss_sent_data(data_type, data_amount)
        queue_packets_amount = math.ceil(self.queue_for_ue[ue_id][data_type] / type_data_amount_dict[data_type])
        sent_packets_amount = len(self.queue_trigger_time[ue_id][data_type]) - queue_packets_amount

        for i in range(sent_packets_amount):
            queue_time = SystemInfo.system_time - self.queue_trigger_time[ue_id][data_type][0]
            DelayCalculate.add_delay_data(data_type, queue_time)
            del self.queue_trigger_time[ue_id][data_type][0]

    def drop_data_for_ue(self, ue_id, data_type):
        packet_deadline_dict = {
            "CBR": 300,
            "voice": 100,
            "video": 150
        }
        type_data_amount_dict = {
            "CBR": (1460 * 8),
            "voice": (10 * 8),
            "video": (1000 * 8)
        }

        while len(self.queue_trigger_time[ue_id][data_type]) > 0:
            queue_time = SystemInfo.system_time - self.queue_trigger_time[ue_id][data_type][0]
            if queue_time > packet_deadline_dict[data_type]:
                del self.queue_trigger_time[ue_id][data_type][0]
                DelayCalculate.add_delay_data(data_type,queue_time)
                self.queue_for_ue[ue_id][data_type] = type_data_amount_dict[data_type] * len(self.queue_trigger_time[ue_id][data_type])
                DelayCalculate.add_loss_drop_data(data_type)
            else:
                break

