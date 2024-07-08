# NYCMTCCameras
Uses NYC Traffic Management Center Cameras to count cars in Intersections

## Introduction
Many traffic monitoring systems that utilize OpenCV require users to install cameras at their desired study locations. However, New York City is already equipped with a semi-comprehensive network of traffic cameras. The [NYC DOT Traffic Management Center’s webcams](https://webcams.nyctmc.org/map)  are available online, providing live feeds. Users can access these feeds without needing to install additional cameras. It's important to note, though, that this limits the study locations to those already equipped with a NYCTMC camera.

> [!NOTE]
This code was developed for Google Colab and may require some modification to work in other environments. 

The first code snippet captures JPG stills from the camera and saves them to a folder named "annotated frames" in the root directory of your Google Drive. It also records the image locations and corresponding filenames in a Google Spreadsheet named "ImageCaptues." After a 10-second delay, the process repeats. To stop the image capturing, use a keyboard interrupt. Other multi-camera approaches appeared to cycle through the cameras randomly, resulting in inconsistent counts. Saving the images, on the other hand, provided a more reliable outcome.

> [!TIP]
Make sure the camera is facing the same direction]
It is important to verify that the cameras you are analyzing are oriented correctly during the timeframe you are studying, as they may change direction periodically.

The second code snippet retrieves a list of images from the ‘ImageCaptures’ worksheet and utilizes TinyYOLO and OpenCV for vehicle detection. Afterward, it generates a 'DetectionCounts' worksheet containing a date/time column, a column for counts at each location, and the corresponding file location for each count, providing an opportunity for manual count verification.

## List of NYC Traffic Cameras
All traffic camera locations in NYC have been compiled into a [JSON](https://gist.github.com/camb416/f5a1b180a980b776d419) by @camb416 

## Dependencies
Dependencies are listed in requirements.txt and can be installed with the following command:
> pip install -r requirements.txt

## Acknowledgments

This project was developed with the assistance of [ChatGPT](https://chat.openai.com/), an AI language model developed by OpenAI. ChatGPT provided guidance and support in:

- Developing and optimizing the vehicle detection code using TinyYOLO and OpenCV.
- Integrating Google Sheets API for logging detection counts.
- Implementing multithreading for improved performance.
- Debugging and refining the code for better reliability and maintainability.

This project was sparked by [Leo Ueno’s post](https://blog.roboflow.com/video-stream-analysis/), which demonstrated:

- OpenCV
- Google Colab
- Google Sheets 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



