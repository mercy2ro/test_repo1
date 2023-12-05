# Date: 2023/12/05  23:00     
# Name: rs2pcd.py
# Note: リアルセンスのデータをPLYに変換する

import pyrealsense2 as rs
import numpy as np
import cv2
from open3d import *
import os
import subprocess
import datetime

#PLYを保存する場所
ply_data_dir = os.environ['HOME'] + '/repo/vscode/test_repo1/data/'

#現在時刻の取得
dt_now = datetime.datetime.now()
time_str = dt_now.strftime('%Y-%m-%d-%H-%M-%S')

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

#　デバイス情報の取得
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()

# RGBがあるか確認
found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

# RGBとDepthの設定を行う
config.enable_stream(rs.stream.depth, rs.format.z16, 30)
config.enable_stream(rs.stream.color, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Get stream profile and camera intrinsics
profile = pipeline.get_active_profile()
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
depth_intrinsics = depth_profile.get_intrinsics()
w, h = depth_intrinsics.width, depth_intrinsics.height

# デプスフレームからポイントクラウドを作成する。
# https://intelrealsense.github.io/librealsense/python_docs/_generated/pyrealsense2.pointcloud.html#pyrealsense2.pointcloud
pc = rs.pointcloud()

# フレームクラスの拡張
# https://intelrealsense.github.io/librealsense/python_docs/_generated/pyrealsense2.points.html#pyrealsense2.points
points = rs.points()

# plyのテクスチャ設定
colorizer = rs.colorizer()

try:
    # Wait for the next set of frames from the camera
    frames = pipeline.wait_for_frames()
    colorized = colorizer.process(frames)

    # Create save_to_ply object
    ply = rs.save_to_ply(ply_data_dir + '{}.ply'.format(time_str))

    # Set options to the desired values
    # In this example we'll generate a textual PLY with normals (mesh is already created by default)
    ply.set_option(rs.save_to_ply.option_ply_binary, False)
    ply.set_option(rs.save_to_ply.option_ply_normals, True)

    print("Saving to 1.ply...")
    # Apply the processing block to the frameset which contains the depth frame and the texture
    ply.process(colorized)
    print("Done")
finally:
    pipeline.stop()