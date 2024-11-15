import streamlit as st
import openai
import pandas as pd
from datetime import datetime
import json

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
if 'metadata_history' not in st.session_state:
    st.session_state['metadata_history'] = []

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

def generate_metadata(title, description, material_type, date_created, creator, subject_terms):
    """Generate structured metadata based on user input"""
    try:
        # Create metadata prompt for GPT
        prompt = f"""Generate detailed archival metadata in Markdown format for the following item using Dublin Core and DACS standards.
        
        Item Information:
        - Title: {title}
        - Description: {description}
        - Material Type: {material_type}
        - Date Created: {date_created}
        - Creator: {creator}
        - Subject Terms: {subject_terms}
        
        Please include the following sections with clear headers:

        1. Dublin Core Elements
           - Include all relevant DC elements (Title, Creator, Subject, Description, Date, Type, Format, etc.)
           
        2. DACS Elements
           - Reference Code
           - Title
           - Date
           - Extent
           - Creator
           - Scope and Content
           - Arrangement
           - Access Points
           
        3. Physical Description
           - Detailed description of physical characteristics
           - Preservation condition
           - Storage requirements
           
        4. Access and Use
           - Access restrictions
           - Copyright status
           - Preferred citation
           
        5. Administrative Information
           - Acquisition information
           - Processing information
           - Related materials
        
        Format the output in clear Markdown with proper headers and bullet points."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert archivist specializing in metadata creation following archival standards."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Save to session state
        metadata_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "metadata": response.choices[0].message.content
        }
        st.session_state['metadata_history'].append(metadata_record)
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating metadata: {str(e)}")
        return None

def export_metadata_to_csv(metadata_records):
    """Convert metadata records to CSV format"""
    df = pd.DataFrame(metadata_records)
    return df.to_csv(index=False)

# Main interface
st.title("📚 Digital Archives Reference Desk")

# Add the sidebar
with st.sidebar:
    st.header("Navigation")
    service = st.radio(
        "Select Service:",
        ["Research Consultation", "Document Analysis", "Citation Help", "Preservation Guide", "Metadata Generator"]
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
    elif service == "Metadata Generator":
        st.info("Generate standardized metadata following Dublin Core and DACS standards.")

# Main content area
if service == "Metadata Generator":
    st.markdown("## 📋 Metadata Generator")
    st.markdown("""
    This tool generates standardized metadata following Dublin Core and DACS standards for your archival materials.
    Fill in the form below to create detailed metadata records.
    """)

    with st.form("metadata_form"):
        # Basic Information
        st.subheader("Basic Information")
        title = st.text_input("Title of Item/Collection*")
        description = st.text_area("Description*", 
            help="Provide a brief description of the material")
        
        # Material Details
        st.subheader("Material Details")
        col1, col2 = st.columns(2)
        with col1:
            material_type = st.selectbox(
                "Material Type*", 
                ["Textual Records", "Photographs", "Audio Recordings", 
                 "Video Recordings", "Digital Records", "Artifacts", 
                 "Correspondence", "Publications", "Maps/Plans", "Artwork"]
            )
        with col2:
            date_created = st.text_input(
                "Date Created*", 
                help="Enter date or date range (YYYY or YYYY-YYYY)"
            )

        # Creator and Subject Terms
        st.subheader("Creator and Subject Information")
        creator = st.text_input("Creator*", help="Enter the name of the creator(s)")
        subject_terms = st.text_area(
            "Subject Terms*", 
            help="Enter subject terms separated by commas"
        )

        submit_button = st.form_submit_button("Generate Metadata")
        
        if submit_button:
            if title and description and material_type and date_created and creator and subject_terms:
                with st.spinner("Generating metadata..."):
                    metadata = generate_metadata(
                        title, description, material_type, 
                        date_created, creator, subject_terms
                    )
                    if metadata:
                        st.success("Metadata generated successfully!")
                        st.markdown("### Generated Metadata:")
                        st.markdown(metadata)
                        
                        # Export options
                        st.markdown("### Export Options")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Download as CSV"):
                                csv_data = export_metadata_to_csv(st.session_state['metadata_history'])
                                st.download_button(
                                    label="Download CSV",
                                    data=csv_data,
                                    file_name=f"metadata_export_{datetime.now().strftime('%Y%m%d')}.csv",
                                    mime="text/csv"
                                )
                        with col2:
                            if st.button("Download as JSON"):
                                json_data = json.dumps(st.session_state['metadata_history'], indent=2)
                                st.download_button(
                                    label="Download JSON",
                                    data=json_data,
                                    file_name=f"metadata_export_{datetime.now().strftime('%Y%m%d')}.json",
                                    mime="application/json"
                                )
            else:
                st.error("Please fill in all required fields marked with *")

    # Show metadata history
    if st.session_state['metadata_history']:
        st.markdown("### Previous Metadata Records")
        for record in st.session_state['metadata_history']:
            with st.expander(f"{record['title']} - {record['timestamp']}"):
                st.markdown(record['metadata'])

else:
    # Original chat interface
    st.markdown("""
    ### Welcome to the Archives!
    I'm your digital archivist assistant. How can I help you today?
    """)

    # Chat interface
    with st.form(key='message_form', clear_on_submit=True):
        user_input = st.text_area("Type your message:", key='input', height=100)
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
