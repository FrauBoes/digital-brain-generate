from moviepy.editor import VideoFileClip, AudioFileClip

def combine_audio_to_video(video_path, audio_path, output_path):
    trim_duration=30

    # Load the video file
    video = VideoFileClip(video_path)
    
    # Load the audio file
    audio = AudioFileClip(audio_path)
    
    # trim both video and audio
    video = video.subclip(0, trim_duration)
    audio = audio.subclip(0, trim_duration)
    
    # Set the trimmed audio on the trimmed video
    final_video = video.set_audio(audio)
    
    # Export the final video
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
