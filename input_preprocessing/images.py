from io import BytesIO
from PIL import Image, ExifTags
from shared.models import ImageMeta

def extract_exif(image: Image.Image) -> dict:
    exif_data = {}
    try:
        raw = image.getexif()
        if raw:
            for tag_id, value in raw.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                try:
                    if isinstance(value, bytes):
                        value = value.decode(errors="ignore")
                except Exception:
                    pass
                exif_data[str(tag)] = value
    except Exception:
        pass
    return exif_data

def analyze_image(file_bytes: bytes, filename: str) -> ImageMeta:
    im = Image.open(BytesIO(file_bytes))
    exif = extract_exif(im)
    return ImageMeta(width=im.width, height=im.height, format=str(im.format), exif=exif)
