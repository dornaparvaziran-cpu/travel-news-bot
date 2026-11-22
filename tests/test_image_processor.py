import tempfile
import unittest
from pathlib import Path

from PIL import Image

from image_processor import process_image


class ImageProcessorTests(unittest.TestCase):
    def test_outputs_exact_dimensions_and_webp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.jpg"
            overlay = root / "overlay.png"
            output = root / "out.webp"
            Image.new("RGB", (1200, 800), "navy").save(source)
            Image.new("RGBA", (750, 450), (180, 0, 0, 0)).save(overlay)

            result = process_image(source, overlay, output)
            self.assertTrue(result.exists())
            with Image.open(result) as image:
                self.assertEqual(image.size, (750, 450))
                self.assertEqual(image.format, "WEBP")

    def test_rejects_wrong_overlay_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.jpg"
            overlay = root / "overlay.png"
            Image.new("RGB", (800, 600), "white").save(source)
            Image.new("RGBA", (100, 100), (0, 0, 0, 0)).save(overlay)
            with self.assertRaises(ValueError):
                process_image(source, overlay, root / "out.webp")


if __name__ == "__main__":
    unittest.main()
