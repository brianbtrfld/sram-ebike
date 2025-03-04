<script>
  import { invoke } from "@tauri-apps/api/core";
  import { goto } from '$app/navigation';

  let name = $state("");
  let greetMsg = $state("");
  let uploadResponse = $state("");
  let rideInfo = $state({ name: "", waypoints: 0 });
  /** @type {Array<{name: string}>} */
  let items = $state([]);

  /**
   * @param {Event} event - The submit event
   */
  async function greet(event) {
    // Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
    greetMsg = await invoke("greet", { name });
  }

  async function fetchItems() {
    try {
      // Get items from the API - now returns parsed JSON directly
      const response = await invoke("get_items");
      items = response.items || [];
      console.log("Fetched items:", items);
      return response;
    } catch (error) {
      console.error("Error fetching items:", error);
      return { items: [] };
    }
  }

  async function uploadName() {
    try {
      // Call our Rust command instead of using fetch directly
      const response = await invoke("upload_name", { name });
      uploadResponse = `Upload success! Server responded with: ${response}`;

      // After successful upload, fetch the updated list of items
      await fetchItems();
    } catch (error) {
      uploadResponse = `Error: ${error}`;
    }
  }

  async function readRideChill() {
    try {
      const data = await invoke("read_ride_chill");
      rideInfo = {
        name: data.name || "No name",
        waypoints: data.waypoints?.length || 0
      };
    } catch (error) {
      console.error("Error reading ride file:", error);
      rideInfo = { name: "", waypoints: 0 };
    }
  }

  async function startRide(type) {
    try {
      await invoke('start_simulation', { rideType: type });
      goto('/dashboard');
    } catch (error) {
      console.error('Failed to start simulation:', error);
    }
  }

  // Fetch items on initial load
  fetchItems();
</script>

<main>
  <div class="logo-container">
    <img src="/sram-logo.png" alt="SRAM Logo" class="sram-logo" />
  </div>

  <h1>Choose Your Ride</h1>

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
  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    min-height: 100vh;
    background: #1a1a1a;
    color: white;
  }

  .logo-container {
    margin-bottom: 2rem;
  }

  .sram-logo {
    max-width: 300px;
    height: auto;
  }

  h1 {
    font-size: 2.5rem;
    margin-bottom: 3rem;
    text-align: center;
    color: #fff;
  }

  .ride-options {
    display: flex;
    gap: 2rem;
    justify-content: center;
    flex-wrap: wrap;
    max-width: 1200px;
    width: 100%;
  }

  .ride-button {
    position: relative;
    border: none;
    padding: 0;
    cursor: pointer;
    border-radius: 15px;
    overflow: hidden;
    transition: transform 0.3s ease;
    width: 400px;
    background: transparent;
  }

  .ride-button:hover {
    transform: scale(1.02);
  }

  .ride-button img {
    width: 100%;
    height: 300px;
    object-fit: cover;
    border-radius: 15px;
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
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
  }

  @media (max-width: 900px) {
    .ride-button {
      width: 100%;
      max-width: 400px;
    }
  }
</style>
