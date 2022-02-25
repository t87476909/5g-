import random
import numpy as np
from NetworkSettings import NetworkSettings, SystemInfo
#https://support.tetcos.com/support/solutions/articles/14000122887-how-to-get-the-same-throughput-for-ftp-and-cbr-applications
class GenerateCBR: #1.99Mbps
    def __init__(self, event_details, event_manager, tg_id, ue_id):
        self.event_details = event_details
        self.event_manager = event_manager
        self._lambda = 0.162  #事件發生頻率 ms 0.162
        self.tg_id = tg_id
        self.ue_id = ue_id
    
    def execute(self):
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 1:
            target_bs = NetworkSettings.ue_to_bs_mapping_table[self.ue_id][0]
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 2: #單一ue複數bs
            split_ratio = 5
            target_bs = random.choices(NetworkSettings.ue_to_bs_mapping_table[self.ue_id], weights=((10 - split_ratio), split_ratio))[0]
        
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
            split_ratio = 5
            target_bs = random.choices(NetworkSettings.ue_to_bs_mapping_table[self.ue_id], weights=((10 - split_ratio), split_ratio))[0]
        
        event_details = {
            "target_ue": self.ue_id,
            "data_amount": 10 * 8 # bits 
        }
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
        self._lambda = 0.3125  #傳輸到達率 ms
        self.tg_id = tg_id
        self.ue_id = ue_id

    def execute(self):
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 1:
            target_bs = NetworkSettings.ue_to_bs_mapping_table[self.ue_id][0]
        if len(NetworkSettings.ue_to_bs_mapping_table[self.ue_id]) == 2: #單一ue複數bs
            split_ratio = 5
            target_bs = random.choices(NetworkSettings.ue_to_bs_mapping_table[self.ue_id], weights=((10 - split_ratio), split_ratio))[0]
        
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

class TrafficGenerator:
    event_handler_dict = {
        "generate_CBR": GenerateCBR,
        "generate_voice": GenerateVoice,
        "generate_video": GenerateVideo,
    }

    def __init__(self, ue_id, tg_id, event_manager):
        self.ue_id = ue_id
        self.tg_id = tg_id #ue_id + [voice、video、CBR]
        self.event_manager = event_manager
        self.generate_first_event()

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

    def event_handler(self, event_content):
        event_name = event_content['event_name']
        if event_name in self.event_handler_dict:
            self.event_handler_dict[event_name](event_content['event_details'], self.event_manager, self.tg_id, self.ue_id).execute()
        else:
            print("TrafficGenerator: The {} cannot handle this event {}".format(self.bs_id, event_name))


