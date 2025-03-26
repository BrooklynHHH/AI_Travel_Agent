<template>
  <div class="chat-container">
    <!-- Product floating window -->
    <div v-if="showProductWindow" class="product-window" @click="closeProductWindow">
      <div class="product-window-content" :class="{ 'fullscreen': isFullscreen }" @click.stop>
        <div class="product-window-header">
          <h3>商品浮窗</h3>
          <div class="header-buttons">
            <button class="expand-button" @click="toggleFullscreen">{{ isFullscreen ? '▼' : '▲' }}</button>
            <button class="close-button" @click="closeProductWindow">×</button>
          </div>
        </div>
        <div class="product-window-body">
          <iframe v-if="productUrl" :src="productUrl" class="product-iframe" frameborder="0"></iframe>
          <p v-else class="product-name">{{ productName }}</p>
        </div>
      </div>
    </div>
    <!-- Mobile header -->
    <div class="mobile-header">
      <div class="status-bar">
        <div class="time">{{ currentTime }}</div>
        <div class="status-icons">
          <span class="signal">●●●●</span>
          <span class="wifi">●</span>
          <span class="battery">●</span>
        </div>
      </div>
      <div class="chat-header">
        <div class="back-button" @click="goBack">
          <i class="back-icon">←</i>
        </div>
        <div class="spacer"></div>
        <div class="add-button">
          <i class="add-icon">+</i>
        </div>
      </div>
    </div>

    <!-- Chat content -->
    <div class="chat-content" ref="chatContent">
      <!-- Watermark -->
      <div class="watermark">阿柒 0098</div>

      <!-- Messages -->
      <div v-for="(message, index) in messages" :key="index">
        <!-- User message -->
        <div v-if="message.role === 'user'" class="message-container user-message">
          <div class="message-bubble">
            {{ message.content }}
          </div>
        </div>

        <!-- Bot message -->
        <template v-else-if="message.role === 'assistant'">
          <!-- Main response -->
          <div class="message-container bot-message">
            <div class="mi-logo">
              <div class="mi-logo-text">MI</div>
            </div>
            <div class="message-bubble main-response">
              <div v-if="message.streaming" class="response-text">
                <div v-html="renderMarkdown(message.content)"></div><span class="cursor">|</span>
              </div>
              <div v-else class="response-text" v-html="renderMarkdown(message.content)"></div>
              
              <!-- Follow-up question section -->
              <div v-if="message.followUpQuestion" class="follow-up-question">
                <p class="question-text">{{ message.followUpQuestion.question }}</p>
                <div class="option-buttons">
                  <button 
                    v-for="(option, index) in message.followUpQuestion.options" 
                    :key="index" 
                    class="option-button"
                    @click="sendFollowUpResponse(option)"
                  >
                    {{ option }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Progress bar (visible when loading or streaming) -->
      <div v-if="isLoading || isStreaming" class="progress-container">
        <div class="progress-bar"></div>
      </div>
      
      <!-- Extra padding at bottom to ensure scrollability -->
      <div style="height: 150px"></div>
    </div>

    <!-- Input area -->
    <div class="chat-input">
      <div class="input-container">
        <div class="plus-button">
          <i class="plus-icon">+</i>
        </div>
        <input 
          type="text" 
          placeholder="输入你想问的问题" 
          v-model="userInput"
          @keyup.enter="sendMessage"
        />
        <div class="voice-button" @click="sendMessage">
          <i class="send-icon">↑</i>
        </div>
      </div>
      
      <div class="bottom-toolbar">
        <div class="toolbar-item">
          <i class="depth-icon">🔍</i>
          <span>深度思考</span>
        </div>
        <div class="toolbar-item">
          <i class="web-icon">🌐</i>
          <span>联网搜索</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import MarkdownIt from 'markdown-it';

// Product window state
const showProductWindow = ref(false);
const productName = ref('');
const productUrl = ref('');
const isFullscreen = ref(false);

// Function to close product window
const closeProductWindow = () => {
  showProductWindow.value = false;
  productUrl.value = '';
  isFullscreen.value = false;
};

// Function to toggle fullscreen mode
const toggleFullscreen = (event) => {
  event.stopPropagation();
  isFullscreen.value = !isFullscreen.value;
};

// Initialize markdown-it renderer with custom link rendering
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
});

