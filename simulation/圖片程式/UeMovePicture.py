import csv
from multiprocessing.sharedctypes import Value
from statistics import mode
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
from NetworkSettings import SystemInfo
import pandas as pd 
'''
data_row = [[0]system_throughput, [1]avg_ue_throughput, [2]dc_avg_ue_throughput,
            [3]fairness, [4]dc_fairness, [5]cbr_delay, [6]voice_delay,
            [7]video_delay, [8]avg_delay, [9]cbr_loss, [10]voice_loss,
            [11]video_loss, [12]avg_loss,[13]mode,[14]average_UE_awake,[15]ue_number,[16]unit_throughput_awake_time,
            [17]self.power_saving,[18]UE_speed,[19]bs_number,[20]beam_number,[21]bs_dc_range_ratio,
            [22]avg_BS_throughput,[23]unit_bs_throughput_awake_time,[24]NetworkSettings.CBR_data_change,[25]NetworkSettings.Video_data_change]
'''
test_round = 10
# 直方圖
# 指定使用字型和大小
#myfont = FontProperties(fname='D:/Programs/Lib/site-packages/matplotlib/mpl-data/fonts/ttf/msjh.ttc', size=40)
system_throughput = dict()
average_UE_awake = dict()
unit_throughput_awake_time = dict() # mode:[unit_throughput_awake_time]
power_saving = dict()
avg_delay = dict()
avg_loss = dict()
for i in range(6):
  system_throughput[i] = dict()
  average_UE_awake[i] = dict()
  power_saving[i] = dict()
  unit_throughput_awake_time[i] = dict()
  avg_delay[i] = dict()
  avg_loss[i] = dict()

UE_speed = list() # mode:[UE_speed] 
  
# 開啟 CSV 檔案
path  = "ue_move_change.csv"
with open(path, newline='') as csvfile:
  # 讀取 CSV 檔案內容
  rows = csv.reader(csvfile)
  # 以迴圈輸出每一列
  for row in rows:
    float_row = [float(item) for item in row]
    if float_row[18] not in UE_speed:
      UE_speed.append(float_row[18])
    if float_row[13] == 0:
      if float_row[18] not in system_throughput[0]:
        system_throughput[0][float_row[18]] = float_row[0]
        avg_delay[0][float_row[18]] = float_row[8]
        avg_loss[0][float_row[18]] = float_row[12]
        average_UE_awake[0][float_row[18]] = float_row[14]
        unit_throughput_awake_time[0][float_row[18]] = float_row[16]
        power_saving[0][float_row[18]] = float_row[17]
      else:
        system_throughput[0][float_row[18]] += float_row[0]
        avg_delay[0][float_row[18]] += float_row[8]
        avg_loss[0][float_row[18]] += float_row[12]
        average_UE_awake[0][float_row[18]] += float_row[14]
        unit_throughput_awake_time[0][float_row[18]] += float_row[16]
        power_saving[0][float_row[18]] += float_row[17]

    elif float_row[13] == 1:
      if float_row[18] not in system_throughput[1]:
        system_throughput[1][float_row[18]] = float_row[0]
        avg_delay[1][float_row[18]] = float_row[8]
        avg_loss[1][float_row[18]] = float_row[12]
        average_UE_awake[1][float_row[18]] = float_row[14]
        unit_throughput_awake_time[1][float_row[18]] = float_row[16]
        power_saving[1][float_row[18]] = float_row[17]
      else:
        system_throughput[1][float_row[18]] += float_row[0]
        avg_delay[1][float_row[18]] += float_row[8]
        avg_loss[1][float_row[18]] += float_row[12]
        average_UE_awake[1][float_row[18]] += float_row[14]
        unit_throughput_awake_time[1][float_row[18]] += float_row[16]
        power_saving[1][float_row[18]] += float_row[17]

    elif float_row[13] == 2:
      if float_row[18] not in system_throughput[2]:
        system_throughput[2][float_row[18]] = float_row[0]
        avg_delay[2][float_row[18]] = float_row[8]
        avg_loss[2][float_row[18]] = float_row[12]
        average_UE_awake[2][float_row[18]] = float_row[14]
        unit_throughput_awake_time[2][float_row[18]] = float_row[16]
        power_saving[2][float_row[18]] = float_row[17]
      else:
        system_throughput[2][float_row[18]] += float_row[0]
        avg_delay[2][float_row[18]] += float_row[8]
        avg_loss[2][float_row[18]] += float_row[12]
        average_UE_awake[2][float_row[18]] += float_row[14]
        unit_throughput_awake_time[2][float_row[18]] += float_row[16]
        power_saving[2][float_row[18]] += float_row[17]

    elif float_row[13] == 3:
      if float_row[18] not in system_throughput[3]:
        system_throughput[3][float_row[18]] = float_row[0]
        avg_delay[3][float_row[18]] = float_row[8]
        avg_loss[3][float_row[18]] = float_row[12]
        average_UE_awake[3][float_row[18]] = float_row[14]
        unit_throughput_awake_time[3][float_row[18]] = float_row[16]
        power_saving[3][float_row[18]] = float_row[17]
      else:
        system_throughput[3][float_row[18]] += float_row[0]
        avg_delay[3][float_row[18]] += float_row[8]
        avg_loss[3][float_row[18]] += float_row[12]
        average_UE_awake[3][float_row[18]] += float_row[14]
        unit_throughput_awake_time[3][float_row[18]] += float_row[16]
        power_saving[3][float_row[18]] += float_row[17]
    elif float_row[13] == 4:
      if float_row[18] not in system_throughput[4]:
        system_throughput[4][float_row[18]] = float_row[0]
        avg_delay[4][float_row[18]] = float_row[8]
        avg_loss[4][float_row[18]] = float_row[12]
        average_UE_awake[4][float_row[18]] = float_row[14]
        unit_throughput_awake_time[4][float_row[18]] = float_row[16]
        power_saving[4][float_row[18]] = float_row[17]
      else:
        system_throughput[4][float_row[18]] += float_row[0]
        avg_delay[4][float_row[18]] += float_row[8]
        avg_loss[4][float_row[18]] += float_row[12]
        average_UE_awake[4][float_row[18]] += float_row[14]
        unit_throughput_awake_time[4][float_row[18]] += float_row[16]
        power_saving[4][float_row[18]] += float_row[17]
    else:
      if float_row[18] not in system_throughput[5]:
        system_throughput[5][float_row[18]] = float_row[0]
        avg_delay[5][float_row[18]] = float_row[8]
        avg_loss[5][float_row[18]] = float_row[12]
        average_UE_awake[5][float_row[18]] = float_row[14]
        unit_throughput_awake_time[5][float_row[18]] = float_row[16]
        power_saving[5][float_row[18]] = float_row[17]
      else:
        system_throughput[5][float_row[18]] += float_row[0]
        avg_delay[5][float_row[18]] += float_row[8]
        avg_loss[5][float_row[18]] += float_row[12]
        average_UE_awake[5][float_row[18]] += float_row[14]
        unit_throughput_awake_time[5][float_row[18]] += float_row[16]
        power_saving[5][float_row[18]] += float_row[17]

