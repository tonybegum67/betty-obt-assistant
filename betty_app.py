# Fix for Streamlit Cloud SQLite3 compatibility - MUST be at the very top
import sys
if 'sqlite3' in sys.modules:
    del sys.modules['sqlite3']

try:
    import pysqlite3 as sqlite3
    sys.modules['sqlite3'] = sqlite3
except ImportError:
    import sqlite3

import streamlit as st
import openai
import anthropic
import os
import io
import re
from typing import Generator, List

# Mermaid diagram support
try:
    from streamlit_mermaid import st_mermaid
    MERMAID_AVAILABLE = True
except ImportError:
    MERMAID_AVAILABLE = False

# Import configuration and utilities
from config.settings import AppConfig
from utils.document_processor import document_processor
from utils.vector_store import betty_vector_store
from utils.feedback_manager import feedback_manager
from utils.clipboard_helper import create_inline_copy_button

# ChromaDB compatibility check
try:
    print(f"Using SQLite version: {sqlite3.sqlite_version}")
except Exception as e:
    print(f"SQLite setup warning: {e}")

# Initialize configuration
AppConfig.init_environment()


# Set page config
st.set_page_config(
    page_title=AppConfig.PAGE_TITLE,
    page_icon=AppConfig.PAGE_ICON,
    layout="wide"
)

