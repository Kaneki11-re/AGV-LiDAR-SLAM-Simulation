"""
Autonomous navigation using Nav2 + AMCL localization on a map already saved from SLAM.
NOTE: this replaces SLAM Toolbox — do not run slam.launch.py and this at the same time.
SLAM builds the map; this launch localizes against a finished map and plans/drives to goals.

Run:
    ros2 launch agv_bringup gazebo.launch.py                     # world + robot only, no SLAM
    ros2 launch agv_navigation navigation.launch.py map:=/home/<you>/agv_lidar_ws/src/agv_navigation/maps/map.yaml

Then in RViz2: "2D Pose Estimate" to seed AMCL, then "Nav2 Goal" to send a goal.
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    nav_pkg = get_package_share_directory('agv_navigation')
    nav2_bringup_pkg = get_package_share_directory('nav2_bringup')

    default_params = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')
    default_map = os.path.join(nav_pkg, 'maps', 'map.yaml')

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml,
            'params_file': params_file,
            'use_sim_time': use_sim_time,
        }.items(),
    )

    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=default_map),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        nav2,
    ])
