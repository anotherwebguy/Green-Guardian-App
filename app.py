import streamlit as st
import os
import time
from vectors import EmbeddingsManager 
from chatbot import ChatbotManager 


if 'chatbot_manager' not in st.session_state:
    st.session_state['chatbot_manager'] = None

if 'messages' not in st.session_state:
     st.session_state['messages'] = []


st.set_page_config(
    page_title="Document Buddy App",
    layout="wide",
    initial_sidebar_state="expanded",
)

embeddings_created_flag = "embeddings_created.txt"
pdf_folder = "pdf_documents"  

if not os.path.exists(embeddings_created_flag):
    embeddings_manager = EmbeddingsManager(
        model_name="BAAI/bge-small-en",
        device="cpu",
        encode_kwargs={"normalize_embeddings": True},
        qdrant_url="http://localhost:6333",
        collection_name="vector_db"
    )
    result = embeddings_manager.create_embeddings(pdf_folder)
    st.success(result)
    with open(embeddings_created_flag, 'w') as flag_file:
        flag_file.write("Embeddings created")

if st.session_state['chatbot_manager'] is None:
    st.session_state['chatbot_manager'] = ChatbotManager(
        model_name="BAAI/bge-small-en",
        device="cpu",
        encode_kwargs={"normalize_embeddings": True},
        llm_model="llama3.2:3b",
        llm_temperature=0.7,
        qdrant_url="http://localhost:6333",
        collection_name="vector_db"
    )
    print("here4")

with st.sidebar:
    st.image("bio.png", use_container_width=True)
    st.markdown("### 📚 Preserve Nature, Nurture Life")
    st.markdown("---")
    
    menu = ["🏠 Home", "🤖 Chatbot"]
    choice = st.selectbox("Navigate", menu)

if choice == "🏠 Home":
    st.title("🤖 Green Guardian App")
    st.markdown("""
    Welcome to **Green Guardian App**! 🚀

    **Built using Open Source Stack (Llama 3.2, BGE Embeddings, and Qdrant running locally within a Docker Container.)**

    - **Chat**: Interact with our Green Guardian intelligent chatbot.

    Helps answer all your questions related to Wildlife Biodiversity Preservation! 😊
    """)

elif choice == "🤖 Chatbot":
    st.image("green.png", width=200) 
    st.title("Green Guardian Bot")
    st.markdown("---")
        
    st.header("💬 Chat with Green Guardian")
        
    if st.session_state['chatbot_manager'] is None:
        st.info("🤖 Embeddings are being processed. Please wait...")
    else:
        for msg in st.session_state['messages']:
            st.chat_message(msg['role']).markdown(msg['content'])

        if user_input := st.chat_input("Type your message here..."):
            st.chat_message("user").markdown(user_input)
            st.session_state['messages'].append({"role": "user", "content": user_input})

            with st.spinner("🤖 Responding..."):
                try:
                    answer = st.session_state['chatbot_manager'].get_response(user_input)
                    time.sleep(1)
                except Exception as e:
                    answer = f"⚠️ An error occurred while processing your request: {e}"
            
            st.chat_message("assistant").markdown(answer)
            st.session_state['messages'].append({"role": "assistant", "content": answer})

st.markdown("---")
st.markdown("© 2025 Green Guardian App. All rights reserved. 🛡️")
