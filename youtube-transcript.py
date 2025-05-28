from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
from datetime import datetime

def get_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    # If the input is just a video ID (not a URL), return it directly
    if not url.startswith('http') and not url.startswith('www'):
        return url
        
    parsed_url = urlparse(url)
    
    # Handle youtube.com URLs
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query = parse_qs(parsed_url.query)
        video_id = query.get('v', [None])[0]
        if video_id:
            # Strip any additional parameters after the video ID (if any)
            return video_id.split('&')[0]
        return None
    # Handle youtu.be URLs
    elif parsed_url.hostname == 'youtu.be':
        # Strip any query parameters
        path = parsed_url.path.lstrip('/')
        return path.split('?')[0]
    else:
        return None

def fetch_transcript(video_id, language='en'):
    """
    Fetch the transcript for a given YouTube video ID.
    """
    try:
        # Fetch transcript in the specified language
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        
        # Combine the transcript segments into a single string
        transcript_text = "\n".join([segment['text'] for segment in transcript])
        return transcript_text

    except TranscriptsDisabled:
        print("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        print("No transcript available for this video.")
    except Exception as e:
        print(f"An error occurred: {e}")

def save_transcript(transcript, video_id, filename="transcript.txt"):
    """
    Save the transcript to a text file with datetime appended and video ID at the start.
    """
    # Get current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    
    # Split filename and extension to insert timestamp
    if "." in filename:
        name, ext = filename.rsplit(".", 1)
        filename_with_datetime = f"{name}-{timestamp}.{ext}"
    else:
        filename_with_datetime = f"{filename}-{timestamp}"
    
    # Prepare content with video ID at the start
    content = f"YouTube Video ID: {video_id}\nYouTube Link: https://www.youtube.com/watch?v={video_id}\n\n{transcript}"
    
    with open(filename_with_datetime, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Transcript saved to {filename_with_datetime}")

if __name__ == "__main__":
    try:
        # Get YouTube video URL
        youtube_url = input("Enter YouTube video URL or ID: ").strip()
        
        # Extract video ID
        video_id = get_video_id(youtube_url)
        
        if not video_id:
            print("Error: Invalid YouTube URL or ID. Please provide a valid YouTube URL or video ID.")
        else:
            print(f"\nProcessing video ID: {video_id}")
            
            # Fetch transcript
            print("\nFetching transcript...")
            transcript = fetch_transcript(video_id)
            
            if transcript:
                print("\nTranscript successfully retrieved!")
                
                # Save transcript to a file with video ID and metadata
                save_transcript(transcript, video_id)
                print("\nDone!")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please try again with a different video.")
        
    print("\n(Use Ctrl+C to exit)")