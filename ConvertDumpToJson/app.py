import json
import sys
import os
import sqlite3
import argparse
import math

slaveNameLookup = {
    'speedboat_a':128,
    'soloship_a': 1288,
    'boardship_body': 1249,
    'smallboat_body': 129,
    'galleon_body': 393,
    'fishboat': 1360,
    'boxship': 1205,
    'cruise_a': 1046
}

def calc_angle(v, axis):
    angle = 0

    if axis is 'x':
        angle = v[0] / math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    elif axis is 'y':
        angle = v[1] / math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    elif axis is 'z':
        angle = v[2] / math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

    return angle

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='cfg model to attach point convertor')
    parser.add_argument('--db', type=str, help='compact db file path')
    parser.add_argument("--cfg", type=str, nargs='+', help='cfg dumps to parse')
    args = parser.parse_args()

    attachTypes = {}

    conn = sqlite3.connect(args.db)
    c = conn.cursor()

    for row in c.execute('SELECT id, prefab FROM model_attach_point_strings'):
        attachTypes[row[1]] = row[0]

    output = []

    for i, filename in enumerate(args.cfg):
        print("Parsing file {}/{} {}".format(i+1, len(args.cfg), filename))

        modelName = os.path.basename(filename).split('.')[0]

        if modelName not in slaveNameLookup:
            print("Model name {} not found in slave lookup".format(modelName))
            continue
        
        data = {}
        data['ModelId'] = slaveNameLookup[modelName]
        data['AttachPoints'] = {}

        with open(filename,'r') as reader:
            lines = reader.readlines()
        
        for idx,line in enumerate(lines):
            for key in attachTypes:
                if key in line:
                    coordSplit = lines[idx+2].split('trans')
                    coords = coordSplit[1][1:-2].split(' ')
                    x = float(coords[0])
                    y = float(coords[1])
                    z = float(coords[2])

                    # xRotation = [*map(lambda x: float(x), lines[idx+2].split('axisX(')[1].split(')')[0].split(' '))]
                    # yRotation = [*map(lambda x: float(x), lines[idx+2].split('axisY(')[1].split(')')[0].split(' '))]
                    # zRotation = [*map(lambda x: float(x), lines[idx+2].split('axisZ(')[1].split(')')[0].split(' '))]
                    
                    data['AttachPoints'][attachTypes[key]] = {
                        "X":x,"Y":y,"Z":z
                        # "RotationX": calc_angle(xRotation,'x') ,"RotationY": calc_angle(yRotation, 'y'),"RotationZ": calc_angle(zRotation, 'z')
                    }
                    
        output.append(data)

    with open('output.json', 'w') as outfile:
        json.dump(output, outfile, indent=4)

