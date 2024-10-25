from flask import Flask, render_template, request, send_file
from pytube import YouTube
import instaloader
import facebook_scraper as fb
import requests
import os

app = Flask(__name__)

# YouTube downloader function with format and resolution selection
def download_youtube(url, option, quality=None):
    yt = YouTube(url)
    if option == 'video':
        video = yt.streams.filter(res=quality, file_extension='mp4').first()
        return video.download(output_path="downloads/")
    elif option == 'audio':
        audio = yt.streams.filter(only_audio=True, abr=quality).first()
        return audio.download(output_path="downloads/")

# Instagram downloader with post, reel, story, audio options
def download_instagram(username, content_type):
    loader = instaloader.Instaloader(download_pictures=False, download_videos=True)
    if content_type == "post":
        loader.download_profile(username, profile_pic_only=False)
    elif content_type == "reel":
        loader.download_profile(username, download_reels=True)
    elif content_type == "story":
        loader.download_stories(usernames=[username])
    return f"downloads/{username}/"

# Facebook downloader with video, audio, and photos options
def download_facebook(url, option):
    posts = fb.get_posts(url, pages=1)
    for post in posts:
        if option == 'video' and 'video' in post:
            response = requests.get(post['video'])
            file_path = os.path.join("downloads", "facebook_video.mp4")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
        elif option == 'photos' and 'image' in post:
            response = requests.get(post['image'])
            file_path = os.path.join("downloads", "facebook_photo.jpg")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            return file_path
    return None

# Pinterest downloader with video/audio options
def download_pinterest(url, option):
    # Placeholder function for Pinterest download logic
    file_path = os.path.join("downloads", "pinterest_download.mp4")
    return file_path

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling downloads with platform-specific options
@app.route('/download', methods=['POST'])
def download():
    platform = request.form.get('platform')
    url = request.form.get('url')
    option = request.form.get('option')
    quality = request.form.get('quality')
    content_type = request.form.get('content_type')

    if platform == "YouTube":
        file_path = download_youtube(url, option, quality)
    elif platform == "Instagram":
        file_path = download_instagram(url.split('/')[-1], content_type)
    elif platform == "Facebook":
        file_path = download_facebook(url, option)
    elif platform == "Pinterest":
        file_path = download_pinterest(url, option)
    else:
        return "Unsupported platform."

    if file_path:
        return send_file(file_path, as_attachment=True)
    return "Failed to download."

# Open in default browser on start
if __name__ == '__main__':
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)
