from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query = parse_qs(parsed_url.query)
        return query.get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path.lstrip('/')
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

def save_transcript(transcript, filename="transcript.txt"):
    """
    Save the transcript to a text file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(transcript)
    print(f"Transcript saved to {filename}")

if __name__ == "__main__":
    # Example YouTube video URL
    youtube_url = input("Enter YouTube video URL or ID: ").strip()
    
    # Extract video ID
    video_id = get_video_id(youtube_url)
    
    if not video_id:
        print("Invalid YouTube URL.")
    else:
        # Fetch transcript
        transcript = fetch_transcript(video_id)
        
        if transcript:
            # Optionally, print the transcript
            print("\nTranscript:\n")
            print(transcript)
            
            # Save transcript to a file
            save_transcript(transcript)