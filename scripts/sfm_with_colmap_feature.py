import sys
import yaml
import os
sys.path.append('../build')
import GlobalSfMpy as sfm
from loss_functions import *
from sfm_pipeline import *
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--dataset_path", default="../datasets/facade")
args = parser.parse_args()


flagfile = "../flags_1dsfm.yaml"
f = open(flagfile,"r")
config = yaml.safe_load(f)
glog_directory = config['glog_directory']
glog_verbose = config['v']
log_to_stderr = config['log_to_stderr']
sfm.InitGlog(glog_verbose,log_to_stderr,glog_directory)

dataset_path = args.dataset_path
dataset_name = dataset_path.split('/')[-1]

colmap_path = dataset_path+"/colmap/images.txt"
output_reconstruction = "../output/"+dataset_name

print('reading from ', colmap_path)
rotation_error_type = sfm.RotationErrorType.ANGLE_AXIS_COVARIANCE
position_error_type = sfm.PositionErrorType.BASELINE

reconstruction = sfm_pipeline(flagfile,dataset_path,
                                            MAGSACWeightBasedLoss(0.02),HuberLoss(0.1),
                                            rotation_error_type,position_error_type,
                                            onlyRotationAvg=False)
logging.warn('number final tracks %d', reconstruction.NumTracks())
if os.path.exists(output_reconstruction):
    os.remove(output_reconstruction)
sfm.WriteReconstruction(reconstruction, output_reconstruction)
sfm.WritePlyFile(output_reconstruction + '.ply', reconstruction, 2)
colmap_out_dir = output_reconstruction + '_colmap' 
os.makedirs(colmap_out_dir)
status = sfm.WriteColmapFiles(reconstruction, colmap_out_dir)
if not status:
    raise ValueError('unable to write colmap files')

sfm.StopGlog()



