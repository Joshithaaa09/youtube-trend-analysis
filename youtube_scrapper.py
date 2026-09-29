import re

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi


# Stores the latest locally scraped videos
_scraped_videos = []


def extract_video_id(url):
    """Extract a YouTube video ID from a YouTube URL."""

    patterns = [
        r"(?:v=|youtu\.be/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


def get_transcript(video_id):
    """Fetch the English transcript for a YouTube video."""

    try:
        api = YouTubeTranscriptApi()

        transcript = api.fetch(
            video_id,
            languages=["en"]
        )

        formatted_transcript = []

        for snippet in transcript:
            formatted_transcript.append({
                "text": snippet.text,
                "start_time": snippet.start,
                "end_time": snippet.start + snippet.duration
            })

        return formatted_transcript

    except Exception as e:
        print(
            f"Transcript unavailable for {video_id}: {e}"
        )

        return []


def get_channel_videos(
    channel_url,
    num_of_posts=10,
    start_date=None,
    end_date=None
):
    """Collect videos from a YouTube channel locally."""

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": num_of_posts,
        "skip_download": True,
    }

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                channel_url,
                download=False
            )

        entries = info.get("entries", [])

        videos = []

        for entry in entries:

            if not entry:
                continue

            video_id = entry.get("id")

            if not video_id:
                continue

            upload_date = entry.get("upload_date")

            # Date filtering
            if start_date and upload_date:

                if upload_date < start_date.replace("-", ""):
                    continue

            if end_date and upload_date:

                if upload_date > end_date.replace("-", ""):
                    continue

            video_url = (
                f"https://www.youtube.com/watch?v={video_id}"
            )

            print(
                f"Processing transcript: "
                f"{entry.get('title', video_id)}"
            )

            transcript = get_transcript(video_id)

            videos.append({
                "url": video_url,
                "shortcode": video_id,
                "title": entry.get(
                    "title",
                    "Unknown title"
                ),
                "upload_date": upload_date,
                "formatted_transcript": transcript
            })

            if len(videos) >= num_of_posts:
                break

        return videos

    except Exception as e:

        print(
            f"Error collecting videos from "
            f"{channel_url}: {e}"
        )

        return []


def trigger_scraping_channels(
    channel_urls,
    num_of_posts,
    start_date,
    end_date,
    order_by="Latest",
    country=""
):
    """
    Collect YouTube videos without Bright Data
    or any API key.
    """

    global _scraped_videos

    _scraped_videos = []

    for channel_url in channel_urls:

        if not channel_url.strip():
            continue

        videos = get_channel_videos(
            channel_url=channel_url,
            num_of_posts=num_of_posts,
            start_date=start_date,
            end_date=end_date
        )

        _scraped_videos.extend(videos)

    return {
        "snapshot_id": "local_scrape",
        "status": "ready"
    }


def get_progress(snapshot_id):
    """Return the status of the local scraping process."""

    return {
        "status": "ready",
        "snapshot_id": snapshot_id
    }


def get_output(snapshot_id, format="json"):
    """Return the videos collected by the local scraper."""

    return [_scraped_videos]
