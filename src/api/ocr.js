import axios from 'axios'

const BASE_URL = 'http://staging-llm.search.miui.srv/agent-ai-tools';
//const DEV_URL = 'http://localhost:8080/agent-ai-tools'
const USE_URL = BASE_URL;

// 创建一个带有计时功能的请求函数
const timedRequest = async (url, data, config = {}) => {
    const startTime = Date.now()

    try {
        const response = await axios.post(url, data, config)
        const endTime = Date.now()

        return {
            data: response.data,
            time: endTime - startTime
        }
    } catch (error) {
        const endTime = Date.now()
        error.time = endTime - startTime
        throw error
    }
}

// 豆包视觉OCR接口
export const callDoubaoVisionOcr = (formData) => {
    return timedRequest(USE_URL+'/ocr/doubao-vision', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 阿里云OCR接口
export const callAliyunOcr = (formData) => {
    return timedRequest(USE_URL+'/ocr/aliyun-ocr', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 百度OCR接口
export const callBaiduOcr = (formData) => {
    return timedRequest(USE_URL+'/ocr/baidu-ocr', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// RapidOCR接口
export const callRapidOcr = (formData) => {
    return timedRequest(USE_URL+'/ocr/rapid-ocr', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 腾讯云OCR接口
export const callTencentOcr = (formData) => {
    return timedRequest(USE_URL+'/ocr/tencent-ocr', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 火山OCR接口
export const callVolcOcr = (formData) => {
    return timedRequest(USE_URL+'/ocr/volc-ocr', formData, {
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}
