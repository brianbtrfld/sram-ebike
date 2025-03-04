<script lang="ts">
    export let waypoints: {
      timestamp: string;
      lat: number;
      lon: number;
      elevation_ft: number;
    }[];
  </script>
  
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
  
  <style>
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
  </style>