"""
Clipboard helper utilities for Betty AI Assistant.
Provides copy-to-clipboard functionality for responses.
"""

import streamlit as st
import streamlit.components.v1 as components
import json


def create_copy_button(text: str, button_id: str) -> bool:
    """
    Creates a copy-to-clipboard button using Streamlit components.
    
    Args:
        text: The text to copy to clipboard
        button_id: Unique identifier for the button
        
    Returns:
        True if the button was clicked, False otherwise
    """
    # Escape special characters for JavaScript
    escaped_text = json.dumps(text)
    
    # JavaScript code for copying to clipboard
    copy_script = f"""
    <script>
    function copyToClipboard_{button_id}() {{
        const text = {escaped_text};
        
        // Modern clipboard API (preferred)
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(text).then(function() {{
                // Show success message
                const button = document.getElementById('copy_btn_{button_id}');
                const originalText = button.innerText;
                button.innerText = '✅ Copied!';
                button.style.backgroundColor = '#4CAF50';
                
                // Reset button after 2 seconds
                setTimeout(function() {{
                    button.innerText = originalText;
                    button.style.backgroundColor = '';
                }}, 2000);
            }}).catch(function(err) {{
                console.error('Failed to copy: ', err);
                fallbackCopyToClipboard(text);
            }});
        }} else {{
            // Fallback for older browsers or non-secure contexts
            fallbackCopyToClipboard(text);
        }}
    }}
    
    function fallbackCopyToClipboard(text) {{
        // Create a temporary textarea element
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        
        // Select and copy the text
        textArea.focus();
        textArea.select();
        
        try {{
            const successful = document.execCommand('copy');
            if (successful) {{
                const button = document.getElementById('copy_btn_{button_id}');
                const originalText = button.innerText;
                button.innerText = '✅ Copied!';
                button.style.backgroundColor = '#4CAF50';
                
                setTimeout(function() {{
                    button.innerText = originalText;
                    button.style.backgroundColor = '';
                }}, 2000);
            }}
        }} catch (err) {{
            console.error('Fallback copy failed: ', err);
        }}
        
        // Clean up
        document.body.removeChild(textArea);
    }}
    </script>
    
    <button 
        id="copy_btn_{button_id}"
        onclick="copyToClipboard_{button_id}()"
        style="
            background-color: #f0f2f6;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        "
        onmouseover="this.style.backgroundColor='#e0e2e6'"
        onmouseout="this.style.backgroundColor='#f0f2f6'"
    >
        📋 Copy
    </button>
    """
    
    # Render the HTML/JavaScript component
    components.html(copy_script, height=35)
    
    return False  # Since this is a JavaScript-only interaction


