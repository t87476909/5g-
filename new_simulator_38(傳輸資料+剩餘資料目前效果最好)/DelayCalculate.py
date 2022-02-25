from NetworkSettings import NetworkSettings, SystemInfo, Simulation
import numpy as np
import math
import cmath

#update
class DelayCalculateData:
    total_ue_data = {} #{"ue0": 10, "ue1": 20}
    dc_ue_data = {}
    delay_data = {"CBR": {"data_amount": 0, "queue_time": 0}, "voice": {"data_amount": 0, "queue_time": 0}, "video": {"data_amount": 0, "queue_time": 0}}
    loss_data = {"CBR": {"drop_data_amount": 0, "sent_data_amount": 0}, "voice": {"drop_data_amount": 0, "sent_data_amount": 0}, "video": {"drop_data_amount": 0, "sent_data_amount": 0}}

    system_throughput = 0
    avg_ue_throughput = 0
    dc_avg_ue_throughput = 0

    fairness = 0
    dc_fairness = 0

    cbr_delay = 0
    voice_delay = 0
    video_delay = 0
    avg_delay = 0
    
    cbr_loss = 0
    voice_loss = 0
    video_loss = 0
    avg_loss = 0

class DelayCalculate: #基地台每打一次波束就會執行一次 (當執行beam_number次的時候就會進行統整)
    def add_data_amount(ue_id, data_amount):
        #print("ue_id = ",ue_id)
        #print("data_amount = ",data_amount)
        DelayCalculateData.total_ue_data.setdefault(ue_id, 0)
        DelayCalculateData.total_ue_data[ue_id] += data_amount

        if len(NetworkSettings.ue_to_bs_mapping_table[ue_id]) == 2:
            DelayCalculateData.dc_ue_data.setdefault(ue_id, 0)
            DelayCalculateData.dc_ue_data[ue_id] += data_amount

    def add_delay_data(data_type, queue_time):
        type_data_amount_dict = {
            "CBR": (1460 * 8),
            "voice": (10 * 8),
            "video": (1000 * 8)
        }

        DelayCalculateData.delay_data[data_type]["data_amount"] += type_data_amount_dict[data_type]
        DelayCalculateData.delay_data[data_type]["queue_time"] += type_data_amount_dict[data_type] * queue_time

    def add_loss_sent_data(data_type, data_amount):
        DelayCalculateData.loss_data[data_type]["sent_data_amount"] += data_amount

    def add_loss_drop_data(data_type):
        type_data_amount_dict = {
            "CBR": (1460 * 8),
            "voice": (10 * 8),
            "video": (1000 * 8)
        }
        
        DelayCalculateData.loss_data[data_type]["drop_data_amount"] += type_data_amount_dict[data_type]
    
    def throughput_calculate():
        total_ue_data_amount = 0
        total_square_data_amount = 0
        for ue_id, data_amount in DelayCalculateData.total_ue_data.items():
            total_ue_data_amount += data_amount
            total_square_data_amount += (data_amount ** 2)
        DelayCalculateData.system_throughput = total_ue_data_amount * 1000 / SystemInfo.system_time / (10 ** 6)
        DelayCalculateData.avg_ue_throughput = total_ue_data_amount * 1000 / SystemInfo.system_time / (len(NetworkSettings.ue_to_bs_mapping_table)) / (10 ** 6)
        DelayCalculateData.fairness = (total_ue_data_amount ** 2) / ((len(NetworkSettings.ue_to_bs_mapping_table)) * total_square_data_amount)

        dc_ue_data_amount = 0
        dc_square_data_amount = 0
        for ue_id, data_amount in DelayCalculateData.dc_ue_data.items():
            dc_ue_data_amount += data_amount
            dc_square_data_amount += (data_amount ** 2)
        if len(DelayCalculateData.dc_ue_data) != 0:
            DelayCalculateData.dc_avg_ue_throughput = dc_ue_data_amount * 1000 / SystemInfo.system_time / (len(DelayCalculateData.dc_ue_data)) / (10 ** 6)
            DelayCalculateData.dc_fairness = (dc_ue_data_amount ** 2) / ((len(DelayCalculateData.dc_ue_data)) * dc_square_data_amount)
    
    def delay_calculate():
        DelayCalculateData.cbr_delay = DelayCalculateData.delay_data["CBR"]["queue_time"] / DelayCalculateData.delay_data["CBR"]["data_amount"]
        DelayCalculateData.voice_delay = DelayCalculateData.delay_data["voice"]["queue_time"] / DelayCalculateData.delay_data["voice"]["data_amount"]
        DelayCalculateData.video_delay = DelayCalculateData.delay_data["video"]["queue_time"] / DelayCalculateData.delay_data["video"]["data_amount"]
        delay_data_queue_time = DelayCalculateData.delay_data["CBR"]["queue_time"] + DelayCalculateData.delay_data["voice"]["queue_time"] + DelayCalculateData.delay_data["video"]["queue_time"]
        delay_data_data_amount = DelayCalculateData.delay_data["CBR"]["data_amount"] + DelayCalculateData.delay_data["voice"]["data_amount"] + DelayCalculateData.delay_data["video"]["data_amount"]
        DelayCalculateData.avg_delay = delay_data_queue_time / delay_data_data_amount

    def loss_calculate():
        DelayCalculateData.cbr_loss = DelayCalculateData.loss_data["CBR"]["drop_data_amount"] / (DelayCalculateData.loss_data["CBR"]["drop_data_amount"] + DelayCalculateData.loss_data["CBR"]["sent_data_amount"])
        DelayCalculateData.voice_loss = DelayCalculateData.loss_data["voice"]["drop_data_amount"] / (DelayCalculateData.loss_data["voice"]["drop_data_amount"] + DelayCalculateData.loss_data["voice"]["sent_data_amount"])
        DelayCalculateData.video_loss = DelayCalculateData.loss_data["video"]["drop_data_amount"] / (DelayCalculateData.loss_data["video"]["drop_data_amount"] + DelayCalculateData.loss_data["video"]["sent_data_amount"])
        loss_data_drop_data_amount = DelayCalculateData.loss_data["CBR"]["drop_data_amount"] + DelayCalculateData.loss_data["voice"]["drop_data_amount"] + DelayCalculateData.loss_data["video"]["drop_data_amount"]
        loss_data_sent_data_amount = DelayCalculateData.loss_data["CBR"]["sent_data_amount"] + DelayCalculateData.loss_data["voice"]["sent_data_amount"] + DelayCalculateData.loss_data["video"]["sent_data_amount"]
        DelayCalculateData.avg_loss = loss_data_drop_data_amount / (loss_data_drop_data_amount + loss_data_sent_data_amount)