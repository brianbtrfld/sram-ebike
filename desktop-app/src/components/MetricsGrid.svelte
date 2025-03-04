<script lang="ts">
  export let telemetryData: {
    avg_speed_mph: number;
    battery_percentage: number;
    distance_miles: number;
  };
</script>

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
      <p class="battery-text">{Math.round(telemetryData.battery_percentage)}%</p>
    </div>
  </div>

  <div class="metric">
    <h3>Distance</h3>
    <p class="value">{telemetryData.distance_miles.toFixed(2)} <span class="unit">mi</span></p>
  </div>
</div>

<style>
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
</style>