UE_speed = sorted(UE_speed)

for i in range(6): #取平均值
  for j in range(len(UE_speed)):
    system_throughput[i][UE_speed[j]] = system_throughput[i][UE_speed[j]] / test_round
    avg_delay[i][UE_speed[j]] = avg_delay[i][UE_speed[j]] / test_round
    avg_loss[i][UE_speed[j]] = avg_loss[i][UE_speed[j]] / test_round
    average_UE_awake[i][UE_speed[j]] = average_UE_awake[i][UE_speed[j]] / test_round
    unit_throughput_awake_time[i][UE_speed[j]] = unit_throughput_awake_time[i][UE_speed[j]] / test_round
    power_saving[i][UE_speed[j]] = power_saving[i][UE_speed[j]] / test_round


speed = ['5', '20', '40','60','100']
x = np.arange(len(speed))
width = 0.15

system_throughput_dict = dict()
avg_delay_dict = dict()
avg_loss_dict = dict()
unit_throughput_awake_time_dict = dict()
average_UE_awake_dict = dict()
power_saving_dict = dict()

for soulation in range(6):
  system_throughput_dict[soulation] = list()
  avg_delay_dict[soulation] = list()
  avg_loss_dict[soulation] = list()
  unit_throughput_awake_time_dict[soulation] = list()
  average_UE_awake_dict[soulation] = list()
  power_saving_dict[soulation] = list()
  for j in range(len(UE_speed)):  
    system_throughput_dict[soulation].append(system_throughput[soulation][UE_speed[j]])
    avg_delay_dict[soulation].append(avg_delay[soulation][UE_speed[j]])
    avg_loss_dict[soulation].append(avg_loss[soulation][UE_speed[j]])
    unit_throughput_awake_time_dict[soulation].append(unit_throughput_awake_time[soulation][UE_speed[j]])
    average_UE_awake_dict[soulation].append(average_UE_awake[soulation][UE_speed[j]])
    power_saving_dict[soulation].append(power_saving[soulation][UE_speed[j]])

