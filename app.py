import streamlit as st
import openai

# Initialize OpenAI client using Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set page configuration
st.set_page_config(
    page_title="Archival Assistant",
    page_icon="📚",
    layout="wide"
)

# Add voice recording JavaScript
st.markdown("""
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
<script>
let isRecording = false;
let recognition = null;

function startRecording() {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Speech recognition is not supported in this browser. Please use Chrome.');
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = function(event) {
        const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');
        document.getElementById('input').value = transcript;
    };

    recognition.onend = function() {
        isRecording = false;
        document.getElementById('recordButton').textContent = '🎤 Start Recording';
        document.getElementById('recordButton').style.backgroundColor = '#FF4B4B';
    };

    if (!isRecording) {
        recognition.start();
        isRecording = true;
        document.getElementById('recordButton').textContent = '⏹️ Stop Recording';
        document.getElementById('recordButton').style.backgroundColor = '#4CAF50';
    } else {
        recognition.stop();
    }
}
</script>

<button id="recordButton" 
        onclick="startRecording()" 
        style="background-color: #FF4B4B; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">
    🎤 Start Recording
</button>
<div id="status" style="margin-top: 10px;"></div>
""", unsafe_allow_html=True)

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

# Chat interface
with st.form(key='message_form', clear_on_submit=True):
    user_input = st.text_area("Type your message or use voice input above:", 
                             key='input', 
                             height=100)
    
    st.markdown("""
    <style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)
    
    submit_button = st.form_submit_button("Send Message", use_container_width=True)

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
