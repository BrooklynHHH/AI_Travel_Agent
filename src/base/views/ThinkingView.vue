<template>
  <div v-if="thinkingText || normalText" class="summary-wrapper">
    <div class="summary-label-block">
      <i class="summary-label-icon">📢</i>
      <span class="summary-label-text">综合意见</span>
    </div>
    <div class="summary-block">
      <!-- 渲染思考过程 -->
      <div v-if="thinkingText && thinkingText.trim()" class="summary-content"
        v-html="renderThinkingContent()">
      </div>
      <!-- 渲染非思考过程 -->
      <div v-if="normalText && normalText.trim()" class="summary-content"
        v-html="renderNormalContent()">
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, defineProps } from 'vue';
import MarkdownIt from 'markdown-it';

const props = defineProps({
  thinkingText: {
    type: String,
    default: ''
  },
  normalText: {
    type: String,
    default: ''
  },
  // 用于生成唯一ID，避免多个组件实例冲突
  uniqueIdSuffix: {
    type: [String, Number],
    default: () => Math.random().toString(36).substring(7)
  }
});

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
});

// 将 toggleThinkingBlockContent 移到 setup 作用域内，并通过 window 暴露
// 确保在组件挂载后执行，以便 document 对象可用
onMounted(() => {
  window.toggleThinkingBlockContent = (id) => {
    const contentElement = document.getElementById(id);
    if (!contentElement) return;
    const headerElement = contentElement.previousElementSibling;
    const iconElement = headerElement.querySelector('.toggle-icon-think');
    const innerContent = contentElement.querySelector('.thinking-block-inner-content');

    if (!innerContent) return;

    const isCollapsed = innerContent.style.maxHeight === '0px' ||
      innerContent.style.maxHeight === '' ||
      contentElement.style.display === 'none';

    if (isCollapsed) {
      contentElement.style.display = 'block';
      innerContent.style.maxHeight = 'calc(8 * 1.6em)';
      innerContent.style.padding = '10px 12px';
      innerContent.style.overflow = 'auto';
      if (iconElement) iconElement.textContent = '▼';
      innerContent.scrollTop = 0;
    } else {
      contentElement.style.display = 'block';
      innerContent.style.maxHeight = '0px';
      innerContent.style.padding = '0 12px';
      innerContent.style.overflow = 'hidden';
      if (iconElement) iconElement.textContent = '▶';
    }
  };
});


