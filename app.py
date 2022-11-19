import streamlit as st
import pandas as pd
import numpy as np
from random import randint

from youtube_dl import YoutubeDL
from pydub import AudioSegment
import scrapetube


# Broadcast/ News libraries
from youtube_transcript_api import YouTubeTranscriptApi


#### User puts in youtube link, downloads video and then transcribes? ####
### Use this library: https://pypi.org/project/youtube-transcript-api/ ###

### Key Q: Can we download channel 4 and/ or iplayer content? ###

st.title('News Monitoring')
st.header('Campaign Lab Prototype - Nov 2022')
st.write("##")
st.markdown('See [this doc](https://docs.google.com/document/d/1DD6Om2AfKQ-h67_qIHvqyR58MAtHN7yQ6yNC1p5sB1Q/edit#heading=h.38g4fibegj6g) for further details')
st.write("##")

    

yt_type = st.radio('Do you want to search by video or channel?', ['Video', 'Channel'])
if yt_type == 'Video':
    try:
        video_id = st.text_input('Enter Youtube Video ID (the bit after v= in the url). E.g. VkKmPQ1AFks')
        if video_id:
            download_type = st.radio('How do you want to get transcript?', ['Youtube API', 'Download audio and transcribe'])
            if download_type == 'Youtube API':
                video_data = YouTubeTranscriptApi.get_transcript(video_id)
                text_chunks = []
                for chunk in video_data:
                    text_chunks.append(chunk['text'])
                text_output = st.radio(
                'What analysis do you want?',
                ('Full Transcript', 'Labour Mentions', 'Search'))
                # Other options: 'Sentences with other parties', 'Sentences with other parties', Sentences with politicians or SEARCH FOR KEYWORD
                if text_output == 'Full Transcript':
                    for sentence in text_chunks:
                        st.text(sentence)
                elif text_output == 'Labour Mentions': # Get 3 chunk sequence containing 'labour'
                    labour_indices = [i for i, s in enumerate(text_chunks) if 'labour' in s]
                    for i, text in enumerate(text_chunks):
                        if i in labour_indices:
                            st.subheader(f'Labour Mention Context:')
                            # labour_context_string = ' '.join(text_chunks[i-1:i+6])
                            labour_context_sequence = text_chunks[i-1:i+6]
                            for labour_str in labour_context_sequence:
                                st.text(labour_str)
                else: 
                    search_word = st.text_input('word to search')
                    if search_word:
                        search_word_indices = [i for i, s in enumerate(text_chunks) if search_word in s]
                        for i, text in enumerate(text_chunks):
                            if i in search_word_indices:
                                st.subheader(f'Search Word Mention context:')
                                # labour_context_string = ' '.join(text_chunks[i-1:i+6])
                                search_context_sequence = text_chunks[i-1:i+6]
                                for search_str in search_context_sequence:
                                    st.text(search_str)
            elif download_type == 'Download audio and transcribe':
                with st.spinner(text='In progress'):
                    audio_downloader = YoutubeDL({'format':'bestaudio'})
                    yt_link = "https://youtu.be/" + video_id
                    yt_m4a_file = audio_downloader.extract_info(yt_link)
                    yt_file_title = yt_m4a_file['title']
                    yt_file_name = yt_file_title + '-' + video_id + '.m4a'
                    wav_filename = rf"audio_{video_id}.wav"
                    # yt_m4a_file needs to be changed in track.
                    track = AudioSegment.from_file(yt_file_name,  format= 'm4a')
                    file_handle = track.export(wav_filename, format='wav')
                    vid_text_str = speech_recognizer(wav_filename)
                    st.text(vid_text_str[0:20])

    except Exception as e:
        st.text(e)
        st.text('There are no transcripts available for this youtube video')
        st.text('Try using the Download Audio and Transcrive option')

