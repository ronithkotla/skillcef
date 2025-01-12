import streamlit as st
import speech_recognition as sr
import time
import os
from gtts import gTTS
from pdfminer.high_level import extract_text
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
import base64

GROQ_API_KEY = "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"

video_file = open("C:/Users/ronit/OneDrive/Desktop/Major/shorts.mp4", "rb")
video_bytes = video_file.read()
st.sidebar.video(video_bytes,autoplay=True,loop=True,)



on = st.sidebar.toggle("Interviewers Voice",value=True)

if on:
    st.write('Voice Enabled')
else:
    st.write("Disabled")

camera_enable = st.sidebar.checkbox("Enable camera")
st.sidebar.camera_input("Take a picture", disabled=not camera_enable)


# Initialize recognizer
recognizer = sr.Recognizer()
if 'transcription' not in st.session_state:
    st.session_state.transcription = ""

audio_file = st.sidebar.audio_input("Record your response")

# st.title("Groq Interviewer Chatbot with Voice Support")

class GroqChatbot:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-70b-versatile")

    def get_response(self, user_input):
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        prompt_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.conversation_history[-5:]])

        prompt = PromptTemplate.from_template(
            f"""
            ### CONVERSATION HISTORY:
            {prompt_text}

            ### INSTRUCTION:
            Respond as a professional interviewer chatbot. Provide basic interview questions based on conversation history and ask questions to test the skills, asking one question at a time.
            """
        )
        
        retries = 3
        for attempt in range(retries):
            try:
                response = prompt | self.llm
                result = response.invoke(input={})
                bot_response = result.content.strip()

                # Append the bot's response to the conversation history
                st.session_state.conversation_history.append({"role": "Interviewer", "content": bot_response})
                return bot_response
            except OutputParserException as e:
                return f"Error: {str(e)}"
            except Exception as e:
                if 'Rate limit reached' in str(e):
                    wait_time = 60  # Wait for 60 seconds before retrying
                    st.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return f"Error: {str(e)}"

def try2():
    # st.title("Groq Interviewer Chatbot with Voice Support")
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    
    if not st.session_state.pdf_processed:
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        if uploaded_file is not None:
            extracted_text = extract_text(uploaded_file)
            # Set the flag to indicate that the PDF has been processed
            st.session_state.pdf_processed = True

            # After processing the PDF, prompt the chatbot to start asking questions
            chatbot = GroqChatbot()
            initial_question = chatbot.get_response(extracted_text)  # Get the first question based on PDF content
            # st.session_state.conversation_history.append({"role": "Interviewer", "content": initial_question})
        if st.session_state.conversation_history:    
            for msg in st.session_state.conversation_history:
                if msg['role'] == 'user':
                    st.markdown(
                                f"""
                                <div style='text-align: right; background-color: #414A4C; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                                    <strong>You:</strong> {msg['content']}
                                </div>
                                """, unsafe_allow_html=True
                            )
                else:
                                st.markdown(
                                f"""
                                <div style='text-align: left; background-color: #000000; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                                    <strong>Inerviewer:</strong> {msg['content']}
                                </div>
                                """, unsafe_allow_html=True
                            )
            play_bot_response(bot_response=initial_question)
        
        
    if audio_file is not None:
        # Save uploaded audio file
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.getbuffer())

        # Recognize speech from audio file
        with sr.AudioFile("temp_audio.wav") as source:
            audio_data = recognizer.record(source)
            try:
                # Use Google Web Speech API to convert speech to text
                voice_text = recognizer.recognize_google(audio_data)
                st.session_state.user_input = voice_text
                
                # st.write("Transcription: ", text)
            except sr.UnknownValueError:
                st.error("Could not understand the audio.")
            except sr.RequestError:
                st.error("Could not request results from Google Speech Recognition service.")

    st.chat_input("Your Response:",key='user_input', on_change=send_message)
    
    
def send_message(): 
    if st.session_state.user_input:
        # Initialize the chatbot instance
        chatbot = GroqChatbot()
        # Get response from the chatbot with the latest user input
        bot_response = chatbot.get_response(st.session_state.user_input)
        st.title("Groq Interviewer Chatbot with Voice Support")
        if st.session_state.conversation_history:    
            for msg in st.session_state.conversation_history:
                if msg['role'] == 'user':
                        st.markdown(
                        f"""
                        <div style='text-align: right; background-color: #414A4C; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong>You:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                        st.markdown(
                        f"""
                        <div style='text-align: left; background-color: #000000; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong>Inerviewer:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True
                    )
        
        
        

        play_bot_response(bot_response)
        # Clear the input for the next question
        st.session_state.user_input = ""
    


# Function to autoplay audio using base64 encoding
def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
def play_bot_response(bot_response):
    if on:
        if bot_response:
            # Convert text to speech with fast speed (slow=False)
            tts = gTTS(bot_response, lang='en', slow=False)
            output_file = "output.mp3"
            tts.save(output_file)

            # Play the audio using Streamlit's audio player
            st.audio(output_file, format="audio/mp3")

            # Autoplay the audio using base64 encoding (in the browser)
            autoplay_audio(output_file)

        else:
            st.warning("Please enter some text to convert to speech.")


try2()
