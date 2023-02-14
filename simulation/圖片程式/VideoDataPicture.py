import csv
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
# 折線圖
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

Video_data = list() # mode:[Video_data] 
  
# 開啟 CSV 檔案
path  = "video_data_change.csv"
with open(path, newline='') as csvfile:
  # 讀取 CSV 檔案內容
  rows = csv.reader(csvfile)
  # 以迴圈輸出每一列
  for row in rows:
    float_row = [float(item) for item in row]
    if float_row[25] not in Video_data:
      Video_data.append(float_row[25])
    if float_row[13] == 0:
      if float_row[25] not in system_throughput[0]:
        system_throughput[0][float_row[25]] = float_row[0]
        avg_delay[0][float_row[25]] = float_row[8]
        avg_loss[0][float_row[25]] = float_row[12]
        average_UE_awake[0][float_row[25]] = float_row[14]
        unit_throughput_awake_time[0][float_row[25]] = float_row[16]
        power_saving[0][float_row[25]] = float_row[17]
      else:
        system_throughput[0][float_row[25]] += float_row[0]
        avg_delay[0][float_row[25]] += float_row[8]
        avg_loss[0][float_row[25]] += float_row[12]
        average_UE_awake[0][float_row[25]] += float_row[14]
        unit_throughput_awake_time[0][float_row[25]] += float_row[16]
        power_saving[0][float_row[25]] += float_row[17]

    elif float_row[13] == 1:
      if float_row[25] not in system_throughput[1]:
        system_throughput[1][float_row[25]] = float_row[0]
        avg_delay[1][float_row[25]] = float_row[8]
        avg_loss[1][float_row[25]] = float_row[12]
        average_UE_awake[1][float_row[25]] = float_row[14]
        unit_throughput_awake_time[1][float_row[25]] = float_row[16]
        power_saving[1][float_row[25]] = float_row[17]
      else:
        system_throughput[1][float_row[25]] += float_row[0]
        avg_delay[1][float_row[25]] += float_row[8]
        avg_loss[1][float_row[25]] += float_row[12]
        average_UE_awake[1][float_row[25]] += float_row[14]
        unit_throughput_awake_time[1][float_row[25]] += float_row[16]
        power_saving[1][float_row[25]] += float_row[17]

    elif float_row[13] == 2:
      if float_row[25] not in system_throughput[2]:
        system_throughput[2][float_row[25]] = float_row[0]
        avg_delay[2][float_row[25]] = float_row[8]
        avg_loss[2][float_row[25]] = float_row[12]
        average_UE_awake[2][float_row[25]] = float_row[14]
        unit_throughput_awake_time[2][float_row[25]] = float_row[16]
        power_saving[2][float_row[25]] = float_row[17]
      else:
        system_throughput[2][float_row[25]] += float_row[0]
        avg_delay[2][float_row[25]] += float_row[8]
        avg_loss[2][float_row[25]] += float_row[12]
        average_UE_awake[2][float_row[25]] += float_row[14]
        unit_throughput_awake_time[2][float_row[25]] += float_row[16]
        power_saving[2][float_row[25]] += float_row[17]

    elif float_row[13] == 3:
      if float_row[25] not in system_throughput[3]:
        system_throughput[3][float_row[25]] = float_row[0]
        avg_delay[3][float_row[25]] = float_row[8]
        avg_loss[3][float_row[25]] = float_row[12]
        average_UE_awake[3][float_row[25]] = float_row[14]
        unit_throughput_awake_time[3][float_row[25]] = float_row[16]
        power_saving[3][float_row[25]] = float_row[17]
      else:
        system_throughput[3][float_row[25]] += float_row[0]
        avg_delay[3][float_row[25]] += float_row[8]
        avg_loss[3][float_row[25]] += float_row[12]
        average_UE_awake[3][float_row[25]] += float_row[14]
        unit_throughput_awake_time[3][float_row[25]] += float_row[16]
        power_saving[3][float_row[25]] += float_row[17]
    elif float_row[13] == 4:
      if float_row[25] not in system_throughput[4]:
        system_throughput[4][float_row[25]] = float_row[0]
        avg_delay[4][float_row[25]] = float_row[8]
        avg_loss[4][float_row[25]] = float_row[12]
        average_UE_awake[4][float_row[25]] = float_row[14]
        unit_throughput_awake_time[4][float_row[25]] = float_row[16]
        power_saving[4][float_row[25]] = float_row[17]
      else:
        system_throughput[4][float_row[25]] += float_row[0]
        avg_delay[4][float_row[25]] += float_row[8]
        avg_loss[4][float_row[25]] += float_row[12]
        average_UE_awake[4][float_row[25]] += float_row[14]
        unit_throughput_awake_time[4][float_row[25]] += float_row[16]
        power_saving[4][float_row[25]] += float_row[17]
    elif float_row[13] == 5:
      if float_row[25] not in system_throughput[5]:
        system_throughput[5][float_row[25]] = float_row[0]
        avg_delay[5][float_row[25]] = float_row[8]
        avg_loss[5][float_row[25]] = float_row[12]
        average_UE_awake[5][float_row[25]] = float_row[14]
        unit_throughput_awake_time[5][float_row[25]] = float_row[16]
        power_saving[5][float_row[25]] = float_row[17]
      else:
        system_throughput[5][float_row[25]] += float_row[0]
        avg_delay[5][float_row[25]] += float_row[8]
        avg_loss[5][float_row[25]] += float_row[12]
        average_UE_awake[5][float_row[25]] += float_row[14]
        unit_throughput_awake_time[5][float_row[25]] += float_row[16]
        power_saving[5][float_row[25]] += float_row[17]

