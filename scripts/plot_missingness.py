# Create the patient-level missingness map without matplotlib

from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


# Project paths
ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "output" / "measurement_matrix.csv"
OUTPUT_FILE = ROOT / "output" / "missingness_map.png"

print("Reading:", INPUT_FILE)


# Load measurement matrix
measured_matrix = pd.read_csv(
    INPUT_FILE,
    index_col=0
)

print("Matrix shape:", measured_matrix.shape)


# Convert values to boolean
matrix = measured_matrix.astype(bool).T

# Image dimensions
cell_width = 1
row_height = 14
left_margin = 120
top_margin = 45

width = left_margin + matrix.shape[1] * cell_width
height = top_margin + matrix.shape[0] * row_height


# Create white image
img = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(img)


# Draw title
draw.text(
    (10, 10),
    "Patient-Level Measurement Availability During the First 48 Hours",
    fill="black"
)


# Draw variable names and measurement map
for row_index, variable in enumerate(matrix.index):

    y = top_margin + row_index * row_height

    # Variable name
    draw.text(
        (5, y),
        str(variable),
        fill="black"
    )

    # Patient measurement status
    for col_index, measured in enumerate(matrix.loc[variable]):

        x = left_margin + col_index * cell_width

        if measured:
            color = "black"
        else:
            color = "white"

        draw.rectangle(
            [x, y, x + cell_width, y + row_height - 1],
            fill=color
        )


# Save image
img.save(OUTPUT_FILE)

print("Saved:", OUTPUT_FILE)