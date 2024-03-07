# Importing necessary libraries
import os
import json
import cv2
from threading import Thread, Event
from screeninfo import get_monitors

# Defining the directory containing the videos (this should be replaced with the actual directory path)
video_directory = "data"


# Global event to signal when user input is received
user_input_received = Event()


# Function to display video
# Function to display video
def display_video(video_path):
    left_margin = 0
    top_margin = 550
    right_margin = 400
    bottom_margin = 550

    # Get monitor size
    monitor = get_monitors()[0]
    monitor_width, monitor_height = monitor.width, monitor.height

    cap = cv2.VideoCapture(video_path)
    while not user_input_received.is_set():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            continue

        frame_height, frame_width = frame.shape[:2]
        # Calculate the rectangle's top-left and bottom-right points
        start_point = (left_margin, top_margin)
        end_point = (frame_width - right_margin, frame_height - bottom_margin)
        # Rectangle color (Green) and thickness
        color = (0, 255, 0)
        thickness = 2
        # Drawing the rectangle on the frame
        cv2.rectangle(frame, start_point, end_point, color, thickness)

        # Resize frame to fit the monitor if necessary
        if frame_width > monitor_width or frame_height > monitor_height:
            scaling_factor = min(monitor_width / frame_width, monitor_height / frame_height)
            frame = cv2.resize(frame, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)

        cv2.imshow('Video', frame)
        cv2.waitKey(1)

    cap.release()
    cv2.destroyAllWindows()


# Loading existing annotations
def load_annotations(filepath):
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []


# Saving updated annotations
def save_annotations(filepath, annotations):
    with open(filepath, 'w') as file:
        json.dump(annotations, file, indent=4)


# Function to process each video

# Main function to process videos
def process_videos(directory, annotations):
    videos = [file for file in os.listdir(directory) if file.endswith(('.mp4', '.avi', '.mov'))]
    for video in videos:
        if video not in [entry['video'] for entry in annotations]:
            user_input_received.clear()
            video_thread = Thread(target=display_video, args=(os.path.join(directory, video),))
            video_thread.start()

            labels = input(
                f"Label the video {video} \n"
                f"\t1:\t Geteert; \n"
                f"\t2:\t Gepflastert; \n"
                f"\t3:\t Unbefestigt; \n"
                f"\t4;\t Unklar (oder Garage/Test Video) \n")

            while True:

                label_dict = {"1": "geteert", "2": "gepflastert", "3": "unbefestigt", "4": "unklar"}
                labels_list = [label_dict[label] for label in labels if label in label_dict]
                if len(labels_list) > 0:
                    break
                else:
                    labels = input(f"Try again:")
            user_input_received.set()

            r = ""
            for i, (label) in enumerate(labels_list):
                if i+1 < len(labels_list):
                    r += f"{label}, "
                else:
                    r += f"{label}"

            annotations.append({
                "video": video,
                "1_label": r
            })

            save_annotations('annotations.json', annotations)
            video_thread.join()


# Load and process annotations
annotations_path = 'annotations.json'
annotations = load_annotations(annotations_path)
process_videos(video_directory, annotations)


# Note: This script assumes the presence of the 'screeninfo' library for getting monitor information.
# The user should ensure this library is installed or adjust the monitor size retrieval method accordingly.



# Main execution flow
annotations_path = 'annotations.json'
annotations = load_annotations(annotations_path)
process_videos(video_directory, annotations)

# Note: The user needs to replace "/path/to/video/directory" with the actual path to the directory containing their video files.
# This script uses OpenCV for video processing, which is not directly runnable in this environment. The script is meant to be run locally.
