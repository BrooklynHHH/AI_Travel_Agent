/**
 * Utility functions for Qianfan video generation API.
 * 提供千帆视频生成API的调用和任务状态查询功能。
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
 * 文本生成视频 - 千帆接口
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {string} model - 模型名称，如 "MT-Director"
 * @param {string} duration - 视频时长，如 "5"
 * @param {string} aspect_ratio - 宽高比，如 "16:9"
 * @param {string} mode - 生成模式，如 "std"
 * @returns {Promise<Object>} API响应对象
 */
export async function generateVideoFromText(prompt, model = "MT-Director", duration = "5", aspect_ratio = "16:9", mode = "std") {
  const apiUrl = 'http://staging-llm.search.miui.srv/agent-api/qianfan-video/text2video';

  try {
    const requestBody = {
      prompt,
      model,
      duration,
      aspect_ratio,
      mode
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
      const errorMessage = `文本生成视频失败，状态码: ${response.status}: ${errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('文本生成视频时出错:', error);
    throw error;
  }
}

/**
 * 图片生成视频 - 千帆接口
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {File|string} image - 图片文件对象或base64字符串或URL
 * @param {string} model - 模型名称，如 "MI-Director"
 * @param {string} duration - 视频时长，如 "5"
 * @returns {Promise<Object>} API响应对象
 */
export async function generateVideoFromImage(prompt, image, model = "MI-Director", duration = "5") {
  const apiUrl = 'http://staging-llm.search.miui.srv/agent-api/qianfan-video/img2video';

  try {
    let imageData;
    
    // 处理不同类型的图片输入
    if (image instanceof File) {
      // 如果是File对象，转换为base64
      imageData = await imageToDataUrl(image);
    } else if (typeof image === 'string') {
      // 如果是字符串，直接使用（可能是base64或URL）
      imageData = image;
    } else {
      throw new Error('图片参数必须是File对象或字符串');
    }

    const requestBody = {
      prompt,
      image: imageData,
      model,
      duration
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
      const errorMessage = `图片生成视频失败，状态码: ${response.status}: ${errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('图片生成视频时出错:', error);
    throw error;
  }
}

/**
 * 查询视频生成任务状态 - 千帆接口
 * 
 * @param {string} taskId - 任务ID
 * @param {string} model - 模型名称，如 "MT-Director"
 * @returns {Promise<Object>} 任务状态信息
 */
export async function checkQianfanVideoStatus(taskId, model = "MT-Director") {
  if (!taskId) {
    throw new Error('任务ID不能为空');
  }

  const apiUrl = `http://staging-llm.search.miui.srv/agent-api/qianfan-video/query?task_id=${encodeURIComponent(taskId)}&model=${encodeURIComponent(model)}`;

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
      const errorMessage = `任务状态查询失败，状态码: ${response.status}: ${errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('查询千帆视频任务状态时出错:', error);
    throw error;
  }
}

/**
 * 轮询视频生成任务状态直到完成
 * 
 * @param {string} taskId - 任务ID
 * @param {string} model - 模型名称，如 "MT-Director"
 * @param {number} interval - 轮询间隔时间（毫秒），默认5秒
 * @param {number} maxAttempts - 最大轮询次数，默认120次（10分钟）
 * @param {Function} onProgress - 进度回调函数，接收状态信息作为参数
 * @returns {Promise<Object>} 最终的任务状态信息
 */
export async function pollQianfanVideoStatus(taskId, model = "MT-Director", interval = 5000, maxAttempts = 120, onProgress = null) {
  if (!taskId) {
    throw new Error('任务ID不能为空');
  }

  let attempts = 0;
  
  while (attempts < maxAttempts) {
    try {
      const statusResult = await checkQianfanVideoStatus(taskId, model);
      
      // 调用进度回调
      if (onProgress && typeof onProgress === 'function') {
        onProgress(statusResult);
      }
      
      // 检查任务状态
      if (statusResult.code === 0 && statusResult.data) {
        const taskStatus = statusResult.data.task_status;
        
        // 任务完成
        if (taskStatus === 'success' || taskStatus === 'completed') {
          console.log('视频生成任务完成:', statusResult);
          return statusResult;
        }
        
        // 任务失败
        if (taskStatus === 'failed' || taskStatus === 'error') {
          const errorMessage = `视频生成任务失败: ${statusResult.data.error_message || '未知错误'}`;
          console.error(errorMessage, statusResult);
          throw new Error(errorMessage);
        }
        
        // 任务仍在进行中，继续轮询
        console.log(`任务状态: ${taskStatus}, 继续轮询... (${attempts + 1}/${maxAttempts})`);
      }
      
      attempts++;
      
      // 如果不是最后一次尝试，等待指定间隔
      if (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, interval));
      }
      
    } catch (error) {
      console.error(`轮询第${attempts + 1}次失败:`, error);
      attempts++;
      
      // 如果不是最后一次尝试，等待指定间隔后重试
      if (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, interval));
      } else {
        throw error;
      }
    }
  }
  
  throw new Error(`轮询超时: 在${maxAttempts}次尝试后任务仍未完成`);
}

/**
 * 文本生成视频并轮询状态直到完成
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {string} model - 模型名称，如 "MT-Director"
 * @param {string} duration - 视频时长，如 "5"
 * @param {string} aspect_ratio - 宽高比，如 "16:9"
 * @param {string} mode - 生成模式，如 "std"
 * @param {Function} onProgress - 进度回调函数，接收状态信息作为参数
 * @returns {Promise<Object>} 最终的任务状态信息
 */
export async function generateVideoFromTextWithPolling(prompt, model = "MT-Director", duration = "5", aspect_ratio = "16:9", mode = "std", onProgress = null) {
  try {
    // 1. 发起视频生成请求
    const generateResult = await generateVideoFromText(prompt, model, duration, aspect_ratio, mode);
    
    // 2. 检查返回结果并提取task_id
    if (generateResult.code !== 0 || !generateResult.data || !generateResult.data.task_id) {
      throw new Error(`视频生成请求失败: ${generateResult.message || '未知错误'}`);
    }
    
    const taskId = generateResult.data.task_id;
    console.log(`视频生成任务已提交，任务ID: ${taskId}`);
    
    // 3. 开始轮询任务状态
    return await pollQianfanVideoStatus(taskId, model, 5000, 120, onProgress);
    
  } catch (error) {
    console.error('文本生成视频并轮询状态时出错:', error);
    throw error;
  }
}

/**
 * 图片生成视频并轮询状态直到完成
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {File|string} image - 图片文件对象或base64字符串或URL
 * @param {string} model - 模型名称，如 "MI-Director"
 * @param {string} duration - 视频时长，如 "5"
 * @param {Function} onProgress - 进度回调函数，接收状态信息作为参数
 * @returns {Promise<Object>} 最终的任务状态信息
 */
export async function generateVideoFromImageWithPolling(prompt, image, model = "MI-Director", duration = "5", onProgress = null) {
  try {
    // 1. 发起视频生成请求
    const generateResult = await generateVideoFromImage(prompt, image, model, duration);
    
    // 2. 检查返回结果并提取task_id
    if (generateResult.code !== 0 || !generateResult.data || !generateResult.data.task_id) {
      throw new Error(`视频生成请求失败: ${generateResult.message || '未知错误'}`);
    }
    
    const taskId = generateResult.data.task_id;
    console.log(`视频生成任务已提交，任务ID: ${taskId}`);
    
    // 3. 开始轮询任务状态
    return await pollQianfanVideoStatus(taskId, model, 5000, 120, onProgress);
    
  } catch (error) {
    console.error('图片生成视频并轮询状态时出错:', error);
    throw error;
  }
}

/**
 * 首尾帧生成视频 - 千帆接口
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {File|string} startImage - 首帧图片文件对象或base64字符串或URL（必需）
 * @param {File|string|null} endImage - 尾帧图片文件对象或base64字符串或URL（可选）
 * @param {string} model - 模型名称，如 "VQ1"
 * @param {string} duration - 视频时长，如 "5"
 * @returns {Promise<Object>} API响应对象
 */
export async function generateVideoFromStartEnd(prompt, startImage, endImage = null, model = "VQ1", duration = "5") {
  const apiUrl = 'http://staging-llm.search.miui.srv/agent-api/qianfan-video/start-end2video';

  try {
    let startImageData, endImageData;
    
    // 处理首帧图片（必需）
    if (startImage instanceof File) {
      startImageData = await imageToDataUrl(startImage);
    } else if (typeof startImage === 'string') {
      startImageData = startImage;
    } else {
      throw new Error('首帧图片参数必须是File对象或字符串');
    }

    // 构建图片数组，首帧图片是必需的
    const images = [startImageData];

    // 处理尾帧图片（可选）
    if (endImage) {
      if (endImage instanceof File) {
        endImageData = await imageToDataUrl(endImage);
      } else if (typeof endImage === 'string') {
        endImageData = endImage;
      } else {
        throw new Error('尾帧图片参数必须是File对象或字符串');
      }
      images.push(endImageData);
    }

    const requestBody = {
      prompt,
      images: images,
      model,
      duration
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
      const errorMessage = `首尾帧生成视频失败，状态码: ${response.status}: ${errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('首尾帧生成视频时出错:', error);
    throw error;
  }
}

/**
 * 首尾帧生成视频并轮询状态直到完成
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {File|string} startImage - 首帧图片文件对象或base64字符串或URL
 * @param {File|string} endImage - 尾帧图片文件对象或base64字符串或URL
 * @param {string} model - 模型名称，如 "VQ1"
 * @param {string} duration - 视频时长，如 "5"
 * @param {Function} onProgress - 进度回调函数，接收状态信息作为参数
 * @returns {Promise<Object>} 最终的任务状态信息
 */
export async function generateVideoFromStartEndWithPolling(prompt, startImage, endImage, model = "VQ1", duration = "5", onProgress = null) {
  try {
    // 1. 发起视频生成请求
    const generateResult = await generateVideoFromStartEnd(prompt, startImage, endImage, model, duration);
    
    // 2. 检查返回结果并提取task_id
    if (generateResult.code !== 0 || !generateResult.data || !generateResult.data.task_id) {
      throw new Error(`视频生成请求失败: ${generateResult.message || '未知错误'}`);
    }
    
    const taskId = generateResult.data.task_id;
    console.log(`首尾帧视频生成任务已提交，任务ID: ${taskId}`);
    
    // 3. 开始轮询任务状态
    return await pollQianfanVideoStatus(taskId, model, 5000, 120, onProgress);
    
  } catch (error) {
    console.error('首尾帧生成视频并轮询状态时出错:', error);
    throw error;
  }
}

/**
 * 多图参考生成视频 - 千帆接口
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {Array<File|string>} images - 参考图片数组，最多4张图片
 * @param {string} model - 模型名称，如 "V2.0"
 * @param {Object} options - 其他可选参数
 * @returns {Promise<Object>} API响应对象
 */
export async function generateVideoFromMultiImages(prompt, images, model = "V2.0", options = {}) {
  const apiUrl = 'http://staging-llm.search.miui.srv/agent-api/qianfan-video/multi-img2video';

  try {
    if (!Array.isArray(images) || images.length === 0) {
      throw new Error('参考图片数组不能为空');
    }

    if (images.length > 4) {
      throw new Error('参考图片最多支持4张');
    }

    const imageDataArray = [];
    
    // 处理每张图片
    for (let i = 0; i < images.length; i++) {
      const image = images[i];
      let imageData;
      
      if (image instanceof File) {
        imageData = await imageToDataUrl(image);
      } else if (typeof image === 'string') {
        imageData = image;
      } else {
        throw new Error(`第${i + 1}张图片参数必须是File对象或字符串`);
      }
      
      imageDataArray.push(imageData);
    }

    const requestBody = {
      prompt,
      image_list: imageDataArray,
      model,
      ...options
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
      const errorMessage = `多图参考生成视频失败，状态码: ${response.status}: ${errorData.message || '未知错误'}`;
      console.error('API错误数据:', errorData);
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('多图参考生成视频时出错:', error);
    throw error;
  }
}

/**
 * 多图参考生成视频并轮询状态直到完成
 * 
 * @param {string} prompt - 视频生成提示词
 * @param {Array<File|string>} images - 参考图片数组，最多4张图片
 * @param {string} model - 模型名称，如 "V2.0"
 * @param {Object} options - 其他可选参数
 * @param {Function} onProgress - 进度回调函数，接收状态信息作为参数
 * @returns {Promise<Object>} 最终的任务状态信息
 */
export async function generateVideoFromMultiImagesWithPolling(prompt, images, model = "V2.0", options = {}, onProgress = null) {
  try {
    // 1. 发起视频生成请求
    const generateResult = await generateVideoFromMultiImages(prompt, images, model, options);
    
    // 2. 检查返回结果并提取task_id或id
    let taskId;
    if (generateResult.task_id) {
      taskId = generateResult.task_id;
    } else if (generateResult.id) {
      taskId = generateResult.id;
    } else if (generateResult.data && (generateResult.data.task_id || generateResult.data.id)) {
      taskId = generateResult.data.task_id || generateResult.data.id;
    } else {
      throw new Error(`视频生成请求失败: ${generateResult.error || generateResult.message || '未知错误'}`);
    }
    
    console.log(`多图参考视频生成任务已提交，任务ID: ${taskId}`);
    
    // 3. 开始轮询任务状态，使用统一的checkQianfanVideoStatus函数
    return await pollQianfanVideoStatus(taskId, model, 5000, 120, onProgress);
    
  } catch (error) {
    console.error('多图参考生成视频并轮询状态时出错:', error);
    throw error;
  }
}
