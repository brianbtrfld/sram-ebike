<script lang="ts">
    export let rideName: string;
    export let goToUpload: () => void;
</script>
  
<div class="header">
    <h1 class="ride-title">{rideName}</h1>
    <button class="upload-button" on:click={goToUpload}>Upload</button>
</div>
  
<style>
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      max-width: 1000px;
      margin-bottom: 2rem;
    }
  
    .upload-button {
      background: #e31837;
      color: white;
      border: none;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.3s ease;
    }
  
    .upload-button:hover {
      background: #c41430;
    }
  
    .ride-title {
      font-size: 2rem;
      color: #333;
      margin: 0;
    }
</style>