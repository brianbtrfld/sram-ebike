<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  
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
  
  let waypoints: TelemetryUpdate[] = [];
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
          waypoints = [update, ...waypoints].slice(0, 10); // Keep last 10 waypoints
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
</script>

<div class="dashboard">
  <h1 class="ride-title">{rideName}</h1>
  <div class="metrics-grid">
    <div class="metric">
      <h3>Start Time</h3>
      <p class="value date-time">
        <span class="date">{new Date(rideStartTime).toLocaleDateString()}</span>
        <span class="time">{new Date(rideStartTime).toLocaleTimeString()}</span>
      </p>
    </div>
    
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
    padding: 2rem;
    background: #1a1a1a;
    min-height: 100vh;
    color: white;
  }

  .ride-title {
    text-align: center;
    margin-bottom: 2rem;
    color: #fff;
    font-size: 2.5rem;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }

  .metric {
    background: rgba(255, 255, 255, 0.1);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
  }

  .metric h3 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }

  .value {
    font-size: 2.5rem;
    font-weight: bold;
    margin: 0;
    color: #fff;
  }

  .unit {
    font-size: 1rem;
    color: #888;
  }

  .battery-indicator {
    height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 20px;
    position: relative;
    overflow: hidden;
  }

  .battery-level {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #8BC34A);
    transition: width 0.3s ease;
  }

  .battery-level.low {
    background: linear-gradient(90deg, #f44336, #ff9800);
  }

  .battery-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    margin: 0;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
  }

  .waypoints-section {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
  }

  .waypoints-section h2 {
    margin: 0 0 1rem 0;
    font-size: 1.5rem;
    color: #fff;
  }

  .waypoints-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 400px;
    overflow-y: auto;
  }

  .waypoint {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    font-family: monospace;
    transition: background-color 0.3s ease;
  }

  .waypoint.current {
    background: rgba(76, 175, 80, 0.2);
  }

  .waypoint-time {
    color: #888;
  }

  .waypoint-coords {
    text-align: center;
  }

  .waypoint-elevation {
    text-align: right;
  }

  .date-time {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    font-size: 2rem;
  }

  .date {
    font-size: 1.5rem;
    color: #888;
  }

  .time {
    font-weight: bold;
  }

  @media (max-width: 768px) {
    .metrics-grid {
      grid-template-columns: 1fr 1fr;
    }

    .value {
      font-size: 2rem;
    }

    .date-time {
      font-size: 1.5rem;
    }

    .date {
      font-size: 1.2rem;
    }
  }
</style>