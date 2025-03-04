use std::fs;
mod telemetry;
use telemetry::{RideData, TelemetrySimulator, SIMULATOR, get_ride_data};

#[tauri::command]
fn start_simulation(ride_type: &str) -> Result<String, String> {
    let file_path = match ride_type {
        "chill" => "resources/rides/ride-chill.json",
        "hardcore" => "resources/rides/ride-hardcore.json",
        _ => return Err("Invalid ride type".to_string()),
    };

    let file_content = fs::read_to_string(file_path)
        .map_err(|e| e.to_string())?;
    
    let ride_data: RideData = serde_json::from_str(&file_content)
        .map_err(|e| e.to_string())?;

    let simulator = TelemetrySimulator::new(ride_data);
    let mut sim_lock = SIMULATOR.lock().map_err(|e| e.to_string())?;
    *sim_lock = Some(simulator);

    Ok("Simulation started".to_string())
}

#[tauri::command]
fn get_telemetry_update() -> Result<Option<serde_json::Value>, String> {
    let mut sim_lock = SIMULATOR.lock().map_err(|e| e.to_string())?;
    
    if let Some(simulator) = sim_lock.as_mut() {
        if let Some(update) = simulator.next_update() {
            return Ok(Some(serde_json::to_value(update).unwrap()));
        }
    }
    
    Ok(None)
}

#[tauri::command]
fn stop_simulation() -> Result<String, String> {
    let mut sim_lock = SIMULATOR.lock().map_err(|e| e.to_string())?;
    *sim_lock = None;
    Ok("Simulation stopped".to_string())
}

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
async fn upload_name(name: &str) -> Result<String, String> {
    let client = reqwest::Client::new();
    let response = client
        .post("http://127.0.0.1:8000/api/upload")
        .header("Content-Type", "application/json")
        .body(format!(r#"{{"name":"{}"}}"#, name))
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let status = response.status();
    let text = response.text().await.map_err(|e| e.to_string())?;
    
    if status.is_success() {
        Ok(text)
    } else {
        Err(format!("API Error: {} - {}", status, text))
    }
}

#[tauri::command]
async fn get_items() -> Result<serde_json::Value, String> {
    let client = reqwest::Client::new();
    let response = client
        .get("http://127.0.0.1:8000/api/")
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    let status = response.status();
    
    if status.is_success() {
        // Parse the JSON response directly in Rust
        response.json::<serde_json::Value>()
            .await
            .map_err(|e| format!("Failed to parse JSON response: {}", e))
    } else {
        let text = response.text().await.map_err(|e| e.to_string())?;
        Err(format!("API Error: {} - {}", status, text))
    }
}

#[tauri::command]
fn read_ride_chill() -> Result<serde_json::Value, String> {
    let file_content = fs::read_to_string("resources/rides/ride-chill.json")
        .map_err(|e| e.to_string())?;
    
    serde_json::from_str(&file_content)
        .map_err(|e| e.to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            greet, 
            upload_name, 
            get_items, 
            read_ride_chill,
            start_simulation,
            get_telemetry_update,
            stop_simulation,
            get_ride_data
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