elif yt_type == 'Channel':
    try:
        id_list, views_list, title_list, time_list, text_list, url_list = [], [], [], [], [], []
        channels = ['UCyzkxMLeZDcd_Qhzh6uMgbg', 'UCeRYN0tYBQVrC2cKsxJjdow', 'UCm0yTweyAa0PwEIp0l3N_gA', 'UC0vn8ISa4LKMunLbzaXLnOQ', 'UCmbm72l60p3OH4aL4o7BFeA', 'UCnLxFpGiCi-u3RLx9uF8bOg', 'UCO79NsDE5FpMowUH1YcBFcA']
        with st.spinner(text='In progress'):
            for channel_id in channels:
                channel_dict = scrapetube.get_channel(channel_id, limit=15)
            
                for i, vid in enumerate(channel_dict):
                    # if vid['publishedTimeText']['simpleText'] == time_option:
                    #     break 
                    # else:
                    id_list.append(vid['videoId'])
                    views_list.append(vid['viewCountText']['simpleText'])
                    time_list.append(vid['publishedTimeText']['simpleText'])
                    title_list.append(vid['title']['runs'][0]['text'])
                    url_link = 'https://youtu.be/' + vid['videoId']
                    url_list.append(url_link)

                    try:
                        video_data = YouTubeTranscriptApi.get_transcript(vid['videoId'])
                        text_chunks = []
                        for chunk in video_data:
                            text_chunks.append(chunk['text'])
                            full_text = ' '.join(text_chunks)
                        text_list.append(full_text)
                    except:
                        text_list.append('No transcript')
        d = {'video_id': id_list, 'url': url_list, 'views': views_list, 'title': title_list, 'time': time_list, 'text': text_list}
        # Add in Sentiment and Summary later?
        df = pd.DataFrame(data=d)

        text_option = st.radio(
        'What analysis do you want?',
        ('Labour Mentions', 'Custom Search'))
        if text_option == 'Labour Mentions':
            for i, text in enumerate(df.text.values):
                split_text = text.split()

                search_list = ['labour', 'starmer', 'rayner', 'reeves']

                for name in search_list:
                    indices = [i for i, s in enumerate(split_text) if s == name or name in s]
                    if indices:
                        st.text('***********')
                        st.text(df.title.values[i])
                        st.text(df.url.values[i])
                        st.text(df.time.values[i])
                        st.text(df.views.values[i])
                        for j in indices:
                            st.markdown(f'**{name}** Mention Context:')
                            # labour_context_string = ' '.join(text_chunks[i-1:i+6])
                            context_sequence = split_text[j-10:j+10]
                            st.text(' '.join(context_sequence))



        elif text_option == 'Custom Search':
            try:
                custom_search_word = st.text_input('MP to search')
                if custom_search_word:
                    with st.spinner(text='In progress'):
                        for i, text in enumerate(df.text.values):
                            split_text = text.split()

                            indices = [i for i, s in enumerate(split_text) if s == custom_search_word or custom_search_word in s]
                            if indices:
                                st.text('***********')
                                st.text(df.title.values[i])
                                st.text(df.time.values[i])
                                st.text(df.views.values[i])
                                for j in indices:
                                    st.markdown(f'**{custom_search_word}** Mention Context:')
                                    # labour_context_string = ' '.join(text_chunks[i-1:i+6])
                                    context_sequence = split_text[j-10:j+10]
                                    st.text(' '.join(context_sequence))
            except:
                st.text(f'No records found in channel {channel_id} for {custom_search_word}')
                


    except Exception as e:
        st.text(e)
        st.text('There are no transcripts available for this youtube channel')

# st.text('Product Qs')
# st.text('Q1: Do you want aggregate visuals on Topics?')
# st.text('Q2: Do you want aggregate visuals sentiment?')
# st.text('Q3: Do you want aggregate visuals on num times Labour was mentioned?')
# st.text('Q3: Do you want aggregate visuals on Labour mps mentioned?')


# Have a predefined news option that looks through all news channels.