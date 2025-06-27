<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
  background-color: #f5f7fa;
  overflow: hidden;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

#app {
  margin: 0 auto;
  position: relative;
}

/* Responsive styles */
@media (min-width: 480px) {
  body {
    background-color: #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  
  #app {
    height: 100vh;
    max-height: 800px;
    position: relative;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
}
</style>
