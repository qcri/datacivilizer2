import sys
import json

def transform_to_tensor(file_in, file_out, point_end):
    f = open(file_in, "r")

    tensor = []
    points = 400

    for line in f:
        ll = line.split(',')
        cc = [ll[x:x+points] for x in range(0,len(ll),points)]
        tensor.append(cc)

    # initialize the tensor -- in the formr accepted in kyrix
    tensor_new = []
    tensor_final = []
    final_stuct = []
    final_stuct.append([])

    i = 0
    for i in range(0, len(tensor[0])):
        tensor_new.append([])
        for j in range(0, len(tensor)):
            tensor_new[i].append([])
        i += 1
    # semi-invert the tensor
    for i in range(0, len(tensor[0])):
        for j in range(0, len(tensor)):
            # tensor_new[i][j] = tensor[j][i]
            s = ','
            tensor_new[i][j] = s.join(map(str,tensor[j][i]))

    # Create kyrix struct
    padding_start = [0,0,0]
    padding_end = ['3701125', '850', '3701000', '0', '3701250', '1700', '']
    paddind_ekg = []


    index = 0
    for segment in tensor_new:
        pp = padding_start + [str(index)] + tensor_new[index] + paddind_ekg + padding_end
        index += 1
        tensor_final.append(pp)

    tensor_small = tensor_final[:]

    final_stuct.append(tensor_small)

    with open(file_out, 'w') as json_file:
        json.dump(final_stuct, json_file)

def save_as_tensor(data, file_out):
    tensor = []
    points = 400

    for ll in data:
        cc = [ll[x:x+points] for x in range(0,len(ll),points)]
        tensor.append(cc)

    tensor_new = []
    tensor_final = []
    final_stuct = []
    final_stuct.append([])

    i = 0
    for i in range(0, len(tensor[0])):
        tensor_new.append([])
        for j in range(0, len(tensor)):
            tensor_new[i].append([])
        i += 1
    # semi-invert the tensor
    for i in range(0, len(tensor[0])):
        for j in range(0, len(tensor)):
            # tensor_new[i][j] = tensor[j][i]
            s = ','
            tensor_new[i][j] = s.join(map(str,tensor[j][i]))

    # Create kyrix struct
    padding_start = [0,0,0]
    padding_end = ['3701125', '850', '3701000', '0', '3701250', '1700', '']
    paddind_ekg = []


    index = 0
    for segment in tensor_new:
        pp = padding_start + [str(index)] + tensor_new[index] + paddind_ekg + padding_end
        index += 1
        tensor_final.append(pp)

    final_stuct.append(tensor_final)

    with open(file_out, 'w') as json_file:
        json.dump(final_stuct, json_file)
