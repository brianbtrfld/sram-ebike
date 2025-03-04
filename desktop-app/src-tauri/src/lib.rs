mod modules;

use modules::commands::{start_simulation, get_telemetry_update, stop_simulation, get_ride_data, upload_ride};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            start_simulation,
            get_telemetry_update,
            stop_simulation,
            get_ride_data,
            upload_ride
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}