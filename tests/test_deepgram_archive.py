import json
import unittest

from outils import deepgram_archive


class ArchiveMetadataTests(unittest.TestCase):
    def test_original_mp3s_are_sorted_naturally(self):
        metadata = {
            "files": [
                {"name": "10.mp3", "source": "original", "format": "VBR MP3", "length": "30.5", "size": "100"},
                {"name": "2.ogg", "source": "derivative", "format": "Ogg Vorbis", "length": "20", "size": "90"},
                {"name": "2.mp3", "source": "original", "format": "VBR MP3", "length": "20", "size": "80"},
                {"name": "cover.png", "source": "derivative", "format": "PNG"},
            ]
        }

        files = deepgram_archive.original_mp3s(metadata)

        self.assertEqual([item.name for item in files], ["2.mp3", "10.mp3"])
        self.assertEqual(files[0].length_seconds, 20.0)

    def test_archive_download_url_quotes_arabic_and_spaces(self):
        url = deepgram_archive.archive_download_url("course-id", "شرح 1.mp3")

        self.assertEqual(
            url,
            "https://archive.org/download/course-id/%D8%B4%D8%B1%D8%AD%201.mp3",
        )


class DeepgramFormattingTests(unittest.TestCase):
    def test_deepgram_response_renders_markdown_with_utterances(self):
        response = {
            "metadata": {"request_id": "req-1", "duration": 12.3},
            "results": {
                "channels": [{"alternatives": [{"transcript": "النص الكامل", "confidence": 0.91}]}],
                "utterances": [
                    {"start": 0.1, "end": 1.5, "transcript": "السلام عليكم"},
                    {"start": 2.0, "end": 3.0, "transcript": "مرحبا"},
                ],
            },
        }

        markdown = deepgram_archive.deepgram_markdown("1.mp3", response)

        self.assertIn("# 1.mp3", markdown)
        self.assertIn("request_id: `req-1`", markdown)
        self.assertIn("confidence: `0.91`", markdown)
        self.assertIn("[00:00 - 00:02] السلام عليكم", markdown)
        self.assertIn("النص الكامل", markdown)


if __name__ == "__main__":
    unittest.main()
