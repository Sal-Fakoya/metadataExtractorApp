from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd

# Getting file details:
import os
import uuid
from io import BytesIO

# for extracting metadata of audio file:
import eyed3

# to create temporary file:
import tempfile


##  Function to save uploaded audio to temporary file:
def save_to_temp_file(file_bytes, filename):
    temp_file_path = os.path.join(os.path.expanduser('~'), 'temp_audio.mp3')
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_bytes)
    return temp_file_path


# Example function to convert time (implement as needed)
def getTime(timestamp):
    return pd.to_datetime(timestamp, unit='s')

## Function to get time:
def getTime(time):
    return datetime.fromtimestamp(time).strftime("%m-%d-%Y %H:%M")

## Function to get exif object of an image file:
def getExif(img_filename):
    image = Image.open(img_filename)
    exif = image._getexif()  # Use _getexif() for older versions of Pillow
    
    if exif is not None:
        exif_data = {}
        
        for key, value in exif.items():
            tag_name = TAGS.get(key, key)
            exif_data[tag_name] = value
            
            if tag_name == "GPSInfo":
                gps_data = {}
                for gps_key in value.keys():
                    gps_tag_name = GPSTAGS.get(gps_key, gps_key)
                    gps_data[gps_tag_name] = value[gps_key]
                exif_data["GPSInfo"] = gps_data
        
        return exif_data
    return None


## Function to extract meta data of audio files with eyd3 library
def extract_metadata_with_eyed3(audio_file_path):
    
    # Load the audio file with eyed3
    audio = eyed3.load(audio_file_path)

    if audio and audio.tag:
        meta_tags = {
            "Title": audio.tag.title,
            "Artist": audio.tag.artist,
            "Album": audio.tag.album,
            "Track Number": audio.tag.track_num,
            "Genre": audio.tag.genre.name if audio.tag.genre else None,
            "Release Date": audio.tag.release_date
        }
    else:
        meta_tags = {}

    return meta_tags



## Function to create a temporary file
def createTempFile(file_session_state):
    # Generate a unique identifier
    unique_id = str(uuid.uuid4())
    
    # Get the original filename
    original_filename = file_session_state.name
    original_basename = os.path.basename(original_filename)
    
    # Create a unique temporary filename incorporating the original filename
    temp_file_name = f"{unique_id}_{original_basename}"
    
    # Create a temporary file path in the system's temp directory
    temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)
    
    # Write the uploaded file content to the temporary file
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_session_state.getbuffer())
        
    return temp_file_path


## Function to delete temporary file:
def deleteTempFile(temp_file_path):
    os.unlink(temp_file_path)
    return None



