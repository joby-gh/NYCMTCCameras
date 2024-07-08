# Part 2: use TinyYOLO to identify cars in the images that were captured
# 2024-07-06
import os
import cv2
import gspread
from google.colab import auth, drive, userdata
from google.auth import default
import numpy as np
import re

# Constants
YOLO_CONFIG_URL = 'https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3-tiny.cfg'
YOLO_WEIGHTS_URL = 'https://pjreddie.com/media/files/yolov3-tiny.weights'
COCO_NAMES_URL = 'https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names'
YOLO_CONFIG_PATH = 'yolov3-tiny.cfg'
YOLO_WEIGHTS_PATH = 'yolov3-tiny.weights'
YOLO_CLASSES_PATH = 'coco.names'
CONFIDENCE_THRESHOLD = 0.3
NMS_THRESHOLD = 0.4
GOOGLE_SHEET_KEY = 'YOUR_GOOGLE_SHEET_KEY'  # Replace with your Google Sheet key
WORKSHEET_NAME = 'ImageCaptures'
DETECTION_SHEET_NAME = 'DetectionCounts'
LOCATION_NAMES = ['YOUR_CAMERA_LOCATION_1', 'YOUR_CAMERA_LOCATION_2', 'YOUR_CAMERA_LOCATION_3']  # Make sure to customize this list of location names

# Download YOLO files
os.system(f'wget {YOLO_CONFIG_URL} -O {YOLO_CONFIG_PATH}')
os.system(f'wget {YOLO_WEIGHTS_URL} -O {YOLO_WEIGHTS_PATH}')
os.system(f'wget {COCO_NAMES_URL} -O {YOLO_CLASSES_PATH}')

# Load YOLO
net = cv2.dnn.readNet(YOLO_WEIGHTS_PATH, YOLO_CONFIG_PATH)
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load class names
with open(YOLO_CLASSES_PATH, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

# Authenticate Google services
def authenticate_google_services():
    auth.authenticate_user()
    creds, _ = default()
    return creds

# Setup Google Sheets
def setup_google_sheet(creds, sheet_key, sheet_name):
    googlesheets = gspread.authorize(creds)
    document = googlesheets.open_by_key(sheet_key)
    try:
        worksheet = document.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = document.add_worksheet(title=sheet_name, rows="1000", cols="20")
    return worksheet

# Setup Detection Counts worksheet
def setup_detection_sheet(creds, sheet_key, sheet_name):
    googlesheets = gspread.authorize(creds)
    document = googlesheets.open_by_key(sheet_key)
    try:
        worksheet = document.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        worksheet = document.add_worksheet(title=sheet_name, rows="1000", cols="20")
        worksheet.update('A1:E1', [['Date/Time'] + LOCATION_NAMES + ['File Location']])
    return worksheet

# Process image using Tiny YOLO
def process_image(filename):
    image = cv2.imread(filename)
    height, width, channels = image.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Information to show on screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > CONFIDENCE_THRESHOLD:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    cars_count = 0
    for i in range(len(boxes)):
        if i in indexes:
            if classes[class_ids[i]] == 'car':
                cars_count += 1

    return cars_count

# Extract date and time from filename
def extract_datetime_from_filename(filename):
    pattern = re.compile(r'\d{2}-\d{2}-\d{4}_\d{2}-\d{2}-\d{2}')
    match = pattern.search(filename)
    if match:
        return match.group().replace('_', ' ')
    return 'Unknown Date/Time'

# Main function to process images listed in Google Sheet
def main():
    # Authenticate Google services
    creds = authenticate_google_services()

    # Setup Google Sheets
    worksheet = setup_google_sheet(creds, GOOGLE_SHEET_KEY, WORKSHEET_NAME)
    detection_worksheet = setup_detection_sheet(creds, GOOGLE_SHEET_KEY, DETECTION_SHEET_NAME)

    # Iterate through each record in the Google Sheet
    records = worksheet.get_all_records()
    for idx, record in enumerate(records):
        if record.get('Processed') == 'Yes':
            continue  # Skip already processed records

        filename = record['Image Filename']
        location = record['Location']  # Assuming you have a Location column in the worksheet
        image_path = os.path.join('/content/drive/MyDrive', filename)  # Assuming images are in Google Drive

        # Process the image
        cars_count = process_image(image_path)

        # Extract date and time from filename
        datetime_str = extract_datetime_from_filename(filename)

        # Find the next empty row
        next_row = len(detection_worksheet.col_values(1)) + 1

        # Write results to the detection worksheet
        data = [datetime_str] + ['N/A'] * len(LOCATION_NAMES) + [filename]
        if location in LOCATION_NAMES:
            loc_index = LOCATION_NAMES.index(location) + 1
            data[loc_index] = cars_count

        detection_worksheet.update(f'A{next_row}:E{next_row}', [data])

        # Mark the record as processed
        worksheet.update_cell(idx + 2, worksheet.find('Processed').col, 'Yes')  # Add 'Processed' column if not present

        print(f"Processed {filename}: {cars_count} cars detected at {location}")

if __name__ == "__main__":
    main()
