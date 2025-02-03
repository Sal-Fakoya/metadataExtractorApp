from app_utils import *
from db_fxns import *


# Core Packages
import streamlit as st
import streamlit.components.v1 as stc

# EDA Packages:
import pandas as pd
import numpy as np

# Visualization Packages:
import matplotlib.pyplot as plt
import seaborn as sns

# Opening Files/Forensic MetaData: for Image
from PIL import Image
import exifread

# for PDF
from PyPDF2 import PdfReader

# Getting dates and times
from datetime import datetime
import time
from io import BytesIO


# ------------------------------- App Structure
st.set_page_config(
    page_title="Meta Data Extractor App",
    page_icon=":bar_chart:",
    layout="centered",
)

# GLOBAL VARIABLES
metadata_wiki = """
Metadata is defined as the data providing information about one or more aspects of the data;
in other words, it is used to summarize basic information about data which can make tracking
 and working with specific data easier.
"""

HTML_BANNER = """
    <div style="background-color:#3B69DB;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">MetaData Extractor</h1>
    </div>
"""

#### ------------  **Supporting Functions**


## Function to load the image file:
@st.cache_data
def loadImage(image_file):
    img = Image.open(image_file)
    return img


## Function for download:
def downloadFile(data):
    csv_file = data.to_csv().encode("utf-8")
    # Use the built-in Streamlit method for file download

    return st.download_button(
        label="Download CSV",
        data=csv_file,
        file_name="meta_result.csv",
        mime="text/csv",
    )


## Function to for download element:
def downloadElement(*args):
    if args is not None:
        with st.container():
            with st.expander("Download File"):
                final_df = pd.concat(args)

                # call the download file function
                downloadFile(data=final_df)

                st.dataframe(final_df, use_container_width=True)

                return final_df
    else:
        return "This file is has no metadata!"


## Function to get gps coordinates of image:
def getGPSCoords(gps_info):
    gps = "GPS"
    lat_long = ["Latitude", "Longitude"]
    ref = "Ref"
    latitude = "Latitude"
    longitude = "Longitude"

    for key in lat_long:
        if (gps + key in gps_info) and (gps + key + ref in gps_info):
            e = gps_info[gps + key]
            ref = gps_info[gps + key + ref]
            gps_info[key] = (
                str(e[0][0] / e[0][1])
                + f"{chr(223)}"
                + str(e[1][0] / e[1][1])
                + "'"
                + str(e[2][0] / e[2][1])
                + '"'
                + ref
            )

    if latitude in gps_info and longitude in gps_info:
        return [gps_info[latitude], gps_info[longitude]]
    else:
        st.warning("Image does not have Geo-Coordinates!")


## Function to get Decimal coordinates of image:
def getDecimalCoords(gps_info):
    gps = "GPS"
    lat_long = ["Latitude", "Longitude"]
    ref = "Ref"
    latitude = "Latitude"
    longitude = "Longitude"
    for key in lat_long:
        if gps + key in gps_info and gps + key + ref in gps_info:
            e = gps_info[gps + key]
            ref = gps_info[gps + key + ref]
            gps_info[key] = (
                e[0][0] / e[0][1] + e[1][0] / e[1][1] / 60 + e[2][0] / e[2][1] + 3600
            ) * (-1 if ref in ["S", "W"] else 1)

    if latitude in gps_info and longitude in gps_info:
        return [gps_info[latitude], gps_info[longitude]]

    else:
        st.warning("Image does not have Geo-Coordinates!")


# Get and Display file stats of document files
def getDocFileStats(imp_file_path, original_filename, key="doc_file"):
    with st.expander("File Stats: "):
        # Get file stats using the file path
        file_stats = os.stat(imp_file_path)

        # Prepare the stats data
        file_type = "pdf" if original_filename.endswith(".pdf") else "docx"
        file_size = file_stats.st_size
        stats_data = {
            "Filename": original_filename,  # Use the original filename
            "FileType": file_type,
            "FileSize (bytes)": file_size,
            "Creation Time": datetime.fromtimestamp(file_stats.st_ctime),
            "Last Modified Time": datetime.fromtimestamp(file_stats.st_mtime),
            "Last Accessed Time": datetime.fromtimestamp(file_stats.st_atime),
        }

        # track details:
        addFileDetails(original_filename, file_type, file_size, datetime.now())

        # Convert the combined file to a dataframe
        df_stats_data = pd.DataFrame(
            data=stats_data.values(), index=stats_data.keys(), columns=["Values"]
        )
        df_stats_data.index.name = "Meta Tags"

        # create the choice
        stats_choice = st.radio("Format: ", ["JSON", "DataFrame", "Table"], key=key)

        # Display the file stats based on the user's choice
        if stats_choice == "JSON":
            st.write(stats_data)
        elif stats_choice == "DataFrame":
            st.dataframe(df_stats_data, height=250, use_container_width=True)
        elif stats_choice == "Table":
            st.table(df_stats_data)

    return df_stats_data


