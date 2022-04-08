import random
from TrafficGenerator import TrafficGenerator,GenerateUeMove
from NetworkSettings import NetworkSettings,Simulation, SystemInfo
from BeamTransmit import BeamUseFunction

class UeProcessData: #接收基地台傳輸資料
    def __init__(self, event_details, event_manager, ue_id):
        self.event_details = event_details
        self.event_manager = event_manager
        self.ue_id = ue_id
        self.ue = NetworkSettings.object_info_dict[ue_id]
        #self.beam_transmit = BeamUseFunction.bs_transmit_beam #example: bs_id:[beam]
        #self.bs_beam_ue = BeamUseFunction.bs_beam_ue #example: bs_id:{beam:[ue_id]}

        if self.ue_id not in Simulation.ue_open_time:
            Simulation.ue_open_time[self.ue_id] = 0
        
    def execute(self):
        received_amount = self.event_details['data_amount']
        self.ue.add_received_data_amount(received_amount)
        #self.ue_time_calculate(received_amount)

    #def ue_time_calculate(self,received_amount):
    #    for bs_id,beam_map_ue in self.bs_beam_ue.items():
    #        for beam,ue_id in beam_map_ue.items():

class UserEquipment:
    event_handler_dict = {
        "incoming_downlink_data": UeProcessData,
        "generate_ue_move": GenerateUeMove,
    }

    def __init__(self, ue_id, event_manager):
        self.received_data_amount = 0
        self.ue_id = "ue{}".format(ue_id)
        self.event_manager = event_manager
        data_type = ['voice','video','CBR']
        data_type_number = len(data_type)
        for i in range(data_type_number):
            tg_id = self.ue_id + "{}".format(data_type[i])
            tg = TrafficGenerator(self.ue_id, tg_id, event_manager)
            NetworkSettings.object_info_dict[tg_id] = tg

    def event_handler(self, event_content):
        event_name = event_content['event_name']
        #print("user event_name = ",event_name)
        if event_name in self.event_handler_dict and event_name != 'generate_ue_move':
            self.event_handler_dict[event_name](event_content['event_details'], self.event_manager, self.ue_id).execute()
        elif event_name == 'generate_ue_move':
            self.event_handler_dict[event_name](self.event_manager, self.ue_id).execute()
        else:
            print("The {} cannot handle this event {}".format(self.ue_id, event_name))

    def add_received_data_amount(self, data_amount):
        self.received_data_amount += data_amount
