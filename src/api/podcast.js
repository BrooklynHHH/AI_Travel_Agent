import axios from 'axios'

const API_BASE_URL = 'http://staging-llm.search.miui.srv' // 本地服務器地址

export const generatePodcast = async (text, type) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/generate-podcast`, {
      text,
      type
    });

    if (response.data.success) {
      // 檢查返回的 podcast_type 是否與請求的類型匹配
      if (response.data.podcast_type !== type) {
        throw new Error(`音頻類型不匹配：期望 ${type}，但收到 ${response.data.podcast_type}`);
      }
      // 構建完整的音頻文件 URL
      return {
        success: true,
        audioUrl: `${API_BASE_URL}/audio/${response.data.audio_file}`,
        podcastType: response.data.podcast_type
      };
    } else {
      throw new Error(response.data.error || '生成播客失敗');
    }
  } catch (error) {
    console.error('生成播客時發生錯誤:', error);
    throw error;
  }
}; 