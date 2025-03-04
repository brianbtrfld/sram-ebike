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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet, upload_name, get_items])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
