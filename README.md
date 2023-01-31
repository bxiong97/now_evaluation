# NoW Evaluation

This is the official repository for evaluation on the [NoW Benchmark](https://now.is.tue.mpg.de). The goal of the NoW benchmark is to introduce a standard evaluation metric to measure the accuracy and robustness of 3D face reconstruction methods from a single image under variations in viewing angle, lighting, and common occlusions. 

<p align="center"> 
<img src="content_now_dataset.png">
</p>

## Evaluation metric

Given a single monocular image, the challenge consists of reconstructing a 3D face. Since the predicted meshes occur in different local coordinate systems, the reconstructed 3D mesh is rigidly aligned (rotation, translation, and scaling) to the scan using a set of corresponding landmarks between the prediction and the scan. We further perform a rigid alignment based on the scan-to-mesh distance (which is the absolute distance between each scan vertex and the closest point in the mesh surface) between the ground truth scan, and the reconstructed mesh using the landmarks alignment as initialization. For more details, see the [NoW Website](https://now.is.tue.mpg.de) or the [RingNet paper](https://ps.is.tuebingen.mpg.de/uploads_file/attachment/attachment/509/paper_camera_ready.pdf).

```
Learning to Regress 3D Face Shape and Expression from an Image without 3D Supervision
Soubhik Sanyal, Timo Bolkart, Haiwen Feng, Michael J. Black
Computer Vision and Pattern Recognition (CVPR) 2019
```

## Clone the repository 
```
git clone https://github.com/soubhiksanyal/now_evaluation.git
```
## Installation

Please install the virtual environment

```
mkdir <your_home_dir>/.virtualenvs
python3 -m venv <your_home_dir>/.virtualenvs/now_evaluation
source <your_home_dir>/.virtualenvs/now_evaluation/bin/activate
```

Make sure your pip version is up-to-date:
```
pip install -U pip
```

Install the requirements by using:

```
pip install -r requirements.txt
```

Install mesh processing libraries from [MPI-IS/mesh](https://github.com/MPI-IS/mesh) within the virtual environment.

### Installing Scan2Mesh distance:

Clone the [flame-fitting](https://github.com/Rubikplayer/flame-fitting) repository and copy the required folders by the following comments

```
git clone https://github.com/Rubikplayer/flame-fitting.git
cp flame-fitting/smpl_webuser now_evaluation/smpl_webuser -r
cp flame-fitting/sbody now_evaluation/sbody -r
```

Clone [Eigen](http://eigen.tuxfamily.org/index.php?title=Main_Page) and copy the it to the following folder 

```
git clone https://gitlab.com/libeigen/eigen.git
cp eigen now_evaluation/sbody/alignment/mesh_distance/eigen -r
```

Edit the file `now_evaluation/sbody/alignment/mesh_distance/setup.py` to set EIGEN_DIR to the location of Eigen. Then compile the code by following command
```
cd now_evaluation/sbody/alignment/mesh_distance
make
```

The installation of Scan2Mesh is followed by the codebase provided by [flame-fitting](https://github.com/Rubikplayer/flame-fitting).
Please check that repository for more detailed instructions on Scan2Mesh installation.

All of the above can be achieved with the following script ([source](https://github.com/soubhiksanyal/now_evaluation/issues/21)):

```
git clone https://github.com/soubhiksanyal/now_evaluation.git
mkdir my_venv
python3 -m venv my_venv
source my_venv/bin/activate
pip install -U pip
cd now_evaluation
pip install -r requirements.txt
sudo apt-get install libboost-dev
git clone https://github.com/MPI-IS/mesh.git
cd mesh
BOOST_INCLUDE_DIRS=/usr/include/boost make all
cd ..
git clone https://github.com/Rubikplayer/flame-fitting.git
cp flame-fitting/smpl_webuser now_evaluation/smpl_webuser -r
cp flame-fitting/sbody now_evaluation/sbody -r
git clone https://gitlab.com/libeigen/eigen.git
cd eigen
git checkout 3.4.0
cd ..
cp eigen now_evaluation/sbody/alignment/mesh_distance/eigen -r
cd now_evaluation/sbody/alignment/mesh_distance
make
```

with a few catches:
1. I actually downloaded `boost` from its website and unzipped it into the project folder to get the path directly.
1. `BOOST_INCLUDE_DIRS` is different for everyone.
1. Python version in `my_env` needs to be 3.6, or just use conda to specify.
1. You may need to pip install a few missing dependencies before `check_predictions.py` works.
1. Due to a few mis-operations, the virtual env `my_venv` is installed under `~/github/mesh/my_venv`. For future usage, run `source ~/github/mesh/my_venv/bin/activate` to activate it.
1. Run `source /home/yanfeng/github/mesh/my_venv/bin/activate` every time before running the evaluation script in a new terminal window.

## Evaluation

Download the NoW Dataset and the validation set scans from the [NoW website](https://now.is.tue.mpg.de/download.php), and predict 3D faces for all validation images.

#### Check data setup

Note that this step is not actually computing the errors. It is simply checking whether error computation can be performed. If you are confident that your data and folder setup are already working, simply run `compute_error.py`.

Before running the now evaluation,

**1) Check that the predicted meshes can be successfuly loaded by the mesh loader:**
```
python check_predictions.py <predicted_mesh_path>
```
Running this loads the `<predicted_mesh_path>` mesh and exports it to `./predicted_mesh_export.obj`. Please check if this file can be loaded by e.g. [MeshLab](https://www.meshlab.net/) or any other mesh loader, and that the resulting mesh looks like the input mesh.

**2) Check that the landmarks for the predicted meshes are correct by running**
```
python check_predictions.py <predicted_mesh_path> <predicted_mesh_landmark_path> <gt_scan_path> <gt_lmk_path> <save_path>
```
Running this loads the `<predicted_mesh_path>` mesh, rigidly aligns it with the the scan `<gt_scan_path>`, and outputs the aligned mesh to `./predicted_mesh_aligned.obj`, and the cropped scan to `./cropped_scan.obj`. Please check if the output mesh and scan are rigidly aligned by jointly opening them in e.g. [MeshLab](https://www.meshlab.net/).

Sample command to check a single prediction:

```
python check_predictions.py /home/yanfeng/github/now_evaluation/predicted_mesh_export.obj /home/yanfeng/github/DECA-cache/train/pretrain_multiframe/NOW_eval/step_00149600/FaMoS_180424_03335_TA/multiview_neutral/IMG_0041.npy /home/yanfeng/github/DECA-cache/datasets/now/NoW_Dataset/final_release_version/scans/FaMoS_180424_03335_TA/natural_head_rotation.000001.obj /home/yanfeng/github/DECA-cache/datasets/now/NoW_Dataset/final_release_version/scans_lmks_onlypp/FaMoS_180424_03335_TA/natural_head_rotation.000001_picked_points.pp /home/yanfeng/github/now_evaluation/generated
```
or
```
python check_predictions.py /home/yanfeng/github/DECA-cache/run/video_dataset_results/subject_1/scans/Subject1_0_0247.obj /home/yanfeng/github/DECA-cache/run/video_dataset_results/subject_1/keypoints/Subject1_0_0247.npy /home/yanfeng/github/DECA-cache/datasets/mon_face_cap/subject_1/scans/reconstruction_0247.ply /home/yanfeng/github/DECA-cache/datasets/mon_face_cap/subject_1/landmarks/reconstruction_0247.txt /home/yanfeng/github/now_evaluation/generated
```

where:

* Predicted mesh path is `.obj`
* Predicted mesh landmark path is `.npy` or `.txt`
* GT scan path is `.ply`
* GT landmark path is `.pp`, or `.npy`, or `.txt`
* `save_path` is a folder to save the generated files to

#### Error computation

First, activate the virtual env for NOW evaluation. It is different from the `deca` environment for training.

```
cd ../mesh
source my_venv/bin/activate
cd ../now_evaluation
```

To run the now evaluation on the validation set, you should search "TODO" in code and modify the arguments in `compute_error.py`, then run
```
python compute_error.py
```

The function in `metric_computation()` in `compute_error.py` is used to compute the error metric. Check the code to see what inputs it needs. `dataset_folder` is the path to root of the dataset, which contains images, scans and lanmarks.

Finally, run:

```
python cumulative_errors.py
```

The output mesh should be in a .obj or .ply file with a corresponding 3D landmark file (.txt or .npy) for each image.

Both the gt folder and prediction folder should have the following file structure:
```
- root
  - subject_1
    - images (gt only)
      - img_1.png
      - img_2.png
      ...
    - scans
      - img_1.obj/.ply
      - img_2.obj/.ply
      ...
    - landmarks
      - img_1.pp/.npy/.txt
      - img_2.pp/.npy/.txt
      ...
  - subject_2
  ...
```

The landmark embedding is used to initialize the rigid alignment process. If you submit a .npy file containing the 7 landmark points, then it should be a 7x3 array where each row is a landmark point. If you submit a .txt file, the coordinates should be 3 numbers separated by comma, and there should be no new line at the end of the file because each line is treated as a point. The order of the points are as shown in the graph below.

Prior to computing the point-to-surface distance, a rigid alignment between each predicted mesh and the scan is computed. The rigid alignment computation requires for each predicted mesh a file with following 7 landmarks:

<p align="center"> 
<img src="landmarks_7_annotated.png" width="50%">
</p>


#### Visualization

Visualization of the reconstruction error is best done with a cumulative error curve. To generate a cumulative error plot, call `generating_cumulative_error_plots()` in the `cumulative_errors.py` with the list of output files and the corresponding list method names. 

**Note that ground truth scans are only provided for the validation set. In order to participate in the NoW challenge, please submit the test set predictions to ringnet@tue.mpg.de as described [here](https://now.is.tue.mpg.de/index.html)**.

#### Known issues

The used [mesh loader](https://github.com/MPI-IS/mesh) is unable to load OBJ files with vertex colors appended to the vertices. I.e. if the OBJ contains lines of the following format `v vx vy vz cr cg cb\n`, export the meshes without vertex colors.

## License

By using the NoW dataset or code, you acknowledge that you have read the [license terms](https://now.is.tue.mpg.de/license.html), understand them, and agree to be bound by them. If you do not agree with these terms and conditions, you must not use the code.

## Citing

This codebase was developed for evaluation of the [RingNet project](https://github.com/soubhiksanyal/RingNet). When using the code or NoW evaluation results in a scientific publication, please cite
```
@inproceedings{RingNet:CVPR:2019,
title = {Learning to Regress 3D Face Shape and Expression from an Image without 3D Supervision},
author = {Sanyal, Soubhik and Bolkart, Timo and Feng, Haiwen and Black, Michael},
booktitle = {Proceedings IEEE Conf. on Computer Vision and Pattern Recognition (CVPR)},
month = jun,
year = {2019},
month_numeric = {6}
}
```
