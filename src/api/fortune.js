import axios from 'axios';

// 统一 API 根地址（如需切换本地/线上，改这里即可）
const API_BASE = 'http://10.167.107.156:3001';

// 命理分析
export function fortune(data) {
  return axios.post(`${API_BASE}/api/fortune`, data);
}

// 大师群聊
export function mastersChat(data) {
  return axios.post(`${API_BASE}/api/masters-chat`, data);
}

// 健康检查
export function health() {
  return axios.get(`${API_BASE}/agent-fortune/health`);
} 