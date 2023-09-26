#!python3

import ast
import datetime




with open('LASK4_Capture_9-13-2023.txt') as f:
    lask_lines = f.readlines()

with open('uMyo_Capture_9-13-2023.txt') as f:
    umyo_lines = f.readlines()

sample_packet = """[{'datetime': datetime.datetime(2023, 9, 13, 16, 15, 46, 204758), 'id': 3, 'qsg': [-10857, -10725, 20867, -18858], 'xyz': [-15931, 1546, 4107], 'emg': [18706, 18622, 18620, 18649, 18673, 18736, 18841, 18927]}, {'datetime': datetime.datetime(2023, 9, 13, 16, 15, 46, 204758), 'id': 3, 'qsg': [-10857, -10725, 20867, -18858], 'xyz': [-15931, 1546, 4107], 'emg': [18706, 18622, 18620, 18649, 18673, 18736, 18841, 18927]}, {'datetime': datetime.datetime(2023, 9, 13, 16, 15, 46, 204758), 'id': 3, 'qsg': [-10857, -10725, 20867, -18858], 'xyz': [-15931, 1546, 4107], 'emg': [18706, 18622, 18620, 18649, 18673, 18736, 18841, 18927]}, {'datetime': datetime.datetime(2023, 9, 13, 16, 15, 46, 204758), 'id': 3, 'qsg': [-10857, -10725, 20867, -18858], 'xyz': [-15931, 1546, 4107], 'emg': [18706, 18622, 18620, 18649, 18673, 18736, 18841, 18927]}]
{'id': 'OM-LASK4', 'time': (2023, 9, 13, 21, 15, 40, 2, 256), 'data': [5197, 5093, 5001, 5149], 'ticks': 141002, 'rec_time': 0.005518913269042969, 'date_time': datetime.datetime(2023, 9, 13, 16, 15, 41, 989669)}"""

print(umyo_lines[0])
print(lask_lines[0])



# txt to csv
# convert txt json data to csv for ml
import csv


found = []
lasklets = []
umylets = []
last_pair = None

def send_chunk(data):
    global lask
    global band
    temp = []
    # array structure [signal_int * count,received time float]
    if 'OM-LASK' in data['id']:
        for i in data['data']:
            temp.append(i)
        temp.append(data['rec_time'])
        lask.append(temp)
    elif 'OM-Band' in data['id']:
        for i in data['data']:
            temp.append(i)
        temp.append(data['rec_time'])
        band.append(temp)

def check_chunk():
    global lask
    global band
    global last_pair
    global found
    dindexL =[]
    dindexB =[]
    if len(band) > 10:
        for i,x in enumerate(band):
            time = x[-1]
            for o,z in enumerate(lask):
                if abs(z[-1] - time) < .02:
                    found.append([x,z])
                    last_pair = z[-1]
                    del lask[o]
    for i in dindexB:
        del band[i]
    if len(band) > 20:
        band = band[-10:]
    if len(lask) > 20:
        lask = lask[-10:]
    #if not len(found) % 1000:
        #print('found ammount: ',len(found))




lask_text_file = open('LASK4_Capture_9-13-2023.txt','r')
umyo_text_file = open('uMyo_Capture_9-13-2023.txt','r')

csv_file = open('september13-2023-best.csv','w',newline="") #added newline="" FYI FMI
writer = csv.writer(csv_file)
writer.writerow(['u0_time','u0_qgs0','u0_qgs1','u0_qgs2','u0_qgs3','u0_x','u0_y','u0_z',
                 'u1_time','u1_qgs0','u1_qgs1','u1_qgs2','u1_qgs3','u1_x','u1_y','u1_z',
                 'u2_time','u2_qgs0','u2_qgs1','u2_qgs2','u2_qgs3','u2_x','u2_y','u2_z',
                 'u3_time','u3_qgs0','u3_qgs1','u3_qgs2','u3_qgs3','u3_x','u3_y','u3_z',
                 'lask_time','LASK1','LASK2','LASK3','LASK4'])
                 

