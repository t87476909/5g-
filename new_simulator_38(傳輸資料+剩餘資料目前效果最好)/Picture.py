import csv
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
from NetworkSettings import SystemInfo
'''
data_row = [[0]system_throughput, [1]avg_ue_throughput, [2]dc_avg_ue_throughput,
            [3]fairness, [4]dc_fairness, [5]cbr_delay, [6]voice_delay,
            [7]video_delay, [8]avg_delay, [9]cbr_loss, [10]voice_loss,
            [11]video_loss, [12]avg_loss,[13]mode,[14]average_UE_awake,[15]ue_number,[16]unit_throughput_awake_time,
            [17]self.power_saving]
'''
# 指定使用字型和大小
#myfont = FontProperties(fname='D:/Programs/Lib/site-packages/matplotlib/mpl-data/fonts/ttf/msjh.ttc', size=40)
system_throughput = dict()
average_UE_awake = dict()
unit_throughput_awake_time = dict() # mode:[unit_throughput_awake_time]
ue_number = dict() # mode:[ue_number]
power_saving = dict()
avg_delay = dict()
avg_loss = dict()
for i in range(5):
  system_throughput[i] = list()
  average_UE_awake[i] = list()
  power_saving[i] = list()
  unit_throughput_awake_time[i] = list()
  ue_number[i] = list()
  avg_delay[i] = list()
  avg_loss[i] = list()

# 開啟 CSV 檔案
path  = "simulation_result.csv"
with open(path, newline='') as csvfile:
  # 讀取 CSV 檔案內容
  rows = csv.reader(csvfile)
  # 以迴圈輸出每一列
  for row in rows:
    float_row = [float(item) for item in row]
    if float_row[13] == 0:
      if float_row[15] not in ue_number[0]:
        ue_number[0].append(float_row[15])
        system_throughput[0].append(float_row[0])
        avg_delay[0].append(float_row[8])
        avg_loss[0].append(float_row[12])
        average_UE_awake[0].append(float_row[14])
        unit_throughput_awake_time[0].append(float_row[16])
        power_saving[0].append(float_row[17])
      else:
        ue_number_index = ue_number[0].index(float_row[15])
        system_throughput[0][ue_number_index] += float_row[0]
        avg_delay[0][ue_number_index] += float_row[8]
        avg_loss[0][ue_number_index] += float_row[12]
        average_UE_awake[0][ue_number_index] += float_row[14]
        unit_throughput_awake_time[0][ue_number_index] += float_row[16]
        power_saving[0][ue_number_index] += float_row[17]

    elif float_row[13] == 1:
      if float_row[15] not in ue_number[1]:
        ue_number[1].append(float_row[15])
        system_throughput[1].append(float_row[0])
        avg_delay[1].append(float_row[8])
        avg_loss[1].append(float_row[12])
        average_UE_awake[1].append(float_row[14])
        unit_throughput_awake_time[1].append(float_row[16])
        power_saving[1].append(float_row[17])
      else:
        ue_number_index = ue_number[1].index(float_row[15])
        system_throughput[1][ue_number_index] += float_row[0]
        avg_delay[1][ue_number_index] += float_row[8]
        avg_loss[1][ue_number_index] += float_row[12]
        average_UE_awake[1][ue_number_index] += float_row[14]
        unit_throughput_awake_time[1][ue_number_index] += float_row[16]
        power_saving[1][ue_number_index] += float_row[17]

    elif float_row[13] == 2:
      if float_row[15] not in ue_number[2]:
        ue_number[2].append(float_row[15])
        system_throughput[2].append(float_row[0])
        avg_delay[2].append(float_row[8])
        avg_loss[2].append(float_row[12])
        average_UE_awake[2].append(float_row[14])
        unit_throughput_awake_time[2].append(float_row[16])
        power_saving[2].append(float_row[17])
      else:
        ue_number_index = ue_number[2].index(float_row[15])
        system_throughput[2][ue_number_index] += float_row[0]
        avg_delay[2][ue_number_index] += float_row[8]
        avg_loss[2][ue_number_index] += float_row[12]
        average_UE_awake[2][ue_number_index] += float_row[14]
        unit_throughput_awake_time[2][ue_number_index] += float_row[16]
        power_saving[2][ue_number_index] += float_row[17]

    elif float_row[13] == 3:
      if float_row[15] not in ue_number[3]:
        ue_number[3].append(float_row[15])
        system_throughput[3].append(float_row[0])
        avg_delay[3].append(float_row[8])
        avg_loss[3].append(float_row[12])
        average_UE_awake[3].append(float_row[14])
        unit_throughput_awake_time[3].append(float_row[16])
        power_saving[3].append(float_row[17])
      else:
        ue_number_index = ue_number[3].index(float_row[15])
        system_throughput[3][ue_number_index] += float_row[0]
        avg_delay[3][ue_number_index] += float_row[8]
        avg_loss[3][ue_number_index] += float_row[12]
        average_UE_awake[3][ue_number_index] += float_row[14]
        unit_throughput_awake_time[3][ue_number_index] += float_row[16]
        power_saving[3][ue_number_index] += float_row[17]
    else:
      if float_row[15] not in ue_number[4]:
        ue_number[4].append(float_row[15])
        system_throughput[4].append(float_row[0])
        avg_delay[4].append(float_row[8])
        avg_loss[4].append(float_row[12])
        average_UE_awake[4].append(float_row[14])
        unit_throughput_awake_time[4].append(float_row[16])
        power_saving[4].append(float_row[17])
      else:
        ue_number_index = ue_number[4].index(float_row[15])
        system_throughput[4][ue_number_index] += float_row[0]
        avg_delay[4][ue_number_index] += float_row[8]
        avg_loss[4][ue_number_index] += float_row[12]
        average_UE_awake[4][ue_number_index] += float_row[14]
        unit_throughput_awake_time[4][ue_number_index] += float_row[16]
        power_saving[4][ue_number_index] += float_row[17]

