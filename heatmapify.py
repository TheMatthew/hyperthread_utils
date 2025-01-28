import csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys

def csv_to_heatmap(input_csv, output_png):
    """
    Converts a CSV file with axis labels into a heatmap and saves it as a PNG.
    The first row and first column are treated as axis values.
    
    Args:
        input_csv (str): Path to the input CSV file.
        output_png (str): Path to save the output PNG file.
    """
    # Read the CSV into a 2D NumPy array
    with open(input_csv, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Extract axis labels (first row and column)
    x_labels = rows[0][1:]  # Skip the top-left cell
    y_labels = [row[0] for row in rows[1:]]  # Skip the header row
    data = np.array([[float(cell) if cell else 0 for cell in row[1:]] for row in rows[1:]])

    # Normalize the data to a 0-255 range
    data_min, data_max = np.min(data), np.max(data)
    if data_max > data_min:
        normalized_data = ((data - data_min) / (data_max - data_min) * 255).astype(np.uint8)
    else:
        normalized_data = np.zeros_like(data, dtype=np.uint8)

    # Resize data to 512x512
    heatmap = Image.fromarray(normalized_data)
    heatmap = heatmap.resize((512, 512), resample=Image.NEAREST)

    # Add axis labels
    heatmap_with_axes = Image.new("RGB", (550, 550), "white")  # Extra space for labels
    heatmap_with_axes.paste(heatmap, (38, 38))  # Offset for labels

    draw = ImageDraw.Draw(heatmap_with_axes)

    # Use default font (cross-platform lightweight approach)
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()

    # Draw x-axis labels
    for i, label in enumerate(x_labels):
        x = 38 + (i * 512 // len(x_labels))
        draw.text((x, 20), label, fill="black", font=font, anchor="mm")

    # Draw y-axis labels
    for i, label in enumerate(y_labels):
        y = 38 + (i * 512 // len(y_labels))
        draw.text((20, y), label, fill="black", font=font, anchor="mm")

    # Save as PNG
    heatmap_with_axes.save(output_png)
    print(f"Heatmap saved to {output_png}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_to_heatmap_with_axes.py <input_csv> <output_png>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_png = sys.argv[2]
    csv_to_heatmap(input_csv, output_png)

