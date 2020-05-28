import json

data = {}
data['ModelID'] = 128
data['AttachPointId'] = []

attachTypes = {'$helms':35, '$sail0':21,'$lamp_rear':29,'$lamp_front':28,'$ladder_read_right':58,'$ladder_read_left':59,'$cannon11':48,'$cannon12':49,'$cannon10':47}

with open('speedboat.dump','r') as reader:
    lines = reader.readlines()

for idx,line in enumerate(lines):
    for key in attachTypes:
        if key in line:
            coordSplit = lines[idx+2].split('trans')
            coords = coordSplit[1][1:-2].split(' ')
            x = float(coords[0])
            y = float(coords[1])
            z = float(coords[2])
            data['AttachPointId'].append({attachTypes[key]:{"X":x,"Y":y,"Z":z}})

with open('output.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)
