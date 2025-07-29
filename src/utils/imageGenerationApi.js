/**
 * Utility functions for image generation API.
 * 提供图像生成API的调用功能。
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
 * 文本到图像生成
 * 
 * @param {string} prompt - 图像生成的文本提示
 * @param {string} size - 图像尺寸 (默认: '1024x1024')
 * @param {number} guidance_scale - 引导比例 (可选)
 * @param {number} seed - 随机种子 (默认: -1)
 * @param {boolean} watermark - 是否添加水印 (默认: true)
 * @returns {Promise<Object>} API响应对象，包含 imageUrl (data URL格式) 和 processedData
 * @throws {Error} 如果API请求失败
 */
export async function generateImageFromText(prompt, size = '1024x1024', guidance_scale = null, seed = -1, watermark = true) {
  const apiUrl = 'http://staging-llm.search.miui.srv/agent-api/gen-image-t2i';

  try {
    const requestBody = {
      prompt: prompt,
      size: size,
      seed: seed,
      watermark: watermark
    };

    // 只有当 guidance_scale 有值时才添加到请求体中
    if (guidance_scale !== null && guidance_scale !== undefined) {
      requestBody.guidance_scale = guidance_scale;
    }

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
      const errorMessage = `文本到图像生成失败，状态码: ${response.status}: ${errorData.error || errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    const responseData = await response.json();
    
    // 处理返回的 base64 图像数据
    if (responseData.data && responseData.data.length > 0 && responseData.data[0].b64_json) {
      // 将 base64 数据转换为 data URL 格式
      const base64Data = responseData.data[0].b64_json;
      const imageDataUrl = `data:image/jpeg;base64,${base64Data}`;
      
      // 在返回数据中添加处理后的图像 URL
      responseData.imageUrl = imageDataUrl;
      responseData.processedData = {
        ...responseData,
        imageUrl: imageDataUrl,
        originalBase64: base64Data
      };
    }
    
    return responseData;
  } catch (error) {
    console.error('文本到图像生成错误:', error);
    throw error;
  }
}

/**
 * 图像到图像编辑
 * 
 * @param {string} prompt - 图像编辑的文本提示 (可选)
 * @param {File} imageFile - 输入的图像文件
 * @param {string} size - 图像尺寸 (默认: 'adaptive')
 * @param {number} guidance_scale - 引导比例 (可选)
 * @param {number} seed - 随机种子 (默认: -1)
 * @param {boolean} watermark - 是否添加水印 (默认: true)
 * @returns {Promise<Object>} API响应对象
 * @throws {Error} 如果API请求失败
 */
export async function generateImageFromImage(prompt = '', imageFile, size = 'adaptive', guidance_scale = null, seed = -1, watermark = true) {
  const apiUrl = 'http://staging-llm.search.miui.srv/agent-api/gen-image-i2i';

  try {
    if (!imageFile) {
      throw new Error('图像文件不能为空');
    }

    // 将图像文件转换为Data URL
    const imageUrl = await imageToDataUrl(imageFile);

    const requestBody = {
      image: imageUrl,
      size: size,
      seed: seed,
      watermark: watermark
    };

    // 只有当 prompt 有值时才添加到请求体中
    if (prompt && prompt.trim()) {
      requestBody.prompt = prompt;
    }

    // 只有当 guidance_scale 有值时才添加到请求体中
    if (guidance_scale !== null && guidance_scale !== undefined) {
      requestBody.guidance_scale = guidance_scale;
    }

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
      const errorMessage = `图像到图像编辑失败，状态码: ${response.status}: ${errorData.error || errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    const responseData = await response.json();
    return responseData;
  } catch (error) {
    console.error('图像到图像编辑错误:', error);
    throw error;
  }
}
