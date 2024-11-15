import streamlit as st
import openai
from streamlit.components.v1 import html

# Initialize OpenAI client using Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set page configuration
st.set_page_config(
    page_title="Archival Assistant",
    page_icon="📚",
    layout="wide"
)

# JavaScript code for speech recognition
js_code = """
<div>
    <button id="startButton" 
            style="background-color: #FF4B4B; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
        🎤 Start Recording
    </button>
    <p id="status" style="margin-top: 10px;"></p>
    <p id="output" style="margin-top: 10px;"></p>
</div>

<script>
    var outputText = "";
    
    function updateStreamlit() {
        window.parent.document.querySelector("textarea").value = outputText;
        const event = new Event('input', { bubbles: true });
        window.parent.document.querySelector("textarea").dispatchEvent(event);
    }

    const startButton = document.getElementById('startButton');
    const status = document.getElementById('status');
    const output = document.getElementById('output');
    
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        
        startButton.addEventListener('click', () => {
            if (startButton.textContent === '🎤 Start Recording') {
                recognition.start();
                startButton.textContent = '⏹️ Stop Recording';
                startButton.style.backgroundColor = '#4CAF50';
                status.textContent = 'Listening...';
            } else {
                recognition.stop();
                startButton.textContent = '🎤 Start Recording';
                startButton.style.backgroundColor = '#FF4B4B';
                status.textContent = '';
            }
        });
        
        recognition.onresult = (event) => {
            outputText = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            output.textContent = 'Transcribed: ' + outputText;
            updateStreamlit();
        };
        
        recognition.onend = () => {
            startButton.textContent = '🎤 Start Recording';
            startButton.style.backgroundColor = '#FF4B4B';
            status.textContent = '';
        };
        
        recognition.onerror = (event) => {
            console.error(event.error);
            status.textContent = 'Error: ' + event.error;
            startButton.textContent = '🎤 Start Recording';
            startButton.style.backgroundColor = '#FF4B4B';
        };
    } else {
        startButton.style.display = 'none';
        status.textContent = 'Speech recognition is not supported in this browser.';
    }
</script>
"""

# Define the archivist's knowledge
ARCHIVIST_ROLE = """
You are an experienced archivist helping researchers with:
1. Finding and accessing materials
2. Document handling guidance
3. Research methodologies
4. Citation methods
5. Preservation advice
"""

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": ARCHIVIST_ROLE}
    ]

def get_assistant_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Main interface
st.title("📚 Digital Archives Reference Desk")

# Add the sidebar
with st.sidebar:
    st.header("Navigation")
    service = st.radio(
        "Select Service:",
        ["Research Consultation", "Document Analysis", "Citation Help", "Preservation Guide"]
    )

    # Add service-specific instructions
    if service == "Research Consultation":
        st.info("Ask questions about finding and accessing archival materials.")
    elif service == "Document Analysis":
        st.info("Get help understanding and interpreting historical documents.")
    elif service == "Citation Help":
        st.info("Learn how to properly cite archival materials.")
    elif service == "Preservation Guide":
        st.info("Get guidance on document preservation and handling.")

# Main content area
st.markdown("""
### Welcome to the Archives!
I'm your digital archivist assistant. How can I help you today?
""")

# Add speech recognition component
st.markdown("### Voice Input (Optional)")
html(js_code, height=150)

# File upload option
uploaded_file = st.file_uploader("Upload a document for analysis (optional)", type=['pdf', 'txt', 'doc', 'docx'])
if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")
    st.info("You can now ask questions about the uploaded document.")

# Chat interface
st.markdown("### Ask your question:")
with st.form(key='message_form', clear_on_submit=True):
    user_input = st.text_input("Type your message (or use voice input above):", key='input')
    submit_button = st.form_submit_button(label='Send', use_container_width=True)

    if submit_button and user_input:
        context_message = f"[Service: {service}] {user_input}"
        st.session_state['messages'].append({"role": "user", "content": context_message})
        response = get_assistant_response(st.session_state['messages'])
        if response:
            st.session_state['messages'].append({"role": "assistant", "content": response})

# Display chat history
if len(st.session_state['messages']) > 1:
    st.markdown("### Consultation Notes")
    for message in reversed(st.session_state['messages'][1:]):
        if message["role"] == "user":
            display_message = message["content"].split("] ", 1)[-1] if "] " in message["content"] else message["content"]
            st.markdown(f"🔍 **Researcher:** {display_message}")
        else:
            st.markdown(f"📚 **Archivist:** {message['content']}")

# Footer
st.markdown("---")
st.markdown("*Digital Archives Assistant - Here to help with your research needs*")
