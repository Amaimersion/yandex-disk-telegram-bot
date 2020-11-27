import youtube_dl


# region Exceptions


class CustomYoutubeDLError(Exception):
    """
    Base exception for all custom `youtube_dl` errors.
    """
    pass


class UnsupportedURLError(CustomYoutubeDLError):
    """
    Provided URL is not supported by `youtube_dl` or
    not allowed by custom rules to be handled.
    """
    pass


class UnexpectedError(CustomYoutubeDLError):
    """
    Some unexpected error occured.
    """
    pass


# endregion


# region Utils


class Logger:
    """
    Custom logger for `youtube_dl`.
    """
    def debug(self, message: str) -> None:
        pass

    def warning(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass


# endregion


# region youtube_dl


def extract_info(url: str) -> dict:
    """
    Extracts info from URL.
    This info can be used to download this resource.

    - see this for supported sites -
    https://github.com/ytdl-org/youtube-dl/blob/master/docs/supportedsites.md

    :param url:
    URL to resource.
    You can safely pass any URL
    (YouTube video, direct URL to JPG, plain page, etc.)

    :returns:
    `direct_url` - can be used to download resource,
    `filename` - recommended filename.
    If provided URL not supported, then error will be
    raised. So, if result is successfully returned,
    then it is 100% valid result which can be used to
    download resource.

    :raises:
    `UnsupportedURLError`,
    `UnexpectedError`.
    """
    result = {
        "direct_url": None,
        "filename": None
    }
    info = None

    # TODO: implement execution timeout,
    # because long requests blocks server requests
    try:
        info = ydl.extract_info(url)
    except youtube_dl.DownloadError as error:
        raise UnsupportedURLError(str(error))
    except Exception as error:
        raise UnexpectedError(str(error))

    direct_url = info.get("url")

    if not direct_url:
        raise UnsupportedURLError(
            "youtube_dl didn't return direct URL"
        )

    result["direct_url"] = direct_url

    if info.get("direct"):
        result["filename"] = info.get("webpage_url_basename")
    else:
        result["filename"] = ydl.prepare_filename(info)

    return result


# endregion


options = {
    # We using `youtube_dl` to get information
    # for download and pass further to another service
    # (Yandex.Disk, for example).
    # We don't downloading anything.
    # Almost all videos with > Full HD
    # don't provide direct MP4, they are
    # using MPEG-DASH streaming.
    # It is means there is two streams:
    # one for video and one for audio.
    # These two streams should be converted
    # into one to get video with audio.
    # It is really expensive for public server.
    # Also, videos with high resolution have
    # large size, which affects at download time
    # by another service (Yandex.Disk, for example).
    # Probably it can even break the download.
    # So, passing Full HD (maxium) videos is a golden mean.
    # `best` is fallback if there is no
    # needed things (they almost always presented),
    # and in that case final result can be a
    # not that user expected.
    "format": "[height <= 1080]/best",
    "youtube_include_dash_manifest": False,
    "logger": Logger(),
    # disable downloading at all
    "simulate": True,
    "skip_download": True,
    # Ignore YouTube playlists, because large
    # playlists can take long time to parse
    # (affects at server response time)
    "extract_flat": "in_playlist",
    "noplaylist": True
}
ydl = youtube_dl.YoutubeDL(options)