def create_inline_copy_button(text: str, button_id: str, button_text: str = "⧉") -> None:
    """
    Creates a small inline copy button with overlapping squares icon like modern AI chat interfaces.
    
    Args:
        text: The text to copy to clipboard
        button_id: Unique identifier for the button
        button_text: Text or icon to display on the button (default: overlapping squares)
    """
    # Ensure text is valid and escape for JavaScript
    if not text or not text.strip():
        st.warning("No content to copy")
        return
        
    escaped_text = json.dumps(text.strip())
    
    copy_script = f"""
    <style>
    .copy-btn-{button_id} {{
        background-color: transparent;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 6px;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.15s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        color: #6b7280;
        position: relative;
        margin-left: 8px;
    }}
    .copy-btn-{button_id}:hover {{
        background-color: #f3f4f6;
        border-color: #9ca3af;
        color: #374151;
    }}
    .copy-btn-{button_id}.copied {{
        background-color: #dcfce7 !important;
        border-color: #16a34a !important;
        color: #16a34a !important;
    }}
    .copy-btn-{button_id} svg {{
        width: 14px;
        height: 14px;
        stroke: currentColor;
        fill: none;
        stroke-width: 2;
    }}
    </style>
    
    <button 
        class="copy-btn-{button_id}"
        onclick="copyText_{button_id}()"
        title="Copy to clipboard"
    >
        <svg viewBox="0 0 24 24">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
    </button>
    
    <script>
    function copyText_{button_id}() {{
        const text = {escaped_text};
        const button = document.querySelector('.copy-btn-{button_id}');
        
        // Ensure we can actually copy (text must be non-empty)
        if (!text || text.trim() === '') {{
            console.warn('No text to copy');
            return;
        }}
        
        // Use modern clipboard API if available
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(text).then(function() {{
                showCopySuccess(button);
            }}).catch(function(err) {{
                console.error('Modern clipboard API failed:', err);
                fallbackCopy_{button_id}(text, button);
            }});
        }} else {{
            // Fallback for older browsers or non-secure contexts
            fallbackCopy_{button_id}(text, button);
        }}
        
        function showCopySuccess(button) {{
            if (button) {{
                button.classList.add('copied');
                button.innerHTML = '<svg viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>';
                setTimeout(function() {{
                    button.classList.remove('copied');
                    button.innerHTML = '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                }}, 1500);
            }}
        }}
    }}
    
    function fallbackCopy_{button_id}(text, button) {{
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {{
            const successful = document.execCommand('copy');
            if (successful && button) {{
                button.classList.add('copied');
                button.innerHTML = '<svg viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>';
                setTimeout(function() {{
                    button.classList.remove('copied');
                    button.innerHTML = '<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
                }}, 1500);
            }} else {{
                console.error('execCommand copy failed');
            }}
        }} catch (err) {{
            console.error('Fallback copy failed:', err);
        }}
        
        document.body.removeChild(textArea);
    }}
    </script>
    """
    
    components.html(copy_script, height=36)


def create_copy_code_button(code: str, language: str, button_id: str) -> None:
    """
    Creates a copy button specifically for code blocks.
    
    Args:
        code: The code to copy
        language: Programming language for syntax highlighting
        button_id: Unique identifier for the button
    """
    escaped_code = json.dumps(code)
    
    code_block_html = f"""
    <style>
    .code-container-{button_id} {{
        position: relative;
        background-color: #f6f8fa;
        border-radius: 6px;
        padding: 16px;
        margin: 10px 0;
    }}
    .copy-code-btn-{button_id} {{
        position: absolute;
        top: 8px;
        right: 8px;
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 4px 8px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s ease;
    }}
    .copy-code-btn-{button_id}:hover {{
        background-color: #f3f4f6;
    }}
    .copy-code-btn-{button_id}.copied {{
        background-color: #d4edda !important;
        border-color: #28a745 !important;
        color: #28a745;
    }}
    .code-content-{button_id} {{
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 14px;
        line-height: 1.5;
        overflow-x: auto;
        white-space: pre;
    }}
    </style>
    
    <div class="code-container-{button_id}">
        <button 
            class="copy-code-btn-{button_id}"
            onclick="(function() {{
                const code = {escaped_code};
                const button = event.target;
                
                if (navigator.clipboard && window.isSecureContext) {{
                    navigator.clipboard.writeText(code).then(function() {{
                        button.classList.add('copied');
                        button.innerHTML = '✅ Copied';
                        setTimeout(function() {{
                            button.classList.remove('copied');
                            button.innerHTML = '📋 Copy';
                        }}, 2000);
                    }});
                }} else {{
                    const textArea = document.createElement('textarea');
                    textArea.value = code;
                    textArea.style.position = 'fixed';
                    textArea.style.opacity = '0';
                    document.body.appendChild(textArea);
                    textArea.select();
                    try {{
                        document.execCommand('copy');
                        button.classList.add('copied');
                        button.innerHTML = '✅ Copied';
                        setTimeout(function() {{
                            button.classList.remove('copied');
                            button.innerHTML = '📋 Copy';
                        }}, 2000);
                    }} catch (err) {{
                        console.error('Copy failed:', err);
                    }}
                    document.body.removeChild(textArea);
                }}
            }})()"
        >
            📋 Copy
        </button>
        <pre class="code-content-{button_id}"><code>{code}</code></pre>
    </div>
    """
    
    components.html(code_block_html, height=150)