# Get file stats for audio and images:
def getFileStats(imp_file, key, text="View File Stats"):

    with st.expander("View File Stats"):
        img_details = {
            "Filename": imp_file.name,
            "FileType": imp_file.type,
            "FileSize": imp_file.size,
        }

        # track details:
        addFileDetails(imp_file.name, imp_file.type, imp_file.size, datetime.now())

        stats_choice = st.radio(
            "Stats", ["JSON", "DataFrame", "Table"], index=0, key=key
        )

        # Getting OS details of file
        stats_info = os.stat(imp_file.readable())
        # st.write(stats_info)

        stat_details = {
            "CreatedTime": getTime(stats_info.st_ctime),
            "AccessedTime": getTime(stats_info.st_atime),
            "ModifiedTime": getTime(stats_info.st_mtime),
        }

        # Combine the JSON details and stat_details
        combined_file_details = {**img_details, **stat_details}

        # Convert the combined file to a dataframe
        df_file_details = pd.DataFrame(
            data=combined_file_details.values(),
            index=combined_file_details.keys(),
            columns=["Values"],
        )
        df_file_details.index.name = "Meta Tags"

        # Display the file stats based on the user's choice
        if stats_choice == "JSON":
            st.write(combined_file_details)
        elif stats_choice == "DataFrame":
            st.dataframe(df_file_details, height=250, use_container_width=True)
        elif stats_choice == "Table":
            st.table(df_file_details)

        return df_file_details, combined_file_details


