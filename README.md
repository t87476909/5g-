# 5g-
python with 5G BaseStation simulation(論文模擬)

1. main.py 程式主程序執行檔案
2. NetworkSetting.py 網路架構設定
3. CellUser.py 生成隨機使用者座標
4. BeamMapping.py 基地台波束間的關係生成
5. EventManager.py 事件管理程序
6. BaseStation.py 基地台行為
7. UserEquipment.py 使用者行為
8. TrafficGenerator.py 封包生成
9. BeamTransmit.py 基地台波束打出動作
10. RateCalulate.py 計算路徑損耗與資源塊速率
11. ProportionalFair.py PF公平比例演算法計算使用者資源分配
12. ValueCalculate.py 計算波束生成機率統計生成流量
13. Beamforming.py 基地台波束生成
14. BeamPredict.py 基地與使用者台波束計算生成結果
15. BeamExchange.py 基地台波束調換
16. Dominate.py 基地台修改優先權分配
17. UeTime.py UE開啟時間計算
18. StatisticWork.py 模擬數值統計與輸出檔案
19. DelayCalculate.py 平均延遲、封包掉落率、輸出流量計算

我們在仿真結果證明，與其他方法相比而言，我們所提出的波束調度方式大幅提升了系統吞吐量，並且大幅降低了平均封包的被丟棄率與平均延遲統，同時強調了UE應當知曉基地台波束排程所帶來的節電優勢，並在基地台協作過程當中，照顧到基地台資源分配不均的問題，同時與傳統靜態波束FIX相比，在相同的耗電量下，提升了23%的吞吐量。

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_1.PNG)

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_2.PNG)

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_3.PNG)

![image](https://github.com/t87476909/5g-/blob/main/Simulation%20results/Figure_4.PNG)
