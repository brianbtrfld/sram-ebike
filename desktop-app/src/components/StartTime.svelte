<script lang="ts">
    export let rideStartTime: string;
  </script>
  
  <div class="start-time">
    <p class="value date-time">
      <span class="date">{new Date(rideStartTime).toLocaleDateString()}</span>
      <span class="time">{new Date(rideStartTime).toLocaleTimeString()}</span>
    </p>
  </div>
  
  <style>
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
  </style>