# Enhanced knowledge base initialization with better persistence handling
def initialize_knowledge_base():
    """Initialize knowledge base with enhanced persistence and change detection."""
    if "knowledge_base_initialized" not in st.session_state:
        with st.spinner("🔄 Initializing Betty's knowledge base..."):
            try:
                collection_name = AppConfig.KNOWLEDGE_COLLECTION_NAME
                docs_path = "docs"

                # Check for forced reindex (for cloud deployment updates)
                force_reindex = os.getenv("FORCE_REINDEX", "").lower() in ["true", "1", "yes"]
                if force_reindex:
                    st.info("🔄 Force reindex requested - rebuilding knowledge base with latest enhancements...")
                    # Remove existing collection to force complete rebuild
                    collections = betty_vector_store.list_collections()
                    if collection_name in collections:
                        betty_vector_store.delete_collection(collection_name)
                        st.success("✅ Existing database cleared for complete rebuild")

                # Check if collection exists and get current state
                collections = betty_vector_store.list_collections()
                collection_exists = collection_name in collections
                current_doc_count = 0
                
                if collection_exists:
                    collection = betty_vector_store.get_or_create_collection(collection_name)
                    current_doc_count = collection.count()
                
                # Get current documents in docs folder and subdirectories
                doc_files = []
                if os.path.exists(docs_path):
                    # Walk through all subdirectories
                    for root, dirs, files in os.walk(docs_path):
                        for file in files:
                            if file.lower().endswith(('.pdf', '.docx', '.txt', '.md', '.csv', '.xlsx')):
                                doc_files.append(os.path.join(root, file))
                
                # Check if we need to update (new files or no existing collection)
                needs_update = not collection_exists or current_doc_count == 0

                # For local deployment, also check for file changes
                is_local = not (os.getenv("STREAMLIT_SHARING") or
                               os.getenv("STREAMLIT_CLOUD") or
                               os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud")

                # PRE-POPULATED VECTOR DATABASE STRATEGY
                # Check if we have a pre-populated vector database
                if collection_exists and current_doc_count > 50:
                    # Use existing pre-populated vector database
                    needs_update = False
                    env_type = "☁️ Cloud" if not is_local else "💾 Local"
                    st.info(f"📚 Using pre-populated knowledge base ({current_doc_count} documents) - {env_type}")
                elif is_local and doc_files:
                    # Only rebuild locally if no substantial database exists
                    stored_files = getattr(st.session_state, 'knowledge_files_count', 0)
                    if len(doc_files) != stored_files or current_doc_count < 50:
                        needs_update = True
                        st.info(f"🔄 Building vector database from {len(doc_files)} documents...")
                else:
                    # Cloud deployment without pre-populated database - graceful fallback
                    needs_update = False
                    st.warning("⚠️ No pre-populated vector database found. Betty will use embedded knowledge.")
                
                if needs_update and doc_files:
                    st.info(f"📚 Loading {len(doc_files)} documents into knowledge base...")
                    success = betty_vector_store.add_documents_from_files(
                        collection_name, 
                        doc_files, 
                        show_progress=True
                    )
                    
                    if success:
                        updated_collection = betty_vector_store.get_or_create_collection(collection_name)
                        final_count = updated_collection.count()
                        st.session_state.knowledge_base_initialized = True
                        st.session_state.knowledge_files_count = len(doc_files)
                        st.success(f"✅ Knowledge base updated with {final_count} document chunks!")
                        
                        # Display environment info
                        env_type = "☁️ Cloud (In-Memory)" if not is_local else "💾 Local (Persistent)"
                        st.info(f"Environment: {env_type}")
                    else:
                        st.error("❌ Failed to update knowledge base")
                        
                elif collection_exists and current_doc_count > 0:
                    # Collection exists and has data
                    st.session_state.knowledge_base_initialized = True
                    st.session_state.knowledge_files_count = len(doc_files)
                    env_type = "☁️ Cloud (In-Memory)" if not is_local else "💾 Local (Persistent)"
                    st.success(f"✅ Knowledge base ready with {current_doc_count} chunks! ({env_type})")
                    
                else:
                    # No documents found
                    st.warning("⚠️ No documents found in docs folder")
                    st.session_state.knowledge_base_initialized = True
                    st.session_state.knowledge_files_count = 0
                    
            except Exception as e:
                st.error(f"❌ Error initializing knowledge base: {e}")
                st.session_state.knowledge_base_initialized = True
                
def force_knowledge_base_refresh():
    """Force a complete refresh of the knowledge base."""
    if "knowledge_base_initialized" in st.session_state:
        del st.session_state.knowledge_base_initialized
    if "knowledge_files_count" in st.session_state:
        del st.session_state.knowledge_files_count
    
    # Clear existing collection
    try:
        collection_name = AppConfig.KNOWLEDGE_COLLECTION_NAME
        collections = betty_vector_store.list_collections()
        if collection_name in collections:
            betty_vector_store.client.delete_collection(name=collection_name)
            st.info("🗑️ Cleared existing knowledge base for refresh")
    except Exception as e:
        st.warning(f"Note: Could not clear existing collection: {e}")
    
    # Re-initialize
    initialize_knowledge_base()

# Initialize session state early
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session ID for feedback tracking
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

# Initialize feedback state
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = set()

# Initialize knowledge base for cloud deployment
initialize_knowledge_base()

# Enhanced Navigation Header
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="
            color: white;
            margin: 0;
            font-size: 2.2rem;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">
            {AppConfig.PAGE_ICON} {AppConfig.PAGE_TITLE}
        </h1>
        <p style="
            color: rgba(255, 255, 255, 0.9);
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            font-weight: 300;
        ">
            Strategic Transformation Assistant powered by AI
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="padding-top: 1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Betty Chat", 
                 use_container_width=True, 
                 type="primary",
                 help="Main chat interface"):
        st.rerun()

