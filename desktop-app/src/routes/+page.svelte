<script>
  import { invoke } from "@tauri-apps/api/core";

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

  // Fetch items on initial load
  fetchItems();
</script>

<main class="container">
  <h1>Welcome to Tauri + Svelte</h1>

  <div class="row">
    <a href="https://vitejs.dev" target="_blank">
      <img src="/vite.svg" class="logo vite" alt="Vite Logo" />
    </a>
    <a href="https://tauri.app" target="_blank">
      <img src="/tauri.svg" class="logo tauri" alt="Tauri Logo" />
    </a>
    <a href="https://kit.svelte.dev" target="_blank">
      <img src="/svelte.svg" class="logo svelte-kit" alt="SvelteKit Logo" />
    </a>
  </div>
  <p>Click on the Tauri, Vite, and SvelteKit logos to learn more.</p>

  <!-- Ride Info Section -->
  <div class="section">
    <h2>Ride Information</h2>
    <button onclick={readRideChill}>Load Ride Info</button>
    {#if rideInfo.name}
      <div class="info-box">
        <p>Ride Name: <strong>{rideInfo.name}</strong></p>
        <p>Number of Waypoints: <strong>{rideInfo.waypoints}</strong></p>
      </div>
    {/if}
  </div>

  <!-- Original form section -->
  <div class="section">
    <form class="row" onsubmit={e => { e.preventDefault(); greet(e); }}>
      <input id="greet-input" placeholder="Enter a name..." bind:value={name} />
      <button type="submit">Greet</button>
    </form>
    <p>{greetMsg}</p>

    <div class="row" style="margin-top: 20px;">
      <button onclick={uploadName}>Upload Name to API</button>
    </div>
    <p>{uploadResponse}</p>
  </div>

  <!-- Display items from the API -->
  <div class="section">
    <h2>Items from API</h2>
    {#if items.length === 0}
      <p>No items available</p>
    {:else}
      <ul style="list-style-type: none; padding: 0;">
        {#each items as item}
          <li style="margin: 5px 0;">{item.name}</li>
        {/each}
      </ul>
    {/if}
  </div>
</main>

<style>
.logo.vite:hover {
  filter: drop-shadow(0 0 2em #747bff);
}

.logo.svelte-kit:hover {
  filter: drop-shadow(0 0 2em #ff3e00);
}

:root {
  font-family: Inter, Avenir, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 24px;
  font-weight: 400;

  color: #0f0f0f;
  background-color: #f6f6f6;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

.container {
  margin: 0;
  padding-top: 10vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: 0.75s;
}

.logo.tauri:hover {
  filter: drop-shadow(0 0 2em #24c8db);
}

.row {
  display: flex;
  justify-content: center;
}

a {
  font-weight: 500;
  color: #646cff;
  text-decoration: inherit;
}

a:hover {
  color: #535bf2;
}

h1 {
  text-align: center;
}

input,
button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  color: #0f0f0f;
  background-color: #ffffff;
  transition: border-color 0.25s;
  box-shadow: 0 2px 2px rgba(0, 0, 0, 0.2);
}

button {
  cursor: pointer;
}

button:hover {
  border-color: #396cd8;
}
button:active {
  border-color: #396cd8;
  background-color: #e8e8e8;
}

input,
button {
  outline: none;
}

#greet-input {
  margin-right: 5px;
}

@media (prefers-color-scheme: dark) {
  :root {
    color: #f6f6f6;
    background-color: #2f2f2f;
  }

  a:hover {
    color: #24c8db;
  }

  input,
  button {
    color: #ffffff;
    background-color: #0f0f0f98;
  }
  button:active {
    background-color: #0f0f0f69;
  }
}

.section {
  margin: 2rem 0;
  padding: 1rem;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.05);
}

.info-box {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background-color: rgba(36, 200, 219, 0.1);
}

.info-box p {
  margin: 0.5rem 0;
}

h2 {
  margin-bottom: 1rem;
  font-size: 1.5rem;
}
</style>