###system_throughput
plt.figure()
plt.bar(x - width * 2.5, system_throughput_dict[5], width, label='OUR')
plt.bar(x - width * 1.5, system_throughput_dict[0], width, label='OUR+${DC_{1rx}}$')
plt.bar(x - width * 0.5, system_throughput_dict[1], width, label='OUR+${DC_{2rx}}$')
plt.bar(x + width * 0.5, system_throughput_dict[2], width, label='FIX')
plt.bar(x + width * 1.5, system_throughput_dict[3], width, label='DOM')
plt.bar(x + width * 2.5, system_throughput_dict[4], width, label='BPF')
plt.xticks(x, speed)
plt.xlabel("Ue_speed(km/hr)")
plt.ylabel('System throughput(Mbps)')
plt.legend(loc = "best")
plt.savefig('UE_speed_System_throughput.pdf')


###average_UE_awake
plt.figure()
plt.bar(x - width * 2.5, power_saving_dict[5], width, label='OUR')
plt.bar(x - width * 1.5, power_saving_dict[0], width, label='OUR+${DC_{1rx}}$')
plt.bar(x - width * 0.5, power_saving_dict[1], width, label='OUR+${DC_{2rx}}$')
plt.bar(x + width * 0.5, power_saving_dict[2], width, label='FIX')
plt.bar(x + width * 1.5, power_saving_dict[3], width, label='DOM')
plt.bar(x + width * 2.5, power_saving_dict[4], width, label='BPF')
plt.xticks(x, speed)
plt.xlabel("Ue_speed(km/hr)")
plt.ylabel('awake time of UEs(%)')
plt.legend(loc = "best")
plt.savefig('UE_speed_average_UE_awake.pdf')

###unit_awake_time_system_throughput
plt.figure()
plt.bar(x - width * 2.5, unit_throughput_awake_time_dict[5], width, label='OUR')
plt.bar(x - width * 1.5, unit_throughput_awake_time_dict[0], width, label='OUR+${DC_{1rx}}$')
plt.bar(x - width * 0.5, unit_throughput_awake_time_dict[1], width, label='OUR+${DC_{2rx}}$')
plt.bar(x + width * 0.5, unit_throughput_awake_time_dict[2], width, label='FIX')
plt.bar(x + width * 1.5, unit_throughput_awake_time_dict[3], width, label='DOM')
plt.bar(x + width * 2.5, unit_throughput_awake_time_dict[4], width, label='BPF')
plt.xticks(x, speed)
plt.xlabel("Ue_speed(km/hr)")
plt.ylabel('unit awake time of System throughput(Mbps)')
plt.legend(loc = "best")
plt.savefig('UE_speed_unit_time_System_throughput.pdf')

###avg_delay
plt.figure()
plt.bar(x - width * 2.5, avg_delay_dict[5], width, label='OUR')
plt.bar(x - width * 1.5, avg_delay_dict[0], width, label='OUR+${DC_{1rx}}$')
plt.bar(x - width * 0.5, avg_delay_dict[1], width, label='OUR+${DC_{2rx}}$')
plt.bar(x + width * 0.5, avg_delay_dict[2], width, label='FIX')
plt.bar(x + width * 1.5, avg_delay_dict[3], width, label='DOM')
plt.bar(x + width * 2.5, avg_delay_dict[4], width, label='BPF')
plt.xticks(x, speed)
plt.xlabel("Ue_speed(km/hr)")
plt.ylabel('Average_delay(ms)')
plt.legend(loc = "best")
plt.savefig('UE_speed_delay.pdf')

###avg_loss
plt.figure()
plt.bar(x - width * 2.5, avg_loss_dict[5], width, label='OUR')
plt.bar(x - width * 1.5, avg_loss_dict[0], width, label='OUR+${DC_{1rx}}$')
plt.bar(x - width * 0.5, avg_loss_dict[1], width, label='OUR+${DC_{2rx}}$')
plt.bar(x + width * 0.5, avg_loss_dict[2], width, label='FIX')
plt.bar(x + width * 1.5, avg_loss_dict[3], width, label='DOM')
plt.bar(x + width * 2.5, avg_loss_dict[4], width, label='BPF')
plt.xticks(x, speed)
plt.xlabel("Ue_speed(km/hr)")
plt.ylabel('Average packet loss(%)')
plt.legend(loc = "best")
plt.savefig('UE_speed_packet_loss.pdf')

plt.show()
#再加一張圖 plt.figure
    