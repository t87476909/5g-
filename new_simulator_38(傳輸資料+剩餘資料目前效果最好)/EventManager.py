from queue import PriorityQueue
from NetworkSettings import NetworkSettings,SystemInfo,Simulation
from StatisticWork import StatisticWork
import random


class EventManager:
    def __init__(self):
        self.event_list = PriorityQueue()
        #將事件 設定為優先順序佇列 
    def execute(self):
        while self.event_list.qsize() > 0 and SystemInfo.system_time < NetworkSettings.simulation_time: #事件不為空 and 模擬時間未到
            event = self.event_list.get()
            event_content = event[2]
            SystemInfo.system_time = event_content['event_trigger_time']
            #print ("EventManager: current_system_time: {}, event_content: {}".format(event_content['event_trigger_time'], event_content))
            if type(event_content['event_target']) is list: #單一ue複數bs(list)
                for value in range(len(event_content['event_target'])):
                    NetworkSettings.object_info_dict[event_content['event_target'][value]].event_handler(event_content)
            else: #單一ue 單一bs
                NetworkSettings.object_info_dict[event_content['event_target']].event_handler(event_content)
        StatisticWork().execute()

    def add_new_event(self, event_time, event_content):
        self.event_list.put((event_time, SystemInfo.event_priority, event_content))
        SystemInfo.event_priority += 1
        #print("EventManager: insert event ", event_content)