// Add a custom attribute to links to identify them
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx];
  const href = token.attrGet('href');
  
  // Check if link starts with aisearch://
  if (href && href.startsWith('aisearch://')) {
    // Add styling class for all aisearch links
    token.attrPush(['class', 'special-link']);
    
    // Check if it's a product link
    if (href.startsWith('aisearch://product/')) {
      const productPath = href.substring('aisearch://product/'.length);
      token.attrPush(['data-product-url', productPath]);
      token.attrPush(['data-product', productPath]);
    } else {
      token.attrPush(['data-product', href.substring('aisearch://'.length)]);
    }
  } else {
    // For regular links, open in new tab
    token.attrPush(['target', '_blank']);
    token.attrPush(['rel', 'noopener noreferrer']);
  }
  
  return self.renderToken(tokens, idx, options);
};

// Function to handle click on rendered content
const handleContentClick = (event) => {
  // Check if clicked element is an aisearch link (with the special-link class)
  if (event.target.tagName === 'A' && event.target.classList.contains('special-link')) {
    event.preventDefault();
    
    // Check if it has a product URL
    const productUrlAttr = event.target.getAttribute('data-product-url');
    if (productUrlAttr) {
      productName.value = productUrlAttr;
      productUrl.value = productUrlAttr;
      showProductWindow.value = true;
    } else {
      // Handle regular aisearch links
      const product = event.target.getAttribute('data-product');
      if (product) {
        productName.value = product;
        productUrl.value = '';
        showProductWindow.value = true;
      }
    }
  }
};

// Data
const currentTime = ref('');
const userInput = ref('');
const chatContent = ref(null);
const isLoading = ref(false);
const streamingMessage = ref('');
const streamingMessageFollowUp = ref(null);
const conversationId = ref('');
const isStreaming = ref(false);

// Store messages
const messages = ref([]);

// Markdown renderer function
const renderMarkdown = (content) => {
  if (!content) return '';
  return md.render(content);
};

// Methods
const updateTime = () => {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, '0');
  currentTime.value = `${hours}:${minutes}`;
};

const goBack = () => {
  // Handle back navigation
  console.log('Back button clicked');
};

const scrollToBottom = () => {
  if (chatContent.value) {
    chatContent.value.scrollTop = chatContent.value.scrollHeight;
  }
};

// Function to handle sending follow-up responses
const sendFollowUpResponse = (optionText) => {
  // Create Baidu search URL with the option text
  const searchUrl = `https://www.baidu.com/s?wd=${encodeURIComponent(optionText)}`;
  
  // Open product window with the search URL
  productName.value = optionText;
  productUrl.value = searchUrl;
  showProductWindow.value = true;
};