## Function to Extract Image Metadata:
def getImageMetaData(image_file):

    # get file stats
    df_file_details, _ = getFileStats(imp_file=image_file, key="for_img")

    # ---- LAYOUT
    col1, col2 = st.columns(2)

    with col1:
        with st.expander("View Image"):
            # Text input for caption

            caption = st.text_input(
                "Enter caption",
                key="caption",
                value="",
                placeholder="Enter caption here",
            )

            if image_file is not None:
                # Update session state with the latest caption input
                # st.session_state['caption'] = caption
                img = loadImage(image_file)
                st.image(img, caption=caption, use_container_width=True)

    with col2:
        with st.expander("Default (JPEG)"):
            st.info("Using PILLOW")
            img = loadImage(image_file)
            #  st.write(dir(img)): to check image details
            # Get image details
            img_details = {
                "format": img.format,
                "format description": img.format_description,
                "filename": image_file.name,
                "size": img.size,
                "height": img.height,
                "width": img.width,
                # use getatrr to Handle the case where encoderinfo might not be available
                # "encoder": getattr(img, 'encoderinfo', 'N/A'
            }

            # convert the combined file to a dataframe:
            df_image_details = pd.DataFrame(
                data=img_details.values(), index=img_details.keys(), columns=["Values"]
            )
            df_image_details.index.name = "Meta Tags"

            st.dataframe(df_image_details, height=250)

    # Layouts for Forensic:
    f_col1, f_col2 = st.columns(2)

    with f_col1:
        with st.expander("Using Exifread Tool"):
            # exifreed.process_file class is file-like binary byte:
            meta_tags = exifread.process_file(image_file)
            # st.write(meta_tags)

            if meta_tags is not None:
                try:
                    # Process EXIF data
                    meta_tags = exifread.process_file(
                        image_file, details=False, strict=True
                    )

                    # we can handle decoding errors by converting values to strings using a dictionary comprehension
                    meta_tags_cleaned = {
                        k: v.printable.encode("latin1", "replace").decode(
                            "utf-8", "replace"
                        )
                        for k, v in meta_tags.items()
                    }

                    # Create Exif DataFrame
                    df_exif_details = pd.DataFrame(
                        data=meta_tags_cleaned.values(),
                        index=meta_tags_cleaned.keys(),
                        columns=["Values"],
                    )
                    df_exif_details.index.name = "Meta Tags"

                    # Display DataFrame:
                    st.success("Exif data decoded successfully!")
                    st.dataframe(df_exif_details, height=250)

                except UnicodeDecodeError as e:
                    st.error(f"Error decoding EXIF data: {e}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    with f_col2:
        with st.expander("Image Geo-Coordinates"):
            exif_img_details = getExif(img_filename=image_file)

            try:
                gps_info = exif_img_details

            except:
                gps_info = "None Found"

            # st.write(gps_info)

            img_coords = getDecimalCoords(gps_info)
            st.write(img_coords)

    final_df = downloadElement(df_file_details, df_image_details, df_exif_details)


## Function to get Audio file:
def getAudioFile():
    return st.file_uploader("Upload Audio", type=["mp3", "ogg"])


## Function to load page banner:
def loadBanner():
    return stc.html(HTML_BANNER)  # Banner/ Title


## Function to load page image:
def loadPageImage():
    return st.image(
        loadImage("meta-data-img.png"),
        caption="MetaData Extractor App",
        use_container_width=True,
    )


def Home():
    st.subheader("Home")

    # Include
    # Home Page Info:

    # load page image
    st.write(metadata_wiki)

    # Expanders & Columns
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.expander("Get Image MetaData 📷"):
            st.info("Image MetaData")
            st.markdown("📷")
            st.text("Upload JPEG,JPG,PNG Images")

    with col2:
        with st.expander("Get Audio MetaData 🔉"):
            st.info("Audio MetaData")
            st.markdown("🔉")
            st.text("Upload Mp3,Ogg")

    with col3:
        with st.expander("Get DocumentFiles MetaData 📄"):
            st.info("DocumentFiles MetaData")
            st.markdown("📄")
            st.text("Upload PDF, Docx")


def main():
    """Meta Extractor App"""

    createTable = createUploadedFileTable()

    loadBanner()

    # Create title and Sidebar for App
    menu = ["Home", "Image", "Audio", "DocumentFiles", "Analytics", "About"]

    # Get menu choice from the sidebar
    choice = st.sidebar.selectbox("Menu", menu)

    # if menu choice is "Home":
    if choice == "Home":
        loadPageImage()
        Home()

    elif choice == "Image":
        st.subheader("Image MetaData Extractor")

        # get image from user:
        image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

        if image_file is not None:

            getImageMetaData(image_file=image_file)
            # Image details are added to the database

            # display the os stat of the image file
            # st.write(os.stat(image_file.readable()))

    # else if menu choice is "Audio"
    elif choice == "Audio":
        st.subheader("Audio MetaData Extractor")

        audio_file = getAudioFile()

        # Initialize session state for the audio file
        if "audio_file" not in st.session_state:
            st.session_state["audio_file"] = None
            st.session_state["audio_file_bytes"] = None
            st.session_state["audio_file_type"] = None
            st.session_state["audio_file_name"] = None
        if audio_file is not None:
            # Read file contents
            audio_bytes = audio_file.read()
            # Store file contents and metadata in session state
            st.session_state["audio_file_bytes"] = audio_bytes
            st.session_state["audio_file_type"] = audio_file.type
            st.session_state["audio_file_name"] = audio_file.name
            st.session_state["audio_file"] = audio_file

        # Read and play audio file from session state
        if st.session_state["audio_file"] is not None:

            # Create a BytesIO object from the bytes
            audio_bytes_io = BytesIO(st.session_state["audio_file_bytes"])

            # Ensure the file pointer is at the beginning
            audio_bytes_io.seek(0)

            # Display current file:
            file_name = st.session_state.audio_file.name
            st.info(f"Audio File: {file_name}")

            # Layout:
            col1, col2 = st.columns(2)

            with col1:
                with st.spinner("Loading audio..."):
                    time.sleep(1)  # Simulate loading time
                    st.audio(audio_bytes_io, format=st.session_state["audio_file_type"])

            with col2:
                df_audio_details, _ = getFileStats(
                    imp_file=st.session_state["audio_file"], key="for_audio"
                )
                # st.dataframe(df_file_details)

            with st.expander("Metadata with eyed3"):
                # Save the uploaded file to a temporary file
                temp_audio_path = save_to_temp_file(
                    st.session_state["audio_file_bytes"],
                    st.session_state["audio_file_name"],
                )

                # Extract metadata using eyed3
                meta_tags = extract_metadata_with_eyed3(temp_audio_path)

                if meta_tags:
                    st.subheader("ID3 Metadata Tags:")
                    # for tag, value in meta_tags.items():
                    #     st.write(f"{tag}: {value}")
                    meta_data_details = {tag: value for tag, value in meta_tags.items()}
                    meta_data_details = pd.DataFrame(
                        data=meta_data_details.values(),
                        index=meta_data_details.keys(),
                        columns=["Values"],
                    )
                    meta_data_details.index.name = "Meta Tags"
                    st.dataframe(meta_data_details)

                else:
                    st.warning("No metadata tags found in the audio file.")
                    meta_data_details = 0

            with st.expander("Download File"):
                try:

                    if meta_data_details == 0:
                        downloadFile(df_audio_details)
                        # st.table(data = df_audio_details)
                        st.dataframe(df_audio_details, use_container_width=True)

                    elif df_audio_details is None:
                        downloadFile(meta_data_details)

                    else:
                        downloadElement(df_audio_details, meta_data_details)

                except Exception as e:
                    st.warning(f"An error occured {e}")

        # mutagen library is used in this block to extract audio file:

        # audio()

    # else if menu choice is "DocumentFiles"
    elif choice == "DocumentFiles":
        st.subheader("DocumentFiles MetaData Extractor")

        # File Upload:
        text_file = st.file_uploader(
            "Upload a file", type=["pdf", "docx"], key="upload_docFile"
        )

        if "upload_text" not in st.session_state:
            st.session_state["upload_text"] = None

        if text_file is not None:
            st.session_state["upload_text"] = text_file

        if st.session_state["upload_text"] is not None:
            try:
                # Create a temporary file and get the path
                temp_file_path = createTempFile(st.session_state["upload_text"])

                # Get the original filename
                original_filename = st.session_state["upload_text"].name
                st.info(f"File: {original_filename}")

                # Create layout columns
                col1, col2 = st.columns(2)

                with col1:
                    # Get file stats using temporary file
                    text_file_stats = getDocFileStats(
                        imp_file_path=temp_file_path,
                        original_filename=original_filename,
                    )

                    # Convert stats_data to a DataFrame for display
                    # df_file_stats = pd.DataFrame(text_file_stats.items(), columns=["Meta Tags", "Value"])

                    # Display the file statistics
                    # st.dataframe(df_file_stats)

                with col2:
                    with st.expander("Metadata"):
                        # Read the PDF file from file session_state
                        pdf_file = PdfReader(st.session_state.upload_text)

                        # Extract PDF metadata
                        pdf_info = (
                            pdf_file.metadata
                        )  # Updated attribute for PyPDF2 >= 2.0.0

                        # st.write(pdf_info)

                        # Display PDF metadata
                        st.write("PDF Metadata:")
                        if pdf_info:
                            # Convert metadata dictionary to DataFrame for display
                            pdf_info = {
                                key.lstrip("/"): value
                                for key, value in pdf_info.items()
                            }  # clean the metadata keys
                            df_pdf_metadata = pd.DataFrame(
                                data=pdf_info.values(),
                                index=pdf_info.keys(),
                                columns=["Values"],
                            )
                            df_pdf_metadata.index.name = "Meta Tags"
                            st.dataframe(
                                df_pdf_metadata, use_container_width=True, height=250
                            )
                        else:
                            st.write("No metadata found in the PDF file.")
                            df_pdf_metadata = None

                # Download expander
                if df_pdf_metadata is not None and text_file_stats is not None:
                    downloadElement(text_file_stats, df_pdf_metadata)
                elif df_pdf_metadata is None and text_file_stats is not None:
                    downloadFile(text_file_stats)
                elif text_file_stats is None and df_pdf_metadata is not None:
                    downloadFile(df_pdf_metadata)

            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                # Clean up the temporary file
                if "temp_file_path" in locals() and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        else:
            st.info("Please upload a PDF file to extract metadata.")

    elif choice == "Analytics":
        st.subheader("Analytics")

        # Monitor uploads:
        with st.expander("File Uploads History"):
            try:
                uploaded_files = viewAllData()
                df = pd.DataFrame(
                    data=uploaded_files,
                    columns=["Filename", "Filetype", "Filesize", "Upload Time"],
                )
                if df is not None:
                    st.success("View Uploaded Files")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No files have been uploaded yet.")

            except Exception as e:
                st.write("An error {e} occured")

        if df is not None:
            with st.expander("Distribution of Uploaded File Types"):
                fig, ax = plt.subplots()
                sns.countplot(x="Filetype", data=df, ax=ax)
                st.pyplot(fig)

    # else if menu choice is "About"
    elif choice == "About":
        st.subheader("About App")

        # load the page image:
        loadPageImage()


if __name__ == "__main__":
    main()
