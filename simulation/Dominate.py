from random import randrange
from NetworkSettings import NetworkSettings, SystemInfo, Simulation
from ValueCalculate import ValueControlData
from BeamForming import BeamFormingFunction
from BeamExchange import BeamChangeControl
import random


class DominateControlValue:
    bs_dominate = dict()


class Dominate:
    def __init__(self, bs_id):
        self.bs_id = bs_id
        self.bs_list = NetworkSettings.bs_id_list
        # example:[bs_id][bs_id] 鄰居不包含自己
        self.bs_neighbor = NetworkSettings.bs_neighbor
        self.bs_number = NetworkSettings.num_of_bs
        self.last_bs = NetworkSettings.bs_id_list[-1]  # 最後一個基地台
        self.mode = Simulation.mode
        # example [target bs][neighbor bs][target beam][neighbor beam]
        self.bs_beam_neighbor = NetworkSettings.bs_beam_neighbor
        # example:[bs_id][last or before]
        self.bs_throughput = ValueControlData.bs_throughput
        # example:bs_id:[beam_throughput]
        self.beam_throughput = ValueControlData.beam_throughput
        # example:[bs_id][last or before]
        self.bs_beam_list = BeamFormingFunction.bs_generator_beam_list
        # [bs_id][beam list]
        self.beam_change_or_not = BeamChangeControl.beam_change_or_not
        self.beam_number = round(360 / NetworkSettings.beam_angle)
        self.beam_index = SystemInfo.system_time % self.beam_number
        self.complete_bs = 0
        self.bs_allocated = list()  # example:[bs_id]
        self.coordinate_mask = dict()

        if self.bs_id not in DominateControlValue.bs_dominate:
            DominateControlValue.bs_dominate[self.bs_id] = None

    def execute(self):
        self.bs_throughput_calculate()
        if self.beam_index == 0 and self.bs_throughput[self.bs_id]['last_time'] != None:
            if self.bs_id == self.last_bs:  # 若所有的dominate都決定完了

                for i in range(len(self.bs_list)):
                    bs = self.bs_list[i]
                    self.coordinate_mask[bs] = dict()
                    for j in range(self.beam_number):
                        self.coordinate_mask[bs][j] = list()

                while self.complete_bs < self.bs_number:
                    self.dominate_determine()
                    self.coordinate()
                    for dominate_bs_id, dominate_bs in DominateControlValue.bs_dominate.items():
                        DominateControlValue.bs_dominate[dominate_bs_id] = None

    def bs_throughput_calculate(self):
        if self.beam_index == 0 and SystemInfo.system_time != 0:
            bs_data_amount = 0
            bs_data_amount = sum(self.beam_throughput[self.bs_id])

            if self.bs_throughput[self.bs_id]['last_time'] == None:
                self.bs_throughput[self.bs_id]['last_time'] = bs_data_amount
                if self.bs_throughput[self.bs_id]['last_time'] == 0:
                    self.bs_throughput[self.bs_id]['last_time'] += random.random()
            else:
                self.bs_throughput[self.bs_id]['time_before_last_time'] = self.bs_throughput[self.bs_id]['last_time']
                self.bs_throughput[self.bs_id]['last_time'] = bs_data_amount

    def dominate_determine(self):  # 決定該bs可以被誰支配(支配的人可以知道幫其鄰近的基地台進行波束分配)
        for target_bs_id, neighbor_bs_id_list in self.bs_neighbor.items():
            max_throughput = 0
            target_throughput = self.bs_throughput[target_bs_id]['last_time']
            for i in range(len(neighbor_bs_id_list)):
                neighbor_bs = neighbor_bs_id_list[i]
                neighbor_throughput = self.bs_throughput[neighbor_bs]['last_time']
                if target_bs_id not in self.bs_allocated and neighbor_bs not in self.bs_allocated:  # 假若自己沒有在已分配名單內
                    if target_throughput == neighbor_throughput:  # 避免流量相同導致優先權出現錯誤
                        target_throughput += random.random()
                        neighbor_throughput += random.random()
                    if target_throughput > neighbor_throughput and max_throughput <= neighbor_throughput:
                        DominateControlValue.bs_dominate[target_bs_id] = target_bs_id
                        max_throughput = self.bs_throughput[target_bs_id]['last_time']
                    if target_throughput < neighbor_throughput and max_throughput <= neighbor_throughput:
                        DominateControlValue.bs_dominate[target_bs_id] = neighbor_bs
                        max_throughput = self.bs_throughput[neighbor_bs]['last_time']

    def coordinate(self):
        bs_neighbor_beam_throughput = dict()
        Dominator = list()
        for target_bs_id, editor_bs_id in DominateControlValue.bs_dominate.items():  # editor = 被修改的基地台
            if target_bs_id == editor_bs_id:  # 自己是自己的支配者
                Dominator.append(target_bs_id)

        for target_bs, neighbor_bs in self.bs_neighbor.items():
            if target_bs in Dominator:
                self.bs_allocated.append(target_bs)
                self.complete_bs += 1
                for j in range(len(neighbor_bs)):
                    if neighbor_bs[j] != target_bs and neighbor_bs[j] not in self.bs_allocated:
                        if self.mode == 1:
                            self.coordinate_two(target_bs, neighbor_bs[j])
                        else:
                            self.coordinate_one(target_bs, neighbor_bs[j])

    def coordinate_one(self, target_bs, neighbor_bs):  # 要避免波束進行相交的動作

        for index in range(self.beam_number):
            if self.beam_change_or_not[neighbor_bs][index] == 0:
                current_target_beam = self.bs_beam_list[target_bs]['last_time'][index]
                for target_beam, neighbor_beam in self.bs_beam_neighbor[target_bs][neighbor_bs].items():
                    if target_beam == current_target_beam and neighbor_beam not in self.coordinate_mask[neighbor_bs][index]:
                        self.coordinate_mask[neighbor_bs][index].append(
                            neighbor_beam)  # 當前被修改鄰居基地台要記錄index位置不能放入的波束(避免波束相交)

        for i in range(self.beam_number):
            if self.beam_change_or_not[neighbor_bs][i] == 0:  # 該基地台的波束能被修改
                # 當前目標波束
                current_target_beam = self.bs_beam_list[target_bs]['last_time'][i]
                # 當前鄰居波束
                current_neighbor_beam = self.bs_beam_list[neighbor_bs]['last_time'][i]
                # 沒有再加一層for迴圈是因為beam_neighbor剛好都是單一對單一
                # 當前被修改基地台所打出的波束在被修改基地台不能放入的波束集合內（表示波束相交）
                if current_neighbor_beam in self.coordinate_mask[neighbor_bs][i]:
                    for j in range(self.beam_number):
                        if i != j:
                            # 當前鄰居波束的第j個index可以修改
                            if self.beam_change_or_not[neighbor_bs][j] == 0:
                                if self.bs_beam_list[neighbor_bs]['last_time'][i] not in self.coordinate_mask[neighbor_bs][j] and self.bs_beam_list[neighbor_bs]['last_time'][j] not in self.coordinate_mask[neighbor_bs][i]:
                                    self.bs_beam_list[neighbor_bs]['last_time'][i], self.bs_beam_list[neighbor_bs]['last_time'][
                                        j] = self.bs_beam_list[neighbor_bs]['last_time'][j], self.bs_beam_list[neighbor_bs]['last_time'][i]
                                    self.beam_change_or_not[neighbor_bs][i] = 1
                                    break

    def coordinate_two(self, target_bs, neighbor_bs):  # 要讓波束進行相交的動作
        for i in range(self.beam_number):
            if self.beam_change_or_not[neighbor_bs][i] == 0:  # 該鄰居基地台的波束能被修改
                # 當前目標波束
                current_target_beam = self.bs_beam_list[target_bs]['last_time'][i]
                # 當前鄰居波束
                current_neighbor_beam = self.bs_beam_list[neighbor_bs]['last_time'][i]
                # 沒有再加一層for迴圈是因為beam_neighbor剛好都是單一對單一
                for target_beam, neighbor_beam in self.bs_beam_neighbor[target_bs][neighbor_bs].items():
                    if target_beam == current_target_beam and neighbor_beam == current_neighbor_beam:  # 打出的波束與鄰居打出的波束有相交
                        # 該鄰居波束設定為不能被修改
                        self.beam_change_or_not[neighbor_bs][i] = 1
                        # 有相交的波束不用動
                    # 打出的波束與鄰居打出的波束沒有相交(所以要讓其相交)
                    if target_beam == current_target_beam and neighbor_beam != current_neighbor_beam:
                        # 表示鄰居基地台有雙連街的波束存在
                        if self.bs_beam_neighbor[target_bs][neighbor_bs][current_target_beam] != None:
                            for j in range(self.beam_number):
                                if i != j:  # 要i位置的波束跟j位置的波束的位置不同
                                    # 第j個波束可以交換且第j個波束是可以使第i個波束位置雙連接的波束
                                    if self.beam_change_or_not[neighbor_bs][j] == 0 and self.bs_beam_list[neighbor_bs]['last_time'][j] == neighbor_beam:
                                        self.bs_beam_list[neighbor_bs]['last_time'][i], self.bs_beam_list[neighbor_bs]['last_time'][
                                            j] = self.bs_beam_list[neighbor_bs]['last_time'][j], self.bs_beam_list[neighbor_bs]['last_time'][i]
                                        self.beam_change_or_not[neighbor_bs][i] = 1
                                        break
