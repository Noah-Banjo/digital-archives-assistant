import streamlit as st
import openai
import speech_recognition as sr

# Initialize OpenAI client using Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set page configuration
st.set_page_config(
    page_title="Archival Assistant",
    page_icon="📚",
    layout="wide"
)

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

if 'audio_text' not in st.session_state:
    st.session_state['audio_text'] = ""

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

def transcribe_audio():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.markdown("🎤 **Listening... Speak now!**")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            st.markdown("Processing...")
            text = r.recognize_google(audio)
            return text
    except sr.RequestError:
        st.error("Could not request results. Check your internet connection.")
        return None
    except sr.UnknownValueError:
        st.error("Could not understand audio. Please try again.")
        return None
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

# Input method selection
st.markdown("### Input Method")
input_method = st.radio("Choose input method:", ["Text", "Voice"])

if input_method == "Voice":
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🎤 Record", type="primary"):
            transcribed_text = transcribe_audio()
            if transcribed_text:
                st.session_state['audio_text'] = transcribed_text
    
    with col2:
        if st.session_state.get('audio_text'):
            st.success(f"Transcribed: {st.session_state['audio_text']}")
            if st.button("✅ Send"):
                user_input = st.session_state['audio_text']
                context_message = f"[Service: {service}] {user_input}"
                st.session_state['messages'].append({"role": "user", "content": context_message})
                response = get_assistant_response(st.session_state['messages'])
                if response:
                    st.session_state['messages'].append({"role": "assistant", "content": response})
                st.session_state['audio_text'] = ""  # Clear the audio text

else:
    # Text input form
    with st.form(key='message_form', clear_on_submit=True):
        user_input = st.text_input("Type your message:", key='input')
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
