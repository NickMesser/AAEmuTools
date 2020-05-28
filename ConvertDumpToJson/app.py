import json

attachTypes = {
    '$driver':1,
    '$passenger0':2,
    '$passenger1':3,
    '$passenger2':4,
    '$passenger3':5,
    '$passenger4':6,
    '$passenger5':7,
    '$passenger6':8,
    '$cannon0':9,
    '$cannon1':10,
    '$cannon2':11,
    '$cannon3':12,
    '$cannon4':13,
    '$cannon5':14,
    '$cannot6':15,
    '$cannon7':16,
    '$cannon8':17,
    '$hook':18,
    '$mast0':19,
    '$mast1':20,
    '$sail0':21,
    '$sail1':22,
    '$anchor':23,
    '$ladder_left':24,
    '$ladder_right':25,
    '$plank_left':26,
    '$plank_right':27,
    '$lamp_front':28,
    '$lamp_rear':29,
    '$trailed0':30,
    '$trailed1':31,
    '$trailed2':32,
    '$trailed3':33,
    '$trailed4':34,
    '$helms':35,
    '$heal_point_0':36,
    '$heal_point_1':37,
    '$heal_point_2':38,
    '$heal_point_3':39,
    '$heal_point_4':40,
    '$heal_point_5':41,
    '$heal_point_6':42,
    '$heal_point_7':43,
    '$heal_point_8':44,
    '$heal_point_8':45,
    '$cannon10':47,
    '$cannon11':48,
    '$cannon12':49,
    '$ladder_rear_right':58,
    '$ladder_rear_left':59
 }


data = {}
data['ModelID'] = 128 #Must change to match current model
data['AttachPointId'] = []

with open('speedboat.dump','r') as reader: #Must change this to match filename you want to convert
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