import numpy as np
import copy
from NetworkSettings import NetworkSettings,Simulation,SystemInfo
import time
import pickle

class ProportionalFairControlValue:
    location_beam_priority = dict() #[bs][beam][self.location_beam_priority]
    
class ProportionalFair:
    def __init__(self, history_rate, current_rb_rate, bs_id, ue_data, ue_id,bs_beamforming_list):
        self.mapping_table = NetworkSettings.ue_to_bs_mapping_table
        self.Number_resource_block = NetworkSettings.Number_resource_block
        self.current_rb_rate = current_rb_rate
        self.history_rate = copy.copy(history_rate) #好像可以用copy
        self.ue_data = pickle.loads(pickle.dumps(ue_data))
        self.bs_id = bs_id
        self.origin_ue_data = ue_data
        self.ue_id = ue_id
        self.number_of_ue = len(self.ue_id)
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.bs_beamforming_list = bs_beamforming_list
        self.except_total_rate = 0

        self.pf_metric = []
        self.priority_ue_index = []

        self.beta = 0.2
        self.mode = Simulation.mode

        self.allowed_data = {}

        for ue_data_key in list(self.ue_data.keys()):
            self.allowed_data[ue_data_key] = {"CBR": 0, "voice": 0, "video": 0}
        
        self.rb_allocate_list = []
        for _ in range(self.Number_resource_block):
            self.rb_allocate_list.append(None)

    def execute(self):
        self.metric_calculate() #0.4s
        self.priority_calculate() #0.6s
        self.rb_allocate() #0.35
        self.history_data_update() #0.34
        if self.mode == 4:
            self.all_user_expected_rate()
        #print("self.pf_metric: ", self.pf_metric)

        #print("self.allowed_data: ", self.allowed_data)
        #print("self.rb_allocate_list: ", self.rb_allocate_list)

        return self.allowed_data, self.history_rate
    
    def metric_calculate(self):
        for ue in range(self.number_of_ue):
            pf_metric_per_ue = []
            current_ue_id = self.ue_id[ue]

            if self.history_rate[current_ue_id] < 10 ** -6:
                self.history_rate[current_ue_id] = 10 ** -6

            for _ in range(self.Number_resource_block):
                pf_metric_per_ue.append(self.current_rb_rate[ue] / self.history_rate[current_ue_id])
            self.pf_metric.append(pf_metric_per_ue)

    def priority_calculate(self):
        for rb in range(self.Number_resource_block):
            pf_metric_per_rb = []
            priority_ue_index_per_rb = []

            for ue in range(self.number_of_ue):
                pf_metric_per_rb.append(self.pf_metric[ue][rb])
            
            priority_ue_index_per_rb = sorted(range(self.number_of_ue), key = lambda k: pf_metric_per_rb[k], reverse = True) #0.32s
            self.priority_ue_index.append(priority_ue_index_per_rb)

    def rb_allocate(self):
        rb = 0
        for priority_ue_index_per_rb in self.priority_ue_index:
            for ue_index in priority_ue_index_per_rb:
                current_ue_id = self.ue_id[ue_index]
                allowed_data_bits = self.current_rb_rate[ue_index] * (10 ** 6)
                current_ue_data = self.ue_data.get("ue{}".format(current_ue_id))
            
                if  current_ue_data != None:
                    if current_ue_data["voice"] > 0:
                        if allowed_data_bits > current_ue_data["voice"]:
                            self.allowed_data["ue{}".format(current_ue_id)]["voice"] = self.origin_ue_data["ue{}".format(current_ue_id)]["voice"]
                            self.ue_data["ue{}".format(current_ue_id)]["voice"] = 0
                            self.rb_allocate_list[rb] = [current_ue_id, current_ue_data["voice"]]
                        else:
                            self.allowed_data["ue{}".format(current_ue_id)]["voice"] += allowed_data_bits
                            self.ue_data["ue{}".format(current_ue_id)]["voice"] -= allowed_data_bits
                            self.rb_allocate_list[rb] = [current_ue_id, allowed_data_bits]
                        
                        break

                    elif current_ue_data["video"] > 0:
                        if allowed_data_bits > current_ue_data["video"]:
                            self.allowed_data["ue{}".format(current_ue_id)]["video"] = self.origin_ue_data["ue{}".format(current_ue_id)]["video"]
                            self.ue_data["ue{}".format(current_ue_id)]["video"] = 0
                            self.rb_allocate_list[rb] = [current_ue_id, current_ue_data["video"]]
                        else:
                            self.allowed_data["ue{}".format(current_ue_id)]["video"] += allowed_data_bits
                            self.ue_data["ue{}".format(current_ue_id)]["video"] -= allowed_data_bits
                            self.rb_allocate_list[rb] = [current_ue_id, allowed_data_bits]

                        break

                    elif current_ue_data["CBR"] > 0:
                        if allowed_data_bits > current_ue_data["CBR"]:
                            self.allowed_data["ue{}".format(current_ue_id)]["CBR"] = self.origin_ue_data["ue{}".format(current_ue_id)]["CBR"]
                            self.ue_data["ue{}".format(current_ue_id)]["CBR"] = 0
                            self.rb_allocate_list[rb] = [current_ue_id, current_ue_data["CBR"]]
                        else:
                            self.allowed_data["ue{}".format(current_ue_id)]["CBR"] += allowed_data_bits
                            self.ue_data["ue{}".format(current_ue_id)]["CBR"] -= allowed_data_bits
                            self.rb_allocate_list[rb] = [current_ue_id, allowed_data_bits]

                        break
            rb += 1

    def history_data_update(self):
        for ue in range(self.number_of_ue):
            current_ue_id = self.ue_id[ue]
            current_ue_rate = 0

            for rb in range(self.Number_resource_block):
                if self.rb_allocate_list[rb] != None:
                    if self.rb_allocate_list[rb][0] == current_ue_id:
                        current_ue_rate += self.rb_allocate_list[rb][1]
                        
            self.except_total_rate += current_ue_rate
            self.history_rate[current_ue_id] = ((1 - self.beta) * self.history_rate[current_ue_id]) + (self.beta * current_ue_rate)
    
    def all_user_expected_rate(self):
        sum_history_rate = 0 #波束跑越多次會越大
        beam_index = (SystemInfo.system_time - 1) % self.beam_number
        beam = self.bs_beamforming_list[beam_index]
        
        if self.bs_id not in ProportionalFairControlValue.location_beam_priority:
            ProportionalFairControlValue.location_beam_priority[self.bs_id] = dict()
            for i in range(self.beam_number):
                ProportionalFairControlValue.location_beam_priority[self.bs_id][i] = 0
        
        #for ue in range(self.number_of_ue):
        #    current_ue_id = self.ue_id[ue]
        #    sum_history_rate += self.history_rate[current_ue_id]

        sum_history_rate = sum(self.history_rate)

        if SystemInfo.system_time < self.beam_number:
            priority =  self.except_total_rate
            #priority =  user_expected_rate
        else:
            #priority =  sum_history_rate / user_expected_rate
            priority =  self.except_total_rate / sum_history_rate
            
        ProportionalFairControlValue.location_beam_priority[self.bs_id][beam] = priority
