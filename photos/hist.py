import cv2 # OpenCV for image processing
import matplotlib.pyplot as plt # Matplotlib for plotting histograms

import tkinter as tk # Tkinter for GUI
from tkinter import filedialog # File dialog for selecting images

root = tk.Tk()
root.withdraw()

def show_image_histogram(image_path):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError("Image not found or invalid path.")

    # Check if image is grayscale or color
    if len(img.shape) == 2 or img.shape[2] == 1:
        # Grayscale image
        plt.figure()
        plt.title("Grayscale Histogram")
        plt.xlabel("Pixel Value")
        plt.ylabel("Frequency")
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        plt.plot(hist, color='black')
        plt.xlim([0, 256])
        plt.show()
    else:
        # Color image: BGR channels
        color_channels = {'r': 0, 'g': 1, 'b': 2}
        for color, channel in color_channels.items():
            plt.figure()
            plt.title(f"{color.upper()} Channel Histogram")
            plt.xlabel("Pixel Value")
            plt.ylabel("Frequency")
            hist = cv2.calcHist([img], [channel], None, [256], [0, 256])
            plt.plot(hist, color=color)
            plt.xlim([0, 256])
            plt.show()

file_types = (
        ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
        ("All files", "*.*")
    )
file_path = filedialog.askopenfilename(title="Select an image for Histograms", filetypes=file_types)

if file_path:
    show_image_histogram(file_path)
else:
    print("No file selected.")


