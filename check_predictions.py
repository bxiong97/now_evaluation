"""
Max-Planck-Gesellschaft zur Foerderung der Wissenschaften e.V. (MPG) is holder of all proprietary rights on this computer program. 
Using this computer program means that you agree to the terms in the LICENSE file (https://ringnet.is.tue.mpg.de/license). 
Any use not explicitly granted by the LICENSE is prohibited.
Copyright 2020 Max-Planck-Gesellschaft zur Foerderung der Wissenschaften e.V. (MPG). acting on behalf of its 
Max Planck Institute for Intelligent Systems. All rights reserved.
More information about the NoW Challenge is available at https://ringnet.is.tue.mpg.de/challenge.
For comments or questions, please email us at ringnet@tue.mpg.de
"""

import os
import sys
import numpy as np
from scan2mesh_computations import crop_face_scan as crop_face_scan
from scan2mesh_computations import compute_rigid_alignment as compute_rigid_alignment
from psbody.mesh import Mesh


def load_pp(fname):
    lamdmarks = np.zeros([7, 3]).astype(np.float32)
    # import ipdb; ipdb.set_trace()
    with open(fname, "r") as f:
        lines = f.readlines()
        for j in range(8, 15):  # for j in xrange(9,15):
            # import ipdb; ipdb.set_trace()
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
            # import ipdb; ipdb.set_trace()
    return lamdmarks


def load_txt(fname):
    landmarks = []  # np.zeros([7,3]).astype(np.float32)
    with open(fname, "r") as f:
        lines = f.read().splitlines()
    # import ipdb; ipdb.set_trace()
    line = []
    for i in range(len(lines)):  # For Jiaxiang_Shang
        line.append(lines[i].split(" "))
    # import ipdb; ipdb.set_trace()
    landmarks = np.array(line, dtype=np.float32)
    lmks = landmarks
    return lmks


def save_obj(path, v, f, c):
    with open(path, "w") as file:
        for i in range(len(v)):
            file.write(
                "v %f %f %f %f %f %f\n"
                % (v[i, 0], v[i, 1], v[i, 2], c[i, 0], c[i, 1], c[i, 2])
            )
        file.write("\n")

        for i in range(len(f)):
            file.write("f %d %d %d\n" % (f[i, 0], f[i, 1], f[i, 2]))
    file.close()


def check_mesh_import_export(pred_mesh_filename):
    """
    Import and export predicted mesh to check if mesh is properly loaded
    """
    if not os.path.exists(pred_mesh_filename):
        print("Predicted mesh not found - %s" % pred_mesh_filename)
        return

    # Load and export the predicted mesh
    predicted_mesh = Mesh(filename=pred_mesh_filename)
    predicted_mesh.write_obj("./predicted_mesh_export.obj")


masked_scan_folder_name = "masked_scan"
predicted_mesh_aligned_folder_name = "predicted_mesh_aligned"


def check_mesh_alignment(
    pred_mesh_file_path,
    pred_lmk_file_path,
    gt_mesh_file_path,
    gt_lmk_file_path,
    save_path,
):
    """
    Compute rigid alignment between the predicted mesh and the ground truth scan.
    :param pred_mesh_filename: path of the predicted mesh to be aligned
    :param pred_lmk_filename: path of the landmarks of the predicted mesh
    :param gt_mesh_filename: path of the ground truth scan
    :param gt_lmk_filename: path of the ground truth landmark file
    :param save_path: path for saving generated files
    """

    if not os.path.exists(pred_mesh_file_path):
        print("Predicted mesh not found - %s" % pred_mesh_file_path)
        return
    if not os.path.exists(pred_lmk_file_path):
        print("Predicted mesh landmarks not found - %s" % pred_lmk_file_path)
        return
    if not os.path.exists(gt_mesh_file_path):
        print("Ground truth scan not found - %s" % gt_mesh_file_path)
        return
    if not os.path.exists(gt_lmk_file_path):
        print("Ground truth scan landmarks not found - %s" % gt_lmk_file_path)
        return

    # Load ground truth data
    groundtruth_scan = Mesh(filename=gt_mesh_file_path)
    grundtruth_landmark_points = load_pp(gt_lmk_file_path)

    # Load predicted data
    predicted_mesh = Mesh(filename=pred_mesh_file_path)
    pred_lmk_ext = os.path.splitext(pred_lmk_file_path)[-1]
    if pred_lmk_ext == ".txt":
        predicted_lmks = load_txt(pred_lmk_file_path)
    elif pred_lmk_ext == ".npy":
        predicted_lmks = np.load(pred_lmk_file_path)
    else:
        print("Unable to load predicted landmarks, must be of format txt or npy")
        return

    # Crop face scan
    masked_gt_scan = crop_face_scan(
        groundtruth_scan.v, groundtruth_scan.f, grundtruth_landmark_points
    )

    # Rigidly align predicted mesh with the ground truth scan
    predicted_mesh_vertices_aligned, masked_gt_scan = compute_rigid_alignment(
        masked_gt_scan,
        grundtruth_landmark_points,
        predicted_mesh.v,
        predicted_mesh.f,
        predicted_lmks,
    )

    masked_gt_scan_save_folder_path = os.path.join(save_path, masked_scan_folder_name)
    os.makedirs(masked_gt_scan_save_folder_path, exist_ok=True)

    predicted_mesh_aligned_save_folder_path = os.path.join(
        save_path, predicted_mesh_aligned_folder_name
    )
    os.makedirs(predicted_mesh_aligned_save_folder_path, exist_ok=True)

    # Output masked gt scan
    pred_mesh_file_name = pred_mesh_file_path.split(os.path.sep)[-1]
    pred_mesh_file_name_no_ext = os.path.splitext(pred_mesh_file_name)[0]

    masked_gt_scan_save_file_path = os.path.join(
        masked_gt_scan_save_folder_path, f"{pred_mesh_file_name_no_ext}.obj"
    )
    print("Saving masked gt scan at", masked_gt_scan_save_file_path)
    masked_gt_scan.write_obj(masked_gt_scan_save_file_path)

    # Output cropped aligned mesh
    aligned_mesh_save_file_path = os.path.join(
        predicted_mesh_aligned_save_folder_path, f"{pred_mesh_file_name_no_ext}.obj"
    )
    print("Saving predicted mesh vertices aligned at", aligned_mesh_save_file_path)
    Mesh(predicted_mesh_vertices_aligned, predicted_mesh.f).write_obj(
        aligned_mesh_save_file_path
    )


def main(argv):
    if len(argv) < 2:
        return

    pred_mesh_filename = argv[1]
    if len(argv) == 2:
        check_mesh_import_export(pred_mesh_filename)
    elif len(argv) == 6:
        pred_lmk_filename = argv[2]
        gt_mesh_filename = argv[3]
        gt_lmk_filename = argv[4]
        save_path = argv[5]
        check_mesh_alignment(
            pred_mesh_filename,
            pred_lmk_filename,
            gt_mesh_filename,
            gt_lmk_filename,
            save_path,
        )
    else:
        print("Number of parameters wrong - %d != (%d or %d)" % (len(argv), 2, 6))
        return


if __name__ == "__main__":
    main(sys.argv)
