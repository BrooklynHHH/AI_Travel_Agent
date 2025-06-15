/**
 * Utility functions for video generation API.
 * 提供视频生成API的调用和任务状态查询功能。
 */

/**
 * Converts a File object to a Base64 Data URL.
 * This function is intended for browser environments.
 * @param {File} file - The image file.
 * @returns {Promise<string>} A promise that resolves with the Data URL.
 */
function imageToDataUrl(file) {
  return new Promise((resolve, reject) => {
    if (!(file instanceof File)) {
      return reject(new TypeError('Expected a File object.'));
    }
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}

/**
 * Generates a video based on text and an image using the local video generation API.
 *
 * @param {string} text - The main text prompt for video generation.
 * @param {string} resolution - The desired video resolution (e.g., "1080p").
 * @param {number} duration - The desired video duration in seconds (e.g., 5).
 * @param {boolean} cameraFixed - Whether the camera should be fixed.
 * @param {File} imageFile - The image file to be used in the video. (Must be a File object from a file input or similar)
 * @returns {Promise<Object>} A promise that resolves with the API response JSON.
 * @throws {Error} If the API request fails or if image conversion fails.
 */
export async function generateVideo(text, resolution, duration, cameraFixed, imageFile) {
  const apiUrl = 'http://localhost:5001/ge-video';

  try {
    const imageUrl = await imageToDataUrl(imageFile);

    // 构建请求体，按照新的格式
    const requestBody = {
      text: text,
      resolution: resolution,
      duration: String(duration), // 转换为字符串
      camerafixed: String(cameraFixed).toLowerCase(), // 转换为小写的字符串
      image_base64: imageUrl // 直接使用 Data URL
    };

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: response.statusText, status: response.status };
      }
      // Construct a more informative error message
      const errorMessage = `API request failed with status ${response.status}: ${errorData.message || 'Unknown error'}`;
      console.error('API Error Data:', errorData);
      throw new Error(errorMessage);
    }

    const responseData = await response.json();
    return responseData;
  } catch (error) {
    console.error('Error in generateVideo function:', error);
    // Re-throw the error so it can be caught by the caller
    throw error;
  }
}

/**
 * 查询视频生成任务的状态
 * 
 * @param {string} taskId - 任务ID，从generateVideo返回的响应中获取
 * @returns {Promise<Object>} 包含任务状态信息的对象
 * @throws {Error} 如果API请求失败
 */
export async function checkVideoGenerationStatus(taskId) {
  if (!taskId) {
    throw new Error('任务ID不能为空');
  }

  const apiUrl = `http://localhost:5001/gen_task?task_id=${encodeURIComponent(taskId)}`;

  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: response.statusText, status: response.status };
      }
      // 构建更详细的错误信息
      const errorMessage = `任务状态查询失败，状态码: ${response.status}: ${errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('查询任务状态时出错:', error);
    // 重新抛出错误，以便调用者可以捕获
    throw error;
  }
}

// Example usage (for testing in a browser console, assuming you have an image file object):
/*
async function testGenerateVideo() {
  const textPrompt = "无人机以极快速度穿越复杂障碍或自然奇观，带来沉浸式飞行体验";
  const res = "1080p";
  const dur = 5;
  const camFixed = false;
  
  // Create a dummy file input for testing
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'image/*';
  document.body.appendChild(input);
  
  input.onchange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        console.log("Attempting to generate video with file:", file.name);
        const result = await generateVideo(textPrompt, res, dur, camFixed, file);
        console.log("API Response:", result);
        alert("Video generation task started. Check console for API response.");
      } catch (error) {
        console.error("Failed to generate video:", error);
        alert("Failed to start video generation: " + error.message);
      } finally {
        document.body.removeChild(input); // Clean up
      }
    }
  };
  input.click(); // Open file dialog
}

// To test, you could open your browser's developer console on a page where this script is loaded
// and then call: testGenerateVideo();
// You would then select an image file.
*/
