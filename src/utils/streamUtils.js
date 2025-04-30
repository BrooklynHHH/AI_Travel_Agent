/**
 * Utility functions for handling streaming API responses
 */

/**
 * Safely parses a JSON string with enhanced error handling and recovery
 * @param {string} jsonString - The JSON string to parse
 * @returns {Object} - The parsed data and any error that occurred
 */
export const safeJsonParse = (jsonString) => {
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
      
      // Step 1: Handle problematic Unicode escapes
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

/**
 * Helper function to extract error position from an error message
 * @param {string} errorMessage - The error message
 * @returns {number} - The position of the error, or -1 if not found
 */
export const getErrorPosition = (errorMessage) => {
  const posMatch = errorMessage.match(/position (\d+)/);
  if (posMatch && posMatch[1]) {
    return parseInt(posMatch[1]);
  }
  return -1;
};

/**
 * Helper function to fix unterminated strings
 * @param {string} jsonStr - The JSON string to fix
 * @returns {string} - The fixed JSON string
 */
export const fixUnterminatedStrings = (jsonStr) => {
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

/**
 * Helper function to balance quotes in a JSON string
 * @param {string} jsonStr - The JSON string to balance
 * @returns {string} - The balanced JSON string
 */
export const balanceQuotes = (jsonStr) => {
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

/**
 * Helper function to fix common structural issues
 * @param {string} jsonStr - The JSON string to fix
 * @returns {string} - The fixed JSON string
 */
export const fixStructuralIssues = (jsonStr) => {
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

/**
 * Helper function to extract valid partial JSON
 * @param {string} jsonStr - The JSON string to extract from
 * @param {number} errorPos - The position of the error
 * @returns {Object|null} - The extracted JSON, or null if none could be extracted
 */
export const extractValidPartial = (jsonStr, errorPos) => {
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

/**
 * Handles streaming API responses from Server-Sent Events (SSE)
 * @param {Response} response - The fetch API response
 * @param {Object} options - Configuration options
 * @returns {Promise<Object>} - A promise that resolves when streaming is complete
 */
export const handleStreamingResponse = async (response, options = {}) => {
  const {
    onData = () => {},           // Callback for each data event
    onStart = () => {},          // Callback at start of streaming
    onComplete = () => {},       // Callback when streaming is complete
    onError = () => {},          // Callback when an error occurs
    eventHandlers = {},          // Custom handlers for specific event types
    endEvents = ['workflow_finished'], // Events that should end the stream
    debug = false                // Enable debug logging
  } = options;

  // Validate response
  if (!response.ok) {
    const error = new Error(`HTTP error! Status: ${response.status}`);
    onError(error);
    throw error;
  }

  // Setup streaming
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let isStreamEnded = false;  // Flag to track if an end event has been received
  
  // Process an SSE line
  const processSSELine = (line) => {
    // Skip empty lines
    if (!line.trim()) return;
    
    // Check if line starts with "data: "
    if (line.startsWith('data: ')) {
      // Extract content after "data: " prefix
      const dataContent = line.substring(6).trim();
      
      // If it's the DONE marker, just return
      if (dataContent === '[DONE]') {
        debug && console.log('Received [DONE] marker');
        return;
      }
      
      // Special case for ping events
      if (line === 'event: ping') {
        debug && console.log('Received ping event');
        return;
      }
      
      // Try to parse the JSON
      try {
        const { data, error } = safeJsonParse(dataContent);
        if (error) {
          debug && console.error(`Failed to parse JSON, skipping`);
          onError(new Error(`JSON parse error: ${error.message}`));
          return;
        }
        
        // Provide the raw data to the general handler
        onData(data);
        
        // Check for specific event types and use custom handlers if available
        if (data.event && eventHandlers[data.event]) {
          eventHandlers[data.event](data);
        }
        
        // Check if this is an event that should end streaming
        if (data.event && endEvents.includes(data.event)) {
          debug && console.log(`Received ${data.event} event, marking stream as ended`);
          isStreamEnded = true;
        }
      } catch (parseError) {
        debug && console.error('Error processing line:', parseError);
        onError(parseError);
      }
    } else {
      // Handle non-data lines (like error responses)
      debug && console.log('Received non-data line:', line);
    }
  };
  
  try {
    // Notify streaming has started
    onStart();
    
    // Start reading the stream
    let buffer = '';          // Buffer for incomplete chunks
    let reading = true;       // Flag to control the reading loop
    
    // Keep reading until explicitly stopped by an end event
    while (reading) {
      // Read the next chunk
      const { done, value } = await reader.read();
      
      // If reader says it's done but we haven't seen an end event yet, we'll continue
      // This handles cases where the connection might temporarily report as done
      if (done && !value) {
        debug && console.log('Reader indicated stream is done');
        
        // Only break if we've already seen an end event
        if (isStreamEnded) {
          debug && console.log('Stream end event received, ending stream reception');
          reading = false;
          
          // Process any remaining data in the buffer
          if (buffer.trim()) {
            processSSELine(buffer.trim());
          }
          break;
        }
        
        // Add a small delay to prevent tight loop if reader keeps returning done
        await new Promise(resolve => setTimeout(resolve, 100));
        continue;
      }
      
      // Skip if no value (might happen in some edge cases)
      if (!value || value.length === 0) {
        continue;
      }
      
      // Decode the chunk and add to buffer
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;
      
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
            processSSELine(line);
          }
        }
      } catch (streamError) {
        debug && console.error('Error processing buffer:', streamError);
        onError(streamError);
        // Don't break the loop, continue reading
      }
    }
    
    // Mark streaming as complete
    onComplete();
    
  } catch (error) {
    debug && console.error('Error reading from stream:', error);
    onError(error);
    throw error;
  }
  
  return { success: true };
};