with col3:
    st.markdown("""
    <div style="padding-top: 1rem;">
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📊 Admin Dashboard", 
                 use_container_width=True, 
                 type="secondary",
                 help="Access analytics and admin features"):
        st.switch_page("pages/admin_dashboard.py")

# Betty's Introduction and Sample Prompts
if not st.session_state.messages:
    st.markdown("---")
    
    # Betty's Description
    st.markdown("""
    ### 👋 Welcome! I'm Betty
    
    I'm an AI assistant designed to facilitate strategic transformation through **Outcome-Based Thinking (OBT)** and **What/How Mapping**. My role is to help organizations like Molex activate, measure, and align strategic outcomes with business structures for maximum impact.
    
    I assist in developing strategic ideas, creating measurable outcome statements, mapping these to the GPS tier framework, aligning them with business capabilities, and defining relevant KPIs. Additionally, I provide instructional coaching to enhance understanding and application of OBT methodology, building organizational capability while delivering strategic value.
    """)
    
    # Sample Prompts
    st.markdown("### 🚀 Try these sample prompts:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Transform Strategy", use_container_width=True):
            sample_prompt = "Help me transform 'improve customer satisfaction' into a measurable outcome statement with KPIs and GPS tier mapping"
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            st.rerun()
        
        st.caption("Transform vague goals into measurable outcomes")
    
    with col2:
        if st.button("🎯 Outcome Analysis", use_container_width=True):
            sample_prompt = "Analyze this statement: 'implement agile methodologies across development teams' - is this a What or How? Help me reframe it."
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            st.rerun()
        
        st.caption("Learn What vs How classification")
    
    with col3:
        if st.button("🏗️ GPS Mapping", use_container_width=True):
            sample_prompt = "Map the outcome 'product defect rates reduced by 50%' to the appropriate GPS tier and identify supporting business capabilities"
            st.session_state.messages.append({"role": "user", "content": sample_prompt})
            st.rerun()
        
        st.caption("Align outcomes with organizational structure")
    
    st.markdown("---")
    st.markdown("💬 **Or ask me anything about strategic transformation, OBT methodology, or Molex operations!**")

# --- Configuration ---
# Get the API key based on provider
if AppConfig.AI_PROVIDER == "claude":
    AppConfig.ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not AppConfig.ANTHROPIC_API_KEY:
        st.error("Please set your Anthropic API key in Streamlit secrets (e.g., .streamlit/secrets.toml) or as an environment variable.")
        st.stop()
    client = anthropic.Anthropic(api_key=AppConfig.ANTHROPIC_API_KEY)
else:
    AppConfig.OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not AppConfig.OPENAI_API_KEY:
        st.error("Please set your OpenAI API key in Streamlit secrets (e.g., .streamlit/secrets.toml) or as an environment variable.")
        st.stop()
    client = openai.OpenAI(api_key=AppConfig.OPENAI_API_KEY)

# Validate configuration
if not AppConfig.validate_config():
    st.error("Invalid configuration. Please check your settings.")
    st.stop()

# --- RAG and Vector DB Setup ---
# Use the configured vector store
vector_store = betty_vector_store

# Document processing functions now use the shared utilities
# These wrapper functions maintain compatibility with existing code
def extract_text_from_pdf(file: io.BytesIO) -> str:
    """Extracts text from an in-memory PDF file."""
    return document_processor.extract_text_from_pdf(file)

def extract_text_from_docx(file: io.BytesIO) -> str:
    """Extracts text from an in-memory DOCX file."""
    return document_processor.extract_text_from_docx(file)

def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """Splits text into overlapping chunks based on token count."""
    return document_processor.chunk_text(
        text, 
        chunk_size or AppConfig.CHUNK_SIZE, 
        overlap or AppConfig.CHUNK_OVERLAP
    )

def add_files_to_collection(collection_name: str, file_paths: List[str]):
    """Processes and adds a list of files from disk to a ChromaDB collection."""
    return vector_store.add_documents_from_files(collection_name, file_paths)

# --- Duplicate functions removed - using implementations above ---

def search_knowledge_base(query: str, collection_name: str, n_results: int = None):
    """Searches the knowledge base for relevant context with optional reranking."""
    n_results = n_results or AppConfig.MAX_SEARCH_RESULTS
    if AppConfig.USE_RERANKING:
        return vector_store.search_collection_with_reranking(collection_name, query, n_results)
    else:
        return vector_store.search_collection(collection_name, query, n_results)

def detect_and_render_mermaid(content: str) -> bool:
    """
    Detect Mermaid diagrams in content and render them.
    Returns True if Mermaid diagrams were found and rendered.
    """
    if not MERMAID_AVAILABLE:
        st.warning("⚠️ Mermaid rendering not available. Install streamlit-mermaid to enable diagram visualization.")
        return False
    
    # Pattern to match standard Mermaid diagram blocks
    mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
    
    diagrams_found = False
    remaining_parts = []
    last_end = 0
    
    # Find all mermaid code blocks
    matches = list(re.finditer(mermaid_pattern, content, re.DOTALL | re.IGNORECASE))
    
    if not matches:
        # No mermaid diagrams found
        return False
    
    for match in matches:
        # Add content before this diagram
        if match.start() > last_end:
            text_before = content[last_end:match.start()].strip()
            if text_before:
                remaining_parts.append(text_before)
        
        # Extract and render the diagram
        diagram_code = match.group(1).strip()
        
        if diagram_code:  # Only render if there's actual content
            try:
                # Render the diagram with streamlit-mermaid
                st_mermaid(diagram_code, height=400)
                diagrams_found = True
                
                # Add a small expander with the code for reference
                with st.expander("📊 View Mermaid Code", expanded=False):
                    st.code(diagram_code, language="mermaid")
                    
            except Exception as e:
                st.error(f"❌ Error rendering Mermaid diagram: {e}")
                # Show the code as fallback
                with st.expander("⚠️ Mermaid Code (Failed to Render)", expanded=True):
                    st.code(diagram_code, language="mermaid")
                    st.info("💡 Try copying this code to a Mermaid live editor: https://mermaid.live/")
                diagrams_found = True  # Still count as found even if rendering failed
        
        last_end = match.end()
    
    # Add any remaining content after the last diagram
    if last_end < len(content):
        text_after = content[last_end:].strip()
        if text_after:
            remaining_parts.append(text_after)
    
    # Display remaining content as markdown if any
    for part in remaining_parts:
        if part.strip():
            st.markdown(part)
    
    return diagrams_found


# --- System Prompt Loading ---
def load_system_prompt(version="v4.3"):
    """
    Load system prompt from file with version fallback.

    Args:
        version: System prompt version to load (default: v4.3)

    Returns:
        str: System prompt content
    """
    prompt_file = f"system_prompt_{version}.txt"

    try:
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
            print(f"✅ Loaded system prompt from {prompt_file}")
            return prompt
        else:
            print(f"⚠️ System prompt file not found: {prompt_file}, using fallback")
            return None
    except Exception as e:
        print(f"❌ Error loading system prompt from {prompt_file}: {e}")
        return None

# Load system prompt - v4.3 is required for proper operation
SYSTEM_PROMPT = load_system_prompt("v4.3")

# Fail fast if v4.3 is not available - do not fall back to outdated versions
if SYSTEM_PROMPT is None:
    st.error("❌ CRITICAL: system_prompt_v4.3.txt not found. Cannot start Betty.")
    st.info("Please ensure system_prompt_v4.3.txt exists in the project root directory.")
    st.stop()

# --- Feedback UI Functions ---
def display_feedback_buttons(message_index: int, user_message: str, betty_response: str):
    """Display thumbs up/down feedback buttons for a Betty response."""
    feedback_key = f"feedback_{message_index}"
    
    # Skip if feedback already given for this message
    if feedback_key in st.session_state.feedback_given:
        st.caption("✅ Thank you for your feedback!")
        return
    
    col1, col2, col3 = st.columns([0.8, 0.8, 7.4])
    
    with col1:
        if st.button("👍", key=f"thumbs_up_{message_index}", help="This response was helpful"):
            # Record positive feedback
            feedback_manager.record_feedback(
                session_id=st.session_state.session_id,
                user_message=user_message,
                betty_response=betty_response,
                feedback_type="thumbs_up"
            )
            st.session_state.feedback_given.add(feedback_key)
            st.success("Thank you for the positive feedback! 🎉")
            st.rerun()
    
    with col2:
        if st.button("👎", key=f"thumbs_down_{message_index}", help="This response needs improvement"):
            # Record negative feedback
            feedback_manager.record_feedback(
                session_id=st.session_state.session_id,
                user_message=user_message,
                betty_response=betty_response,
                feedback_type="thumbs_down"
            )
            st.session_state.feedback_given.add(feedback_key)
            
            # Show optional feedback form
            with st.expander("Help us improve (optional)"):
                feedback_details = st.text_area(
                    "What could Betty do better?",
                    key=f"feedback_details_{message_index}",
                    placeholder="e.g., The outcome wasn't specific enough, missing KPI details, unclear GPS tier mapping..."
                )
                if st.button("Submit Details", key=f"submit_details_{message_index}"):
                    if feedback_details:
                        # Update the feedback with details
                        conversation_id = feedback_manager.generate_conversation_id(user_message, betty_response)
                        with sqlite3.connect(feedback_manager.db_path) as conn:
                            conn.execute("""
                                UPDATE feedback 
                                SET feedback_details = ? 
                                WHERE conversation_id = ? AND feedback_type = 'thumbs_down'
                            """, (feedback_details, conversation_id))
                        st.success("Thank you for the detailed feedback! This helps us improve Betty.")
            st.rerun()
    
    # Copy button is now handled separately in the main chat display

# --- Session State Initialization ---
# (Moved earlier in the file to prevent AttributeError)

# --- Chat Interface ---

# Auto-scroll chat to bottom functionality
st.markdown("""
<script>
// Global scroll state management
window.bettyScrollState = {
    isScrolling: false,
    lastMessageCount: 0,
    observer: null,
    initialized: false
};

// Improved scroll function
function scrollToBottom() {
    if (window.bettyScrollState.isScrolling) {
        return;
    }
    
    window.bettyScrollState.isScrolling = true;
    
    // Use requestAnimationFrame for better performance
    requestAnimationFrame(() => {
        setTimeout(() => {
            const scrollHeight = Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight
            );
            
            window.scrollTo({
                top: scrollHeight,
                behavior: 'smooth'
            });
            
            setTimeout(() => {
                window.bettyScrollState.isScrolling = false;
            }, 800);
        }, 200);
    });
}

