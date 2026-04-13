import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('fast_lio_sam_sc_qn')
    # 假设 fast_lio 的 ROS2 版本包名为 fast_lio
    fast_lio_pkg = get_package_share_directory('fast_lio')

    # Arguments
    rviz_arg = DeclareLaunchArgument('rviz', default_value='true')
    lidar_arg = DeclareLaunchArgument('lidar', default_value='livox')
    odom_topic_arg = DeclareLaunchArgument('odom_topic', default_value='/Odometry')
    lidar_topic_arg = DeclareLaunchArgument('lidar_topic', default_value='/cloud_registered')

    # Paths
    rviz_config_path = os.path.join(pkg_share, 'config', 'sam_rviz.rviz')
    config_file_path = os.path.join(pkg_share, 'config', 'config.yaml')

    # Nodes
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_sam',
        arguments=['-d', rviz_config_path],
        condition=IfCondition(LaunchConfiguration('rviz'))
    )

    sam_node = Node(
        package='fast_lio_sam_sc_qn',
        executable='fast_lio_sam_sc_qn_node',
        name='fast_lio_sam_sc_qn_node',
        parameters=[config_file_path],
        remappings=[
            ('/Odometry', LaunchConfiguration('odom_topic')),
            ('/cloud_registered', LaunchConfiguration('lidar_topic'))
        ],
        output='screen'
    )

    # Fast LIO Includes (Conditionals)
    mapping_ouster = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fast_lio_pkg, 'launch', 'mapping_ouster64.launch.py')),
        launch_arguments={'rviz': 'false'}.items(),
        condition=LaunchConfigurationEquals('lidar', 'ouster')
    )

    mapping_velodyne = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fast_lio_pkg, 'launch', 'mapping_velodyne.launch.py')),
        launch_arguments={'rviz': 'false'}.items(),
        condition=LaunchConfigurationEquals('lidar', 'velodyne')
    )

    mapping_livox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fast_lio_pkg, 'launch', 'mapping_mid360.launch.py')),
        launch_arguments={'rviz': 'false'}.items(),
        condition=LaunchConfigurationEquals('lidar', 'livox')
    )

    # 其他自定义配置文件的路径映射 (kitti, mulran 等)
    # ROS2 通常直接放在包的 launch 目录下
    mapping_kitti = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(fast_lio_pkg, 'launch', 'kitti.launch.py')),
        launch_arguments={'rviz': 'false'}.items(),
        condition=LaunchConfigurationEquals('lidar', 'kitti')
    )

    return LaunchDescription([
        rviz_arg,
        lidar_arg,
        odom_topic_arg,
        lidar_topic_arg,
        rviz_node,
        sam_node,
        mapping_ouster,
        mapping_velodyne,
        mapping_livox,
        mapping_kitti
    ])