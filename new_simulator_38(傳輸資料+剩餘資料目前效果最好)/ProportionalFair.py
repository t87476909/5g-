import numpy as np
import copy
from NetworkSettings import NetworkSettings

class ProportionalFair:
    def __init__(self, history_rate, current_rb_rate, bs_id, ue_data, ue_id):
        self.Number_resource_block = NetworkSettings.Number_resource_block
        self.current_rb_rate = current_rb_rate
        self.history_rate = copy.deepcopy(history_rate)
        self.bs_id = bs_id
        self.origin_ue_data = ue_data
        self.ue_data = copy.deepcopy(ue_data)
        self.ue_id = ue_id
        self.number_of_ue = len(self.ue_id)

        self.pf_metric = []
        self.priority_ue_index = []

        self.beta = 0.5

        self.allowed_data = {}
        for ue_data_key in list(self.ue_data.keys()):
            self.allowed_data[ue_data_key] = {"CBR": 0, "voice": 0, "video": 0}
        
        self.rb_allocate_list = []
        for _ in range(self.Number_resource_block):
            self.rb_allocate_list.append(None)

    def execute(self):
        self.metric_calculate()
        self.priority_calculate()
        self.rb_allocate()
        self.history_data_update()

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

            priority_ue_index_per_rb = sorted(range(self.number_of_ue), key = lambda k: pf_metric_per_rb[k], reverse = True)
            self.priority_ue_index.append(priority_ue_index_per_rb)

    '''
    def rb_allocate_full_packet(self):
        rb = 0
        for priority_ue_index_per_rb in self.priority_ue_index:
            for ue_index in priority_ue_index_per_rb:
                current_ue_id = self.ue_id[ue_index]
                current_ue_data = self.ue_data.get("ue{}".format(current_ue_id))
                allowed_data_bits = self.current_rb_rate[ue_index] * (10 ** 6)
            
                if  current_ue_data != None:
                    if current_ue_data["voice"] > 0:
                        if allowed_data_bits > current_ue_data["voice"]:
                            self.allowed_data["ue{}".format(current_ue_id)]["voice"] = self.origin_ue_data["ue{}".format(current_ue_id)]["voice"]
                            self.ue_data["ue{}".format(current_ue_id)]["voice"] = 0
                            self.rb_allocate_list[rb] = current_ue_id
                            break
                        else:
                            allowed_data_packet_num = int(allowed_data_bits / (10 * 8))
                            if allowed_data_packet_num > 0:
                                self.allowed_data["ue{}".format(current_ue_id)]["voice"] += ((10 * 8) * allowed_data_packet_num)
                                self.ue_data["ue{}".format(current_ue_id)]["voice"] -= ((10 * 8) * allowed_data_packet_num)
                                self.rb_allocate_list[rb] = current_ue_id
                                break

                    elif current_ue_data["video"] > 0:
                        if allowed_data_bits > current_ue_data["video"]:
                            self.allowed_data["ue{}".format(current_ue_id)]["video"] = self.origin_ue_data["ue{}".format(current_ue_id)]["video"]
                            self.ue_data["ue{}".format(current_ue_id)]["video"] = 0
                            self.rb_allocate_list[rb] = current_ue_id
                            break
                        else:
                            allowed_data_packet_num = int(allowed_data_bits / (1000 * 8))
                            if allowed_data_packet_num > 0:
                                self.allowed_data["ue{}".format(current_ue_id)]["video"] += ((1000 * 8) * allowed_data_packet_num)
                                self.ue_data["ue{}".format(current_ue_id)]["video"] -= ((1000 * 8) * allowed_data_packet_num)
                                self.rb_allocate_list[rb] = current_ue_id
                                break

                    elif current_ue_data["CBR"] > 0:
                        if allowed_data_bits > current_ue_data["CBR"]:
                            self.allowed_data["ue{}".format(current_ue_id)]["CBR"] = self.origin_ue_data["ue{}".format(current_ue_id)]["CBR"]
                            self.ue_data["ue{}".format(current_ue_id)]["CBR"] = 0
                            self.rb_allocate_list[rb] = current_ue_id
                            break
                        else:
                            allowed_data_packet_num = int(allowed_data_bits / (1460 * 8))
                            if allowed_data_packet_num > 0:
                                self.allowed_data["ue{}".format(current_ue_id)]["CBR"] += ((1460 * 8) * allowed_data_packet_num)
                                self.ue_data["ue{}".format(current_ue_id)]["CBR"] -= ((1460 * 8) * allowed_data_packet_num)
                                self.rb_allocate_list[rb] = current_ue_id
                                break
            
            rb += 1
    '''

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

            self.history_rate[current_ue_id] = ((1 - self.beta) * self.history_rate[current_ue_id]) + (self.beta * current_ue_rate)