import cv2
import numpy as np
import matplotlib.pyplot as plt

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

# Replace with your image file
show_image_histogram('source.png')
#show_image_histogram('control.png')
#show_image_histogram('test.png')
