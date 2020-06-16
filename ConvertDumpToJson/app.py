import json
import sys
import os
import sqlite3
import argparse
import math
import re

slave_name_lookup = {
    'speedboat_a':128,
    'soloship_a': 1288,
    'boardship_body': 1249,
    'smallboat_body': 129,
    'galleon_body': 393,
    'fishboat': 1360,
    'boxship': 1205,
    'cruise_a': 1046
}

slave_model_duplicate_lookup = {
    1360: [1383, 1384]
}

regex_pattern = re.compile("localTM: axisX\((.+)\s(.+)\s(.+)\) axisY\((.+)\s(.+)\s(.+)\) axisZ\((.+)\s(.+)\s(.+)\) trans\((.+)\s(.+)\s(.+)\)")

# Axis of rotation
# x-axis
# 1 0 0
# 0 v v
# 0 v v

# y-axis
# v 0 v
# 0 1 0
# v 0 v

# z-axis
# v v 0
# v v 0
# 0 0 1

matrix_lookup = {
    "pi/2": {"matrix": [[0.0, -1.0, 0.0], 
                        [1.0, 0.0, 0.0], 
                        [0.0, 0.0, 1.0]], 
            "rotation": (0, 0, -64)},
    "pi": {"matrix": [[-1.0, 0.0, 0.0], 
                      [0.0, -1.0, 0.0], 
                      [0.0, 0.0, 1.0]], 
            "rotation": (0, 0, -127)},
    "3pi/2": {"matrix": [[0.0, 1.0, 0.0], 
                        [-1.0, 0.0, 0.0], 
                        [0.0, 0.0, 1.0]], 
            "rotation": (0, 0, 64)}
}

def calc_rotation(axis_x, axis_y, axis_z):
    # Not sure how to deal with values of magnitude ~e-7 n.
    # Since they are << 1 treat as zero?
    for i, v in enumerate(axis_x):
        axis_x[i] = round(v)

    for i, v in enumerate(axis_y):
        axis_y[i] = round(v)

    for i, v in enumerate(axis_z):
        axis_z[i] = round(v)

    # Construct matrix
    matrix = [axis_x, axis_y, axis_z]

    for k, v in matrix_lookup.items():
        if v["matrix"] == matrix:
            return v["rotation"]

    return (0, 0, 0)

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

        if modelName not in slave_name_lookup:
            print("Model name {} not found in slave lookup".format(modelName))
            continue
        
        data = {}
        data['ModelId'] = slave_name_lookup[modelName]
        data['AttachPoints'] = {}

        with open(filename,'r') as reader:
            lines = reader.readlines()
        
        for idx,line in enumerate(lines):
            for key in attachTypes:
                if key in line:
                    search_result = re.search(regex_pattern, lines[idx+2])

                    if search_result is None:
                        print("Regex did not match for {}", filename)
                        continue

                    axis_x = [float(search_result.group(1)), float(search_result.group(2)), float(search_result.group(3))]
                    axis_y = [float(search_result.group(4)), float(search_result.group(5)), float(search_result.group(6))]
                    axis_z = [float(search_result.group(7)), float(search_result.group(8)), float(search_result.group(9))]

                    rotation = calc_rotation(axis_x, axis_y, axis_z)

                    trans_x = float(search_result.group(10))
                    trans_y = float(search_result.group(11))
                    trans_z = float(search_result.group(12))

                    data['AttachPoints'][attachTypes[key]] = {
                        "X":trans_x,"Y":trans_y,"Z":trans_z,
                        "RotationX": rotation[0],
                        "RotationY": rotation[1],
                        "RotationZ": rotation[2],
                    }

        # Hard-coded value corrections
        if slave_name_lookup[modelName] == 1360:
            data['AttachPoints'][35]["Z"] = 5.86128

        output.append(data)

        if slave_name_lookup[modelName] in slave_model_duplicate_lookup:
            for id in slave_model_duplicate_lookup[slave_name_lookup[modelName]]:
                d = data.copy()
                d['ModelId'] = id
                output.append(d)

    with open('slave_attach_points.json', 'w') as outfile:
        json.dump(output, outfile, indent=4)