// Function to safely handle JSON parsing with enhanced error handling
const safeJsonParse = (jsonString) => {
  try {
    return { data: JSON.parse(jsonString), error: null };
  } catch (parseError) {
    console.error('JSON parse error:', parseError);
    
    // Print the raw text that caused the error
    console.log('========== RECEIVED RAW TEXT (START) ==========');
    console.log(jsonString);
    console.log('========== RECEIVED RAW TEXT (END) ============');
    
    // Additional debug info
    console.log('Problematic JSON string length:', jsonString.length);
    
    // Print a truncated version for console readability
    if (jsonString.length >= 500) {
      console.log('Problematic JSON string (truncated):');
      console.log('- Start:', jsonString.substring(0, 100) + '...');
      
      // Also show text around the error position if available
      if (parseError.message.includes('position')) {
        const errorPos = getErrorPosition(parseError.message);
        if (errorPos > -1) {
          const start = Math.max(0, errorPos - 100);
          const end = Math.min(jsonString.length, errorPos + 100);
          console.log(`- Around error position ${errorPos}:`, 
            jsonString.substring(start, errorPos) + ' 👉 ERROR HERE 👈 ' + jsonString.substring(errorPos, end));
        }
      }
      
      console.log('- End:', '...' + jsonString.substring(jsonString.length - 100));
    }
    
    // First level sanitization: Fix common Unicode escape problems
    try {
      // Pre-process to handle escaped quotes and other issues
      console.log('Attempting to sanitize JSON string...');
      
      // Step 1: Handle problematic Unicode escape sequences
      let sanitizedStr = jsonString
        // Replace invalid Unicode escapes
        .replace(/\\u[0-9a-fA-F]{0,3}([^0-9a-fA-F]|$)/g, match => {
          console.log('Found bad Unicode escape:', match);
          return match.replace('\\u', '\\\\u');
        })
        // Handle any other known problematic sequences
        .replace(/\\x/g, '\\\\x');
      
      // Step 2: Handle double-escaped quotes (\" inside JSON strings)
      // When the string already contains escaped quotes, we need to be careful
      // First, we'll try a direct parse
      try {
        return { data: JSON.parse(sanitizedStr), error: null };
      } catch (directParseError) {
        console.log('Direct parse after basic sanitization failed, trying additional fixes...');
        
        // Step 3: Try to handle double-escaped quotes
        // This is tricky because we need to handle cases where there are legitimate escaped quotes
        // One approach is to replace \" with a temporary placeholder, then restore after parsing
        const QUOTE_PLACEHOLDER = "__ESCAPED_QUOTE__";
        
        // Replace escaped quotes with a placeholder
        const processedStr = sanitizedStr.replace(/\\"/g, QUOTE_PLACEHOLDER);
        
        // Try to parse with placeholders
        try {
          const parsedWithPlaceholders = JSON.parse(processedStr);
          
          // Success! Now we need to restore the escaped quotes in all string values
          const restoreEscapedQuotes = (obj) => {
            if (typeof obj === 'string') {
              return obj.replace(new RegExp(QUOTE_PLACEHOLDER, 'g'), '\\"');
            } else if (Array.isArray(obj)) {
              return obj.map(item => restoreEscapedQuotes(item));
            } else if (obj !== null && typeof obj === 'object') {
              const result = {};
              for (const key in obj) {
                result[key] = restoreEscapedQuotes(obj[key]);
              }
              return result;
            }
            return obj;
          };
          
          return { data: restoreEscapedQuotes(parsedWithPlaceholders), error: null };
        } catch (placeholderError) {
          console.log('Placeholder approach failed:', placeholderError.message);
          
          // Step 4: More aggressive handling - double-unescape the entire string
          // This is a last-resort attempt
          try {
            console.log('Trying double unescaping...');
            // Add extra backslashes to all backslashes
            const doubleEscaped = sanitizedStr.replace(/\\/g, '\\\\');
            return { data: JSON.parse(doubleEscaped), error: null };
          } catch (doubleEscapeError) {
            console.log('Double unescaping failed, throwing original error');
            throw directParseError; // Throw the original error to continue to next recovery level
          }
        }
      }
    } catch (firstSanitizeError) {
      console.log('First level sanitization failed:', firstSanitizeError.message);
      
      // Second level sanitization: Fix unterminated strings and other issues
      try {
        // Check for unterminated string error
        if (parseError.message.includes('Unterminated string')) {
          console.log('Attempting to fix unterminated string');
          
          // Try to determine where the unterminated string is
          const errorPosition = getErrorPosition(parseError.message);
          if (errorPosition !== -1) {
            console.log('Error position:', errorPosition);
            
            // Extract problematic part of the string
            const problemRange = {
              start: Math.max(0, errorPosition - 50),
              end: Math.min(jsonString.length, errorPosition + 50)
            };
            console.log('Problem range:', 
              jsonString.substring(problemRange.start, problemRange.end));
            
            // First attempt: Manually add quotes at strategic positions
            console.log('Applying specific fixes...');
            
            // Create a custom fixed string
            const fixedStr = fixUnterminatedStrings(jsonString);
            console.log('Applied string termination fixes');
            
            return { data: JSON.parse(fixedStr), error: null };
          }
        }
        
        // Fall back to just trying to repair JSON with more aggressive methods
        console.log('Applying aggressive JSON repair...');
        
        // Method 1: Try to balance all quotes
        let repairedStr = balanceQuotes(jsonString);
        
        // Method 2: Fix common structural issues
        repairedStr = fixStructuralIssues(repairedStr);
        
        console.log('Applied aggressive repairs');
        return { data: JSON.parse(repairedStr), error: null };
      } catch (secondSanitizeError) {
        console.error('All sanitization attempts failed:', secondSanitizeError);
        
        // Last resort: Try to extract usable data even if it's not valid JSON
        try {
          // Extract just the part before the error
          if (parseError.message.includes('position')) {
            const pos = getErrorPosition(parseError.message);
            if (pos > 0) {
              // Try to find the last valid object or array before the error
              const partialJson = extractValidPartial(jsonString, pos);
              if (partialJson) {
                console.log('Extracted partial valid JSON');
                return { 
                  data: partialJson, 
                  error: null, 
                  partial: true 
                };
              }
            }
          }
        } catch (lastError) {
          console.error('Even partial extraction failed');
        }
        
        return { data: null, error: parseError };
      }
    }
  }
};

// Helper function to extract error position
const getErrorPosition = (errorMessage) => {
  const posMatch = errorMessage.match(/position (\d+)/);
  if (posMatch && posMatch[1]) {
    return parseInt(posMatch[1]);
  }
  return -1;
};

// Helper function to fix unterminated strings
const fixUnterminatedStrings = (jsonStr) => {
  // Strategy 1: Add missing quotes at the end of string values
  let fixed = jsonStr;
  
  // Look for patterns like: "key": "value with no closing quote
  fixed = fixed.replace(/"([^"\\]*):\s*"([^"\\]*)(?=[,}]|$)/g, (match, key, value) => {
    return `"${key}": "${value}"`;
  });
  
  // Look for unbalanced quotes in general
  let inString = false;
  let fixedWithBalancedQuotes = '';
  
  for (let i = 0; i < fixed.length; i++) {
    const char = fixed[i];
    const prevChar = i > 0 ? fixed[i - 1] : '';
    
    // Check for unescaped quotes
    if (char === '"' && prevChar !== '\\') {
      if (!inString) {
        inString = true;
      } else {
        inString = false;
      }
    }
    
    fixedWithBalancedQuotes += char;
    
    // If we reach the end of input and still inside a string, add a closing quote
    if (i === fixed.length - 1 && inString) {
      fixedWithBalancedQuotes += '"';
    }
  }
  
  return fixedWithBalancedQuotes;
};

