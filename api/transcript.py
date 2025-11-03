from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

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
        raise Exception("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise Exception("No transcript available for this video.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            video_url = data.get('video_url', '').strip()

            if not video_url:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Please provide a video_url'
                }).encode())
                return

            # Extract video ID
            video_id = get_video_id(video_url)

            if not video_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Invalid YouTube URL or video ID'
                }).encode())
                return

            # Fetch transcript
            transcript = fetch_transcript(video_id)

            if not transcript:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'No transcript found for this video'
                }).encode())
                return

            # Return success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'video_id': video_id,
                'transcript': transcript
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e)
            }).encode())

    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
