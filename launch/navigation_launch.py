# Copyright (c) 2025, IoT Convergence & Open Sharing System (IoTCOSS)
#
# All rights reserved. This software and its documentation are proprietary and confidential.
# The IoT Convergence & Open Sharing System (IoTCOSS) retains all intellectual property rights,
# including but not limited to copyrights, patents, and trade secrets, in and to this software
# and related documentation. Any use, reproduction, disclosure, or distribution of this software
# and related documentation without explicit written permission from IoTCOSS is strictly prohibited.
#

import os
import yaml

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import LogInfo

# Occupancy map origin in USD coordinates. 
# DO NOT MODIFY.
OCCUPANCY_MAP_ORIGIN = {
    'demo': {
        'x': -86.7541493,
        'y': 160.2545698
    },
    'dongcheon': {
        'x': -76.2897327,
        'y': -21.2256001
    },
    'jiphyeon': {
        'x': -9.8303455,
        'y': -235.424633
    },
    'gwanggaeto': {
        'x': -52.4983671,
        'y': -81.8953669
    }
}

# Generate description for ROS2 launch
def generate_launch_description():
    # Get scenario name from environment variable
    scenario = os.getenv('ENV_METASEJONG_SCENARIO', 'demo')
    metasejong = os.getenv('METASEJONG_PROJECT_PATH', '')
    scenario_file = os.path.join('/workspace', 'metasejong', 'scenario-data', f'{scenario}.yaml')
    print(f"scenario: {scenario}, scenario_file: {scenario_file}")

    # Get absolute path of current file and find parent directory
    current_file_path = os.path.abspath(__file__)
    workspace_dir = os.path.dirname(os.path.dirname(current_file_path))
    
    # Set map file path
    map_yaml_file = os.path.join(workspace_dir, 'config', 'maps', f'{scenario}_map.yaml')
    
    # Log map file path
    map_path_info = LogInfo(msg=f'Map file path: {map_yaml_file}')

    print(f"map_yaml_file: {map_yaml_file}")    

    # Load Scenario file
    scenario_data = None
    try:
        with open(scenario_file, "r") as f:
            scenario_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Error while parsing configuration file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error while loading configuration file: {str(e)}")


    #   Create map server ROS2 Node 
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        namespace='metasejong2025',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml_file,
            'frame_id': 'metasejong2025/map',
            'topic_name': 'map',
            'update_topic_name': 'map_updates',
            'image_format': 'png'
        }]
    )

    # Create lifecycle manager ROS2 Node 
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map_server',
        namespace='metasejong2025',
        output='screen',
        parameters=[{
            'use_sim_time': False,
            'autostart': True,
            'node_names': ['map_server']
        }]
    )

    # Create static_transform_publisher ROS2 Node 

    # Get robot start position from scenario data
    if scenario_data is not None:
        robot_start_position = scenario_data['robot']['start_point']
        robot_usd_position_x = robot_start_position[0]
        robot_usd_position_y = robot_start_position[1]
    else:
        robot_usd_position_x = 0.0
        robot_usd_position_y = 0.0

    # Get map origin from scenario data
    if OCCUPANCY_MAP_ORIGIN[scenario] is not None:
        map_usd_origin_x = OCCUPANCY_MAP_ORIGIN[scenario]['x'] # map_yaml_data['origin'][0] * 100
        map_usd_origin_y = OCCUPANCY_MAP_ORIGIN[scenario]['y'] # map_yaml_data['origin'][1] * 100
    else:
        map_usd_origin_x = 0.0
        map_usd_origin_y = 0.0

    # Calculate robot initial position in map frame
    robot_initial_position_x = robot_usd_position_x - map_usd_origin_x
    robot_initial_position_y = robot_usd_position_y - map_usd_origin_y

    # Create static_transform_publisher ROS2 Node 
    static_tf_map_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_map_odom',
        arguments=[f'{robot_initial_position_x}', f'{robot_initial_position_y}', '0.0', '0.0', '0.0', '0.0', 'metasejong2025/map', 'odom']
    )


    # Create RViz2 ROS2 Node 
    rviz_config_file = os.path.join(workspace_dir, 'config', 'rviz', 'map_view.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': False}],
        arguments=['-d', rviz_config_file],
    )

    # Return LaunchDescription
    return LaunchDescription([
        map_path_info,
        map_server,
        static_tf_map_odom,
        lifecycle_manager,
        rviz_node,
    ]) 