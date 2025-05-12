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
        # Color image: convert BGR to RGB for consistent plotting
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        colors = ('r', 'g', 'b')
        plt.figure()
        plt.title("Color Histogram")
        plt.xlabel("Pixel Value")
        plt.ylabel("Frequency")

        for i, color in enumerate(colors):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(hist, color=color)
            plt.xlim([0, 256])

        plt.show()

# Example usage:
# Replace 'your_image.jpg' with your actual image file path
show_image_histogram('source.png')
