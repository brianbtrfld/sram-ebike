<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { invoke } from "@tauri-apps/api/core";
  import { goto } from '$app/navigation';
  import Header from '../../components/Header.svelte';
  import StartTime from '../../components/StartTime.svelte';
  import MetricsGrid from '../../components/MetricsGrid.svelte';
  import WaypointsList from '../../components/WaypointsList.svelte';
  
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
    }, 50);
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
  <Header {rideName} {goToUpload} />
  <StartTime {rideStartTime} />
  <MetricsGrid {telemetryData} />
  <WaypointsList {waypoints} />
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
</style>