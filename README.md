# 5g-
A simulation of 5G multi-base station beam scheduling implemented using Python.(論文模擬)

Paper Hyperlink: [https://hdl.handle.net/11296/3wr446]

# Achievement

In our simulation results, we have demonstrated that our proposed beam scheduling method significantly improves system throughput and reduces the average packet drop rate and delay compared to other methods. We also emphasize the power-saving advantages of base station beam scheduling for UEs and address the issue of uneven resource allocation among base stations in cooperative processes. Compared to traditional static beamforming (FIX), our method increases throughput by 23% and reduces packet loss by 20% at the same power consumption.

# File Description
1.main.py: The main program execution file

2.NetworkSetting.py: Network architecture configuration

3.CellUser.py: Generates random user coordinates

4.BeamMapping.py: Generates the relationship between base station beams

5.EventManager.py: Event management program

6.BaseStation.py: Base station behavior

7.UserEquipment.py: User behavior

8.TrafficGenerator.py: Generates packets

9.BeamTransmit.py: Performs base station beam transmission actions

10.RateCalulate.py: Calculates path loss and resource block rates

11.ProportionalFair.py: Calculates user resource allocation using the PF fair proportion algorithm

12.ValueCalculate.py: Calculates beam generation probability and statistical flow generation

13.Beamforming.py: Generates base station beams

14.BeamPredict.py: Calculates and generates results for base station and user beams

15.BeamExchange.py: Performs base station beam exchange

16.Dominate.py: Modifies priority allocation for base stations

17.UeTime.py: Calculates UE activation time

18.StatisticWork.py: Performs simulation numerical statistics and output file

19.DelayCalculate.py: Calculates average delay, packet drop rate, and output flow rate

# Analog picture

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_1.PNG)

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_2.PNG)

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_3.PNG)

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_4.PNG)
