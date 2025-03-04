<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import { goto } from '$app/navigation';
  
  interface TelemetryUpdate {
    timestamp: string;
    lat: number;
    lon: number;
    elevation_ft: number;
    avg_speed_mph: number;
    battery_percentage: number;
    distance_miles: number;
  }
  
  let rideStartTime = '';
  let rideName = '';
  let telemetryData: TelemetryUpdate = {
    timestamp: new Date().toISOString(),
    lat: 0,
    lon: 0,
    elevation_ft: 0,
    avg_speed_mph: 0,
    battery_percentage: 100,
    distance_miles: 0
  };
  
  let waypoints: TelemetryUpdate[] = Array(6).fill({
    timestamp: new Date().toISOString(),
    lat: 0,
    lon: 0,
    elevation_ft: 0,
    avg_speed_mph: 0,
    battery_percentage: 100,
    distance_miles: 0
  });
  let updateInterval: number;

  async function initializeRide() {
    try {
      // Get the ride data to access the start time and name
      const rideData = await invoke<{ start_time: string, name: string }>('get_ride_data');
      rideStartTime = rideData.start_time;
      rideName = rideData.name;
    } catch (error) {
      console.error('Failed to get ride data:', error);
    }
  }
  
  onMount(async () => {
    await initializeRide();
    
    updateInterval = setInterval(async () => {
      try {
        const update = await invoke<TelemetryUpdate>('get_telemetry_update');
        if (update) {
          telemetryData = update;
          // Keep exactly 6 waypoints, shifting out the oldest one
          waypoints = [update, ...waypoints.slice(0, 5)];
        }
      } catch (error) {
        console.error('Failed to get telemetry update:', error);
      }
    }, 1000);
  });

  onDestroy(() => {
    clearInterval(updateInterval);
    invoke('stop_simulation');
  });

  function goToUpload() {
    invoke('stop_simulation');
    goto('/');
  }
</script>

<div class="dashboard">
  <div class="header">
    <h1 class="ride-title">{rideName}</h1>
    <button class="upload-button" on:click={goToUpload}>Upload</button>
  </div>

  <div class="start-time">
    <p class="value date-time">
      <span class="date">{new Date(rideStartTime).toLocaleDateString()}</span>
      <span class="time">{new Date(rideStartTime).toLocaleTimeString()}</span>
    </p>
  </div>
  
  <div class="metrics-grid">
    <div class="metric">
      <h3>Speed</h3>
      <p class="value">{telemetryData.avg_speed_mph.toFixed(1)} <span class="unit">MPH</span></p>
    </div>

    <div class="metric">
      <h3>Battery</h3>
      <div class="battery-indicator">
        <div 
          class="battery-level" 
          class:low={telemetryData.battery_percentage < 20}
          style="width: {telemetryData.battery_percentage}%"
        ></div>
        <p class="battery-text">{telemetryData.battery_percentage.toFixed(1)}%</p>
      </div>
    </div>

    <div class="metric">
      <h3>Distance</h3>
      <p class="value">{telemetryData.distance_miles.toFixed(2)} <span class="unit">mi</span></p>
    </div>
  </div>

  <div class="waypoints-section">
    <h2>Recent Waypoints</h2>
    <div class="waypoints-list">
      {#each waypoints as point, i}
        <div class="waypoint" class:current={i === 0}>
          <div class="waypoint-time">{new Date(point.timestamp).toLocaleTimeString()}</div>
          <div class="waypoint-coords">
            {point.lat.toFixed(6)}°, {point.lon.toFixed(6)}°
          </div>
          <div class="waypoint-elevation">
            {point.elevation_ft.toFixed(0)} ft
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .dashboard {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem;
    min-height: 100vh;
    background: white;
    color: #333;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    max-width: 1000px;
    margin-bottom: 2rem;
  }

  .upload-button {
    background: #e31837;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }

  .upload-button:hover {
    background: #c41430;
  }

  .ride-title {
    font-size: 2rem;
    color: #333;
    margin: 0;
  }

  .start-time {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    width: 100%;
    max-width: 1000px;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
    width: 100%;
    max-width: 1000px;
  }

  .metric {
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .metric h3 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .value {
    font-size: 1.8rem;
    font-weight: bold;
    margin: 0;
    color: #333;
  }

  .unit {
    font-size: 0.8rem;
    color: #666;
  }

  .battery-indicator {
    height: 30px;
    background: rgba(0, 0, 0, 0.1);
    border-radius: 15px;
    position: relative;
    overflow: hidden;
  }

  .battery-level {
    height: 100%;
    background: linear-gradient(90deg, #e31837, #ff4d6a);
    transition: width 0.3s ease;
  }

  .battery-level.low {
    background: linear-gradient(90deg, #ff9800, #ff4d00);
  }

  .battery-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    margin: 0;
    font-size: 0.9rem;
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  }

  .date-time {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    align-items: center;
    font-size: 1.5rem;
  }

  .date {
    font-size: 2rem;
    color: #333;
    font-weight: bold;
  }

  .time {
    font-size: 1.2rem;
    color: #666;
  }

  .waypoints-section {
    background: #f5f5f5;
    border-radius: 12px;
    padding: 1rem;
    width: 100%;
    max-width: 1000px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }

  .waypoints-section h2 {
    margin: 0 0 0.8rem 0;
    font-size: 1.2rem;
    color: #333;
  }

  .waypoints-list {
    display: grid;
    grid-template-rows: repeat(6, 1fr);
    gap: 0.4rem;
  }

  .waypoint {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    gap: 0.8rem;
    padding: 0.8rem;
    background: white;
    border-radius: 8px;
    font-family: monospace;
    font-size: 0.9rem;
    transition: background-color 0.3s ease;
    border: 1px solid #eee;
  }

  .waypoint.current {
    background: rgba(227, 24, 55, 0.1);
    border-color: #e31837;
  }

  .waypoint-time {
    color: #666;
  }

  .waypoint-coords {
    text-align: center;
    color: #333;
  }

  .waypoint-elevation {
    text-align: right;
    color: #333;
  }

  @media (max-width: 768px) {
    .header {
      flex-direction: column;
      gap: 1rem;
    }

    .ride-title {
      text-align: center;
    }

    .metrics-grid {
      grid-template-columns: 1fr 1fr;
      gap: 0.8rem;
    }

    .value {
      font-size: 1.5rem;
    }

    .date-time {
      font-size: 1.2rem;
    }

    .date {
      font-size: 1.8rem;
    }

    .time {
      font-size: 1rem;
    }

    .waypoint {
      font-size: 0.8rem;
      padding: 0.6rem;
    }
  }

  @media (max-width: 480px) {
    .dashboard {
      padding: 1rem;
    }

    .metrics-grid {
      grid-template-columns: 1fr;
    }

    .date {
      font-size: 1.5rem;
    }

    .time {
      font-size: 0.9rem;
    }
  }
</style>