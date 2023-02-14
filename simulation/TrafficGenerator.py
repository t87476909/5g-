import random
import numpy as np
import math
import cmath
import copy
import pickle
from NetworkSettings import NetworkSettings, SystemInfo,Simulation
from BeamTransmit import BeamUseFunction
from collections import Counter
import time
#https://support.tetcos.com/support/solutions/articles/14000122887-how-to-get-the-same-throughput-for-ftp-and-cbr-applications
class GenerateCBR: #1.99Mbps
    def __init__(self, event_details, event_manager, tg_id, ue_id):
        self.event_details = event_details
        self.event_manager = event_manager
        self._lambda = 0.162 / 2 * NetworkSettings.CBR_data_change #事件發生頻率 ms 0.162
        self.tg_id = tg_id
        self.ue_id = ue_id
    
    def execute(self):
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 1:
            target_bs = NetworkSettings.ue_to_bs_mapping_table[self.ue_id][0]
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 2: #單一ue複數bs
            ratio = 5
            target_bs = random.choices(NetworkSettings.ue_to_bs_mapping_table[self.ue_id], weights=(ratio, 10 - ratio))[0]
            
        event_details = {
            "target_ue": self.ue_id,
            "data_amount": 1460 * 8 #1460 * 8 bits
        }
        self.generate_event_to_target_bs(target_bs, event_details)
        self.generate_event_to_self()
    
    def generate_event_to_target_bs(self, target_bs, event_details):
        event = {
            "event_target": target_bs,
            "event_name": "incoming_CBR_data",
            "event_trigger_time": SystemInfo.system_time,
            "event_details": event_details
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def generate_event_to_self(self):
        event = {
            "event_target": self.tg_id,
            "event_name": "generate_CBR",
            "event_trigger_time": SystemInfo.system_time + random.expovariate(self._lambda),
            "event_details": {}
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)
#https://www.cisco.com/c/en/us/support/docs/voice/voice-quality/7934-bwidth-consume.html
class GenerateVoice: # G.729
    def __init__(self, event_details, event_manager, tg_id, ue_id):
        self.event_details = event_details
        self.event_manager = event_manager
        self._lambda = 0.1  #到達率
        self.tg_id = tg_id
        self.ue_id = ue_id

    def execute(self):
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 1:
            target_bs = NetworkSettings.ue_to_bs_mapping_table[self.ue_id][0]
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 2: #單一ue複數bs
            ratio = 5
            target_bs = random.choices(NetworkSettings.ue_to_bs_mapping_table[self.ue_id], weights=(ratio, 10 - ratio))[0]
        
        event_details = {
            "target_ue": self.ue_id,
            "data_amount": 10 * 8 # bits 
        }
        #加入判斷ue移動到其他基地台底下的時候剩下資料要傳給其他基地台
        self.generate_event_to_target_bs(target_bs, event_details)
        self.generate_event_to_self()
    
    def generate_event_to_target_bs(self, target_bs, event_details): #event_name 換成 incoming_voice_data
        event = {
            "event_target": target_bs,
            "event_name": "incoming_voice_data",
            "event_trigger_time": SystemInfo.system_time,
            "event_details": event_details
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def generate_event_to_self(self):
        event = {
            "event_target": self.tg_id,
            "event_name": "generate_voice",
            "event_trigger_time": SystemInfo.system_time + random.expovariate(self._lambda), #指數分佈的隨機數(poisson) lambda = 0.5
            "event_details": {}
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)
#https://support.google.com/youtube/answer/78358?hl=en
class GenerateVideo: #以 YouTube 720p HD 視頻為標準
    def __init__(self, event_details, event_manager, tg_id, ue_id):
        self.event_details = event_details
        self.event_manager = event_manager
        self._lambda = 0.3125 / 2.5 * NetworkSettings.Video_data_change #傳輸到達率 ms
        self.tg_id = tg_id
        self.ue_id = ue_id

    def execute(self):
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 1:
            target_bs = NetworkSettings.ue_to_bs_mapping_table[self.ue_id][0]
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 2: #單一ue複數bs
            ratio = 5
            target_bs = random.choices(NetworkSettings.ue_to_bs_mapping_table[self.ue_id], weights=(ratio, 10 - ratio))[0]  

        event_details = {
            "target_ue": self.ue_id,
            "data_amount": 1000 * 8 #封包 bits 大小 
        }
        self.generate_event_to_target_bs(target_bs, event_details)
        self.generate_event_to_self()
    
    def generate_event_to_target_bs(self, target_bs, event_details):
        event = {
            "event_target": target_bs,
            "event_name": "incoming_video_data",
            "event_trigger_time": SystemInfo.system_time,
            "event_details": event_details
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def generate_event_to_self(self):
        event = {
            "event_target": self.tg_id,
            "event_name": "generate_video",
            "event_trigger_time": SystemInfo.system_time + random.expovariate(self._lambda),
            "event_details": {}
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

class GenerateUeMove:
    def __init__(self, event_manager, ue_id):
        self.event_manager = event_manager
        self.mapping_table = NetworkSettings.ue_to_bs_mapping_table
        self.distance = NetworkSettings.bs_ue_distance
        self.ue_id = ue_id
        self.bs_beam_neighbor = NetworkSettings.bs_beam_neighbor #bs_id:{bs_id:{beam:{beam}}}
        self.move_speed = NetworkSettings.UE_speed #km/hr
        self.all_ue_location = BeamUseFunction.all_ue_location
        self.bs_location = BeamUseFunction.bs_location
        self.bs_id_list = NetworkSettings.bs_id_list
        self.bs_number = NetworkSettings.num_of_bs
        self.bs_range = NetworkSettings.bs_range
        self.bs = NetworkSettings.object_info_dict
        self.overlap_ue_id = 0
        self.beam_angle = NetworkSettings.beam_angle
        self.ue_move_cycle = SystemInfo.ue_move_cycle
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.ue_direction = NetworkSettings.ue_move_direction
        self.ue_move_ms = random.expovariate(1 / self.ue_move_cycle)
        
    def execute(self):
        NetworkSettings.record_ue_connect_bs[self.ue_id] = pickle.loads(pickle.dumps(self.mapping_table[self.ue_id])) #2.415
        self.ue_location_move()
        self.bs_data_change()
        self.generate_event_to_self()

    def generate_event_to_self(self): #生成下一次ue移動的事件(ue移動事件不用告知bs) --> 資料有放到NetworkSetting裡
        event = {
            "event_target": self.ue_id,
            "event_name": "generate_ue_move",
            "event_trigger_time": SystemInfo.system_time + self.ue_move_ms,
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def ue_location_move(self):
        ue_index = int(self.ue_id.lstrip('ue'))
        self.mapping_table[self.ue_id].clear()
        self.distance[self.ue_id].clear()
        Distribution_speed_m = self.move_speed * self.ue_move_ms * 1000 / 60 / 60 / 1000 # km/hr -> m / (ms * ue_move_cycle)
        #print("self.mapping_table = ",self.mapping_table)
        while True:
            return_beginning = 0
            ue_direction = NetworkSettings.ue_move_direction[ue_index]
            self.location_move(ue_direction,Distribution_speed_m,return_beginning,ue_index)
            for j in range(len(self.bs_id_list)): # 所有基地台
                bs_ue_x_distance = self.bs_location[j][0] - self.all_ue_location[ue_index][0]
                bs_ue_y_distance = self.bs_location[j][1] - self.all_ue_location[ue_index][1]
                if len(self.mapping_table[self.ue_id]) < 2:
                    distance = math.sqrt(bs_ue_x_distance**2 + bs_ue_y_distance**2)
                    if distance < self.bs_range: #UE在基地台覆蓋範圍內
                        self.mapping_table[self.ue_id].append("bs{}".format(j))
                        self.distance[self.ue_id].append(distance)
                else:
                    break
            if len(self.mapping_table[self.ue_id]) == 0: #該UE不再任何基地台範圍內則座標回到原位
                return_beginning = 1
                self.location_move(ue_direction,Distribution_speed_m,return_beginning,ue_index)
            elif len(self.mapping_table[self.ue_id]) > 0:
                break
        if len(self.mapping_table[self.ue_id]) >= 2: #表示該ue在overlapping的ue_list內
            self.overlap_ue_id = self.ue_id

    def location_move(self,Distribution_direction,Distribution_speed_m,return_beginning,ue_index):
        if Distribution_direction == 1: #上
            if return_beginning == 0: #一開始
                self.all_ue_location[ue_index][1] += Distribution_speed_m
            else:
                direction = [2,3,4]
                Distribution_direction = random.choice(direction)
                NetworkSettings.ue_move_direction[ue_index] = Distribution_direction #到邊界往其他方向走
                self.all_ue_location[ue_index][1] -= Distribution_speed_m
        elif Distribution_direction == 2: #下
            if return_beginning == 0: #一開始 
                self.all_ue_location[ue_index][1] -= Distribution_speed_m
            else:
                direction = [1,3,4]
                Distribution_direction = random.choice(direction)
                NetworkSettings.ue_move_direction[ue_index] = Distribution_direction #到邊界往反方向走
                self.all_ue_location[ue_index][1] += Distribution_speed_m
        elif Distribution_direction == 3: #左
            if return_beginning == 0: #一開始 
                self.all_ue_location[ue_index][0] -= Distribution_speed_m
            else:
                direction = [1,2,4]
                Distribution_direction = random.choice(direction)
                NetworkSettings.ue_move_direction[ue_index] = Distribution_direction #到邊界往反方向走
                self.all_ue_location[ue_index][0] += Distribution_speed_m
        else: #右
            if return_beginning == 0: #一開始 
                self.all_ue_location[ue_index][0] += Distribution_speed_m
            else:
                direction = [1,2,3]
                Distribution_direction = random.choice(direction)
                NetworkSettings.ue_move_direction[ue_index] = Distribution_direction #到邊界往反方向走
                self.all_ue_location[ue_index][0] -= Distribution_speed_m

    def bs_data_change(self):
        if self.mapping_table[self.ue_id] != NetworkSettings.record_ue_connect_bs[self.ue_id]: #舊bs ue資料丟給新bs
            send_bs_id = NetworkSettings.record_ue_connect_bs[self.ue_id] #這是舊的連接關係 [bs_id,bs_id]
            receive_bs_id = self.mapping_table[self.ue_id] #這是新的連接關係 [bs_id,bs_id]
            repeat_number = len(set(send_bs_id) & set(receive_bs_id)) #重複的bs數量
            
            for j in range(len(receive_bs_id)):
                if receive_bs_id[j] not in send_bs_id: #新資料建立
                    self.bs[receive_bs_id[j]].queue_for_ue[self.ue_id] = {"CBR":0,"voice":0,"video":0}
                    self.bs[receive_bs_id[j]].queue_trigger_time[self.ue_id] = {"CBR":[],"voice":[],"video":[]}
            
            if repeat_number > 2: # queue_trigger_time特殊
                if len(send_bs_id) == 1: #只有一個舊資料不在新資料內
                    for i in range(len(send_bs_id)):
                        for j in range(len(receive_bs_id)):
                            self.bs[receive_bs_id[j]].queue_for_ue[self.ue_id] = self.bs[send_bs_id[i]].queue_for_ue[self.ue_id] / 2
                            self.bs[receive_bs_id[j]].queue_trigger_time[self.ue_id] = self.bs[send_bs_id[i]].queue_trigger_time[self.ue_id]
                    del self.bs[send_bs_id[0]].queue_for_ue[self.ue_id] #舊bs ue資料刪除
                    del self.bs[send_bs_id[0]].queue_trigger_time[self.ue_id] #舊bs ue資料刪除
                else: #多個舊資料不在新資料內
                    if len(receive_bs_id) == 1:
                        for i in range(len(send_bs_id)):
                            for j in range(len(receive_bs_id)):
                                self.bs[receive_bs_id[j]].queue_for_ue[self.ue_id] += self.bs[send_bs_id[i]].queue_for_ue[self.ue_id] / 2
                                send_data = Counter(self.bs[send_bs_id[i]].queue_trigger_time[self.ue_id])
                                receive = self.bs[receive_bs_id[j]].queue_trigger_time[self.ue_id]
                                total_queue_trigger_time = dict(send_data + receive)
                        self.bs[receive_bs_id[0]].queue_trigger_time[self.ue_id] = total_queue_trigger_time
                    else:
                        self.bs[receive_bs_id[0]].queue_for_ue[self.ue_id] = self.bs[send_bs_id[0]].queue_for_ue[self.ue_id]
                        self.bs[receive_bs_id[0]].queue_trigger_time[self.ue_id] = self.bs[send_bs_id[0]].queue_trigger_time[self.ue_id]
                        self.bs[receive_bs_id[1]].queue_for_ue[self.ue_id] = self.bs[send_bs_id[1]].queue_for_ue[self.ue_id]
                        self.bs[receive_bs_id[1]].queue_trigger_time[self.ue_id] = self.bs[send_bs_id[1]].queue_trigger_time[self.ue_id]
                    for all_data in range(len(send_bs_id)):
                        del self.bs[send_bs_id[all_data]].queue_for_ue[self.ue_id] #舊bs ue資料刪除
                        del self.bs[send_bs_id[all_data]].queue_trigger_time[self.ue_id] #舊bs ue資料刪除
            else:
                for i in range(len(send_bs_id)):
                    if send_bs_id[i] not in receive_bs_id: #舊資料不在新資料內
                        for k in range(len(receive_bs_id)):
                            if receive_bs_id[k] not in send_bs_id: #新資料不在舊資料內
                                self.bs[receive_bs_id[k]].queue_for_ue[self.ue_id] = self.bs[send_bs_id[i]].queue_for_ue[self.ue_id]
                                self.bs[receive_bs_id[k]].queue_trigger_time[self.ue_id] = self.bs[send_bs_id[i]].queue_trigger_time[self.ue_id]
                        if self.ue_id in self.bs[send_bs_id[i]].queue_for_ue:
                            del self.bs[send_bs_id[i]].queue_for_ue[self.ue_id] #舊bs ue資料刪除
                            del self.bs[send_bs_id[i]].queue_trigger_time[self.ue_id] #舊bs ue資料刪除

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

class TrafficGenerator:
    event_handler_dict = {
        "generate_CBR": GenerateCBR,
        "generate_voice": GenerateVoice,
        "generate_video": GenerateVideo,
        "generate_ue_move": GenerateUeMove,
    }

    def __init__(self, ue_id, tg_id, event_manager):
        self.ue_id = ue_id
        self.tg_id = tg_id #ue_id + [voice、video、CBR]
        self.event_manager = event_manager
        self.ue_move_cycle = SystemInfo.ue_move_cycle
        self.generate_first_event()
        if Simulation.ue_move_control == True:
            self.generate_first_ue_move()

    def generate_first_event(self):
        if self.tg_id == self.ue_id + "CBR": #CBR
            event = {
                "event_target": self.tg_id,
                "event_name": "generate_CBR",
                "event_trigger_time": random.random(), #random.randint(1,20)
                "event_details": {}
            }
        elif self.tg_id == self.ue_id + "voice": #voice
            event = {
                "event_target": self.tg_id,
                "event_name": "generate_voice",
                "event_trigger_time": random.random(), #random.randint(1,20)
                "event_details": {}
            }
        else: #video
            event = {
                "event_target": self.tg_id,
                "event_name": "generate_video",
                "event_trigger_time": random.random(), #random.randint(1,20)
                "event_details": {}
            }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def generate_first_ue_move(self):
        event = {
            "event_target": self.ue_id,
            "event_name": "generate_ue_move",
            "event_trigger_time": random.expovariate(1 / self.ue_move_cycle),
        }
        self.event_manager.add_new_event(event['event_trigger_time'], event)

    def event_handler(self, event_content):
        event_name = event_content['event_name']
        #print("tra event_name = ",event_name)
        if event_name in self.event_handler_dict:
            self.event_handler_dict[event_name](event_content['event_details'], self.event_manager, self.tg_id, self.ue_id).execute()
        else:
            print("TrafficGenerator: The {} cannot handle this event {}".format(self.bs_id, event_name))