// Helper function to balance quotes in a JSON string
const balanceQuotes = (jsonStr) => {
  // Count unescaped quotes
  let count = 0;
  let inEscape = false;
  
  for (let i = 0; i < jsonStr.length; i++) {
    const char = jsonStr[i];
    
    if (inEscape) {
      inEscape = false;
    } else if (char === '\\') {
      inEscape = true;
    } else if (char === '"') {
      count++;
    }
  }
  
  // If odd number of quotes, add one at the end
  let result = jsonStr;
  if (count % 2 !== 0) {
    result += '"';
  }
  
  return result;
};

// Helper function to fix common structural issues
const fixStructuralIssues = (jsonStr) => {
  let result = jsonStr;
  
  // Fix missing object closing brackets
  const openBraces = (result.match(/{/g) || []).length;
  const closeBraces = (result.match(/}/g) || []).length;
  if (openBraces > closeBraces) {
    result += '}'.repeat(openBraces - closeBraces);
  }
  
  // Fix missing array closing brackets
  const openBrackets = (result.match(/\[/g) || []).length;
  const closeBrackets = (result.match(/\]/g) || []).length;
  if (openBrackets > closeBrackets) {
    result += ']'.repeat(openBrackets - closeBrackets);
  }
  
  // Fix trailing commas in objects/arrays
  result = result.replace(/,\s*}/g, '}').replace(/,\s*\]/g, ']');
  
  return result;
};

