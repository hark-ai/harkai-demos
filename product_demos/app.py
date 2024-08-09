import os
from google.cloud import texttospeech
from pydub import AudioSegment
import subprocess

# Ensure you have set up authentication for Google Cloud
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials.json"

def text_to_speech(text, output_file):
    client = texttospeech.TextToSpeechClient.from_service_account_json(
            "narration-box-8deaeb70acb8.json"
        )
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", 
        name="en-US-Studio-O"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    with open(output_file, "wb") as out:
        out.write(response.audio_content)

def create_silent_audio(duration_ms, output_file):
    silent_segment = AudioSegment.silent(duration=duration_ms)
    silent_segment.export(output_file, format="mp3")

def add_audio_to_video(video_file, audio_file, output_file):
    cmd = [
        "ffmpeg",
        "-i", video_file,
        "-i", audio_file,
        "-filter_complex", 
        "[1:a]aresample=async=1:first_pts=0[a1];[0:a][a1]amix=inputs=2:duration=longest",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        output_file
    ]
    subprocess.run(cmd, check=True)

def main():
    input_video = "input_video.mp4"
    output_video = "output_video.mp4"
    temp_audio = "temp_audio.mp3"

    annotations = [
        (0, "Let's dive in and see how easy it is to filter your data."),
        (2000, "We're looking at the 'expressive_styles' table, and you can see all the different columns available."),
        (4000, "To get started, we'll filter based on the 'value' column."),
        (5000, "We want to see any rows that don't have a value of 'abc'."),
        (6000, "So, we select 'value', choose the 'not equals' operator, type in 'abc', and hit 'Run Query'."),
        (10000, "Looks like we have no rows that match this criteria!"),
        (11000, "This means that every row in this table has a value of 'abc'."),
        (12000, "Pretty neat!")
    ]

    full_audio = AudioSegment.empty()

    for i, (timestamp, text) in enumerate(annotations):
        audio_file = f"audio_{i}.mp3"
        text_to_speech(text, audio_file)
        
        if i == 0:
            silence_duration = timestamp
        else:
            silence_duration = timestamp - annotations[i-1][0] - len(AudioSegment.from_mp3(f"audio_{i-1}.mp3"))
        
        if silence_duration > 0:
            silence_file = f"silence_{i}.mp3"
            create_silent_audio(silence_duration, silence_file)
            full_audio += AudioSegment.from_mp3(silence_file)
        
        full_audio += AudioSegment.from_mp3(audio_file)

    full_audio.export(temp_audio, format="mp3")

    add_audio_to_video(input_video, temp_audio, output_video)

    # Clean up temporary files
    for i in range(len(annotations)):
        os.remove(f"audio_{i}.mp3")
        if i > 0:
            os.remove(f"silence_{i}.mp3")
    os.remove(temp_audio)

if __name__ == "__main__":
    main()