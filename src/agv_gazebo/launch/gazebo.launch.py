"""
Starts Gazebo Harmonic (gz sim) with the warehouse world, publishes robot_description
from the AGV xacro, spawns the AGV into the world, and starts the ros_gz_bridge so
/cmd_vel, /odom, /tf, /scan, /joint_states, /clock cross between gz transport and ROS 2.

Run:
    ros2 launch agv_gazebo gazebo.launch.py

Verify:
    ros2 topic list          # expect /scan /odom /tf /cmd_vel /joint_states /clock
    ros2 topic hz /scan      # ~10 Hz
    gz topic -l              # gz-side topics also visible
"""
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    gz_pkg = get_package_share_directory('agv_gazebo')
    desc_pkg = get_package_share_directory('agv_description')

    world_path = os.path.join(gz_pkg, 'worlds', 'warehouse.world')
    bridge_config = os.path.join(gz_pkg, 'config', 'gz_bridge.yaml')
    xacro_path = os.path.join(desc_pkg, 'urdf', 'agv.urdf.xacro')

    use_sim_time = LaunchConfiguration('use_sim_time')

    robot_description = ParameterValue(
    Command(['xacro ', xacro_path]),
    value_type=str
)

    # Launch gz sim with the world. -r = run immediately, -v4 = verbose logging.
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r -v4 {world_path}'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
    )

    # Spawns the robot into the running gz sim world by reading /robot_description
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'agv',
            '-topic', 'robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.05',
        ],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        parameters=[{'config_file': bridge_config, 'use_sim_time': use_sim_time}],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gz_sim,
        robot_state_publisher,
        spawn_entity,
        bridge,
    ])
