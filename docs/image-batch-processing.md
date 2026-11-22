# DornaParvaz batch image processing

The first implementation is a reusable local processing engine. It does not call an image-generation model.

## Output contract
- 750 x 450 pixels (5:3)
- Transparent PNG overlay supplied by the project
- WebP output, quality 85
- Per-image failures are recorded; other images continue
- A ZIP contains processed images and a JSON report

## Install
`pip install -r requirements.txt`

## Run
Place the approved transparent frame at `assets/dorna_frame.png`, then run:

```bash
python image_batch.py ./incoming_photos --output ./processed_images.zip
```

Optional flags: `--overlay path/to/frame.png` and `--quality 85`.

The frame file must be an RGBA PNG exactly 750x450. The crop currently uses a center focal point; the processing API accepts a normalized focal point for later manual or automatic subject positioning.

## Telegram integration
The repository's current chat workflow is a manually dispatched GitHub Actions job, not a persistent Telegram update receiver. The batch engine is intentionally decoupled until a continuously running Telegram worker and its hosting environment are selected.