// Helper function to extract valid partial JSON
const extractValidPartial = (jsonStr, errorPos) => {
  // Try to extract a complete object or array up to the error
  const partial = jsonStr.substring(0, errorPos);
  
  // Find last complete object or array
  let validJson = null;
  
  // Try to find the last valid object
  const lastObjectMatch = partial.match(/\{(?:[^{}]|(\{(?:[^{}]|(\{[^{}]*\}))*\}))*\}/g);
  if (lastObjectMatch && lastObjectMatch.length > 0) {
    try {
      validJson = JSON.parse(lastObjectMatch[lastObjectMatch.length - 1]);
    } catch (e) {
      // Not valid, continue to next method
    }
  }
  
  // If no valid object, try to find the last valid array
  if (!validJson) {
    const lastArrayMatch = partial.match(/\[(?:[^[\]]|(\[(?:[^[\]]|(\[[^[\]]*\]))*\]))*\]/g);
    if (lastArrayMatch && lastArrayMatch.length > 0) {
      try {
        validJson = JSON.parse(lastArrayMatch[lastArrayMatch.length - 1]);
      } catch (e) {
        // Not valid, continue to fallback
      }
    }
  }
  
  // If we couldn't find a complete object/array, return null
  return validJson;
};

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  const userMessage = userInput.value;
  console.log('Message sent:', userMessage);
  
  // Add user message to messages array
  messages.value.push({
    role: 'user',
    content: userMessage
  });
  
  // Clear input field
  userInput.value = '';
  
  // Scroll to bottom
  nextTick(() => {
    scrollToBottom();
  });
  
  // Set loading state
  isLoading.value = true;
  streamingMessage.value = '';
  
  try {
    // Create placeholder for assistant response
    messages.value.push({
      role: 'assistant',
      content: '',
      streaming: true
    });
    
    // Set streaming state to true
    isStreaming.value = true;
    
    // Call Xiaomi API
    const url = 'https://mify-be.pt.xiaomi.com/api/v1/chat-messages';
    
    const headers = {
      'Authorization': 'Bearer app-u456N01sF3Us7rg7QBpcOI2R',
      'Content-Type': 'application/json'
    };
    
    const body = {
      inputs: {},
      query: userMessage,
      response_mode: "streaming",
      conversation_id: conversationId.value,
      user: "taoliang",
      files: []
    };
    
    // Since we need to use headers and POST with streaming, we use fetch
    const response = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(body)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // Set up streaming
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    // Get the last index for updating the streaming content
    const lastIndex = messages.value.length - 1;
    
    // Function to process an SSE line
    const processSSELine = (line, messageIndex) => {
      // Skip empty lines
      if (!line.trim()) return;
      
      // Check if line starts with "data: "
      if (line.startsWith('data: ')) {
        // Extract content after "data: " prefix
        const dataContent = line.substring(6).trim();
        
        // If it's the DONE marker, just return
        if (dataContent === '[DONE]') {
          return;
        }
        
        console.log(`Processing data line. Length: ${dataContent.length}`);
        
        // Special case for ping events
        if (line === 'event: ping') {
          console.log('Received ping event');
          return;
        }
        
        // Try to parse the JSON
        try {
          const { data, error } = safeJsonParse(dataContent);
          if (error) {
            console.error(`Failed to parse JSON, skipping`);
            return;
          }
          
          // Handle conversation ID
          if (data.conversation_id) {
            conversationId.value = data.conversation_id;
          }
          
          // Handle message event (contains answer content)
          if (data.event === "message" && data.answer) {
            // Append new content to streaming message
            streamingMessage.value += data.answer;
            
            // Update the message content
            messages.value[messageIndex].content = streamingMessage.value;
            
            // Scroll to bottom with new content
            nextTick(() => {
              scrollToBottom();
            });
          }
          
          // Only workflow_finished event should end streaming
          if (data.event === "workflow_finished") {
            console.log('Received workflow_finished event, ending stream');
            isWorkflowFinished = true;
          }
          
          // Log message_end event but don't end streaming
          if (data.event === "message_end") {
            console.log('Received message_end event (continuing to read stream)');
          }
          
          // Handle more_question event
          if (data.event === "node_finished" && data.data && data.data.title === "more_question") {
            console.log('More question detected:', data.data);
            
            if (data.data.outputs && data.data.outputs.text) {
              const rawText = data.data.outputs.text;
              console.log('Raw text from more_question:', rawText);
              
              const { data: parsedData, error } = safeJsonParse(rawText);
              if (!error && parsedData) {
                console.log('Successfully parsed text data:', parsedData);
                
                // Check if it has question and option property
                if (parsedData.question && Array.isArray(parsedData.option)) {
                  console.log('Valid question and options found');
                  
                // Cache the follow-up question data, but don't show it until streaming is complete
                const cachedQuestion = {
                  question: parsedData.question,
                  options: parsedData.option
                };
                
                // Store the cached question in a variable to be used when streaming is complete
                // We'll assign it to the message later when streaming finishes
                streamingMessageFollowUp.value = cachedQuestion;
                
                console.log('Cached follow-up question, will show after streaming completes');
                }
              }
            }
          }
        } catch (parseError) {
          console.error('Error processing line:', parseError);
          console.log('Problematic content:', dataContent);
        }
      } else {
        // Handle non-data lines (like error responses)
        console.log('Received non-data line:', line);
      }
    };
    
    // Start reading the stream
    let reading = true;
    let isWorkflowFinished = false;
    let buffer = ''; // Buffer to handle incomplete chunks
    
    // Keep reading until explicitly stopped by workflow_finished event
    while (reading) {
      try {
        const { done, value } = await reader.read();
        
        // Even if reader says it's done, we'll continue unless we've seen workflow_finished
        if (done && !value) {
          console.log('Reader indicated stream is done, but continuing to read until workflow_finished');
          // Add a small delay to prevent tight loop if reader keeps returning done
          await new Promise(resolve => setTimeout(resolve, 100));
          
          // Only break if we've already seen workflow_finished
          if (isWorkflowFinished) {
            console.log('Reader done and workflow finished, ending stream reception');
            reading = false;
            
            // Process any remaining data in the buffer
            if (buffer.trim()) {
              processSSELine(buffer.trim(), lastIndex);
            }
            break;
          }
          continue;
        }
        
        // Skip if no value (might happen in some edge cases)
        if (!value || value.length === 0) {
          continue;
        }
        
        // Decode the chunk and add to buffer
        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;
        console.log('Received chunk, length:', chunk.length, 'Buffer length:', buffer.length);
        
        // Process complete lines from the buffer
        try {
          // Find newline characters in the buffer
          let newlineIndex;
          while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
            // Extract a complete line
            const line = buffer.substring(0, newlineIndex).trim();
            // Remove the processed line from buffer
            buffer = buffer.substring(newlineIndex + 1);
            
            // Process the complete line
            if (line) {
              processSSELine(line, lastIndex);
            }
          }
        } catch (streamError) {
          console.error('Error processing buffer:', streamError);
          // Don't break the loop, continue reading
        }
      } catch (streamError) {
        console.error('Error reading from stream:', streamError);
        console.log('Buffer state:', buffer);
        // Don't break the loop, try to continue reading
      }
    }
    
    // Mark streaming as complete once done
    if (lastIndex >= 0) {
      messages.value[lastIndex].streaming = false;
      
      // Add the follow-up question to the message if available
      if (streamingMessageFollowUp.value) {
        console.log('Adding follow-up question to message:', streamingMessageFollowUp.value);
        messages.value[lastIndex].followUpQuestion = streamingMessageFollowUp.value;
        // Reset the follow-up cache
        streamingMessageFollowUp.value = null;
      }
    }
    
    // Set streaming state to false
    isStreaming.value = false;
    
  } catch (error) {
    console.error('Error calling chat API:', error);
    
    // Remove the streaming message placeholder
    if (messages.value.length > 0 && messages.value[messages.value.length - 1].streaming) {
      messages.value.pop();
    }
    
    // Add error message
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，无法回答您的问题。',
      error: true
    });
    
  } finally {
    // Reset loading and streaming states
    isLoading.value = false;
    isStreaming.value = false;
    
    // Scroll to bottom
    nextTick(() => {
      scrollToBottom();
    });
  }
};