matched_pairs = []

lask = lask_text_file.read().replace("datetime.datetime","").split('\n')
umyo = umyo_text_file.read().replace("datetime.datetime","").replace("datetime",'date_time').split('\n')

l = []
u = []

for i in lask:
    if i:
        item = ast.literal_eval(i)
        if item and len(item) > 0:
            l.append(item)

for i in umyo:
    if i:
        item = ast.literal_eval(i)
        for x in item:
            if x and len(x) > 0:
                u.append(x)

#send_chunk(j)
#check_chunk()

combined_list = l + u
sorted_list = sorted(combined_list,key=lambda x: x['date_time'])

tup = sorted_list[0]['date_time']
first_packet_time = datetime.datetime(*tup)
print('first packet time:',first_packet_time)

umyo_zero = []
u0 = False
umyo_one = []
u1 = False
umyo_two = []
u2 = False
umyo_three = []
u3 = False
lask_four = []
l4 = False
condition = False
condition_two = False


for i in sorted_list:
    if i['id'] == 'OM-LASK4':
        l4 = True
        lask_four.append(i)
        if u0 and u1 and u2 and u3 and l4:
            condition = True
    if i['id'] == 0:
        u0 = True
        umyo_zero.append(i)
        if u0 and u1 and u2 and u3 and l4:
            condition = True
    if i['id'] == 1:
        u1 = True
        umyo_one.append(i)
        if u0 and u1 and u2 and u3 and l4:
            condition = True
    if i['id'] == 2:
        u2 = True
        umyo_two.append(i)
        if u0 and u1 and u2 and u3 and l4:
            condition = True
    if i['id'] == 3:
        u3 = True
        umyo_three.append(i)
        if u0 and u1 and u2 and u3 and l4:
            condition = True
    if condition:
         writer.writerow([(datetime.datetime(*umyo_zero[-1]['date_time'])-first_packet_time).total_seconds(),umyo_zero[-1]['qsg'][0],umyo_zero[-1]['qsg'][1],umyo_zero[-1]['qsg'][2],umyo_zero[-1]['qsg'][3],umyo_zero[-1]['xyz'][0],umyo_zero[-1]['xyz'][1],umyo_zero[-1]['xyz'][2],
                 (datetime.datetime(*umyo_one[-1]['date_time'])-first_packet_time).total_seconds(),umyo_one[-1]['qsg'][0],umyo_one[-1]['qsg'][1],umyo_one[-1]['qsg'][2],umyo_one[-1]['qsg'][3],umyo_one[-1]['xyz'][0],umyo_one[-1]['xyz'][1],umyo_one[-1]['xyz'][2],
                 (datetime.datetime(*umyo_two[-1]['date_time'])-first_packet_time).total_seconds(),umyo_two[-1]['qsg'][0],umyo_two[-1]['qsg'][1],umyo_two[-1]['qsg'][2],umyo_two[-1]['qsg'][3],umyo_two[-1]['xyz'][0],umyo_two[-1]['xyz'][1],umyo_two[-1]['xyz'][2],
                 (datetime.datetime(*umyo_three[-1]['date_time'])-first_packet_time).total_seconds(),umyo_three[-1]['qsg'][0],umyo_three[-1]['qsg'][1],umyo_three[-1]['qsg'][2],umyo_three[-1]['qsg'][3],umyo_three[-1]['xyz'][0],umyo_three[-1]['xyz'][1],umyo_three[-1]['xyz'][2],
                 (datetime.datetime(*lask_four[-1]['date_time'])-first_packet_time).total_seconds(),lask_four[-1]['data'][0],lask_four[-1]['data'][1],lask_four[-1]['data'][2],lask_four[-1]['data'][3]])
         condition,u0,u1,u2,u3,l4 = False,False,False,False,False,False
         

#datetime.datetime(*lask_four[-1]['date_time'])
        
        





#for i in found:
#    writer.writerow(i[0] + i[1])

csv_file.close()
        
    
    


    



