from typing import List
from shared.models import NormalizedIncident, MediaItem
from .utils import to_base64, detect_language, parse_latlon
import geocoder

def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.latlng  # returns [lat, lon]
    return None, None


def normalize_inputs(
    source: str,
    text: str,
    latlon_str: str | None,
    uploaded: list[tuple[str, bytes, str]],  # (filename, bytes, mime)
    notes: List[str],
) -> NormalizedIncident:
    lat, lon = parse_latlon(latlon_str)
    
    #if lat/lon not provided, try to get from IP(IP Mean Address of the user)
    if lat is None or lon is None:
        lat, lon = get_current_location()
    print("Parsed Lat/Lon:", lat, lon)
    media_items = [
        MediaItem(
            modality=("image" if m.startswith("image/") else "audio" if m.startswith("audio/") else "video" if m.startswith("video/") else "text"),
            filename=fn,
            mime_type=m,
            bytes_b64=to_base64(b),
        )
        for (fn, b, m) in uploaded
    ]
    det_lang = detect_language(text)
    print("Detected Language:", det_lang)
    print(detect_language("Hello world"))  # Output: 'en'
    print(detect_language("Bonjour tout le monde"))  # Output: 'fr'
    
    return NormalizedIncident(
        channel=source,
        text=text,
        media=media_items,
        images_meta=[],
        transcripts=[],
        lat=lat,
        lon=lon,
        detected_language=det_lang,
        notes=notes,
    )
