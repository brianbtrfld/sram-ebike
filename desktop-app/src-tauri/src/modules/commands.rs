use crate::modules::models::RideData;
use crate::modules::simulator::TelemetrySimulator;
use std::sync::Mutex;
use reqwest::blocking::Client;

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

#[tauri::command]
pub fn start_simulation(ride_type: &str) -> Result<String, String> {
    let file_path = match ride_type {
        "chill" => "resources/rides/ride-chill.json",
        "hardcore" => "resources/rides/ride-hardcore.json",
        _ => return Err("Invalid ride type".to_string()),
    };

    let file_content = std::fs::read_to_string(file_path)
        .map_err(|e| e.to_string())?;
    
    let ride_data: RideData = serde_json::from_str(&file_content)
        .map_err(|e| e.to_string())?;

    let simulator = TelemetrySimulator::new(ride_data);
    let mut sim_lock = SIMULATOR.lock().map_err(|e| e.to_string())?;
    *sim_lock = Some(simulator);

    Ok("Simulation started".to_string())
}

#[tauri::command]
pub fn get_telemetry_update() -> Result<Option<serde_json::Value>, String> {
    let mut sim_lock = SIMULATOR.lock().map_err(|e| e.to_string())?;
    
    if let Some(simulator) = sim_lock.as_mut() {
        if let Some(update) = simulator.next_update() {
            return Ok(Some(serde_json::to_value(update).unwrap()));
        }
    }
    
    Ok(None)
}

#[tauri::command]
pub fn stop_simulation() -> Result<String, String> {
    let mut sim_lock = SIMULATOR.lock().map_err(|e| e.to_string())?;
    *sim_lock = None;
    Ok("Simulation stopped".to_string())
}

#[tauri::command]
pub fn upload_ride() -> Result<String, String> {
    let sim_lock = SIMULATOR.lock().map_err(|e| e.to_string())?;
    
    if let Some(simulator) = &*sim_lock {
        // Clone the ride data while keeping simulator active
        let ride_data = simulator.ride_data.clone();
        
        // Upload the data while keeping simulation active
        let client = Client::new();
        let response = client
            .post("http://127.0.0.1:8000/api/rides/upload")
            .json(&ride_data)
            .send()
            .map_err(|e| e.to_string())?;
            
        let status = response.status();
        
        if status.is_success() {
            Ok("Ride uploaded successfully".to_string())
        } else {
            let error_text = response.text().unwrap_or_else(|_| status.to_string());
            Err(format!("Upload failed: {}", error_text))
        }
    } else {
        Err("No active simulation to upload".to_string())
    }
}