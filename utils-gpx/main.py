#!/usr/bin/env python3
"""
GPX to JSON converter with ride metrics calculation.
Converts GPX tracking data to JSON format and calculates various ride metrics.
Uses imperial/standard units (miles, feet) for measurements.
"""

import gpxpy
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse
from pathlib import Path
import sys
from utils import (
    calculate_distance,
    calculate_elevation_gain,
    meters_to_feet,
    format_elapsed_time,
    is_valid_speed
)
from models import Waypoint, RideData

def parse_gpx_to_json(input_gpx_file: str, output_json_file: str) -> RideData:
    """
    Parse GPX file and convert to JSON format with additional ride metrics.
    All measurements are in imperial/standard units (miles, feet).
    
    Args:
        input_gpx_file: Path to input GPX file
        output_json_file: Path to output JSON file
    
    Returns:
        Dictionary containing ride data and metrics
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        gpxpy.GPXException: If GPX file is invalid
        PermissionError: If unable to write output file
    """
    try:
        with open(input_gpx_file, 'r') as gpx_file:
            gpx = gpxpy.parse(gpx_file)
    except FileNotFoundError:
        print(f"Error: Input file '{input_gpx_file}' not found", file=sys.stderr)
        raise
    except gpxpy.GPXException as e:
        print(f"Error: Invalid GPX file - {str(e)}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error reading GPX file: {str(e)}", file=sys.stderr)
        raise

    ride_data = create_empty_ride_data()
    total_points = sum(len(segment.points) for track in gpx.tracks for segment in track.segments)
    points_processed = 0
    speed_readings = []
    last_valid_speed = 0.0
    
    for track in gpx.tracks:
        ride_data['name'] = track.name
        
        for segment in track.segments:
            prev_point = None
            prev_time = None
            segment_elevations_ft = []
            
            for point in segment.points:
                waypoint, distance, speed, new_last_valid_speed = process_point(
                    point, prev_point, prev_time, last_valid_speed
                )
                
                ride_data['waypoints'].append(waypoint)
                ride_data['total_distance_mi'] += distance
                
                if speed is not None:
                    speed_readings.append(speed)
                    last_valid_speed = new_last_valid_speed
                
                if point.elevation is not None:
                    segment_elevations_ft.append(waypoint['elevation_ft'])
                
                prev_point = point
                prev_time = point.time
                points_processed += 1
                
                if total_points > 1000 and points_processed % 100 == 0:
                    print(f"\rProcessing points: {points_processed}/{total_points}", 
                          end='', file=sys.stderr)
            
            if segment_elevations_ft:
                ride_data['total_elevation_gain_ft'] += calculate_elevation_gain(segment_elevations_ft)

    if total_points > 1000:
        print(file=sys.stderr)

    calculate_ride_stats(ride_data, speed_readings)

    try:
        with open(output_json_file, 'w') as json_file:
            json.dump(ride_data, json_file, indent=2)
    except PermissionError:
        print(f"Error: Unable to write to output file '{output_json_file}'", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error writing JSON file: {str(e)}", file=sys.stderr)
        raise

    return ride_data

def create_empty_ride_data() -> RideData:
    """Create an empty RideData structure with default values."""
    return {
        'name': None,
        'start_time': None,
        'end_time': None,
        'number_waypoints': 0,
        'total_distance_mi': 0.0,
        'total_elevation_gain_ft': 0.0,
        'average_speed_mph': None,
        'max_speed_mph': None,
        'elapsed_time': None,
        'waypoints': []
    }

def process_point(point: gpxpy.gpx.GPXTrackPoint,
                 prev_point: Optional[gpxpy.gpx.GPXTrackPoint],
                 prev_time: Optional[datetime],
                 last_valid_speed: float) -> Tuple[Waypoint, float, float, Optional[float]]:
    """
    Process a single GPX track point and calculate derived metrics.
    
    Returns:
        Tuple containing:
        - Waypoint data
        - Distance traveled since last point (miles)
        - Current speed (mph)
        - Updated last valid speed
    """
    elevation_ft = meters_to_feet(point.elevation) if point.elevation is not None else 0.0
    waypoint: Waypoint = {
        'lat': point.latitude,
        'lon': point.longitude,
        'elevation_ft': elevation_ft,
        'timestamp': point.time.isoformat() if point.time else None
    }
    
    distance = 0.0
    speed = None
    new_last_valid_speed = last_valid_speed
    
    if prev_point and point.time and prev_time:
        distance = calculate_distance(
            prev_point.latitude, prev_point.longitude,
            point.latitude, point.longitude
        )
        
        time_diff = (point.time - prev_time).total_seconds() / 3600
        if time_diff > 0.00027777:  # Minimum 1 second between readings
            speed = distance / time_diff
            if is_valid_speed(speed, last_valid_speed):
                new_last_valid_speed = speed
    
    return waypoint, distance, speed, new_last_valid_speed

def calculate_ride_stats(ride_data: RideData, speed_readings: List[float]) -> None:
    """Calculate and update ride statistics based on collected data."""
    if not ride_data['waypoints']:
        return
        
    first_point = ride_data['waypoints'][0]
    last_point = ride_data['waypoints'][-1]
    
    ride_data['start_time'] = first_point['timestamp']
    ride_data['end_time'] = last_point['timestamp']
    ride_data['number_waypoints'] = len(ride_data['waypoints'])
    
    if first_point['timestamp'] and last_point['timestamp']:
        start_time = datetime.fromisoformat(first_point['timestamp'])
        end_time = datetime.fromisoformat(last_point['timestamp'])
        elapsed_seconds = (end_time - start_time).total_seconds()
        duration_hours = elapsed_seconds / 3600
        
        if duration_hours > 0:
            ride_data['average_speed_mph'] = ride_data['total_distance_mi'] / duration_hours
            
            if speed_readings:
                sorted_speeds = sorted(speed_readings)
                percentile_95_idx = int(len(sorted_speeds) * 0.95)
                ride_data['max_speed_mph'] = sorted_speeds[percentile_95_idx]
            
            ride_data['elapsed_time'] = format_elapsed_time(elapsed_seconds)

def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description='Convert GPX file to JSON with ride metrics')
    parser.add_argument('input', help='Input GPX file')
    parser.add_argument('-o', '--output', help='Output JSON file (default: input_file_name.json)')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not args.output:
        output_path = input_path.with_suffix('.json')
    else:
        output_path = Path(args.output)

    try:
        result = parse_gpx_to_json(str(input_path), str(output_path))
        print(f"\nSuccessfully processed GPX file:")
        print(f"Ride name: {result['name']}")
        print(f"Start time: {result['start_time']}")
        print(f"End time: {result['end_time']}")
        print(f"Elapsed time: {result['elapsed_time']}")
        print(f"Number of waypoints: {result['number_waypoints']}")
        print(f"Total distance: {result['total_distance_mi']:.2f} mi")
        print(f"Total elevation gain: {result['total_elevation_gain_ft']:.1f} ft")
        if result['average_speed_mph']:
            print(f"Average speed: {result['average_speed_mph']:.1f} mph")
        if result['max_speed_mph']:
            print(f"Max speed: {result['max_speed_mph']:.1f} mph")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()