const renderMarkdownInternal = (content, idPrefix = 'default', isForThinkingBlocks = false) => {
  if (!content) return '';

  if (isForThinkingBlocks) {
    const parts = content.split(/(<think>|<\/think>)/g);
    let htmlOutput = '';
    let inThinkBlock = false;
    let currentThinkContent = '';
    let thinkBlockCounter = 0;
    let currentThinkId = ''; // 用于存储当前处理的思考块的ID

    const finalizeThinkBlock = () => {
      const endsWithClosedThinkBlock = htmlOutput.trim().endsWith('</div> <!-- close thinking-block-wrapper -->');
      const hasThinkingBlock = currentThinkId && htmlOutput.includes(`data-thinking-id="${currentThinkId}"`);

      if ((currentThinkContent.trim() !== '' || (inThinkBlock && !endsWithClosedThinkBlock)) && hasThinkingBlock) {
        const contentToRender = currentThinkContent.trim() === '' ? '> ' : currentThinkContent.split('\n').map(line => `> ${line.trimEnd()}`).filter(line => line !== '> ').join('\n');
        const finalQuotedContent = contentToRender.trim() === '' ? '> ' : contentToRender;

        if (htmlOutput.includes(currentThinkId) && !htmlOutput.substring(htmlOutput.lastIndexOf(currentThinkId)).includes('</div> <!-- close thinking-block-inner-content -->')) {
          htmlOutput += md.render(finalQuotedContent);
          htmlOutput += `
              </div> <!-- close thinking-block-inner-content -->
            </div> <!-- close thinking-block-content-container -->
          </div> <!-- close thinking-block-wrapper -->
            `;
        }
      } else if ((currentThinkContent.trim() !== '' || inThinkBlock) && !hasThinkingBlock) {
        const thinkId = currentThinkId || `thinking-block-${idPrefix}-${props.uniqueIdSuffix}-${thinkBlockCounter++}`;
        const contentToRender = currentThinkContent.trim() === '' ? '> ' : currentThinkContent.split('\n').map(line => `> ${line.trimEnd()}`).filter(line => line !== '> ').join('\n');
        const finalQuotedContent = contentToRender.trim() === '' ? '> ' : contentToRender;

        htmlOutput += `
          <div class="thinking-block-wrapper" data-thinking-id="${thinkId}">
            <div class="thinking-block-header" onclick="window.toggleThinkingBlockContent('${thinkId}')">
              思考过程 <span class="toggle-icon-think">▼</span>
            </div>
            <div id="${thinkId}" class="thinking-block-content-container" style="display: block;">
              <div class="thinking-block-inner-content" style="max-height: calc(8 * 1.6em); overflow: auto;">
                ${md.render(finalQuotedContent)}
              </div> <!-- close thinking-block-inner-content -->
            </div> <!-- close thinking-block-content-container -->
          </div> <!-- close thinking-block-wrapper -->
        `;
        if (!currentThinkId) {
          currentThinkId = thinkId;
        }
      }
      currentThinkContent = '';
    };

    parts.forEach(part => {
      if (part === '<think>') {
        if (inThinkBlock) {
          finalizeThinkBlock();
        }
        inThinkBlock = true;
        currentThinkId = `thinking-block-${idPrefix}-${props.uniqueIdSuffix}-${thinkBlockCounter++}`;
        htmlOutput += `
          <div class="thinking-block-wrapper" data-thinking-id="${currentThinkId}">
            <div class="thinking-block-header" onclick="window.toggleThinkingBlockContent('${currentThinkId}')">
              思考过程 <span class="toggle-icon-think">▼</span>
            </div>
            <div id="${currentThinkId}" class="thinking-block-content-container" style="display: block;">
              <div class="thinking-block-inner-content" style="max-height: calc(8 * 1.6em); overflow: auto;">`;
      } else if (part === '</think>') {
        if (inThinkBlock) {
          finalizeThinkBlock(); // Finalize the current block
          inThinkBlock = false; // Explicitly mark as not in think block
        } else {
          htmlOutput += md.render(part);
        }
      } else if (inThinkBlock) {
        currentThinkContent += part;
      } else {
        if (part.trim() !== '') {
          let normalHtml = md.render(part);
          normalHtml = normalHtml.replace(/(<\/p>)(\s*)<p>/g, '$1<div style="height:1em"></div><p>');
          normalHtml = normalHtml.replace(/(<\/h[1-6]>)(\s*)<p>/g, '$1<div style="height:1em"></div><p>');
          normalHtml = normalHtml.replace(/(<\/p>)(\s*)<(h[1-6]>)/g, '$1<div style="height:1em"></div><$3');
          normalHtml = normalHtml.replace(/(<\/h[1-6]>)(\s*)<(h[1-6]>)/g, '$1<div style="height:1em"></div><$3');
          htmlOutput += normalHtml;
        } else {
          htmlOutput += part;
        }
      }
    });

    if (inThinkBlock) {
      finalizeThinkBlock();
    }
    return htmlOutput;
  } else {
    // 只保留原始 markdown 渲染，不做标题前后换行的正则替换
    return md.render(content);
  }
};

const renderThinkingContent = () => {
  // Always wrap thinkingText with <think> tags for processing
  return renderMarkdownInternal(`<think>${props.thinkingText}</think>`, 'thinking', true);
};

const renderNormalContent = () => {
  return renderMarkdownInternal(props.normalText, 'normal', false);
};

</script>

