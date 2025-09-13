from io import BytesIO
from PIL import Image, ExifTags
from shared.models import ImageMeta
import base64  # ADD THIS IMPORT
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
    
    # ADD THESE TWO LINES:
    b64_data = base64.b64encode(file_bytes).decode('utf-8')
    mime_type = f"image/{im.format.lower()}"
    
    return ImageMeta(
        width=im.width, 
        height=im.height, 
        format=str(im.format), 
        exif=exif,
        bytes_b64=b64_data,    # ADD THIS LINE
        mime_type=mime_type    # ADD THIS LINE
    )