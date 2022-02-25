from NetworkSettings import NetworkSettings,Simulation,SystemInfo
from BeamExchange import BeamChangeControl
from BeamForming import BeamFormingFunction
from BeamPredict import PredictControlValue
from BeamTransmit import BeamUseFunction
from Dominate import DominateControlValue
from UeTime import TimeControlValue
from ValueCalculate import ValueControlData
from DelayCalculate import DelayCalculate,DelayCalculateData
import csv

class StatisticWork:
    def __init__(self):
        self.total_received_data = 0
        self.total_unsent_data = 0
        self.average_UE_awake = 0
        self.unit_throughput_awake_time = 0
        self.power_saving = 0
        self.ue_number = NetworkSettings.num_of_ue + NetworkSettings.num_of_ue_overlap

    def execute(self):
        self.calculate_ue_data()
        self.calculate_bs_data()
        self.calculate_ue_open_time()
        self.print_all_results()
        if NetworkSettings.write_data == True:
            self.write_csv()
        self.data_clear()
        if Simulation.mode == 4: #方法是最後一個時要更換參數 記得要換成4
            #self.system_refrash()
            self.data_change()
    
    def calculate_ue_data(self):
        for ue in NetworkSettings.ue_id_list:
            self.total_received_data += NetworkSettings.object_info_dict[ue].received_data_amount
            #print("ue = ",ue)
            #print("self.total_received_data = ",self.total_received_data)
    def calculate_bs_data(self):
        for bs in NetworkSettings.bs_id_list:
            bs_queue = NetworkSettings.object_info_dict[bs].queue_for_ue
            for ue_id, ue_type_data in bs_queue.items():
                for data_type,data_amount in ue_type_data.items(): 
                    self.total_unsent_data += data_amount
            #print("bs = {} , bs_queue = {} ".format(bs,bs_queue))
            #print("self.total_unsent_data = ",self.total_unsent_data)
        
    def calculate_ue_open_time(self):
        total_ue_open_time = sum(Simulation.ue_open_time.values())
        self.average_UE_awake = total_ue_open_time / (NetworkSettings.num_of_bs * (NetworkSettings.num_of_ue + NetworkSettings.num_of_ue_overlap))

    def print_all_results(self):
        print("執行模式 = ",Simulation.mode)
        print("DelayCalculateData.dc_ue_data: ", DelayCalculateData.dc_ue_data)
        print("NetworkSettings.bs_ue_distance: ", NetworkSettings.bs_ue_distance)
        
        DelayCalculate.throughput_calculate()
        print("System Throughput(Mbps): ", DelayCalculateData.system_throughput)
        print("Average UE Throughput(Mbps): ", DelayCalculateData.avg_ue_throughput)
        print("Average DC UE Throughput(Mbps): ", DelayCalculateData.dc_avg_ue_throughput)
        print("UE Fairness: ", DelayCalculateData.fairness)
        print("DC UE Fairness: ", DelayCalculateData.dc_fairness)
        
        DelayCalculate.delay_calculate()
        DelayCalculate.loss_calculate()
        print("CBR Delay: ", DelayCalculateData.cbr_delay)
        print("Voice Delay: ", DelayCalculateData.voice_delay)
        print("Video Delay: ", DelayCalculateData.video_delay)
        print("Average Delay: ", DelayCalculateData.avg_delay)
        print("CBR Loss: ", DelayCalculateData.cbr_loss)
        print("Voice Loss: ", DelayCalculateData.voice_loss)
        print("Video Loss: ", DelayCalculateData.video_loss)
        print("Average Loss: ", DelayCalculateData.avg_loss)
        
        #print("所有ue總共開啟時間 = ",Simulation.ue_open_time)
        self.unit_throughput_awake_time = DelayCalculateData.system_throughput / self.average_UE_awake
        self.power_saving = self.average_UE_awake / NetworkSettings.simulation_time * 100 #開啟時間比率(百分比)
        print("所有ue平均開啟時間 = ",self.average_UE_awake)
        print("單位醒來時間吞吐量 = ",self.unit_throughput_awake_time)
        print("開啟時間百分比 = ",self.power_saving)
        print("total_received_data: {}".format(self.total_received_data)) #bytes
        print("total_unsent_data: {}".format(self.total_unsent_data))

    def write_csv(self):
        path  = "simulation_result.csv"
        with open(path, 'a+', newline='') as f:
            csv_write = csv.writer(f)
            data_row = [DelayCalculateData.system_throughput, DelayCalculateData.avg_ue_throughput, DelayCalculateData.dc_avg_ue_throughput,
                        DelayCalculateData.fairness, DelayCalculateData.dc_fairness, DelayCalculateData.cbr_delay, DelayCalculateData.voice_delay,
                        DelayCalculateData.video_delay, DelayCalculateData.avg_delay, DelayCalculateData.cbr_loss, DelayCalculateData.voice_loss,
                        DelayCalculateData.video_loss, DelayCalculateData.avg_loss,Simulation.mode,self.average_UE_awake,self.ue_number,
                        self.unit_throughput_awake_time,self.power_saving]
            csv_write.writerow(data_row)

    def data_clear(self): #清除上一次檔案測試留存
        BeamChangeControl.beam_change_or_not.clear()
        BeamFormingFunction.bs_generator_beam_list.clear()
        BeamFormingFunction.control_variable.clear()
        BeamFormingFunction.bs_generator_beam_state.clear()
        PredictControlValue.bs_miss_beam.clear()
        BeamUseFunction.ue_location.clear()
        BeamUseFunction.ue_overlap_location.clear()
        BeamUseFunction.bs_location.clear()
        BeamUseFunction.bs_transmit_beam.clear()
        BeamUseFunction.bs_transmit_state = 0
        DelayCalculateData.total_ue_data = {}
        DelayCalculateData.dc_ue_data = {}
        DelayCalculateData.delay_data = {"CBR": {"data_amount": 0, "queue_time": 0}, "voice": {"data_amount": 0, "queue_time": 0}, "video": {"data_amount": 0, "queue_time": 0}}
        DelayCalculateData.loss_data = {"CBR": {"drop_data_amount": 0, "sent_data_amount": 0}, "voice": {"drop_data_amount": 0, "sent_data_amount": 0}, "video": {"drop_data_amount": 0, "sent_data_amount": 0}}
        DelayCalculateData.system_throughput = 0
        DelayCalculateData.avg_ue_throughput = 0
        DelayCalculateData.dc_avg_ue_throughput = 0
        DelayCalculateData.fairness = 0
        DelayCalculateData.dc_fairness = 0
        DelayCalculateData.cbr_delay = 0
        DelayCalculateData.voice_delay = 0
        DelayCalculateData.video_delay = 0
        DelayCalculateData.avg_delay = 0    
        DelayCalculateData.cbr_loss = 0
        DelayCalculateData.voice_loss = 0
        DelayCalculateData.video_loss = 0
        DelayCalculateData.avg_loss = 0
        DominateControlValue.bs_dominate.clear()
        NetworkSettings.BS_center_frequency.clear()
        NetworkSettings.ue_id_list.clear()
        NetworkSettings.bs_id_list.clear()
        NetworkSettings.object_info_dict.clear()
        NetworkSettings.ue_to_bs_mapping_table.clear()
        NetworkSettings.bs_ue_distance.clear()
        NetworkSettings.bs_beam_neighbor.clear()
        NetworkSettings.bs_neighbor.clear()
        NetworkSettings.beam_eliminate.clear()
        SystemInfo.system_time = 0
        Simulation.ue_open_time.clear()
        TimeControlValue.bs_beam_ue.clear()
        TimeControlValue.ue_beam_allocated.clear()
        ValueControlData.beam_throughput.clear()
        ValueControlData.bs_throughput.clear()
        ValueControlData.beam_probability.clear()
        ValueControlData.transmission_beam_throughput.clear()

    def data_change(self): #x軸變換
        NetworkSettings.num_of_ue += 5
        NetworkSettings.num_of_ue_overlap += 20
        #("NetworkSettings.num_of_ue = ",NetworkSettings.num_of_ue)
        #print("NetworkSettings.num_of_ue_overlap = ",NetworkSettings.num_of_ue_overlap)
        #NetworkSettings.num_of_bs += 5
        #SystemInfo.control_variable += 10
        