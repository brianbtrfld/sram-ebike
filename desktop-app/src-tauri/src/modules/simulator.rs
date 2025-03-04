use crate::modules::models::{RideData, TelemetryUpdate};
use std::time::SystemTime;

const EARTH_RADIUS_MILES: f64 = 3959.0; // Earth's radius in miles

/// Simulates telemetry data for an e-bike ride
pub struct TelemetrySimulator {
    pub ride_data: RideData,
    current_index: usize,
    battery_level: f64,
    distance: f64,
}

impl TelemetrySimulator {
    /// Creates a new TelemetrySimulator with the given ride data
    pub fn new(ride_data: RideData) -> Self {
        Self {
            ride_data,
            current_index: 0,
            battery_level: 100.0,
            distance: 0.0,
        }
    }

    /// Returns the next telemetry update in the sequence, or None if the simulation is complete
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
        let (avg_speed, segment_distance) = self.calculate_speed_and_distance(lat, lon, current.timestamp.as_str());

        // Update battery and distance after all calculations are done
        self.update_battery(avg_speed);
        self.distance += segment_distance;

        let update = TelemetryUpdate {
            timestamp: current.timestamp.clone(),
            lat,
            lon,
            elevation_ft,
            avg_speed_mph: avg_speed,
            battery_percentage: self.battery_level,
            distance_miles: self.distance,
        };

        self.current_index += 1;
        Some(update)
    }

    /// Calculates the speed and distance between the current point and the previous point
    fn calculate_speed_and_distance(&self, current_lat: f64, current_lon: f64, current_timestamp: &str) -> (f64, f64) {
        if self.current_index == 0 {
            return (0.0, 0.0);
        }

        let prev = &self.ride_data.waypoints[self.current_index - 1];
        
        let Some((prev_lat, prev_lon)) = prev.lat.zip(prev.lon) else {
            return (0.0, 0.0);
        };

        let distance = Self::calculate_distance(prev_lat, prev_lon, current_lat, current_lon);
        
        // Calculate speed using time difference
        let Some(prev_time) = Self::parse_timestamp(&prev.timestamp) else {
            return (0.0, distance);
        };
        
        let Some(curr_time) = Self::parse_timestamp(current_timestamp) else {
            return (0.0, distance);
        };

        match curr_time.duration_since(prev_time) {
            Ok(duration) => {
                let hours = duration.as_secs_f64() / 3600.0;
                if hours > 0.0 {
                    (distance / hours, distance) // Return (speed in mph, distance)
                } else {
                    (0.0, distance)
                }
            }
            Err(_) => (0.0, distance),
        }
    }

    /// Calculates the distance between two points using the Haversine formula
    fn calculate_distance(lat1: f64, lon1: f64, lat2: f64, lon2: f64) -> f64 {
        let lat1_rad = lat1.to_radians();
        let lon1_rad = lon1.to_radians();
        let lat2_rad = lat2.to_radians();
        let lon2_rad = lon2.to_radians();

        let dlat = lat2_rad - lat1_rad;
        let dlon = lon2_rad - lon1_rad;
        
        let a = (dlat / 2.0).sin().powi(2) 
                + lat1_rad.cos() * lat2_rad.cos() * (dlon / 2.0).sin().powi(2);
        let c = 2.0 * a.sqrt().asin();

        EARTH_RADIUS_MILES * c
    }

    /// Parses an ISO 8601 timestamp string into a SystemTime
    fn parse_timestamp(timestamp: &str) -> Option<SystemTime> {
        chrono::DateTime::parse_from_rfc3339(timestamp)
            .map(|datetime| {
                SystemTime::UNIX_EPOCH + std::time::Duration::new(
                    datetime.timestamp() as u64,
                    datetime.timestamp_subsec_nanos()
                )
            })
            .ok()
    }

    /// Updates the battery level based on current speed
    fn update_battery(&mut self, speed: f64) {
        let speed_factor = speed / 20.0;
        let drain_rate = 0.005 * (1.0 + speed_factor);
        self.battery_level = (self.battery_level - drain_rate).max(0.0);
    }
}