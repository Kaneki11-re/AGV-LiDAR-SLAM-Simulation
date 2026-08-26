"""
One-shot bringup: Gazebo Harmonic + AGV spawn + ros_gz bridge + SLAM Toolbox + RViz2.
This is the file the final demo uses. Individual pieces (gazebo.launch.py / slam.launch.py /
rviz.launch.py) stay available separately for step-by-step debugging.

Run:
    ros2 launch agv_bringup bringup.launch.py

Then drive with (separate terminal):
    ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel

Args:
    slam:=false   -> skip SLAM Toolbox (e.g. when running Nav2 with a saved map instead)
    rviz:=false   -> skip RViz2
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    gz_pkg = get_package_share_directory('agv_gazebo')
    bringup_pkg = get_package_share_directory('agv_bringup')

    slam_enabled = LaunchConfiguration('slam')
    rviz_enabled = LaunchConfiguration('rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_pkg, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_pkg, 'launch', 'slam.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
        condition=IfCondition(slam_enabled),
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_pkg, 'launch', 'rviz.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
        condition=IfCondition(rviz_enabled),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('slam', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        gazebo,
        slam,
        rviz,
    ])