<style scoped>
.summary-wrapper {
  display: block !important;
  visibility: visible !important;
  margin-top: 20px;
  padding: 5px;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.summary-label-block {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  margin-top: 20px;
}

.summary-label-icon {
  font-size: 20px;
  margin-right: 6px;
  color: #1976d2;
  font-style: normal;
}

.summary-label-text {
  font-size: 20px;
  font-weight: 600;
  color: #1976d2;
}

.summary-block {
  background: none;
  border-left: none;
  border-radius: 0;
  padding: 0;
  font-size: 17px;
}

.summary-content {
  color: #333;
  font-size: 15px;
  line-height: 1.7;
  word-break: break-word;
  display: block !important;
  visibility: visible !important;
}

.summary-content :deep(h1) {
  font-size: 18px;
}

.summary-content :deep(h2),
.summary-content :deep(h3) {
  font-size: 16px;
}

.summary-content :deep(ul),
.summary-content :deep(ol) {
  padding-left: 2em !important;
  margin-left: 0 !important;
  list-style-position: outside !important;
}

.summary-content :deep(li) {
  margin-left: 0 !important;
  list-style-position: outside !important;
}

.summary-content :deep(p) {
  margin: 0 0 16px 0;
}


/* Styles for thinking blocks */
.thinking-block-wrapper {
  margin: 1em 0;
  font-size: 1em;
  /* Base font size for wrapper */
}

.thinking-block-header {
  padding: 8px 12px;
  background-color: #f0f0f0;
  /* Light grey background */
  border: 1px solid #e0e0e0;
  /* Softer border */
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  /* Slightly less bold */
  color: #555;
  /* Darker grey text */
}

.thinking-block-header:hover {
  background-color: #e9e9e9;
}

.toggle-icon-think {
  font-size: 0.9em;
  /* Adjusted size */
  transition: transform 0.2s ease-in-out;
  color: #555;
}

/* Container for the collapsable area, distinct from the blockquote itself */
.thinking-block-content-container {
  margin-top: 0.5em;
  overflow: hidden;
}

.thinking-block-inner-content {
  max-height: calc(8 * 1.6em);
  /* 增加高度显示更多行 */
  overflow-y: auto;
  padding: 10px 12px;
  /* Padding inside the scrollable area */
  line-height: 1.6;
  font-size: 0.9em;
  /* Slightly smaller font for content */
  color: #333;
  /* Standard text color */
}

/* 思考块内容的样式 */
.thinking-block-inner-content :deep(blockquote) {
  margin: 0;
  /* Reset default blockquote margin */
  padding: 10px 12px;
  /* Apply padding to the blockquote itself */
  background-color: #f8f9fa;
  /* Light background for the quote */
  border-left: 3px solid #007bff;
  /* Standard quote border */
  border-radius: 4px;
  /* Apply border-radius to the blockquote */
  font-size: 0.9em;
  /* 缩小思考内容字体 */
  color: #666;
  /* 思考内容用灰色显示 */
}

/* 针对以 | 开头的思考内容行的样式 */
.thinking-block-inner-content :deep(blockquote p) {
  margin-bottom: 0.5em;
  /* Adjust paragraph spacing within the quote */
  font-size: 0.85em;
  /* 思考内容比正常内容小一号 */
  line-height: 1.5;
  /* Ensure line-height inside blockquote is consistent */
  color: #666;
  /* 思考内容用灰色显示 */
}

/* 针对以 | 开头的文本添加特殊样式 */
.thinking-block-inner-content :deep(blockquote p:first-letter) {
  margin-right: 3px;
  color: #999;
  /* 竖线符号颜色更浅 */
}

/* Styling for the blockquote generated by markdown-it inside .thinking-block-inner-content */
.thinking-block-inner-content :deep(blockquote) {
  margin: 0;
  /* Reset default blockquote margin */
  padding: 10px 12px;
  /* Apply padding to the blockquote itself */
  background-color: #f8f9fa;
  /* Light background for the quote */
  border-left: 3px solid #007bff;
  /* Standard quote border */
  border-radius: 4px;
  /* Apply border-radius to the blockquote */
}

.thinking-block-inner-content :deep(blockquote p) {
  margin-bottom: 0.5em;
  /* Adjust paragraph spacing within the quote */
  font-size: 1em;
  /* Ensure p inside blockquote inherits font size correctly */
  line-height: 1.5;
  /* Ensure line-height inside blockquote is consistent */
}

.thinking-block-inner-content :deep(blockquote p:last-child) {
  margin-bottom: 0;
}

/* Ensure direct children paragraphs/headings in inner content have no extra margin if they are NOT blockquotes */
.thinking-block-inner-content > :first-child:not(blockquote) {
  margin-top: 0;
}

.thinking-block-inner-content > :last-child:not(blockquote) {
  margin-bottom: 0;
}

/* 确保非思考内容正确显示 */
.summary-content > :deep(p),
.summary-content > :deep(ul),
.summary-content > :deep(ol),
.summary-content > :deep(h1),
.summary-content > :deep(h2),
.summary-content > :deep(h3) {
  margin-top: 16px !important;
}
</style>
