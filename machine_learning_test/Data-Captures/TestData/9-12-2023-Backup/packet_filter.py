#!python3

with open('LASK4 9-12-Capture.txt') as f:
    lask_lines = f.readlines()

with open('uMyo 9-12-Capture.txt') as f:
    umyo_lines = f.readlines()

packet = {}
for i in umyo_lines:
    b = ast.literal_eval(i)
    if len(b) > 1:
        packet_time = b[0]
        if len(i) < 10:
        packet['id'] = b[1]
        packet['ax'] = b[2]
        packet['ay'] = b[3]
        packet['az'] = b[4]
        packet['qsg0'] = b[5]
        packet['qsg1'] = b[6]
        packet['qsg2'] = b[7]
        packet['qsg3'] = b[8]
        packet['datetime'] = b[0]
    


print(umyo_lines[0])
print(lask_lines[0])
