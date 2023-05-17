import argparse
import enum
import threading

from pytube import YouTube
from pytube import Playlist

VIDEO_DIRECTORY_DEFAULT = "./videos"


class Thread(threading.Thread):
    def __init__(self, url, dir_save):
        super(Thread, self).__init__()
        self._url = url
        self._dir_save = dir_save

    def run(self) -> None:
        download_video(self._url, self._dir_save)


class Type(enum.Enum):
    VIDEO = 1
    PLAYLIST = 2


class UrlInfo:
    def __init__(self, url, url_type):
        self._url_type = url_type
        self._url = url

    @property
    def url_type(self):
        return self._url_type

    @property
    def url(self):
        return self._url


class VideoDownloader:
    def __init__(self, url_info, dir_save):
        self._url_info = url_info
        self._dir_save = dir_save

    def run(self) -> None:
        if self._url_info.url_type == Type.VIDEO:
            self.download_video()
        elif self._url_info.url_type == Type.PLAYLIST:
            self.download_playlist()

    def download_video(self):
        download_video(self._url_info.url, self._dir_save)

    def download_playlist(self):
        playlist = Playlist(self._url_info.url)

        thread_pool = []
        for url in playlist.video_urls:
            thread_pool.append(Thread(url, self._dir_save))
        for thread in thread_pool:
            thread.run()


def download_video(url, dir_save):
    video = YouTube(url)
    video = video.streams.get_highest_resolution()
    video_name = video.default_filename
    print("start download video: {video_name}".format(video_name=video_name))
    try:
        video.download(dir_save)
    except:
        print("Failed to download video")

    print("end download video: {video_name}".format(video_name=video_name))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--url", required=True, help="URL to youtube video")
    ap.add_argument("-t", "--type", required=True, help="Type of url: video or playlist")
    ap.add_argument("-d", "--dir", required=False, help="directory save video")
    args = vars(ap.parse_args())

    VideoDownloader(UrlInfo(url=args["url"], url_type=Type[args["type"].upper()]),
                    dir_save=VIDEO_DIRECTORY_DEFAULT if args["dir"] is None else args["dir"]).run()
