use serde::{Deserialize, Serialize};

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