// fortuneUtils.js

/**
 * 提取章節內容
 * @param {string} text - The full text to search within.
 * @param {string} marker - The marker to find, e.g., 'xingzuo-zongjie'.
 * @param {object} resultObj - The object to save the extracted content to.
 * @param {string} field - The field in resultObj to save the content to.
 */
function extractSection(text, marker, resultObj, field) {
  const possibleMarkers = [
    `【${marker}】`,
    `[${marker}]`,
    `<${marker}>`,
    `${marker}:`,
    marker
  ];
  let found = false;
  for (const startMarker of possibleMarkers) {
    const startIndex = text.indexOf(startMarker);
    if (startIndex !== -1) {
      const contentStart = startIndex + startMarker.length;
      let contentEnd = text.length;
      const possibleEndMarkers = ['【', '[', '<', '\n\n', '\n#'];
      for (const endMarker of possibleEndMarkers) {
        const nextMarkerIndex = text.indexOf(endMarker, contentStart);
        if (nextMarkerIndex !== -1 && nextMarkerIndex < contentEnd) {
          contentEnd = nextMarkerIndex;
        }
      }
      const content = text.substring(contentStart, contentEnd).trim();
      if (content) { // Only assign if content is not empty
        resultObj[field] = content;
      }
      found = true;
      break;
    }
  }
  if (!found && field === 'fenxi' && marker.includes('fenxi')) {
    const baseMarker = marker.replace('-fenxi', '').replace('_fenxi', '');
    const zongjieMarkers = [
      `【${baseMarker}-zongjie】`,
      `[${baseMarker}-zongjie]`,
      `<${baseMarker}-zongjie>`,
      `【${baseMarker}_zongjie】`,
      `[${baseMarker}_zongjie]`,
      `<${baseMarker}_zongjie>`,
      `【${baseMarker}】`,
      `[${baseMarker}]`,
      `<${baseMarker}>`
    ];
    for (const zongjieMarker of zongjieMarkers) {
      const zongjieIndex = text.indexOf(zongjieMarker);
      if (zongjieIndex !== -1) {
        const zongjieContentStart = zongjieIndex + zongjieMarker.length;
        const zongjieContent = resultObj['zongjie'] || '';
        const contentAfterZongjie = text.substring(zongjieContentStart + zongjieContent.length).trim();
        if (contentAfterZongjie.length > 0) {
          resultObj[field] = contentAfterZongjie;
          return;
        }
      }
    }
  }
}

/**
 * 從API結果中提取標記內容
 * @param {string} text - The full text from the API.
 * @param {object} results - The results object to populate.
 */
export function extractMarkedContent(text, results) {
  extractSection(text, 'xingzuo-zongjie', results.xingzuo, 'zongjie');
  extractSection(text, 'xingzuo-fenxi', results.xingzuo, 'fenxi');
  if (!results.xingzuo.zongjie) {
    extractSection(text, 'xingzuo_zongjie', results.xingzuo, 'zongjie');
    extractSection(text, 'xingzuo', results.xingzuo, 'zongjie');
  }
  if (!results.xingzuo.fenxi) {
    extractSection(text, 'xingzuo_fenxi', results.xingzuo, 'fenxi');
  }
  extractSection(text, 'bazi-zongjie', results.bazi, 'zongjie');
  extractSection(text, 'bazi-fenxi', results.bazi, 'fenxi');
  if (!results.bazi.zongjie) {
    extractSection(text, 'bazi_zongjie', results.bazi, 'zongjie');
    extractSection(text, 'bazi', results.bazi, 'zongjie');
  }
  if (!results.bazi.fenxi) {
    extractSection(text, 'bazi_fenxi', results.bazi, 'fenxi');
  }
  extractSection(text, 'xingpan-zongjie', results.xingpan, 'zongjie');
  extractSection(text, 'xingpan-fenxi', results.xingpan, 'fenxi');
  if (!results.xingpan.zongjie) {
    extractSection(text, 'xingpan_zongjie', results.xingpan, 'zongjie');
    extractSection(text, 'xingpan', results.xingpan, 'zongjie');
  }
  if (!results.xingpan.fenxi) {
    extractSection(text, 'xingpan_fenxi', results.xingpan, 'fenxi');
  }
}

/**
 * 從文本中提取 JSON 字符串
 * @param {string} text - 包含 JSON 的文本
 * @returns {string|null} - 提取的 JSON 字符串或 null
 */
function extractJSON(text) {
  if (!text || typeof text !== 'string') {
    return null;
  }

  // 嘗試找到 JSON 對象的開始和結束
  const jsonStart = text.indexOf('{');
  const jsonEnd = text.lastIndexOf('}');

  if (jsonStart === -1 || jsonEnd === -1 || jsonStart >= jsonEnd) {
    return null;
  }

  const jsonString = text.substring(jsonStart, jsonEnd + 1);

  try {
    // 驗證 JSON 是否有效
    JSON.parse(jsonString);
    return jsonString;
  } catch (error) {
    // 如果解析失敗，嘗試清理後再解析
    const cleanedJson = cleanDuplicateFields(jsonString);
    try {
      JSON.parse(cleanedJson);
      return cleanedJson;
    } catch (secondError) {
      console.error('Failed to parse JSON after cleaning:', secondError);
      return null;
    }
  }
}

/**
 * 遞歸清理對象中的重複字段
 * @param {object} obj - 要清理的對象
 * @returns {object} - 清理後的對象
 */
function cleanObject(obj) {
  if (typeof obj !== 'object' || obj === null) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(cleanObject);
  }

  const cleaned = {};
  const seen = new Set();

  for (const [key, value] of Object.entries(obj)) {
    if (!seen.has(key)) {
      seen.add(key);
      cleaned[key] = cleanObject(value);
    }
  }

  return cleaned;
}

/**
 * 清理 JSON 字符串中的重複字段
 * @param {string} jsonStr - JSON 字符串
 * @returns {string} - 清理後的 JSON 字符串
 */
function cleanDuplicateFields(jsonStr) {
  if (!jsonStr || typeof jsonStr !== 'string') {
    return jsonStr;
  }

  try {
    const obj = JSON.parse(jsonStr);
    return JSON.stringify(cleanObject(obj));
  } catch (error) {
    console.error('Error cleaning JSON:', error);
    return jsonStr;
  }
}

/**
 * 安全地解析 JSON 字符串
 * @param {string} jsonString - JSON 字符串
 * @returns {object} - 包含 data 和 error 屬性的對象
 */
function safeJsonParse(jsonString) {
  try {
    const data = JSON.parse(jsonString);
    return { data, error: null };
  } catch (error) {
    return { data: null, error: error.message };
  }
}

/**
 * 格式化 JSON 字符串，使其更易讀
 * @param {string} jsonString - JSON 字符串
 * @returns {string} - 格式化後的 JSON 字符串
 */
function formatJSON(jsonString) {
  try {
    const obj = JSON.parse(jsonString);
    return JSON.stringify(obj, null, 2);
  } catch (error) {
    return jsonString;
  }
}

export {
  extractJSON,
  cleanDuplicateFields,
  safeJsonParse,
  formatJSON
}; 