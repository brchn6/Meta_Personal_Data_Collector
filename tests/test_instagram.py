from unittest.mock import patch, MagicMock
from pathlib import Path
from fb_image_extractor import InstagramImageExtractor


class FakeImg:
    def __init__(self, src, width=640, height=640):
        self._src = src
        self._size = {"width": width, "height": height}
        self.size = self._size

    def get_attribute(self, attr):
        if attr == "src":
            return self._src
        return None

    def is_displayed(self):
        return True


def test_default_sections():
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser")
    assert ext.sections == ["", "tagged"]


def test_custom_sections():
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser", sections=["tagged"])
    assert ext.sections == ["tagged"]


def test_skip_profile_avatars_default():
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser")
    assert ext.skip_profile_avatars is True


def test_skip_profile_avatars_false():
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser", skip_profile_avatars=False)
    assert ext.skip_profile_avatars is False


def test_collect_large_images_skips_small_when_toggle_on():
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser", skip_profile_avatars=True)
    imgs = [
        FakeImg("https://cdninstagram.com/photo1.jpg", width=1080, height=1080),
        FakeImg("https://cdninstagram.com/avatar.jpg", width=44, height=44),
        FakeImg("https://cdninstagram.com/photo2.jpg", width=640, height=640),
    ]
    mock_driver.find_elements.return_value = imgs

    urls = set()
    ext._collect_large_images(urls)
    assert "https://cdninstagram.com/photo1.jpg" in urls
    assert "https://cdninstagram.com/photo2.jpg" in urls
    assert "https://cdninstagram.com/avatar.jpg" not in urls


def test_collect_large_images_keeps_small_when_toggle_off():
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser", skip_profile_avatars=False)
    imgs = [
        FakeImg("https://cdninstagram.com/photo1.jpg", width=1080, height=1080),
        FakeImg("https://cdninstagram.com/avatar.jpg", width=44, height=44),
    ]
    mock_driver.find_elements.return_value = imgs

    urls = set()
    ext._collect_large_images(urls)
    assert len(urls) == 2


def test_collect_skips_non_cdninstagram():
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser")
    imgs = [
        FakeImg("https://cdninstagram.com/photo.jpg", width=1080, height=1080),
        FakeImg("https://other.com/img.png", width=1080, height=1080),
    ]
    mock_driver.find_elements.return_value = imgs

    urls = set()
    ext._collect_large_images(urls)
    assert len(urls) == 1
    assert "https://cdninstagram.com/photo.jpg" in urls


@patch("fb_image_extractor.instagram.requests.get")
def test_ig_download(mock_get, tmp_path):
    mock_driver = MagicMock()
    ext = InstagramImageExtractor(mock_driver, "testuser", save_dir=str(tmp_path / "ig_out"))
    mock_get.return_value = type("Fake", (), {
        "content": b"igdata",
        "headers": {"content-type": "image/jpeg"},
        "status_code": 200,
    })()

    ext._images = ["https://cdninstagram.com/photo1.jpg"]
    count = ext.download()
    assert count == 1
    assert (tmp_path / "ig_out" / "0.jpg").exists()


def test_log_callback():
    mock_driver = MagicMock()
    logs = []

    def cb(msg):
        logs.append(msg)

    ext = InstagramImageExtractor(mock_driver, "testuser", log_callback=cb)
    ext.log("hello")
    ext.log("world")
    assert logs == ["hello", "world"]


def test_switch_to_ig_tab_not_found():
    mock_driver = MagicMock()
    mock_driver.window_handles = ["tab1", "tab2"]
    mock_driver.current_url = "https://www.facebook.com/"

    ext = InstagramImageExtractor(mock_driver, "testuser")
    result = ext._switch_to_ig_tab()
    assert result is False
