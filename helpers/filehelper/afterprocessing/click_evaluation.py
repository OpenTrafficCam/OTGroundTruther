import cv2
import pandas as pd
import os

color_codes = [
    (255, 0, 0),       # Red
    (0, 255, 0),       # Green
    (0, 0, 255),       # Blue
    (255, 255, 0),     # Yellow
    (255, 0, 255),     # Magenta
    (0, 255, 255),     # Cyan
    (128, 0, 0),       # Maroon
    (0, 128, 0),       # Green (Mid)
    (0, 0, 128),       # Navy
    (128, 128, 0),     # Olive
    (128, 0, 128),     # Purple
    (0, 128, 128),     # Teal
    (128, 128, 128),   # Gray
    (192, 192, 192)    # Silver
]

# definition of vehicleclasses and hotkeys as dictionary keys
class_color_dictionary = {
    "Pkw ohne Anhänger": None,
    "Fahrrad ohne Anhänger": None,
    "Person": None,
    "Bus": None,
    "Lkw ohne Anhänger": None,
    "Lkw mit Anhänger": None,
    "Pkw mit Anhänger": None,
    "Lieferwagen ohne Anhänger": None,
    "Lieferwagen mit Anhänger": None,
    "Motorisierte Zweiräder": None,
    "Scooter": None,
    "Lastenrad": None,
    "Fahrrad mit Anhänger": None,
    "Schienenfahrzeug": None,
}
# assign color to key
for key, color in zip(class_color_dictionary.keys(), color_codes):
    class_color_dictionary[key] = color


city = "Saarbruecken"

Scene = "17"

safe_name = f"{city}_Otcamera{Scene}.PNG"

# better create image from video
image_path = r"\\vs-grp08.zih.tu-dresden.de\otc_live\validate\ground truth events\sections\Querschnitte\Saarbruecken_OTCamera17.PNG"


csv_dir = r"\\vs-grp08.zih.tu-dresden.de\otc_live\validate\ground truth events\events\Saarbrücken"

# Load the image you want to draw on
img = cv2.imread(image_path)
overlay = img.copy()


# get list of csv files
csv_files = [f for f in os.listdir(csv_dir) if f.endswith(
    '.csv') and f'OTCamera{Scene}' in f]


alpha = 0.4  # Transparency factor.
for csv_file in csv_files:
    # Read in the CSV file as a pandas DataFrame
    csv_path = os.path.join(csv_dir, csv_file)
    data = pd.read_csv(csv_path)
    # Iterate through each row of the DataFrame and draw a point on the image
    for index, row in data.iterrows():
        color = class_color_dictionary[row["Class"]]
        x = int(row['X'])
        y = int(row['Y'])
        cv2.circle(img, (x, y), radius=4, color=color, thickness=-1)
        # Following line overlays transparent rectangle over the image
        image_new = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

# Save the final image with a safe filename
cv2.imwrite(safe_name, image_new)

# Display the image with the points drawn on it
cv2.imshow('Image', image_new)
cv2.waitKey(0)
cv2.destroyAllWindows()
