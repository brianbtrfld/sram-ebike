use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use std::time::SystemTime;

const EARTH_RADIUS_MILES: f64 = 3959.0; // Earth's radius in miles

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Waypoint {
    pub timestamp: String,
    pub lat: Option<f64>,
    pub lon: Option<f64>,
    pub elevation_ft: Option<f64>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RideData {
    pub name: String,
    pub start_time: String,
    pub end_time: String,
    pub number_waypoints: usize,
    pub waypoints: Vec<Waypoint>,
}

#[derive(Debug, Serialize)]
pub struct TelemetryUpdate {
    pub timestamp: String,
    pub lat: f64,
    pub lon: f64,
    pub elevation_ft: f64,
    pub avg_speed_mph: f64,
    pub battery_percentage: f64,
    pub distance_miles: f64,
}

pub struct TelemetrySimulator {
    ride_data: RideData,
    current_index: usize,
    battery_level: f64,
    distance: f64,
    last_update: SystemTime,
}

impl TelemetrySimulator {
    pub fn new(ride_data: RideData) -> Self {
        TelemetrySimulator {
            ride_data,
            current_index: 0,
            battery_level: 100.0,
            distance: 0.0,
            last_update: SystemTime::now(),
        }
    }

    fn calculate_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
        // Convert coordinates to radians
        let lat1_rad = lat1.to_radians();
        let lon1_rad = lon1.to_radians();
        let lat2_rad = lat2.to_radians();
        let lon2_rad = lon2.to_radians();

        // Haversine formula
        let dlat = lat2_rad - lat1_rad;
        let dlon = lon2_rad - lon1_rad;
        let a = (dlat / 2.0).sin().powi(2) 
                + lat1_rad.cos() * lat2_rad.cos() * (dlon / 2.0).sin().powi(2);
        let c = 2.0 * a.sqrt().asin();

        // Calculate distance in miles
        EARTH_RADIUS_MILES * c
    }

    fn parse_timestamp(timestamp: &str) -> Option<SystemTime> {
        // Parse ISO 8601 timestamp to SystemTime
        if let Ok(datetime) = chrono::DateTime::parse_from_rfc3339(timestamp) {
            let seconds = datetime.timestamp() as u64;
            let nanos = datetime.timestamp_subsec_nanos();
            Some(SystemTime::UNIX_EPOCH + std::time::Duration::new(seconds, nanos))
        } else {
            None
        }
    }

    pub fn next_update(&mut self) -> Option<TelemetryUpdate> {
        if self.current_index >= self.ride_data.waypoints.len() {
            return None;
        }

        let current = &self.ride_data.waypoints[self.current_index].clone();
        
        let (lat, lon, elevation_ft) = if let (Some(lat), Some(lon), Some(elev)) = (current.lat, current.lon, current.elevation_ft) {
            (lat, lon, elev)
        } else {
            // Fallback to simulation values if GPS data is missing
            (40.0 + (self.current_index as f64 * 0.001),
             -105.0 + (self.current_index as f64 * 0.001),
             5400.0 + (self.current_index as f64))
        };

        // Calculate speed and distance using actual GPS coordinates
        let (avg_speed, segment_distance) = if self.current_index > 0 {
            let prev = &self.ride_data.waypoints[self.current_index - 1];
            
            if let (Some(prev_lat), Some(prev_lon)) = (prev.lat, prev.lon) {
                let distance = Self::calculate_distance(prev_lat, prev_lon, lat, lon);
                
                // Calculate time difference between waypoints
                if let (Some(prev_time), Some(curr_time)) = (
                    Self::parse_timestamp(&prev.timestamp),
                    Self::parse_timestamp(&current.timestamp)
                ) {
                    if let Ok(duration) = curr_time.duration_since(prev_time) {
                        let hours = duration.as_secs_f64() / 3600.0;
                        if hours > 0.0 {
                            let speed = distance / hours; // mph
                            (speed, distance)
                        } else {
                            (0.0, 0.0)
                        }
                    } else {
                        (0.0, 0.0)
                    }
                } else {
                    (0.0, 0.0)
                }
            } else {
                (0.0, 0.0)
            }
        } else {
            (0.0, 0.0)
        };

        // Update battery and distance after all calculations are done
        self.update_battery(avg_speed);
        self.distance += segment_distance;
        let battery_level = self.battery_level;
        let total_distance = self.distance;

        let update = TelemetryUpdate {
            timestamp: current.timestamp.clone(),
            lat,
            lon,
            elevation_ft,
            avg_speed_mph: avg_speed,
            battery_percentage: battery_level,
            distance_miles: total_distance,
        };

        self.current_index += 1;
        Some(update)
    }

    fn update_battery(&mut self, speed: f64) {
        // Simple battery simulation
        // Battery drains faster at higher speeds
        let speed_factor = speed / 20.0;
        let drain_rate = 0.005 * (1.0 + speed_factor);
        self.battery_level = (self.battery_level - drain_rate).max(0.0);
    }
}

// Static storage for the active simulator
pub static SIMULATOR: Mutex<Option<TelemetrySimulator>> = Mutex::new(None);

#[tauri::command]
pub fn get_ride_data() -> Option<RideData> {
    if let Ok(sim) = SIMULATOR.lock() {
        if let Some(simulator) = &*sim {
            return Some(simulator.ride_data.clone());
        }
    }
    None
}