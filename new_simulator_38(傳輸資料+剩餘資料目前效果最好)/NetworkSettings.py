class NetworkSettings:
    num_of_bs = 1 #基地台數量
    num_of_ue = 15 #單一基地台的UE數量(非重疊區域)
    num_of_ue_overlap = 60 #單一基地台的UE數量(重疊區域)
    simulation_time = 5000 #模擬時間 ms
    bs_range = 500 #基地台覆蓋範圍(m)
    Neighbor_Distance = 750 #基地台與基地台間距(m) < 500就會完全重疊了 #900和950會出錯明天看
    beam_angle = 45 #波束角度45 波束角度沒辦法被360整除會有錯
    BS_transmission_power = 23 #基地台傳輸功率(tx power)
    UE_transmission_power = 0.25 #0.25W(瓦特) = 23.98 dbm
    BS_antenna_gain = 8 #dbi
    UE_antenna_gain = 5
    Thermal_noise_dbm = -174 #熱聲噪
    Number_resource_block = 25 #資源塊數量 264
    system_bandwidth = 50 #系統帶寬(MHZ) 400
    beam_clear_index = [0,4] #固定波束清除設定
    UE_speed = 100 #km/hr(使用者速度上限)

    CBR_data_change = 2 #CBR資料量(Mbps)
    Video_data_change = 2.5 #video資料量(Mbps)
    write_data = True #是否輸出檔案

    BS_center_frequency = list()
    ue_id_list = list() #所有ue的儲存用列表
    bs_id_list = list() #所有bs的儲存用列表
    object_info_dict = dict() #事件物件的字典
    record_ue_connect_bs = dict()
    ue_to_bs_mapping_table = dict() #ue和bs的連接關係以字典表示
    bs_ue_distance = dict() #基地台與UE的距離
    bs_beam_neighbor = dict() #基地台的波束關係
    bs_neighbor = dict() #基地台的鄰居關係
    beam_eliminate = dict() #基地台一開始哪些波束裡面不會有ue

    ue_move_direction = dict() #ue移動方向改變

    #基地台個數36(固定)
    #執行時間 30000ms
    #ue個數 25、50、75、100、125、25 * 9 (會變的參數比例1:4)
    #control_variable 10、20...90

class SystemInfo:
    system_time = 0
    event_priority = 0 #事件優先度
    system_round = 50 #系統執行輪數(老師規定要9次)
    ntu_T_time = 2 #台大系統執行T時間
    ue_move_cycle = 1 # ms 1ms移動一次ue座標

class Simulation:
    mode = 0 #系統執行模式 0為我的方法(one) 1為我的方法(two) 2為全部靜態 3為台大參考論文方法 4為新論文
    all_mode_test = True #為全部方法模擬
    beam_clear = False #是否讓某些波束消失
    ue_move_control = True
    picture = 1 # 0為ue數量為x軸、1為ue_speed為x軸、2為
    #random_beam_clear_number = 3 #消除波束數量(1~3)
    beam_clear_mode = 1 # 0 為固定清除某些beam 1為隨機清除某些beam
    ue_open_time = dict() #儲存ue的開啟時間
    execution_time = 0
    mode4_dynamic_beam_number = 300 #500個動態波束