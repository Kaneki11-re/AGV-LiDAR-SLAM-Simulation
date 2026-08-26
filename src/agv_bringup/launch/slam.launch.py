"""
Starts SLAM Toolbox in online_async mode, consuming /scan + TF (odom->base_footprint),
producing /map, /map_metadata, and the map->odom TF.

Run (after gazebo.launch.py is already up):
    ros2 launch agv_bringup slam.launch.py

Verify:
    ros2 topic list | grep map        # /map /map_metadata
    ros2 topic echo /map_metadata --once
    ros2 run tf2_tools view_frames    # expect map -> odom -> base_footprint -> base_link -> laser_link
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_pkg = get_package_share_directory('agv_bringup')
    default_params = os.path.join(bringup_pkg, 'config', 'slam_toolbox_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('slam_params_file', default_value=default_params),

        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[slam_params_file, {'use_sim_time': use_sim_time}],
        ),
    ])
