<template>
  <div class="route-links-view">
    <h1>页面索引</h1>
    <ul class="route-list">
      <li v-for="route in availableRoutes" :key="route.path" class="route-item">
        <router-link :to="route.path">
          <span class="icon">{{ getIconForRoute(route) }}</span>
          {{ route.name || route.path }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import { routes } from '@/router/index';

export default {
  name: 'RouteLinksView',
  computed: {
    availableRoutes() {
      // Filter out redirect routes or any routes you don't want to show
      // Also filter out the RouteLinksView itself
      return routes.filter(route => (route.component || route.children) && route.name !== 'RouteLinks');
    }
  },
  methods: {
    getIconForRoute(route) {
      // Placeholder icons - can be extended with a meta field in routes
      // For now, cycle through a few simple icons
      const icons = ['📄', '🔗', '➡️', '⭐', '💡', '⚙️'];
      // Use a simple hash of the route path to pick an icon consistently
      let hash = 0;
      for (let i = 0; i < route.path.length; i++) {
        hash = (hash << 5) - hash + route.path.charCodeAt(i);
        hash |= 0; // Convert to 32bit integer
      }
      return icons[Math.abs(hash) % icons.length];
    }
  }
};
</script>

<style scoped>
.route-links-view {
  padding: 20px;
  font-family: sans-serif;
}
.route-list {
  list-style-type: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Two columns */
  gap: 15px; /* Space between items */
}
.route-item {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease-in-out;
}
.route-item:hover {
  transform: translateY(-3px);
}
a {
  text-decoration: none;
  color: #42b983;
  font-weight: bold;
  display: flex;
  align-items: center;
}
a:hover {
  color: #36a374;
}
.icon {
  margin-right: 10px;
  font-size: 1.2em;
}
</style>
