
class uMyo:    
    def __init__(self, uid):
        self.last_pack_id = 0
        self.unit_id = uid
        self.packet_type = 0
        self.data_count = 0
        self.batt = 0
        self.version = 0
        self.steps = 0
        self.data_id = 0
        self.prev_data_id = 0
        self.data_array = [0] * 64 #in case of further changes, right now 16 data points
        self.device_spectr = [0] * 16
#	sQ Qsg;
#	sQ zeroQ;
        self.Qsg = [0,0,0,0]
        self.zeroQ = [0,0,0,0]
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.dev_yaw = 0
        self.dev_pitch = 0
        self.dev_roll = 0
        self.update_time = 0
        self.yaw_speed = 0
        self.pitch_speed = 0
        self.roll_speed = 0
    
    

