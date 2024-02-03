import json
import sys
from pathlib import Path 
import shutil

from PIL import Image, ImageDraw, ImageFont


# Loading settings from settings.json
file_settings = "settings.json"
with open(file_settings, "r") as f:
    settings = json.load(f)

IMAGE_COUNT = 0

path = Path('.')

def create_default_folders_if_gone():
    filenames = [file.name for file in path.iterdir()]

    # Remakes watermark folder.
    shutil.rmtree('./watermark', ignore_errors=True)  
    Path("./watermark").mkdir(exist_ok=True)

    if "originals" not in filenames:
        Path("./originals").mkdir()
        sys.exit("No orignals folder. Creating orignals folder and exiting...")


def get_all_folders_and_images_names():
    # Returns dictionary
    # k,v => folder_name, [image_names]

    folders = {}

    originals_folder = [file for file in Path('./originals').iterdir()]

    for folder in originals_folder:
        if not folder.is_dir():
            continue

        # Creating mirror folders in "./watermark"
        Path(f"./watermark/{folder.name}").mkdir(exist_ok=True)

        images_in_folder = []
        for file in Path(f'./originals/{folder.name}').iterdir():
            if file.name.lower().endswith((".png", ".jpg", ".jpeg", "heif")):
                global IMAGE_COUNT
                IMAGE_COUNT += 1
                images_in_folder.append(file.name)

        folders[folder.name] = images_in_folder
    
    return folders


def generate_watermarked_images():
    folders_and_data = get_all_folders_and_images_names()

    counter = 1
    for folder, images in folders_and_data.items():
        for image in images:
            global IMAGE_COUNT
            print(f"{counter}/{IMAGE_COUNT}: Creating watermarked image for: {image}")
            counter += 1

            my_font = ImageFont.load_default(size=settings["font_size"])
            img = Image.open(f"./originals/{folder}/{image}")
            length, width = img.size
            x = settings["left"]
            y = settings["top"]

            # If the user chooses the right or bottom spacing, we gotta make slight calculations for the x and y position depending on the image size.
            if settings["right"]:
                x = length - settings["right"] - (settings["font_size"] * len(folder) * 0.50)
                # x = length - settings["right"] - (settings["font_size"] * len(folder))
            if settings["bottom"]:
                y = width - settings["bottom"] - settings["font_size"]

            watermarked_img = ImageDraw.Draw(img)
            watermarked_img.text((x, y), f"[{folder}]", font=my_font, fill=settings["color"])
            img.save(f"./watermark/{folder}/{image}")
    print(f"Finished creating watermarks for {IMAGE_COUNT} images")
    

def main():
    create_default_folders_if_gone()
    generate_watermarked_images()
    

if __name__ == "__main__":
    if settings["top"] and settings["bottom"] or settings["left"] and settings["right"]:
        # Distance from top and bottom or left and right can not both be active at the same time.
        sys.exit("Settings file invalid. Only top or bottom and left or right value allowed. Please set top or bottom and left or right as 0")

    main()