system_throughput_list = dict()
avg_delay_list = dict()
avg_loss_list = dict()  
average_UE_awake_list = dict()
unit_throughput_awake_time_list = dict()
power_saving_list = dict()
for y in range(6):
  system_throughput_list[y] = list()
  avg_delay_list[y] = list()
  avg_loss_list[y] = list()  
  average_UE_awake_list[y] = list()
  unit_throughput_awake_time_list[y] = list()
  power_saving_list[y] = list()

Video_data = sorted(Video_data)
for i in range(6): #取平均值
  for j in range(len(Video_data)):
    system_throughput_list[i].append(system_throughput[i][Video_data[j]] / test_round)
    avg_delay_list[i].append(avg_delay[i][Video_data[j]] / test_round)
    avg_loss_list[i].append(avg_loss[i][Video_data[j]] / test_round)
    average_UE_awake_list[i].append(average_UE_awake[i][Video_data[j]] / test_round)
    unit_throughput_awake_time_list[i].append(unit_throughput_awake_time[i][Video_data[j]] / test_round)
    power_saving_list[i].append(power_saving[i][Video_data[j]] / test_round)

plt.figure()
plt.plot(Video_data,unit_throughput_awake_time_list[5],'*-',color = 'm', label="OUR")
plt.plot(Video_data,unit_throughput_awake_time_list[0],'s-',color = 'r', label="OUR+${DC_{1rx}}$")
plt.plot(Video_data,unit_throughput_awake_time_list[1],'o-',color = 'g', label="OUR+${DC_{2rx}}$")
plt.plot(Video_data,unit_throughput_awake_time_list[2],'h-',color = 'b', label="FIX")
plt.plot(Video_data,unit_throughput_awake_time_list[3],'H-',color = 'c', label="DOM")
plt.plot(Video_data,unit_throughput_awake_time_list[4],'8-',color = 'k', label="BPF")
plt.xlabel("Video_data(Mbps)")
plt.ylabel("unit awake time of System throughput(Mbps)")
plt.legend(loc = "best")
plt.savefig('Video_unit_time_System_throughput.pdf')

plt.figure()
plt.plot(Video_data,system_throughput_list[5],'*-',color = 'm', label="OUR")
plt.plot(Video_data,system_throughput_list[0],'s-',color = 'r', label="OUR+${DC_{1rx}}$")
plt.plot(Video_data,system_throughput_list[1],'o-',color = 'g', label="OUR+${DC_{2rx}}$")
plt.plot(Video_data,system_throughput_list[2],'h-',color = 'b', label="FIX")
plt.plot(Video_data,system_throughput_list[3],'H-',color = 'c', label="DOM")
plt.plot(Video_data,system_throughput_list[4],'8-',color = 'k', label="BPF")
plt.xlabel("Video_data(Mbps)")
plt.ylabel("System throughput(Mbps)")
plt.legend(loc = "best")
plt.savefig('Video_System_throughput.pdf')

plt.figure()
plt.plot(Video_data,power_saving_list[5],'*-',color = 'm', label="OUR")
plt.plot(Video_data,power_saving_list[0],'s-',color = 'r', label="OUR+${DC_{1rx}}$")
plt.plot(Video_data,power_saving_list[1],'o-',color = 'g', label="OUR+${DC_{2rx}}$")
plt.plot(Video_data,power_saving_list[2],'h-',color = 'b', label="FIX")
plt.plot(Video_data,power_saving_list[3],'H-',color = 'c', label="DOM")
plt.plot(Video_data,power_saving_list[4],'8-',color = 'k', label="BPF")
plt.xlabel("Video_data(Mbps)")
plt.ylabel("awake time of UEs(%)")
plt.legend(loc = "best")
plt.savefig('Video_awake_time.pdf')

plt.figure()
plt.plot(Video_data,avg_delay_list[5],'*-',color = 'm', label="OUR")
plt.plot(Video_data,avg_delay_list[0],'s-',color = 'r', label="OUR+${DC_{1rx}}$")
plt.plot(Video_data,avg_delay_list[1],'o-',color = 'g', label="OUR+${DC_{2rx}}$")
plt.plot(Video_data,avg_delay_list[2],'h-',color = 'b', label="FIX")
plt.plot(Video_data,avg_delay_list[3],'H-',color = 'c', label="DOM")
plt.plot(Video_data,avg_delay_list[4],'8-',color = 'k', label="BPF")
plt.xlabel("Video_data(Mbps)")
plt.ylabel("Average delay(ms)")
plt.legend(loc = "best")
plt.savefig('Video_Average_delay.pdf')

plt.figure()
plt.plot(Video_data,avg_loss_list[5],'*-',color = 'm', label="OUR")
plt.plot(Video_data,avg_loss_list[0],'s-',color = 'r', label="OUR+${DC_{1rx}}$")
plt.plot(Video_data,avg_loss_list[1],'o-',color = 'g', label="OUR+${DC_{2rx}}$")
plt.plot(Video_data,avg_loss_list[2],'h-',color = 'b', label="FIX")
plt.plot(Video_data,avg_loss_list[3],'H-',color = 'c', label="DOM")
plt.plot(Video_data,avg_loss_list[4],'8-',color = 'k', label="BPF")
plt.xlabel("Video_data(Mbps)")
plt.ylabel("Average packet loss(%)")
plt.legend(loc = "best")
plt.savefig('Video_packet_loss.pdf')

plt.show()
#再加一張圖 plt.figure
    