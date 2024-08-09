import moviepy.editor as mpe
from google.cloud import texttospeech
import os

# Set up Google Cloud Text-to-Speech
client = texttospeech.TextToSpeechClient.from_service_account_json("narration-box-8deaeb70acb8.json")
          

# Your script with timestamps (replace with your actual script)
script = [
    {"time": "0:00:00", "text": "Let's filter our data."},
    {"time": "0:00:02", "text": "We're looking at the 'expressive_styles' table. "}, 
    {"time": "0:00:03", "text": "We'll filter based on the 'value' column. "}, 
    {"time": "0:00:05", "text": "We want to see any rows where the value isn't 'abc'. "}, 
    {"time": "0:00:07", "text": "We select 'value', choose 'not equals', type 'abc', and run the query."},
    {"time": "0:00:10", "text": "No rows match our criteria!"},
    {"time": "0:00:11", "text": "This means every row has a 'value' of 'abc'."},
    {"time": "0:00:12", "text": "Pretty neat!"}
]

# Choose a voice (replace with desired voice)
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name='en-US-Studio-O',
 
)

# Audio configuration
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

# Generate voiceover segments
voiceover_segments = []
for segment in script:
    synthesis_input = texttospeech.SynthesisInput(text=segment["text"])
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(f"segment_{segment['time']}.mp3", "wb") as out:
        out.write(response.audio_content)
    voiceover_segments.append(
        mpe.AudioFileClip(f"segment_{segment['time']}.mp3")
    )

# Combine segments into a single voiceover track
voiceover = mpe.concatenate_audioclips(voiceover_segments)

# Load your video
video = mpe.VideoFileClip("input_video.mp4")  # Replace with your video filename

# Combine voiceover with video
final_video = video.set_audio(voiceover)

# Save the final video
final_video.write_videofile("output_with_voiceover.mp4")

# Clean up temporary audio files
for segment in script:
    temp_audio_file = f"segment_{segment['time']}.mp3"
    if os.path.exists(temp_audio_file):
        os.remove(temp_audio_file)

print("Voiceover added to the video successfully!")