// Lifecycle hooks
onMounted(() => {
  updateTime();
  setInterval(updateTime, 60000);
  
  // Scroll to bottom initially
  nextTick(() => {
    scrollToBottom();
  });
  
  // Add event listener for clicks on chat content
  const chatContentEl = document.querySelector('.chat-content');
  if (chatContentEl) {
    chatContentEl.addEventListener('click', handleContentClick);
  }
});

// Add blinking cursor effect for streaming messages
setInterval(() => {
  const streamingElements = document.querySelectorAll('.cursor');
  streamingElements.forEach(el => {
    el.style.opacity = el.style.opacity === '0' ? '1' : '0';
  });
}, 500);
</script>

<style scoped>
/* Reset and global styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* Main container */
.chat-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-width: 400px;
  width: 100%;
  margin: 0 auto;
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Mobile header styling - fixed at top */
.mobile-header {
  background-color: #f7f8fc;
  padding-top: env(safe-area-inset-top, 10px);
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  width: 100%;
  display: none; /* Hide the mobile header */
}

.status-bar {
  display: flex;
  justify-content: space-between;
  padding: 4px 16px;
  font-size: 12px;
  color: #333;
}

.status-icons {
  display: flex;
  gap: 4px;
}

.chat-header {
  display: none; /* Hide the chat header */
}