for i in range(5): #取平均值(記得list改成numpy 或是 list再加一個迴圈去除10)
  system_throughput[i] = np.array(system_throughput[i]) / SystemInfo.system_round
  avg_delay[i] = np.array(avg_delay[i]) / SystemInfo.system_round
  avg_loss[i] = np.array(avg_loss[i]) / SystemInfo.system_round
  average_UE_awake[i] = np.array(average_UE_awake[i]) / SystemInfo.system_round
  unit_throughput_awake_time[i] = np.array(unit_throughput_awake_time[i]) / SystemInfo.system_round
  power_saving[i] = np.array(power_saving[i]) / SystemInfo.system_round

plt.figure(figsize=(20,20),dpi=100,linewidth = 2)
plt.plot(ue_number[0],unit_throughput_awake_time[0],'s-',color = 'r', label="one_receiver")
plt.plot(ue_number[1],unit_throughput_awake_time[1],'o-',color = 'g', label="two_receiver")
plt.plot(ue_number[2],unit_throughput_awake_time[2],'h-',color = 'b', label="static_beam")
plt.plot(ue_number[3],unit_throughput_awake_time[3],'H-',color = 'c', label="ntu_beam")
plt.plot(ue_number[4],unit_throughput_awake_time[4],'8-',color = 'k', label="BPF_beam")
plt.title("單位醒來時間內的吞吐量與UE數量對比", fontproperties="Microsoft JhengHei",size = 20, x=0.5, y=1.03)
plt.xlabel("Number of UEs", fontsize=20, labelpad = 15)
plt.ylabel("unit awake time of System throughput", fontsize = 20, labelpad = 20)
plt.legend(loc = "best", fontsize=20)

plt.figure(figsize=(20,20),dpi=100,linewidth = 2)
plt.plot(ue_number[0],system_throughput[0],'s-',color = 'r', label="one_receiver")
plt.plot(ue_number[1],system_throughput[1],'o-',color = 'g', label="two_receiver")
plt.plot(ue_number[2],system_throughput[2],'h-',color = 'b', label="static_beam")
plt.plot(ue_number[3],system_throughput[3],'H-',color = 'c', label="ntu_beam")
plt.plot(ue_number[4],system_throughput[4],'8-',color = 'k', label="BPF_beam")
plt.title("吞吐量與UE數量對比", fontproperties="Microsoft JhengHei",size = 20, x=0.5, y=1.03)
plt.xlabel("Number of UEs", fontsize=20, labelpad = 15)
plt.ylabel("System throughput", fontsize = 20, labelpad = 20)
plt.legend(loc = "best", fontsize=20)

plt.figure(figsize=(20,20),dpi=100,linewidth = 2)
plt.plot(ue_number[0],power_saving[0],'s-',color = 'r', label="one_receiver")
plt.plot(ue_number[1],power_saving[1],'o-',color = 'g', label="two_receiver")
plt.plot(ue_number[2],power_saving[2],'h-',color = 'b', label="static_beam")
plt.plot(ue_number[3],power_saving[3],'H-',color = 'c', label="ntu_beam")
plt.plot(ue_number[4],power_saving[4],'8-',color = 'k', label="BPF_beam")
plt.title("醒來時間與UE數量對比", fontproperties="Microsoft JhengHei",size = 20, x=0.5, y=1.03)
plt.xlabel("Number of UEs", fontsize=20, labelpad = 15)
plt.ylabel("awake time of UEs(%)", fontsize = 20, labelpad = 20)
plt.legend(loc = "best", fontsize=20)

plt.figure(figsize=(20,20),dpi=100,linewidth = 2)
plt.plot(ue_number[0],avg_delay[0],'s-',color = 'r', label="one_receiver")
plt.plot(ue_number[1],avg_delay[1],'o-',color = 'g', label="two_receiver")
plt.plot(ue_number[2],avg_delay[2],'h-',color = 'b', label="static_beam")
plt.plot(ue_number[3],avg_delay[3],'H-',color = 'c', label="ntu_beam")
plt.plot(ue_number[4],avg_delay[4],'8-',color = 'k', label="BPF_beam")
plt.title("平均延遲與UE數量對比", fontproperties="Microsoft JhengHei",size = 20, x=0.5, y=1.03)
plt.xlabel("Number of UEs", fontsize=20, labelpad = 15)
plt.ylabel("Average delay", fontsize = 20, labelpad = 20)
plt.legend(loc = "best", fontsize=20)

plt.figure(figsize=(20,20),dpi=100,linewidth = 2)
plt.plot(ue_number[0],avg_loss[0],'s-',color = 'r', label="one_receiver")
plt.plot(ue_number[1],avg_loss[1],'o-',color = 'g', label="two_receiver")
plt.plot(ue_number[2],avg_loss[2],'h-',color = 'b', label="static_beam")
plt.plot(ue_number[3],avg_loss[3],'H-',color = 'c', label="ntu_beam")
plt.plot(ue_number[4],avg_loss[4],'8-',color = 'k', label="BPF_beam")
plt.title("平均loss與UE數量對比", fontproperties="Microsoft JhengHei",size = 20, x=0.5, y=1.03)
plt.xlabel("Number of UEs", fontsize=20, labelpad = 15)
plt.ylabel("Average packet loss", fontsize = 20, labelpad = 20)
plt.legend(loc = "best", fontsize=20)

plt.show()
#再加一張圖 plt.figure
    