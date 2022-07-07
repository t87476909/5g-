from random import randrange
from NetworkSettings import NetworkSettings,SystemInfo,Simulation
from ValueCalculate import ValueControlData
from BeamForming import BeamFormingFunction
from BeamExchange import BeamChangeControl
import random

class DominateControlValue:
    bs_dominate = dict()

class Dominate:
    def __init__(self,bs_id):
        self.bs_id = bs_id
        self.bs_list = NetworkSettings.bs_id_list
        self.bs_neighbor = NetworkSettings.bs_neighbor #example:[bs_id][bs_id] 鄰居不包含自己
        self.bs_number = NetworkSettings.num_of_bs
        self.last_bs = NetworkSettings.bs_id_list[-1] #最後一個基地台
        self.mode = Simulation.mode
        self.bs_beam_neighbor = NetworkSettings.bs_beam_neighbor #example [target bs][neighbor bs][target beam][neighbor beam]
        self.bs_throughput = ValueControlData.bs_throughput #example:[bs_id][last or before]
        self.beam_throughput = ValueControlData.beam_throughput #example:bs_id:[beam_throughput]
        self.bs_beam_list = BeamFormingFunction.bs_generator_beam_list #example:[bs_id][last or before]
        self.beam_change_or_not = BeamChangeControl.beam_change_or_not #[bs_id][beam list]
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.complete_bs = 0
        self.bs_allocated = list() #example:[bs_id]
        self.coordinate_mask = dict()
        
        #self.priority = 0 #優先權都先預設為0

        if self.bs_id not in DominateControlValue.bs_dominate:
            DominateControlValue.bs_dominate[self.bs_id] = None
            #CoordinateControlValue.coordinate_mask[self.bs_id] = dict()
            #for i in range(self.beam_number):
            #    CoordinateControlValue.coordinate_mask[self.bs_id][i] = list()

    def execute(self):
        self.bs_throughput_calculate()
        if self.beam_index == 0 and self.bs_throughput[self.bs_id]['last_time'] != None:
            if self.bs_id == self.last_bs: #若所有的dominate都決定完了

                for i in range(len(self.bs_list)):
                    bs = self.bs_list[i]
                    self.coordinate_mask[bs] = dict()
                    for j in range(self.beam_number):
                        self.coordinate_mask[bs][j] = list()

                while self.complete_bs < self.bs_number:
                    self.dominate_determine()
                    #print("DominateControlValue.bs_dominate(當前支配者) = ",DominateControlValue.bs_dominate)
                    self.coordinate()
                    #print("self.bs_allocated(已分配波束基地台) = {} self.complete_bs(已分配基地台數量) = {} ".format(self.bs_allocated,self.complete_bs))
                    for dominate_bs_id,dominate_bs in DominateControlValue.bs_dominate.items():
                        DominateControlValue.bs_dominate[dominate_bs_id] = None
                #print("self.bs_throughput(全部bs的流量) = ",self.bs_throughput)
                #print("coordinate_mask = ",self.coordinate_mask)
            #print("最終全部基地台波束結果 = ",self.bs_beam_list)
    def bs_throughput_calculate(self): 
        if self.beam_index == 0 and SystemInfo.system_time !=0:
            bs_data_amount = 0
            bs_data_amount = sum(self.beam_throughput[self.bs_id])
            #print("self.beam_throughput 1 =",self.beam_throughput)
            
            if self.bs_throughput[self.bs_id]['last_time'] == None:
                self.bs_throughput[self.bs_id]['last_time'] = bs_data_amount
                if self.bs_throughput[self.bs_id]['last_time'] == 0:
                    self.bs_throughput[self.bs_id]['last_time'] += random.random()
            else:
                self.bs_throughput[self.bs_id]['time_before_last_time'] = self.bs_throughput[self.bs_id]['last_time']
                self.bs_throughput[self.bs_id]['last_time'] = bs_data_amount
            #print("bs_id = {} system_time = {} bs_beam_throughput = {} ".format(self.bs_id,SystemInfo.system_time,ValueControlData.beam_throughput[self.bs_id]))
            #print("bs_id = {} bs_throughput = {} ".format(self.bs_id,self.bs_throughput))

    def dominate_determine(self): #決定該bs可以被誰支配(支配的人可以知道幫其鄰近的基地台進行波束分配)
        #max_throughput = 0
        for target_bs_id,neighbor_bs_id_list in self.bs_neighbor.items():
            max_throughput = 0
            target_throughput = self.bs_throughput[target_bs_id]['last_time']
            for i in range(len(neighbor_bs_id_list)):
                neighbor_bs = neighbor_bs_id_list[i]
                neighbor_throughput = self.bs_throughput[neighbor_bs]['last_time']
                #print("target_throughput = ",target_throughput)
                #print("neighbor_bs = {} neighbor_throughput = {} ".format(neighbor_bs,neighbor_throughput))
                #print("target_bs_id = {} neighbor_bs = {} ".format(target_bs_id,neighbor_bs))
                #print("self.bs_allocated = ",self.bs_allocated)
                if target_bs_id not in self.bs_allocated and neighbor_bs not in self.bs_allocated: #假若自己沒有在已分配名單內
                    if target_throughput == neighbor_throughput: #避免流量相同導致優先權出現錯誤
                        target_throughput += random.random()
                        neighbor_throughput += random.random()
                        #print("self.bs_throughput = ",self.bs_throughput)
                        #print("target_throughput = {} neighbor_throughput = {} max_throughput = {} ".format(target_throughput,neighbor_throughput,max_throughput))
                    if target_throughput > neighbor_throughput and max_throughput <= neighbor_throughput:
                        DominateControlValue.bs_dominate[target_bs_id] = target_bs_id
                        #print("DominateControlValue.bs_dominate[target_bs_id](當前支配者) = ",DominateControlValue.bs_dominate[target_bs_id])
                        max_throughput = self.bs_throughput[target_bs_id]['last_time']
                    if target_throughput < neighbor_throughput and max_throughput <= neighbor_throughput:
                        DominateControlValue.bs_dominate[target_bs_id] = neighbor_bs
                        #print("DominateControlValue.bs_dominate[target_bs_id](當前支配者) = ",DominateControlValue.bs_dominate[target_bs_id])
                        max_throughput = self.bs_throughput[neighbor_bs]['last_time']
        #print("bs_id = {} DominateControlValue.bs_dominate = {} ".format(self.bs_id,DominateControlValue.bs_dominate[self.bs_id]))
    
    def coordinate(self):
        bs_neighbor_beam_throughput = dict()
        Dominator = list()
        for target_bs_id,editor_bs_id in DominateControlValue.bs_dominate.items(): #editor = 被修改的基地台
            if target_bs_id == editor_bs_id: #自己是自己的支配者
                Dominator.append(target_bs_id)

        for target_bs,neighbor_bs in self.bs_neighbor.items():
            if target_bs in Dominator:
                self.bs_allocated.append(target_bs)
                self.complete_bs += 1 #
                if self.mode == 1 and self.bs_number > 1:
                    neighbor_throughput = self.max_neighbor_throughput(target_bs)
                for j in range(len(neighbor_bs)):
                    if neighbor_bs[j] != target_bs and neighbor_bs[j] not in self.bs_allocated:
                        if self.mode == 1:
                            self.coordinate_two(target_bs,neighbor_bs[j],neighbor_throughput)
                        else:
                            self.coordinate_one(target_bs,neighbor_bs[j])
                    #print("target_be = {} neighbor_bs = {}".format(target_bs,neighbor_bs[j]))
                    #print("final = ",self.bs_beam_list[neighbor_bs[j]]['last_time'])
                    #print(" ")
    
    def coordinate_one(self,target_bs,neighbor_bs): #要避免波束進行相交的動作
        exchange = 1
        for i in range(self.beam_number):
            if self.beam_change_or_not[neighbor_bs][i] != 1: #該基地台的波束不能被修改
                current_target_beam = self.bs_beam_list[target_bs]['last_time'][i] #當前目標波束
                current_neighbor_beam = self.bs_beam_list[neighbor_bs]['last_time'][i] #當前鄰居波束
                for target_beam,neighbor_beam in self.bs_beam_neighbor[target_bs][neighbor_bs].items(): #沒有再加一層for迴圈是因為beam_neighbor剛好都是單一對單一
                    #print("current_target_beam = ",current_target_beam)
                    #print("current_neighbor_beam = ",current_neighbor_beam)
                    #print("target_beam = ",target_beam)
                    #print("neighbor_beam = ",neighbor_beam)
                    if target_beam == current_target_beam and neighbor_beam == current_neighbor_beam: #打出的波束與鄰居打出的波束有相交
                        self.coordinate_mask[neighbor_bs][current_neighbor_beam].append(current_target_beam) #當前被修改者要記錄支配者的mask(避免出現的波束)
                        if current_neighbor_beam in self.coordinate_mask[neighbor_bs][current_neighbor_beam]:
                            if i + exchange < self.beam_number:
                                while self.beam_change_or_not[neighbor_bs][i+exchange] != 0 and i != (self.beam_number - 1):
                                    #print("exchange = {} i = {}".format(exchange,i))
                                    if (i + exchange) < self.beam_number - 1: #一直跟後一位進行更換 直到最後一位
                                        exchange += 1
                                    elif exchange == i: #全部輪完沒有可以更換的波束
                                        break
                                    else:
                                        exchange = -i
                                self.bs_beam_list[neighbor_bs]['last_time'][i],self.bs_beam_list[neighbor_bs]['last_time'][i+exchange] = self.bs_beam_list[neighbor_bs]['last_time'][i+exchange],self.bs_beam_list[neighbor_bs]['last_time'][i]
    
    def max_neighbor_throughput(self,target_bs):
        neighbor_beam_throughput_dict = dict() #[beam_index][neighbor_beam_throughput] 紀錄可以配合的波束 的流量值
        for i in range(self.beam_number):
            neighbor_beam_throughput_dict.setdefault(i, [])
            current_target_beam = self.bs_beam_list[target_bs]['last_time'][i] #當前目標波束
            for neighbor_bs,target_neighbor_beam in self.bs_beam_neighbor[target_bs].items():
                current_neighbor_beam = self.bs_beam_list[neighbor_bs]['last_time'][i] #當前鄰居波束
                neighbor_beam_throughput = ValueControlData.beam_throughput[neighbor_bs][current_neighbor_beam] #該鄰居波束的流量
                for target_beam,neighbor_beam in target_neighbor_beam.items():
                    if target_beam == current_target_beam and neighbor_beam != None: #該波束正是現在target打的波束且該波束具有可以配合的鄰居波束
                        neighbor_beam_throughput_dict[i].append(neighbor_beam_throughput)
        #print(" ")
        #print("ValueControlData.beam_throughput[neighbor_bs] = ",ValueControlData.beam_throughput[neighbor_bs])
        #print("target_bs = {} neighbor_beam_throughput_dict = {} ".format(target_bs,neighbor_beam_throughput_dict))
        return neighbor_beam_throughput_dict

    def coordinate_two(self,target_bs,neighbor_bs,neighbor_throughput): #要讓波束進行相交的動作

        for i in range(self.beam_number):
            if self.beam_change_or_not[neighbor_bs][i] != 1: #該基地台的波束不能被修改
                if len(neighbor_throughput[i]) != 0:
                    max_neighbor_throughput = max(neighbor_throughput[i]) #可以交換的最大流量鄰居波束要被交換
                current_target_beam = self.bs_beam_list[target_bs]['last_time'][i] #當前目標波束
                current_neighbor_beam = self.bs_beam_list[neighbor_bs]['last_time'][i] #當前鄰居波束
                #print("current beam = {} neighbor_beam = {} ".format(current_target_beam,current_neighbor_beam))
                for target_beam,neighbor_beam in self.bs_beam_neighbor[target_bs][neighbor_bs].items(): #沒有再加一層for迴圈是因為beam_neighbor剛好都是單一對單一
                    #print("target_beam = {} neighbor_beam = {} ".format(target_beam,neighbor_beam))
                    if target_beam == current_target_beam and neighbor_beam == current_neighbor_beam: #打出的波束與鄰居打出的波束有相交
                        self.beam_change_or_not[neighbor_bs][i] = 1 #該鄰居波束設定為不能被修改
                        #有相交的波束不用動
                    if target_beam == current_target_beam and neighbor_beam != current_neighbor_beam: #打出的波束與鄰居打出的波束沒有相交(所以要讓其相交->根據最高波束流量來決定)
                        neighbor_beam_throughput = ValueControlData.beam_throughput[neighbor_bs][current_neighbor_beam]
                        if neighbor_beam != None and max_neighbor_throughput == neighbor_beam_throughput: #表示該波束有鄰居波束
                            self.bs_beam_list[neighbor_bs]['last_time'][i] = neighbor_beam
                            self.beam_change_or_not[neighbor_bs][i] = 1
        #print("final = ",self.bs_beam_list[neighbor_bs]['last_time'])
        #print(" ")
    