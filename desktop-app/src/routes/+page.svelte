<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import { goto } from '$app/navigation';

  async function startRide(type: 'chill' | 'hardcore') {
    try {
      await invoke('start_simulation', { rideType: type });
      goto('/dashboard');
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
  }
</script>

<main class="container">
  <img src="/sram-logo.png" alt="SRAM Logo" class="sram-logo" />
  <h1>Welcome to E-Bike Ride Tracker</h1>

  <div class="ride-options">
    <button class="ride-button" on:click={() => startRide('chill')}>
      <img src="/ebike-chill.jpg" alt="Chill Ride" />
      <span class="ride-label">Chill Ride</span>
    </button>
    <button class="ride-button" on:click={() => startRide('hardcore')}>
      <img src="/ebike-hardcore.jpg" alt="Hardcore Ride" />
      <span class="ride-label">Hardcore Ride</span>
    </button>
  </div>
</main>

<style>
  :root {
    font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
    font-size: 16px;
  }

  .container {
    margin: 0;
    padding-top: 10vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: center;
  }

  .sram-logo {
    width: 200px;
    margin: 0 auto 2rem;
  }

  h1 {
    margin-bottom: 2rem;
  }

  .ride-options {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    align-items: center;
    max-width: 500px;
    width: 100%;
    margin: 0 auto;
  }

  .ride-button {
    width: 100%;
    position: relative;
    border: none;
    padding: 0;
    cursor: pointer;
    border-radius: 15px;
    overflow: hidden;
    transition: transform 0.3s ease;
    aspect-ratio: 16/9;
  }

  .ride-button img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  .ride-button:hover {
    transform: translateY(-5px);
  }

  .ride-button:hover img {
    transform: scale(1.1);
  }

  .ride-label {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    font-size: 1.5rem;
    text-align: center;
  }

  @media (prefers-color-scheme: dark) {
    .ride-button {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
  }

  @media (max-width: 900px) {
    .ride-button {
      width: 100%;
      max-width: 400px;
    }
  }
</style>
