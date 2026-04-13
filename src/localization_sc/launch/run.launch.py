# localization_sc_launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    # Launch arguments
    rviz_arg = DeclareLaunchArgument('rviz', default_value='true')
    lidar_arg = DeclareLaunchArgument('lidar', default_value='livox')
    odom_topic_arg = DeclareLaunchArgument('odom_topic', default_value='/odometry')
    lidar_topic_arg = DeclareLaunchArgument('lidar_topic', default_value='/current_pcd')

    # Get package paths
    fast_lio_loc_dir = get_package_share_directory('localization_sc')
    fast_lio_sam_dir = get_package_share_directory('fast_lio_sam_sc_qn')

    return LaunchDescription([
        # Launch arguments
        rviz_arg,
        odom_topic_arg,
        lidar_topic_arg,

        # RViz node (optional)
        Node(
            condition=LaunchConfiguration('rviz'),
            package='rviz2',
            executable='rviz2',
            name='rviz_sam_localization',
            arguments=['-d', PathJoinSubstitution([fast_lio_loc_dir, 'config', 'localization_rviz.rviz'])],
            output='screen'
        ),

        # Fast LIO Localization node
        Node(
            package='localization_sc',
            executable='localization_sc_node',
            name='localization_sc_node',
            output='screen',
            parameters=[PathJoinSubstitution([fast_lio_loc_dir, 'config', 'config.yaml'])],
            remappings=[
                ('/localization', LaunchConfiguration('odom_topic')),
                ('/corrected_current_pcd_localization', LaunchConfiguration('lidar_topic'))
            ]
        ),

        # Include Fast LIO SAM localization launch
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([fast_lio_sam_dir, 'launch', 'run_localization.launch.py'])
            )
        )
    ])