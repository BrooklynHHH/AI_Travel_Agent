import axios from 'axios'

const BASE_URL = 'http://staging-llm.search.miui.srv/agent-pic-translate';

export async function translateImage(provider, file, to, from = 'auto') {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('to', to);
    formData.append('from', from);

    try {
        const res = await axios.post(`${BASE_URL}/${provider}`, formData, {
            headers: {'Content-Type': 'multipart/form-data'}
        })
        console.log(`${provider}服务调用成功`);
        return res.data;
    }catch (error) {
        console.error(`${provider} 服务调用失败`, error);
        throw error;
    }
}

