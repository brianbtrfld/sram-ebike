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
      const rideData = await invoke<{ start_time: string, name: string }>('get_ride_data');
      rideStartTime = rideData.start_time;
      rideName = rideData.name;
    } catch (error) {
      console.error('Failed to get ride data:', error);
    }
  }

  function initializeUpdateInterval() {
    updateInterval = setInterval(async () => {
      try {
        const update = await invoke<TelemetryUpdate>('get_telemetry_update');
        if (update) {
          telemetryData = update;
          waypoints = [update, ...waypoints.slice(0, 5)];
        }
      } catch (error) {
        console.error('Failed to get telemetry update:', error);
      }
    }, 50);
  }
  
  onMount(async () => {
    await initializeRide();
    initializeUpdateInterval();
  });

  onDestroy(() => {
    if (updateInterval) {
      clearInterval(updateInterval);
      updateInterval = undefined;
    }
  });

  async function goToUpload() {
    try {
      // First stop the update interval but don't clear simulation yet
      if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = undefined;
      }

      // Try to upload first - this will use the existing simulation data
      const response = await invoke<string>('upload_ride');
      
      // Only after successful upload, stop the simulation
      await invoke('stop_simulation');
      
      // Show success and navigate home
      alert('Success: ' + response);
      goto('/');
      
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload ride: ' + error);
      
      // Restart updates if we failed
      if (!updateInterval) {
        initializeUpdateInterval();
      }
    }
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