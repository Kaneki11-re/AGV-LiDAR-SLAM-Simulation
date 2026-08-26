"""
Standalone launch: publishes robot_description + TF tree from URDF, WITHOUT Gazebo.
Use this first to sanity-check the URDF and TF tree in RViz2 before ever touching Gazebo.

Run:
    ros2 launch agv_description description.launch.py

Verify:
    ros2 run tf2_tools view_frames   (expect base_footprint -> base_link -> wheels/laser/caster)
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_share = get_package_share_directory('agv_description')
    xacro_path = os.path.join(pkg_share, 'urdf', 'agv.urdf.xacro')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_jsp_gui = LaunchConfiguration('use_jsp_gui')

    robot_description = ParameterValue(
    Command(['xacro ', xacro_path]),
    value_type=str
)

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false',
                               description='Use /clock from Gazebo if true'),
        DeclareLaunchArgument('use_jsp_gui', default_value='true',
                               description='Launch joint_state_publisher_gui for manual wheel spin'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': use_sim_time,
            }],
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            condition=IfCondition(use_jsp_gui),
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', os.path.join(pkg_share, 'rviz', 'agv.rviz')],
            parameters=[{'use_sim_time': use_sim_time}],
        ),
    ])
