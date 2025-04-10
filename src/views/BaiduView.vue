<template>
  <div class="baidu-view">
    <h1>百度搜索（无头部版）</h1>
    <div class="search-box">
      <input 
        v-model="searchQuery" 
        @keyup.enter="performSearch" 
        placeholder="输入搜索内容..." 
        class="search-input"
      />
      <button @click="performSearch" class="search-button">搜索</button>
    </div>
    
    <div class="frame-wrapper">
      <BaiduFrame :query="activeQuery" />
    </div>
  </div>
</template>

<script>
import BaiduFrame from '@/components/BaiduFrame.vue'

export default {
  name: 'BaiduView',
  components: {
    BaiduFrame
  },
  data() {
    return {
      searchQuery: '',
      activeQuery: ''
    }
  },
  methods: {
    performSearch() {
      this.activeQuery = this.searchQuery
    }
  }
}
</script>

<style scoped>
.baidu-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

.search-box {
  display: flex;
  margin-bottom: 20px;
  justify-content: center;
}

.search-input {
  flex: 1;
  max-width: 500px;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 16px;
}

.search-button {
  padding: 10px 20px;
  background-color: #4e6ef2;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 16px;
}

.search-button:hover {
  background-color: #4662d9;
}

.frame-wrapper {
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
  height: calc(100vh - 150px);
}
</style>
