from pathlib import Path
from unittest.mock import patch, MagicMock
from fb_image_extractor import FacebookImageExtractor


class FakeResponse:
    def __init__(self, content=b"fake", headers=None):
        self.content = content
        self.headers = headers or {"content-type": "image/jpeg"}


def test_cred_parsing(tmp_path):
    cred_file = tmp_path / ".cred"
    cred_file.write_text(
        "FB_USERNAME=test@test.com\n"
        "FB_PASSWORD=secret\n"
        "FB_PROFILE=testuser\n"
        "SAVE_DIR=./out\n"
        "SKIP_PROFILE_COVER=true\n"
    )
    ext = FacebookImageExtractor(str(cred_file))
    assert ext.username == "test@test.com"
    assert ext.password == "secret"
    assert ext.profile == "testuser"
    assert ext.skip_profile_cover is True


def test_cred_skip_profile_cover_defaults_to_true(tmp_path):
    cred_file = tmp_path / ".cred"
    cred_file.write_text("FB_USERNAME=a\nFB_PASSWORD=b\nFB_PROFILE=c\nSAVE_DIR=./out\n")
    ext = FacebookImageExtractor(str(cred_file))
    assert ext.skip_profile_cover is True


def test_skip_profile_cover_false(tmp_path):
    cred_file = tmp_path / ".cred"
    cred_file.write_text(
        "FB_USERNAME=a\nFB_PASSWORD=b\nFB_PROFILE=c\nSAVE_DIR=./out\nSKIP_PROFILE_COVER=false\n"
    )
    ext = FacebookImageExtractor(str(cred_file))
    assert ext.skip_profile_cover is False


def test_album_list():
    assert FacebookImageExtractor.ALBUMS == ["photos_by", "photos_of"]


def test_save_dir_default(tmp_path):
    cred_file = tmp_path / ".cred"
    cred_file.write_text("FB_USERNAME=a\nFB_PASSWORD=b\nFB_PROFILE=c\n")
    ext = FacebookImageExtractor(str(cred_file))
    assert str(ext.save_dir) == "downloaded_photos"


@patch("fb_image_extractor.extractor.requests.get")
def test_download(mock_get, tmp_path):
    mock_get.return_value = FakeResponse(b"imagedata")
    cred_file = tmp_path / ".cred"
    cred_file.write_text("FB_USERNAME=a\nFB_PASSWORD=b\nFB_PROFILE=c\nSAVE_DIR=./out\n")
    ext = FacebookImageExtractor(str(cred_file))
    ext._images = ["https://scontent.xx/fbcdn.net/photo1.jpg"]
    ext.save_dir = tmp_path / "out"
    count = ext.download()
    assert count == 1
    assert (tmp_path / "out" / "0.jpg").exists()
    assert (tmp_path / "out" / "0.jpg").read_bytes() == b"imagedata"


@patch("fb_image_extractor.extractor.requests.get")
def test_download_skips_data_uris(mock_get, tmp_path):
    cred_file = tmp_path / ".cred"
    cred_file.write_text("FB_USERNAME=a\nFB_PASSWORD=b\nFB_PROFILE=c\n")
    ext = FacebookImageExtractor(str(cred_file))
    ext._images = ["data:image/svg+xml,blah", "https://scontent.xx/fbcdn.net/photo.jpg"]
    ext.save_dir = tmp_path / "out"
    mock_get.return_value = FakeResponse(b"data")
    count = ext.download()
    assert count == 1


@patch("fb_image_extractor.extractor.requests.get")
def test_download_skips_static_fbcdn(mock_get, tmp_path):
    cred_file = tmp_path / ".cred"
    cred_file.write_text("FB_USERNAME=a\nFB_PASSWORD=b\nFB_PROFILE=c\n")
    ext = FacebookImageExtractor(str(cred_file))
    ext._images = [
        "https://static.xx.fbcdn.net/emoji.png",
        "https://scontent.xx.fbcdn.net/photo.jpg",
    ]
    ext.save_dir = tmp_path / "out"
    mock_get.return_value = FakeResponse(b"data")
    count = ext.download()
    assert count == 1