.back-button, .add-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  cursor: pointer;
}

.back-icon, .add-icon {
  font-size: 20px;
}

.spacer {
  flex: 1;
}

/* Watermark */
.watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.05;
  font-size: 18px;
  white-space: nowrap;
  pointer-events: none;
  z-index: 1;
  color: #333;
}

/* Chat content - scrollable area between header and input */
.chat-content {
  flex: 1; 
  overflow-y: scroll;
  padding: 16px;
  padding-bottom: 130px; /* Make room for fixed input area */
  -webkit-overflow-scrolling: touch;
  position: relative;
  height: calc(100vh - 130px); /* Adjust for header and input */
}

.message-container {
  display: flex;
  margin-bottom: 16px;
  position: relative;
}

.user-message {
  justify-content: flex-end;
}

.bot-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 85%;
  padding: 12px 16px;
  border-radius: 18px;
  word-break: break-word;
  line-height: 1.4;
}

.user-message .message-bubble {
  background-color: #d8e8ff;
  color: #333;
  border-top-right-radius: 4px;
}

.bot-message .message-bubble {
  background-color: white;
  color: #333;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.mi-logo, .spacer-logo {
  width: 32px;
  height: 32px;
  margin-right: 8px;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ff6700;
}

.mi-logo-text {
  color: white;
  font-weight: bold;
  font-size: 14px;
  letter-spacing: -1px;
}

.spacer-logo {
  background-color: transparent;
}

.related-content {
  display: flex;
  align-items: center;
  color: #666;
  font-size: 14px;
}

.check-icon {
  color: #ff6700;
  margin-right: 6px;
}

.chevron-right {
  margin-left: auto;
  font-size: 18px;
}

.with-chevron {
  padding: 10px 14px;
  cursor: pointer;
}

.main-response {
  padding: 16px;
  font-size: 15px;
}

.response-text {
  line-height: 1.5;
}

