# Part 1: capture and save images from the traffic cams - stop with Keyboard Interupt
# 2024-07-05
import cv2
import gspread
from google.auth import default
from google.colab import auth, drive, userdata
from datetime import datetime
import pytz
import os
import time

# Constants
GOOGLE_SHEET_KEY = 'YOUR_GOOGLE_SHEET_KEY'  # Replace with your Google Sheet key
WORKSHEET_NAME = 'ImageCaptures'
TIMEZONE = 'America/New_York'
DRIVE_FOLDER = '/content/drive/MyDrive/annotated_frames'
CAMERAS = {
    "Location 1": "YOUR_CAMERA_URL_1",  # Replace with your camera URL
    "Location 2": "YOUR_CAMERA_URL_2",  # Replace with your camera URL
    "Location 3": "YOUR_CAMERA_URL_3"   # Replace with your camera URL
}

def authenticate_google_colab():
    auth.authenticate_user()
    creds, _ = default()
    return creds

def setup_google_sheet(creds):
    googlesheets = gspread.authorize(creds)
    document = googlesheets.open_by_key(GOOGLE_SHEET_KEY)

    try:
        worksheet = document.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = document.add_worksheet(title=WORKSHEET_NAME, rows="1000", cols="20")

    headers = ['Date & Time', 'Location', 'Image Filename']
    if worksheet.row_values(1) != headers:
        worksheet.insert_row(headers, index=1)

    return worksheet

def save_image(location, image):
    ET = pytz.timezone(TIMEZONE)
    dateANDtime_str = datetime.now(ET).strftime("%m/%d/%Y %H:%M:%S")
    filename_date = dateANDtime_str.split()[0].replace("/", "-")
    filename_time = dateANDtime_str.split()[1].replace(":", "-")
    filename = f"{DRIVE_FOLDER}/{location.replace(' ', '_')}_{filename_date}_{filename_time}.jpg"
    cv2.imwrite(filename, image, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return dateANDtime_str, filename

def main():
    drive.mount('/content/drive')
    creds = authenticate_google_colab()
    worksheet = setup_google_sheet(creds)

    if not os.path.exists(DRIVE_FOLDER):
        os.makedirs(DRIVE_FOLDER)
        print(f"Created folder: {DRIVE_FOLDER}")
    else:
        print(f"Folder already exists: {DRIVE_FOLDER}")

    while True:
        for location, url in CAMERAS.items():
            response = cv2.VideoCapture(url)
            ret, frame = response.read()
            if ret:
                date_time, filename = save_image(location, frame)
                worksheet.append_row([date_time, location, filename], "USER_ENTERED")
                print(f"Saved image from {location} to {filename}")
            else:
                print(f"Failed to capture image from {location}")

        time.sleep(10)  # Wait for 10 seconds before capturing the next set of images

if __name__ == "__main__":
    main()