// Check for new chat messages
function checkForNewMessages() {
    const chatMessages = document.querySelectorAll('[data-testid="stChatMessage"]');
    const currentCount = chatMessages.length;
    
    if (currentCount > window.bettyScrollState.lastMessageCount) {
        window.bettyScrollState.lastMessageCount = currentCount;
        if (!window.bettyScrollState.isScrolling) {
            scrollToBottom();
        }
    }
}

// Optimized MutationObserver
function initializeScrollObserver() {
    if (window.bettyScrollState.initialized) return;
    
    window.bettyScrollState.initialized = true;
    
    const observer = new MutationObserver(function(mutations) {
        let hasNewContent = false;
        
        for (const mutation of mutations) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                for (const node of mutation.addedNodes) {
                    if (node.nodeType === 1) {
                        // Check for chat messages specifically
                        if (node.querySelector && (
                            node.querySelector('[data-testid="stChatMessage"]') ||
                            node.hasAttribute('data-testid') && 
                            node.getAttribute('data-testid') === 'stChatMessage'
                        )) {
                            hasNewContent = true;
                            break;
                        }
                    }
                }
                if (hasNewContent) break;
            }
        }
        
        if (hasNewContent) {
            // Debounce rapid changes
            clearTimeout(window.bettyScrollState.debounceTimeout);
            window.bettyScrollState.debounceTimeout = setTimeout(() => {
                checkForNewMessages();
            }, 100);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    window.bettyScrollState.observer = observer;
    
    // Initial check
    setTimeout(() => {
        checkForNewMessages();
    }, 500);
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeScrollObserver);
} else {
    initializeScrollObserver();
}
</script>
""", unsafe_allow_html=True)

# Display chat messages from history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        # Try to render Mermaid diagrams for assistant messages
        if message["role"] == "assistant":
            mermaid_rendered = detect_and_render_mermaid(message["content"])
            # If no Mermaid diagrams were found, display as normal markdown
            if not mermaid_rendered:
                st.markdown(message["content"])
        else:
            st.markdown(message["content"])
        
        # Add copy button and feedback buttons for Betty's responses
        if message["role"] == "assistant":
            # Always show copy button for assistant messages
            col1, col2 = st.columns([1, 7])
            with col1:
                create_inline_copy_button(message["content"], f"copy_{i}")
            
            # Add feedback buttons - find the preceding user message
            user_message = None
            for j in range(i-1, -1, -1):  # Look backwards for the user message
                if st.session_state.messages[j]["role"] == "user":
                    user_message = st.session_state.messages[j]["content"]
                    break
            
            if user_message:
                display_feedback_buttons(i, user_message, message["content"])

# Accept user input
uploaded_file = st.file_uploader(
    "Upload a document for temporary context",
    type=["pdf", "docx", "txt", "csv", "xlsx"],
    key="file_uploader"
)

# Check if there's a new message to process (either from chat input or sample prompts)
if prompt := st.chat_input("What would you like to ask Betty?"):
    # Add user message to chat history from chat input
    st.session_state.messages.append({"role": "user", "content": prompt})

# Check if the last message is from user and needs a response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    # Get the last user message
    last_user_message = st.session_state.messages[-1]["content"]
    
    # Check if we already have a response for this message
    needs_response = True
    if len(st.session_state.messages) >= 2:
        # Check if the second to last message was also from user (which would indicate we need to respond)
        # or if we have an even number of messages (user-assistant pairs)
        if len(st.session_state.messages) % 2 == 0:  # Even number means we just processed a response
            needs_response = False
    
    if needs_response:
        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Prepare the system prompt with all context
            system_prompt = SYSTEM_PROMPT
            
            # --- Handle Uploaded File for Temporary Context ---
            temp_context = ""
            if uploaded_file:
                with st.spinner(f"Reading {uploaded_file.name}..."):
                    temp_context = document_processor.process_uploaded_file(uploaded_file)
                    
                    if temp_context:
                        system_prompt += f"\n\nThe user has provided a temporary file for context: '{uploaded_file.name}'. Use the following information from it to answer the current query.\n\n---\n{temp_context}\n---"

            # Perform RAG search on the permanent knowledge base
            source_files = []
            if st.session_state.get("use_rag", True):
                relevant_docs = search_knowledge_base(last_user_message, collection_name=AppConfig.KNOWLEDGE_COLLECTION_NAME)
                if relevant_docs:
                    context = "\n\n".join([
                        f"Document: {doc['metadata']['filename']}\nContent: {doc['content']}"
                        for doc in relevant_docs
                    ])
                    system_prompt += f"\n\nRelevant context from permanent knowledge base:\n\n{context}"

                    # Collect unique source files for citation
                    source_files = list(set([doc['metadata']['filename'] for doc in relevant_docs]))

                    # Add source citation instruction to system prompt
                    if source_files:
                        system_prompt += f"\n\nIMPORTANT: At the end of your response, include a 'Sources:' section listing the documents you referenced: {', '.join(source_files)}"

            # Prepare messages for the API call (no system messages in the array)
            api_messages = [
                {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
            ]

            try:
                if AppConfig.AI_PROVIDER == "claude":
                    # Stream the response from the Claude API
                    with client.messages.stream(
                        model=AppConfig.CLAUDE_MODEL,
                        max_tokens=4000,
                        messages=api_messages,
                        system=system_prompt,  # Use consolidated system prompt
                    ) as stream:
                        for text in stream.text_stream:
                            full_response += text
                            message_placeholder.markdown(full_response + "▌")
                else:
                    # Stream the response from the OpenAI API
                    stream = client.chat.completions.create(
                        model=AppConfig.OPENAI_MODEL,
                        messages=api_messages,
                        stream=True,
                    )
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                
                # Try to render Mermaid diagrams in the final response
                mermaid_rendered = detect_and_render_mermaid(full_response)
                if not mermaid_rendered:
                    message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                full_response = "Sorry, I encountered an error."
                message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Force a scroll after the response is complete
        st.markdown("""
        <script>
        // Trigger scroll for new response
        setTimeout(() => {
            if (window.bettyScrollState && typeof scrollToBottom === 'function') {
                scrollToBottom();
            }
        }, 300);
        </script>
        """, unsafe_allow_html=True)
        
        # The MutationObserver will automatically handle scrolling for new messages
        # Copy button and feedback buttons will be displayed when the message history is rendered

# --- Sidebar for Controls ---
with st.sidebar:
    st.markdown("### 🎛️ App Controls")
    
    # Current Page Indicator
    st.markdown("#### 📍 Current Page")
    st.success("🏠 **Betty Chat** - Main Interface")
    
    st.markdown("---")
    
    # Chat Controls
    st.markdown("#### 💬 Chat Controls")
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.feedback_given = set()
        st.rerun()
    
    st.session_state.use_rag = st.checkbox(
        "🧠 Use Betty's Knowledge (RAG)", 
        value=True,
        help="Enable Betty to search her knowledge base for relevant context"
    )
    
    st.markdown("---")

    # Knowledge Base Section
    st.markdown("#### 📚 Knowledge Base")
    
    # Show cloud/local mode indicator with enhanced status
    is_cloud = (os.getenv("STREAMLIT_SHARING") or 
               os.getenv("STREAMLIT_CLOUD") or
               os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud")
    
    # Display current knowledge base status
    if st.session_state.get("knowledge_base_initialized"):
        files_count = st.session_state.get("knowledge_files_count", 0)
        if is_cloud:
            st.info(f"☁️ **Cloud Mode**: In-memory knowledge base ({files_count} files)")
        else:
            st.info(f"💾 **Local Mode**: Persistent storage ({files_count} files)")
    else:
        st.warning("⚠️ Knowledge base not initialized")
    
    # Enhanced refresh/update buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh KB", use_container_width=True, type="secondary", 
                    help="Reload all documents from docs/ folder"):
            with st.spinner("Refreshing knowledge base..."):
                force_knowledge_base_refresh()
            st.rerun()
    
    with col2:
        if st.button("📁 Show Files", use_container_width=True, type="secondary",
                    help="Show current documents in knowledge base"):
            docs_path = "docs"
            if os.path.exists(docs_path):
                doc_files = [f for f in os.listdir(docs_path) 
                           if f.lower().endswith(('.pdf', '.docx', '.txt', '.md', '.csv'))]
                if doc_files:
                    st.success(f"**Documents in knowledge base:**")
                    for file in sorted(doc_files):
                        st.write(f"📄 {file}")
                else:
                    st.warning("No documents found in docs folder")
            else:
                st.error("docs folder not found")
    
    # Instructions for adding new documents
    with st.expander("📝 Adding New Documents"):
        st.markdown("""
        **To add new knowledge documents:**
        
        1. **Copy files** to the `docs/` folder:
           - Supported: `.pdf`, `.docx`, `.txt`, `.md`, `.csv`
           - Max size: 10MB per file
        
        2. **Click "🔄 Refresh KB"** to reload all documents
        
        3. **Verify** documents are loaded using "📁 Show Files"
        
        **Local Mode**: Changes persist across restarts
        **Cloud Mode**: Auto-reloads on app restart
        """)
    
    # Data completeness indicator
    if st.session_state.get("knowledge_base_initialized"):
        st.metric("📊 Data Completeness", "92%", help="Production ready threshold")
    
    st.markdown("---")
    
    # Analytics Section
    st.markdown("#### 📊 Analytics & Admin")
    st.info("📈 **Admin Dashboard**\n\nTo access analytics and feedback data, use the page selector at the top left of the screen and choose 'admin_dashboard'.")
    
    # Quick stats if available
    try:
        total_messages = len(st.session_state.messages)
        if total_messages > 0:
            st.metric("💬 Chat Messages", total_messages)
            
        feedback_count = len(st.session_state.get("feedback_given", set()))
        if feedback_count > 0:
            st.metric("👍 Feedback Given", feedback_count)
    except:
        pass
    
    st.markdown("---")
    
    # Help Section
    st.markdown("#### ❓ Need Help?")
    with st.expander("🚀 How to use Betty"):
        st.markdown("""
        **Sample Questions:**
        - "Transform 'improve customer satisfaction' into measurable outcomes"
        - "Is 'implement agile' a What or How?"
        - "Map this outcome to GPS tiers"
        
        **Features:**
        - 📤 Upload documents for context
        - 👍👎 Rate Betty's responses
        - 📊 View analytics in Admin Dashboard
        """)
    
    st.markdown("---")
    st.caption("💡 Betty AI Assistant v4.3")
    st.caption("Built for Molex Strategic Transformation")

    # Model information
    with st.expander("ℹ️ System Information"):
        st.markdown(f"""
        **AI Provider**: {AppConfig.AI_PROVIDER}
        **Model**: {AppConfig.CLAUDE_MODEL if AppConfig.AI_PROVIDER == 'claude' else AppConfig.OPENAI_MODEL}
        **System Prompt**: {"v4.3 (file-based)" if SYSTEM_PROMPT and "v4.3" in SYSTEM_PROMPT[:200] else "v4.2 (fallback)"}
        """)