/* Markdown styles */
.response-text h1, 
.response-text h2, 
.response-text h3, 
.response-text h4, 
.response-text h5, 
.response-text h6 {
  margin: 16px 0 8px 0;
  font-weight: 600;
  line-height: 1.25;
}

.response-text h1 {
  font-size: 1.5em;
}

.response-text h2 {
  font-size: 1.3em;
}

.response-text h3 {
  font-size: 1.2em;
}

.response-text p {
  margin: 8px 0;
}

.response-text a {
  color: #ff6700;
  text-decoration: none;
}

.response-text a:hover {
  text-decoration: underline;
}

.response-text code {
  font-family: monospace;
  background-color: #f1f1f1;
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.9em;
}

.response-text pre {
  background-color: #f1f1f1;
  padding: 12px;
  border-radius: 6px;
  overflow: auto;
  margin: 12px 0;
}

.response-text pre code {
  background-color: transparent;
  padding: 0;
}

.response-text ul, 
.response-text ol {
  margin: 8px 0;
  padding-left: 24px;
}

.response-text li {
  margin: 4px 0;
}

.response-text blockquote {
  border-left: 4px solid #ddd;
  padding-left: 12px;
  color: #666;
  margin: 12px 0;
}

.response-text table {
  border-collapse: collapse;
  margin: 12px 0;
  width: 100%;
}

.response-text table th,
.response-text table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.response-text table th {
  background-color: #f1f1f1;
  font-weight: 600;
}

.cursor {
  display: inline-block;
  font-weight: bold;
  transition: opacity 0.3s;
}

/* Progress bar */
.progress-container {
  width: 100%;
  height: 4px;
  margin: 12px 0;
  background-color: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  width: 30%;
  background-color: #ff6700;
  border-radius: 2px;
  animation: progress-animation 1.5s infinite ease-in-out;
}

@keyframes progress-animation {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(400%);
  }
}

/* Input area - fixed at bottom */
.chat-input {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  min-width: 400px;
  margin: 0 auto;
  background-color: #f7f8fc;
  padding: 8px 16px;
  padding-bottom: env(safe-area-inset-bottom, 16px);
  border-top: 1px solid #eee;
  z-index: 100;
}

.input-container {
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 24px;
  padding: 4px 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.plus-button, .voice-button {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  cursor: pointer;
}

.voice-button {
  color: #ff6700;
  background-color: #f0f0f0;
  border-radius: 50%;
}

.send-icon {
  font-size: 18px;
  font-weight: bold;
}

input {
  flex: 1;
  border: none;
  padding: 8px 12px;
  font-size: 15px;
  outline: none;
  background: transparent;
}

.bottom-toolbar {
  display: flex;
  margin-top: 8px;
  justify-content: space-between;
  padding: 0 20px;
}

.toolbar-item {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 16px;
}

.toolbar-item i {
  margin-right: 4px;
  font-size: 14px;
}

/* Product floating window */
.product-window {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 200;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}

.product-window-content {
  width: 100%;
  height: 50%;
  background-color: white;
  border-top-left-radius: 16px;
  border-top-right-radius: 16px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slide-up 0.3s ease-out forwards;
  transition: height 0.3s ease-out;
}

.product-window-content.fullscreen {
  height: 100%;
  border-radius: 0;
}

@keyframes slide-up {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.product-window-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  align-items: center;
}

.product-window-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.expand-button, .close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  margin-left: 10px;
}

.product-window-body {
  flex: 1;
  padding: 0;
  overflow: hidden;
  position: relative;
}

.product-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.product-name {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 16px;
}

/* Style for special links (aisearch://) */
.special-link {
  color: black !important;
  font-weight: bold;
  font-style: italic;
  text-decoration: underline;
  cursor: pointer;
}

/* Follow-up question styles */
.follow-up-question {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.question-text {
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.option-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.option-button {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.option-button:hover {
  background-color: #e9e9e9;
  border-color: #ccc;
}

.option-button:active {
  background-color: #ff6700;
  color: white;
  border-color: #ff6700;
}
</style>
