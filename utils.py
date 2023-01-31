import os
import numpy as np


def load_lmk_pp(file_path):
    lamdmarks = np.zeros([7, 3]).astype(np.float32)
    with open(file_path, "r") as f:
        lines = f.readlines()
        for j in range(8, 15):
            line_contentes = lines[j].split(" ")
            # Check the .pp file to get to accurately pickup the columns for x , y and z coordinates
            for i in range(len(line_contentes)):
                if line_contentes[i].split("=")[0] == "x":
                    x_content = float((line_contentes[i].split("=")[1]).split('"')[1])
                elif line_contentes[i].split("=")[0] == "y":
                    y_content = float((line_contentes[i].split("=")[1]).split('"')[1])
                elif line_contentes[i].split("=")[0] == "z":
                    z_content = float((line_contentes[i].split("=")[1]).split('"')[1])
                else:
                    pass
            lamdmarks[j - 8, :] = np.array([x_content, y_content, z_content]).astype(
                np.float32
            )
    return lamdmarks


def load_lmk_txt(file_path):
    points = []
    with open(file_path, "r") as file:
        for line in file:
            x, y, z = map(float, line.strip().split(","))
            points.append([x, y, z])
    return np.array(points)


def load_landmarks(file_path):
    pre, ext = os.path.splitext(file_path)
    if ext == ".pp":
        return load_lmk_pp(file_path)
    elif ext == ".txt":
        return load_lmk_txt(file_path)
    else:
        raise TypeError("File path is neither .pp nor .txt")
