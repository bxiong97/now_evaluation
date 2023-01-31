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
import scan2mesh_computations as s2m_opt
from psbody.mesh import Mesh
from utils import load_landmarks


def compute_error_metric(gt_path, gt_lmk_path, predicted_mesh_path, predicted_lmk_path):
    groundtruth_scan = Mesh(filename=gt_path)
    grundtruth_landmark_points = load_landmarks(gt_lmk_path)
    predicted_mesh = predicted_mesh_path
    predicted_mesh_landmark_points = predicted_lmk_path
    distances = s2m_opt.compute_errors(
        groundtruth_scan.v,
        groundtruth_scan.f,
        grundtruth_landmark_points,
        predicted_mesh.v,
        predicted_mesh.f,
        predicted_mesh_landmark_points,
    )
    return np.stack(distances)


def metric_computation(
    dataset_folder,
    prediction_folder,
    error_out_path=None,
    method_identifier="",
):
    """
    :param dataset_folder: Path to root of the dataset, with images, scans and landmarks
    :param prediction_folder: Path to predicted restuls to be evaluated, with scans, and landmarks
    :param method_identifier: Optional. Will be used to name the output file
    """

    os.makedirs(error_out_path, exist_ok=True)
    distance_metric = []

    subjects = os.listdir(prediction_folder)
    for subject in subjects:
        print(f"Processing subject {subject} ======")
        predicted_mesh_folder = os.path.join(prediction_folder, subject, "scans")
        predicted_landmarks_folder = os.path.join(
            prediction_folder, subject, "landmarks"
        )
        gt_mesh_folder = os.path.join(dataset_folder, subject, "scans")
        gt_landmarks_folder = os.path.join(dataset_folder, subject, "landmarks")

        for filename in os.listdir(predicted_mesh_folder):
            print(f"Processing {filename}")
            predicted_mesh_path = os.path.join(predicted_mesh_folder, filename)
            filename_pre, ext = os.path.splitext(filename)
            predicted_landmarks_path_npy = os.path.join(
                predicted_landmarks_folder, filename_pre + ".npy"
            )

            gt_mesh_path = os.path.join(gt_mesh_folder, filename_pre + ".ply")
            gt_landmarks_path = os.path.join(gt_landmarks_folder, filename_pre + ".txt")

            if not os.path.exists(predicted_mesh_path):
                raise FileNotFoundError(
                    f"Predicted mesh not found: {predicted_mesh_path}"
                )
            if not os.path.exists(predicted_landmarks_path_npy):
                raise FileNotFoundError(
                    f"Predicted landmarks was not found:{predicted_landmarks_path_npy}"
                )
            if not os.path.exists(gt_mesh_path):
                raise FileNotFoundError(f"GT mesh not found: {gt_mesh_path}")
            if not os.path.exists(gt_landmarks_path):
                raise FileNotFoundError(f"GT landmarks not found: {gt_landmarks_path}")

            predicted_mesh = Mesh(filename=predicted_mesh_path)
            predicted_lmks = np.load(predicted_landmarks_path_npy)

            distances = compute_error_metric(
                gt_mesh_path, gt_landmarks_path, predicted_mesh, predicted_lmks
            )

            distance_metric.append(distances)
            
    computed_distances = {"computed_distances": distance_metric}
    np.save(
        os.path.join(
            error_out_path, "%s_computed_distances.npy" % method_identifier
        ),
        computed_distances,
    )


if __name__ == "__main__":
    # TODO: modify this before every evaluation
    metric_computation(
        dataset_folder="/home/yanfeng/github/DECA-cache/datasets/mon_face_cap",
        prediction_folder="/home/yanfeng/github/DECA-cache/run/video_dataset_results/single_frame",
        error_out_path="/home/yanfeng/github/now_evaluation/error_output",
    )
