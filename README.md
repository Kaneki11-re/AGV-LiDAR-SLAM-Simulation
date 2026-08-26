# AGV LiDAR SLAM Mapping Simulation

A ROS 2 simulation of a differential-drive Automated Guided Vehicle (AGV) equipped with a 2D LiDAR, performing real-time occupancy-grid mapping using SLAM Toolbox inside a Gazebo indoor environment.

![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy-blue)
![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 1. Overview

This project simulates an indoor AGV built with URDF/Xacro, spawned in Gazebo, and driven manually via keyboard teleoperation while a 2D LiDAR feeds live scan data into **SLAM Toolbox**. The result is a real-time occupancy-grid map (`/map`) visualized in RViz2 and exportable as `map.yaml` + `map.pgm` for reuse in later navigation work.

## 2. Features

- Differential-drive AGV modeled in URDF/Xacro (chassis, drive wheels, caster, LiDAR mount)
- Gazebo simulation environment with walls, corridors, and obstacles for mapping
- Simulated 2D LiDAR publishing `sensor_msgs/msg/LaserScan`
- Keyboard teleoperation via `/cmd_vel`
- Odometry publishing (`/odom`) and full TF tree (`/tf`, `/tf_static`)
- RViz2 visualization of the robot model, LiDAR scan, and TF frames
- Real-time 2D occupancy-grid mapping with SLAM Toolbox (`/map`)
- Map saving to `map.yaml` / `map.pgm` for future reuse

> **Not implemented:** autonomous navigation (Nav2) — see [Future Work](#19-future-work).

## 3. Architecture

```
Gazebo (AGV model + 2D LiDAR)
        │
        ▼
   ros_gz_bridge
        │
        ▼
 ROS 2 topics: /scan, /odom, /tf
        │
        ▼
   SLAM Toolbox
        │
        ▼
      /map  (nav_msgs/msg/OccupancyGrid)
        │
        ▼
      RViz2 (live visualization)
```

Gazebo simulates the AGV's physics, motion, and LiDAR sensing. `ros_gz_bridge` translates Gazebo transport topics into ROS 2 topics. SLAM Toolbox consumes `/scan` and TF to build and publish a live occupancy grid, which RViz2 renders alongside the robot model and TF tree.

## 4. Technologies

| Category | Tool |
|---|---|
| Middleware | ROS 2 Jazzy |
| Simulation | Gazebo |
| Visualization | RViz2 |
| SLAM | SLAM Toolbox |
| Robot description | URDF / Xacro |
| Sim–ROS bridge | ros_gz_bridge |
| Build system | colcon, CMake |
| Languages | Python, XML (URDF/launch) |
| OS | Ubuntu (native or WSL2) |

## 5. ROS 2 Topics

| Topic | Type | Description |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Velocity commands to the AGV |
| `/odom` | `nav_msgs/msg/Odometry` | Wheel odometry |
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D LiDAR scan data |
| `/tf` | `tf2_msgs/msg/TFMessage` | Dynamic transforms |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | Static transforms |
| `/map` | `nav_msgs/msg/OccupancyGrid` | Live occupancy grid from SLAM Toolbox |

## 6. TF Tree

```
odom → base_link → laser_link
```

- **odom**: fixed world-referenced frame updated by odometry
- **base_link**: robot base frame
- **laser_link**: LiDAR sensor frame, fixed offset from `base_link`

> The `map → odom` transform is additionally published by SLAM Toolbox once mapping is running.

## 7. Prerequisites

- Ubuntu 22.04/24.04 (native or WSL2)
- ROS 2 Jazzy installed
- Gazebo (ROS 2 Jazzy's supported Gazebo release) with `ros_gz` packages
- `colcon` and standard ROS 2 build tools
- SLAM Toolbox (`ros-jazzy-slam-toolbox` or equivalent for your distro)

```bash
# Verify installed versions
lsb_release -a
echo $ROS_DISTRO
```

## 8. Installation

```bash
git clone <YOUR_REPO_URL> ~/agv_lidar_ws
cd ~/agv_lidar_ws
rosdep install --from-paths src --ignore-src -y
```

## 9. Build

```bash
cd ~/agv_lidar_ws
colcon build --symlink-install
source install/setup.bash
```

## 10. Run Simulation

```bash
ros2 launch <bringup_package> <bringup_launch_file>
```

> Replace `<bringup_package>` / `<bringup_launch_file>` with your workspace's actual bringup package and launch file name.

Expected result: Gazebo opens with the AGV spawned in the simulation environment, and the LiDAR begins publishing `/scan`.

## 11. Teleoperation

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Drive the AGV using the keyboard controls printed in the terminal. Confirm motion is being commanded:

```bash
ros2 topic echo /cmd_vel
```

## 12. LiDAR Testing

```bash
ros2 topic list
ros2 topic echo /scan
ros2 topic info /scan
ros2 topic hz /scan
```

Confirms the LiDAR is publishing valid `sensor_msgs/msg/LaserScan` data at the expected rate.

## 13. RViz

```bash
ros2 launch <bringup_package> <rviz_launch_file>
```

Add/verify the following displays:
- **RobotModel** — AGV visual geometry
- **LaserScan** — `/scan`
- **TF** — full transform tree
- **Map** — `/map` (once SLAM Toolbox is running)

Verify the TF tree:

```bash
ros2 run tf2_tools view_frames
```

## 14. SLAM Mapping

```bash
ros2 launch <bringup_package> <slam_launch_file>
```

Drive the AGV around the environment with teleoperation while SLAM Toolbox builds the map. Verify:

```bash
ros2 topic list | grep map
ros2 topic echo /map_metadata
```

`/map` should publish as a `nav_msgs/msg/OccupancyGrid` and update live as new areas are explored in RViz2.

## 15. Save Map

```bash
ros2 run nav2_map_server map_saver_cli -f ~/agv_lidar_ws/maps/map
```

Produces:
- `map.yaml` — map metadata (resolution, origin, occupancy thresholds, image reference)
- `map.pgm` — grayscale occupancy image (free / occupied / unknown space)

## 16. Testing / Validation

| Check | Command | Expected Result |
|---|---|---|
| Nodes running | `ros2 node list` | Robot state publisher, bridge, SLAM node present |
| Topics active | `ros2 topic list` | `/cmd_vel`, `/odom`, `/scan`, `/tf`, `/map` present |
| LiDAR rate | `ros2 topic hz /scan` | Stable publish rate, no dropouts |
| TF tree valid | `ros2 run tf2_tools view_frames` | Continuous chain `odom → base_link → laser_link` |
| Map growing | `ros2 topic echo /map_metadata` | Width/height increase as new areas are explored |
| Node graph | `rqt_graph` | Confirms bridge, SLAM, and RViz subscriptions are correctly wired |

## 17. Results

- Successfully mapped an indoor Gazebo environment in real time using SLAM Toolbox
- Stable TF tree and odometry throughout manual teleoperation
- Exported reusable `map.yaml` / `map.pgm` outputs

> _Add screenshots/GIFs of Gazebo, RViz mapping, and the final saved map here._

## 18. Limitations

- No autonomous navigation — the AGV is driven manually via keyboard teleoperation only
- Mapping accuracy depends on manual driving quality (fast turns can introduce drift)
- Simulation-only; not validated on physical hardware
- Single-robot, single-floor environment only

## 19. Future Work

- **Nav2 integration** for autonomous localization (AMCL) and path planning — **not yet implemented**
- Multi-room / multi-floor mapping environments
- Sensor fusion (IMU + odometry) for improved pose estimation
- Support for real AGV hardware deployment

## 20. Author / License

**Author:** _<Kaneki>_
This project is licensed under the [MIT License](LICENSE).
