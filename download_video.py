import argparse
import os
import re
import subprocess
import sys
import io
from loguru import logger
import yt_dlp

# Reconfigure stdout/stderr to handle Unicode characters on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def sanitize_title(title):
    """
    Làm sạch tiêu đề để tạo tên tệp hợp lệ.
    """
    # Chỉ giữ lại số, chữ cái, ký tự tiếng Trung và khoảng trắng
    title = re.sub(r'[^\w\u4e00-\u9fff \d_-]', '', title)
    # Thay thế nhiều khoảng trắng bằng một khoảng trắng
    title = re.sub(r'\s+', ' ', title)
    return title

def get_target_folder(info, folder_path):
    """
    Tạo thư mục đầu ra dựa trên thông tin video.
    """
    sanitized_title = sanitize_title(info['title'])
    sanitized_uploader = sanitize_title(info.get('uploader', 'Unknown'))
    upload_date = info.get('upload_date', 'Unknown')
    if upload_date == 'Unknown':
        return None

    output_folder = os.path.join(
        folder_path, sanitized_uploader, f'{upload_date} {sanitized_title}')

    return output_folder

def download_single_video(info, folder_path, resolution='1080p'):
    """
    Tải xuống một video đơn lẻ.
    """
    sanitized_title = sanitize_title(info['title'])
    sanitized_uploader = sanitize_title(info.get('uploader', 'Unknown'))
    upload_date = info.get('upload_date', 'Unknown')
    if upload_date == 'Unknown':
        return None
    
    output_folder = os.path.join(folder_path, sanitized_uploader, f'{upload_date} {sanitized_title}')
    video_path = os.path.join(output_folder, 'download.mp4')
    
    if os.path.exists(video_path):
        logger.info(f'Video đã được tải xuống trong {output_folder}')
        # Still check for subtitles even if video exists
        logger.info("Kiểm tra phụ đề cho video đã tồn tại...")
    else:
        resolution_value = resolution.replace('p', '')
        ydl_opts = {
            'format': f'bestvideo[ext=mp4][height<={resolution_value}]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'writeinfojson': True,
            'writethumbnail': True,
            'writesubtitles': True,
            'subtitleslangs': ['all'],
            'subtitlesformat': 'srt/best',
            'outtmpl': os.path.join(folder_path, sanitized_uploader, f'{upload_date} {sanitized_title}', 'download'),
            'ignoreerrors': True,
            'cookiefile': 'cookies.txt' if os.path.exists("cookies.txt") else None,
            'progress_hooks': [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([info['webpage_url']])
        logger.info(f'Video được tải xuống trong {output_folder}')
    
    # Always attempt to extract subtitles using FFmpeg if the video file exists
    if os.path.exists(video_path):
        extract_subtitles_with_ffmpeg(video_path, output_folder)
    
    return output_folder

def extract_subtitles_with_ffmpeg(video_path, output_folder):
    """
    Trích xuất phụ đề từ video sử dụng FFmpeg.
    """
    try:
        # Sử dụng ffprobe để lấy thông tin stream một cách chính xác hơn
        ffprobe_result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'csv=p=0', '-select_streams', 's', 
            '-show_entries', 'stream=index,codec_name,language'
        ], stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, 
           input=f'-i "{video_path}"')
        
        if ffprobe_result.returncode == 0 and ffprobe_result.stdout.strip():
            # Có phụ đề nhúng trong video
            subtitle_lines = ffprobe_result.stdout.strip().split('\n')
            extracted_count = 0
            
            for line in subtitle_lines:
                if ',' in line:
                    stream_info = line.split(',')
                    if len(stream_info) >= 3:
                        stream_index = stream_info[0]
                        codec_name = stream_info[1]
                        lang = stream_info[2] if stream_info[2] and stream_info[2] != 'und' else 'und'
                        
                        # Tạo tên file phụ đề
                        subtitle_filename = f"subtitle_stream_{stream_index}_{codec_name}_{lang}.srt"
                        subtitle_path = os.path.join(output_folder, subtitle_filename)
                        
                        # Trích xuất phụ đề
                        extract_result = subprocess.run([
                            'ffmpeg', '-i', video_path, 
                            '-map', f'0:s:{stream_index}', 
                            '-c:s', 'srt', 
                            subtitle_path
                        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        if extract_result.returncode == 0:
                            logger.info(f"Đã trích xuất phụ đề: {subtitle_filename}")
                            extracted_count += 1
                        else:
                            logger.warning(f"Lỗi khi trích xuất phụ đề stream {stream_index}: {extract_result.stderr.decode()}")
            
            if extracted_count == 0:
                logger.info("Không thể trích xuất phụ đề nhúng nào từ video")
            else:
                logger.info(f"Đã trích xuất thành công {extracted_count} phụ đề nhúng")
        else:
            logger.info("Không tìm thấy phụ đề nhúng trong video")
    except subprocess.CalledProcessError as e:
        logger.error(f"Lỗi khi trích xuất phụ đề bằng FFmpeg: {e}")
    except FileNotFoundError:
        logger.error("FFmpeg không được tìm thấy. Vui lòng cài đặt FFmpeg và thêm vào PATH.")
    except Exception as e:
        logger.error(f"Lỗi không xác định khi trích xuất phụ đề: {e}")

def progress_hook(d):
    """
    Hook để hiển thị tiến trình tải xuống.
    """
    if d['status'] == 'downloading':
        if '_percent_str' in d:
            percent = d['_percent_str']
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            logger.info(f"Đang tải xuống: {percent} | Tốc độ: {speed} | ETA: {eta}")
    elif d['status'] == 'finished':
        logger.info("Tải xuống hoàn tất, đang xử lý...")

def download_videos(info_list, folder_path, resolution='1080p'):
    """
    Tải xuống nhiều video.
    """
    last_output_folder = None
    for info in info_list:
        last_output_folder = download_single_video(info, folder_path, resolution)
    return last_output_folder

def get_info_list_from_url(url, num_videos):
    """
    Lấy danh sách thông tin video từ URL.
    """
    if isinstance(url, str):
        url = [url]

    # Tải xuống thông tin JSON trước
    ydl_opts = {
        'dumpjson': True,
        'ignoreerrors': True
    }
    
    # Only add playlistend if num_videos is greater than 0
    if num_videos > 0:
        ydl_opts['playlistend'] = num_videos

    video_info_list = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for u in url:
            result = ydl.extract_info(u, download=False)
            if 'entries' in result:
                # Playlist
                video_info_list.extend(result['entries'])
            else:
                # Video đơn lẻ
                video_info_list.append(result)
        
    return video_info_list

def download_from_url(url, folder_path, resolution='1080p', num_videos=5):
    """
    Tải xuống video từ URL.
    """
    # Tạo thư mục đầu ra nếu chưa tồn tại
    os.makedirs(folder_path, exist_ok=True)
    
    # Lấy danh sách thông tin video
    video_info_list = get_info_list_from_url(url, num_videos)
    
    # Tải xuống video
    example_output_folder = download_videos(video_info_list, folder_path, resolution)
    
    return f"Tất cả video đã được tải xuống trong thư mục {folder_path}", example_output_folder

def main():
    parser = argparse.ArgumentParser(description="Công cụ tải xuống video từ các nền tảng như YouTube, Bilibili, v.v.")
    parser.add_argument("url", nargs="?", default="https://www.bilibili.com/video/BV1m5aGzVEaj/?spm_id_from=333.1007.tianma.28-2-108.click&vd_source=388c9b36ef63cac6c5c43da37e3375fd", 
                        help="URL của video hoặc playlist")
    parser.add_argument("-o", "--output", default="downloads", help="Thư mục đầu ra (mặc định: downloads)")
    parser.add_argument("-r", "--resolution", default="1080p", 
                        choices=['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', '4320p'],
                        help="Độ phân giải video (mặc định: 1080p)")
    parser.add_argument("-n", "--num-videos", type=int, default=5, help="Số lượng video để tải xuống từ playlist (mặc định: 5, dùng -1 để tải toàn bộ playlist)")
    
    args = parser.parse_args()
    
    logger.info(f"Đang tải xuống video từ: {args.url}")
    logger.info(f"Lưu vào thư mục: {args.output}")
    logger.info(f"Độ phân giải: {args.resolution}")
    logger.info(f"Số lượng video: {args.num_videos if args.num_videos > 0 else 'Tất cả'}")
    
    try:
        status, folder = download_from_url(args.url, args.output, args.resolution, args.num_videos)
        logger.success(status)
        if folder:
            logger.info(f"Video cuối cùng được lưu trong: {folder}")
    except Exception as e:
        logger.error(f"Lỗi khi tải xuống video: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
