class NetworkSettings:
    num_of_bs = 25 #基地台數量 Number of base stations
    num_of_ue = 14 #單一基地台的UE數量(非重疊區域) Number of UEs in a single base station (non-overlapping area)
    num_of_ue_overlap = 56 #單一基地台的UE數量(重疊區域) Number of UEs in a single base station (overlapping area)
    simulation_time = 5000 #模擬時間(ms)
    bs_range = 500 #基地台覆蓋範圍(m)
    Neighbor_Distance = 750 #基地台與基地台圓心間距(m) The distance between the base station and the center of the base station (m) should not be less than bs_range
    beam_angle = 45 #波束角度45 波束角度沒辦法被360整除會有錯
    BS_transmission_power = 23 #基地台傳輸功率(tx power)
    UE_transmission_power = 0.25 #0.25W(瓦特) = 23.98 dbm
    BS_antenna_gain = 8 #dbi
    UE_antenna_gain = 5
    Thermal_noise_dbm = -174 #熱聲噪
    Number_resource_block = 25 #資源塊數量 264
    system_bandwidth = 50 #系統帶寬(MHZ) 400
    beam_clear_index = [0,4] #用來選定基地台的波束內使用者不會生成 In-beam users used to select base stations do not generate
    UE_speed = 0 #使用者速度上限(km/hr) user speed limit

    CBR_data_change = 2 #CBR資料量(Mbps)
    Video_data_change = 2.5 #video資料量(Mbps)
    write_data = True #是否輸出檔案 Whether to output .csv files

    BS_center_frequency = list()
    ue_id_list = list() #所有ue的儲存用列表 A list of all ue for storage
    bs_id_list = list() #所有bs的儲存用列表 A list of all bs for storage
    object_info_dict = dict() #事件物件的字典 dictionary of event objects
    record_ue_connect_bs = dict()
    ue_to_bs_mapping_table = dict() #ue和bs的連接關係 The connection relationship between ue and bs
    bs_ue_distance = dict() #基地台與UE的距離 The distance between base station and UE
    bs_beam_neighbor = dict() #基地台間的波束關係 Beam relationship between base stations
    bs_neighbor = dict() #基地台間的鄰居關係 Neighbor relationship between base stations
    beam_eliminate = dict() #基地台一開始哪些波束裡面不會有ue Which beams of the base station will not have ue in the beginning

    ue_move_direction = dict() #ue移動方向改變 ue movement direction change

class SystemInfo:
    system_time = 0
    event_priority = 0 #事件優先度
    system_round = 10 #系統執行輪數
    ntu_T_time = 2 # mode3系統執行T時間設定 Mode3 system executes T time setting
    ue_move_cycle = 1 # 移動一次ue座標頻率(ms) Move the ue coordinates once in 1ms

class Simulation:
    mode = 0 #系統執行模式 0 = our_1rx、1 = our_2rx、2 = FIX、3 = DOM、4 = BPF、5 = OUR
    all_mode_test = True #全部方法模擬 All method simulation
    beam_clear = True #是否讓某些波束消失 Whether to make some beams disappear
    ue_move_control = False
    picture = 0 # 輸出需要的變量圖片設定 Output the required variable image settings
    #random_beam_clear_number = 3 #消除波束數量(1~3) Number of beams eliminated
    beam_clear_mode = 1 # 0 = 固定清除beam、1 = 隨機清除beam 0 = clear beam fixedly, 1 = clear beam randomly
    ue_open_time = dict() #儲存ue的開啟時間 Store the opening time of ue
    execution_time = 0 #當前系統執行時間 Current system execution time
    mode4_dynamic_beam_number = 300
