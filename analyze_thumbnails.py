from PIL import Image, ImageTk
import os
from collections import Counter
import colorsys
import tkinter as tk

# Folder with thumbnails
folder = "/Users/..."
dominant_colors = {}

# --- Step 1: Analyze dominant hue ---
for filename in os.listdir(folder):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = os.path.join(folder, filename)
        img = Image.open(path)
        img = img.resize((50, 50))
        pixels = list(img.getdata())

        # Weighted HSV analysis
        hue_scores = Counter()
        for r, g, b in pixels:
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            h_deg = round(h*360)
            s_pct = s * 100
            v_pct = v * 100

            # Count colored pixels (ignore near-white/gray/black)
            if s_pct > 20 and v_pct > 20:
                hue_scores[h_deg] += s_pct

        if hue_scores:
            dominant_hue = hue_scores.most_common(1)[0][0]
            # Also store avg saturation/value to detect white/black
            avg_s = sum([colorsys.rgb_to_hsv(*[x/255 for x in p])[1]*100 for p in pixels])/len(pixels)
            avg_v = sum([colorsys.rgb_to_hsv(*[x/255 for x in p])[2]*100 for p in pixels])/len(pixels)
            dominant_colors[filename] = (dominant_hue, avg_s, avg_v)
        else:
            dominant_colors[filename] = (None, 0, 0)

# --- Step 2: Map hue to color names including white/black ---
COLOR_RANGES = {
    "red": [(345, 360), (0, 15)],
    "orange": [(16, 45)],
    "yellow": [(46, 75)],
    "green": [(76, 165)],
    "cyan": [(166, 195)],
    "blue": [(196, 255)],
    "purple": [(256, 284)],
    "pink": [(285, 344)]
}

def hue_to_color_name(hue_tuple):
    hue, s, v = hue_tuple
    if v <= 20:
        return "black"
    if s <= 20 and v >= 80:
        return "white"
    if hue is None:
        return "other"
    for color, ranges in COLOR_RANGES.items():
        for start, end in ranges:
            if start <= hue <= end:
                return color
    return "other"

# --- Step 3: Build color dictionary ---
color_dict = {}
for filename, hue_tuple in dominant_colors.items():
    color_name = hue_to_color_name(hue_tuple)
    if color_name not in color_dict:
        color_dict[color_name] = []
    color_dict[color_name].append(filename)

# --- Step 4: Search ---
search_color = input("Enter a color to search (red, orange, yellow, green, cyan, blue, purple, pink, white, black): ").lower()
matches = color_dict.get(search_color, [])

if not matches:
    print("No matches found")
else:
    print(f"Found {len(matches)} matches. Showing in window...")

    # --- Tkinter Window ---
    root = tk.Tk()
    root.title(f"Thumbnails: {search_color}")

    images = []
    cols = 5  # number of columns in grid
    for i, f in enumerate(matches):
        path = os.path.join(folder, f)
        img = Image.open(path)
        img = img.resize((100, 100))  # resize for viewing
        tk_img = ImageTk.PhotoImage(img)
        images.append(tk_img)  # keep reference to avoid garbage collection

        row = i // cols
        col = i % cols
        label = tk.Label(root, image=tk_img)
        label.grid(row=row, column=col, padx=5, pady=5)

    root.mainloop()