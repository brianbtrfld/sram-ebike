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

  <div class="ride-buttons">
    <button class="ride-button chill" on:click={() => startRide('chill')}>
      <img src="/ebike-chill.jpg" alt="Chill E-Bike" />
      <div class="button-content">
        <h2>Chill Ride</h2>
        <p>Track your daily chill rides</p>
      </div>
    </button>
    <button class="ride-button hardcore" on:click={() => startRide('hardcore')}>
      <img src="/ebike-hardcore.jpg" alt="Hardcore E-Bike" />
      <div class="button-content">
        <h2>Hardcore Ride</h2>
        <p>Track your hardcore adventures</p>
      </div>
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

  .ride-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    max-width: 1000px;
    margin: 0 auto;
    padding: 1rem;
  }

  .ride-button {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    padding: 0;
    border-radius: 12px;
    color: #fff;
    text-decoration: none;
    transition: transform 0.2s;
    overflow: hidden;
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

  .button-content {
    position: relative;
    width: 100%;
    padding: 1.5rem;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
    z-index: 1;
  }

  .ride-button h2 {
    margin: 0;
    font-size: 1.5rem;
  }

  .ride-button p {
    margin: 0.5rem 0 0;
    opacity: 0.9;
  }

  @media (prefers-color-scheme: dark) {
    .ride-button {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
  }
</style>
