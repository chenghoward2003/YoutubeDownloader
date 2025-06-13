# Standard library imports
import os
import tempfile
import logging
import ssl
import requests
from io import BytesIO

from django.shortcuts import render, redirect
from django.http import FileResponse
from django.core.files import File
from pytubefix import YouTube
import moviepy.editor as mp
from .models import Content

ssl._create_default_https_context = ssl._create_stdlib_context
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def download_mp3(request):
    if request.method != 'POST':
        return render(request, 'mp3.html', {'content_list': get_latest_content()})
        
    youtube_url = request.POST.get('youtube_url')
    
    if not youtube_url or not youtube_url.startswith(('https://www.youtube.com/', 'https://youtu.be/')): # Check if youtube link is valid
        error_message = 'Please provide a valid YouTube URL' if not youtube_url else 'Invalid YouTube URL. Please provide a valid YouTube URL.'
        return render_with_error(request, 'mp3.html', error_message)
    
    temp_dir = tempfile.mkdtemp()
    video_path = None
    mp3_path = None
    video_clip = None
    
    try:
        yt = YouTube(youtube_url)
        video = yt.streams.filter(only_audio=True).first()
        if not video:
            return render_with_error(request, 'mp3.html', 'No audio stream found for this video')
            
        video_path = video.download(output_path=temp_dir)
        mp3_filename = f"{yt.title}.mp3"
        mp3_path = os.path.join(temp_dir, mp3_filename)
        
        video_clip = mp.AudioFileClip(video_path)
        video_clip.write_audiofile(mp3_path)
        
        save_content(yt, youtube_url)
        
        video_clip.close()
        os.remove(video_path)
        
        response = FileResponse(
            open(mp3_path, 'rb'),
            as_attachment=True,
            filename=mp3_filename
        )
        
        def cleanup():
            cleanup_resources(mp3_path=mp3_path, temp_dir=temp_dir)
        
        response.closed = cleanup
        return response
        
    except Exception as e:
        cleanup_resources(video_clip, video_path, mp3_path, temp_dir)
        logger.error(f"Error processing video: {str(e)}")
        return render_with_error(request, 'mp3.html', f'Error: {str(e)}')

def download_mp4(request):
    if request.method != 'POST':
        return render(request, 'mp4.html', {'content_list': get_latest_content()})
        
    youtube_url = request.POST.get('youtube_url')
    if not youtube_url or not youtube_url.startswith(('https://www.youtube.com/', 'https://youtu.be/')):
        error_message = 'Please provide a valid YouTube URL' if not youtube_url else 'Invalid YouTube URL. Please provide a valid YouTube URL.'
        return render_with_error(request, 'mp4.html', error_message)
    
    temp_dir = tempfile.mkdtemp()
    video_path = None
    
    try:
        yt = YouTube(youtube_url)
        video = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
        if not video:
            return render_with_error(request, 'mp4.html', 'No video stream found for this video')
            
        video_path = video.download(output_path=temp_dir)
        mp4_filename = f"{yt.title}.mp4"
        
        save_content(yt, youtube_url)
        
        response = FileResponse(
            open(video_path, 'rb'),
            as_attachment=True,
            filename=mp4_filename
        )
        
        def cleanup():
            cleanup_resources(video_path=video_path, temp_dir=temp_dir)
        
        response.closed = cleanup
        return response
        
    except Exception as e:
        cleanup_resources(video_path=video_path, temp_dir=temp_dir)
        logger.error(f"Error processing video: {str(e)}")
        return render_with_error(request, 'mp4.html', f'Error: {str(e)}')

def delete_content(request, content_id):
    if request.method == 'POST':
        try:
            content = Content.objects.get(id=content_id)
            content.delete()
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        except Content.DoesNotExist:
            return redirect('home')
    return redirect('home')

def get_latest_content(limit=6):
    return Content.objects.all().order_by('-created_at')[:limit]

def render_with_error(request, template, error_message):
    return render(request, template, {
        'error_message': error_message,
        'content_list': get_latest_content()
    })

def save_content(yt, youtube_url):
    thumbnail_url = yt.thumbnail_url
    response = requests.get(thumbnail_url)
    
    if response.status_code == 200:
        existing_content = Content.objects.filter(title=yt.title).first()
        if not existing_content:
            content_instance = Content(
                title=yt.title,
                link=youtube_url
            )
            thumbnail_file = BytesIO(response.content)
            content_instance.cover.save(f"{yt.title}.jpg", File(thumbnail_file), save=False)
            content_instance.save()

def cleanup_resources(video_clip=None, video_path=None, mp3_path=None, temp_dir=None):
    if video_clip:
        try:
            video_clip.close()
        except:
            pass
    if video_path and os.path.exists(video_path):
        try:
            os.remove(video_path)
        except:
            pass
    if mp3_path and os.path.exists(mp3_path):
        try:
            os.remove(mp3_path)
        except:
            pass
    if temp_dir and os.path.exists(temp_dir):
        try:
            os.rmdir(temp_dir)
        except:
            pass