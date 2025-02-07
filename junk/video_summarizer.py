import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json


# Streamlit webpage layout
st.title('YouTube Video Summarizer')
st.write('This app uses YouTube Transcript API and OpenAI API to summarize YouTube videos.')

# Input for OpenAI API Key
api_key = st.text_input('Enter your OpenAI API key:', type='password')

# Input for YouTube Video ID
video_id = st.text_input('Enter the YouTube Video ID:', '')

# Check if both API key and video ID are provided
if api_key and video_id:
    try:
        # Fetching the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = " ".join([t['text'] for t in transcript_list])

        # Displaying the transcript
        st.subheader('Transcript:')
        st.write(full_transcript)

        # Connect to the ChatGPT API
        endpoint = 'https://api.openai.com/v1/chat/completions'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': 'gpt-4-0613',  # or the model of your choice
            'messages': [{'role': 'user', 'content': f'Summarize the following text using bullet points: {full_transcript}'}],
            'max_tokens': 4000  # change this to whatever you want
        }

        # Send the transcript to ChatGPT for summarization
        response = requests.post(
            endpoint, headers=headers, data=json.dumps(data))

        # Check if the response is successful
        if response.status_code == 200:
            # Extracting the summary from the response
            json_response = response.json()
            summary = json_response['choices'][0]['message']['content'].strip()
            st.subheader('Summary:')
            st.write(summary)
        else:
            st.error(
                f"Error in API request: {response.status_code}, {response.text}")
    except Exception as e:
        st.error(f'An error occurred: {e}')
