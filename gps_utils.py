from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_gps(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    gps_info = {}

    if not exif_data:
        return None

    for tag, value in exif_data.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for t in value:
                gps_info[GPSTAGS.get(t, t)] = value[t]

    if not gps_info:
        return None

    def convert_to_degrees(value):
        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1]
        s = value[2][0] / value[2][1]
        return d + (m / 60.0) + (s / 3600.0)

    lat = convert_to_degrees(gps_info["GPSLatitude"])
    if gps_info["GPSLatitudeRef"] != "N":
        lat = -lat

    lon = convert_to_degrees(gps_info["GPSLongitude"])
    if gps_info["GPSLongitudeRef"] != "E":
        lon = -lon

    return (lat, lon)
