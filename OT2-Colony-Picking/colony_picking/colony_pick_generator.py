# Modified Version 9/9/19

# Modify by Rita Chen 2020-03-23


import csv
import json
import math
import os
import subprocess
from io import StringIO

import tkinter
import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance
from tkinter import filedialog, messagebox

# --------------------------------- CONSTANTS ----------------------------------
CONFIG_PATH = "data/settings.yaml"


def main():
    config = get_config(CONFIG_PATH)
    # User provided input at runtime.
    # num_plates = ask_num_plates() #for multiple agar plates
    # source_plate_filenames = ask_source_plate_filenames(num_plates) #for multiple agar plates
    source_plate_filename = ask_source_plate_filename()

    # Calculate number of images to fetch from folder.
    plates_per_image = len(config["plate_locations"])
    num_images = int(1 // plates_per_image) + (1 % plates_per_image > 0)
    # num_images = int(num_plates // plates_per_image) + (num_plates % plates_per_image > 0) #for multiple agar plates
    image_filenames = get_image_filenames(config["image_folder_path"], num_images)
    background_filenames = get_background_filenames(config["background_folder_path"])
    # ----------------------- Start image preprocessing ------------------------
    preprocessed_image_filenames = preprocess_images(
        image_filenames=image_filenames,
        temp_folder_path=config["temp_folder_path"],
        inverted=config["inverted"],
        blur_radius=config["blur_radius"],
        brightness=config["brightness"],
        contrast=config["contrast"],
        background_filenames=background_filenames,
    )

    # --------------------- Start Colony Identification ------------------------
    plates = generate_plates(
        preprocessed_image_filenames,
        source_plate_filename,
        config["plate_locations"],
    )
    # Run OpenCFU for each image.
    opencfu_outputs = run_opencfu(
        opencfu_folder_path=config["opencfu_folder_path"],
        image_filenames=preprocessed_image_filenames,
        arg_string=config["opencfu_arg_string"],
    )
    # Draw colony location previews for each image.
    if config["draw_previews"]:
        draw_previews(opencfu_outputs, config["temp_folder_path"])
    # Convert pixel coordinates to mm in coordinate system of each plate.
    for plate in plates:
        opencfu_output = opencfu_outputs[plate["image_filename"]]
        plate_location = plate["location_in_image"]
        plate_origin = config["calibration_point_location"]
        plate["colony_locations"] = get_relative_locations(
            opencfu_output=opencfu_output,
            plate_location=plate_location,
            rotate=config["rotate"],
            pixels_per_mm=config["pixels_per_mm"],
            plate_origin=plate_origin,
        )
        if config["draw_previews"]:
            draw_regions(
                preview_path=config["temp_folder_path"],
                preview_filename=plate["image_filename"],
                plate_location=plate_location,
                rotate=config["rotate"],
                pixels_per_mm=config["pixels_per_mm"],
                colony_regions=config["colony_regions"],
                plate_origin=plate_origin,
            )
    # Selects appropriate colonies for each plasmid based on colony_regions in settings.yaml.
    culture_blocks_dict = pick_colonies(
        plates,
        config["colony_regions"],
        config["colonies_to_pick"],
        config["block_rows"],
        config["block_columns"],
        config["calibration_point_location"],
    )
    ###### CREATING OUTPUT BLOCK MAPS AND PROTOCOL FILE ######
    create_block_maps(culture_blocks_dict, config["output_folder_path"])
    create_protocol(
        culture_blocks_dict,
        config["protocol_template_path"],
        config["output_folder_path"],
    )
    if not config["keep_temp_files"]:
        delete_temp_files(config["temp_folder_path"])


# -------------------------- User Input Functionality --------------------------


def get_config(config_path):
    # Load settings from file.
    config = yaml.safe_load(open(config_path))
    # Create a tkiner window and hide it (this will allow us to create dialog boxes)
    window = tkinter.Tk()
    window.withdraw()
    # Ask user to set image folder if not set.
    if not config["image_folder_path"]:
        messagebox.showinfo(
            "Choose image folder",
            "You will now select the folder containing saved "
            "plate images. This can be changed later by editing "
            "settings.yaml in the OT2_MoClo_JoVE/colony_picking/"
            "data folder.",
        )
        config["image_folder_path"] = filedialog.askdirectory(
            title="Choose image folder"
        )
        with open(config_path, "w+") as yaml_file:
            yaml_file.write(yaml.dump(config))

    # Ask user to set output folder if not set.
    if not config["output_folder_path"]:
        messagebox.showinfo(
            "Choose output folder",
            "You will now select the folder to save the protocol and plate maps "
            "to. This can be changed later by editing settings.yaml in the "
            "OT2_MoClo_JoVE/colony_picking/data folder.",
        )

        config["output_folder_path"] = filedialog.askdirectory(
            title="Choose output folder"
        )
        with open(config_path, "w+") as yaml_file:
            yaml_file.write(yaml.dump(config))
    # Ask user to locate OpenCFU.
    if not config["opencfu_folder_path"]:
        messagebox.showinfo(
            "Locate OpenCFU",
            'Select folder of OpenCFU (e.g. "C:/Program Files/OpenCFU"). This '
            "can be changed later by editing settings.yaml in the "
            "OT2_MoClo_JoVE/colony_picking/data folder.",
        )
        config["opencfu_folder_path"] = filedialog.askdirectory(title="Locate OpenCFU")
        with open(config_path, "w+") as yaml_file:
            yaml_file.write(yaml.dump(config))
    return config


def get_image_filenames(image_folder_path, num_images):
    # Get all images from folder and sort by creation time.
    image_filenames = [
        (image_folder_path + "/" + image_name)
        for image_name in os.listdir(image_folder_path)
    ]
    image_filenames.sort(key=lambda x: os.path.getmtime(x))
    return image_filenames[-num_images:]


def get_background_filenames(background_folder_path):
    # Background image filenames (optional). If multiple are found they will be averaged.
    try:
        os.stat(background_folder_path)
    except:
        os.mkdir(background_folder_path)
    return [
        (background_folder_path + "/" + image_name)
        for image_name in os.listdir(background_folder_path)
    ]


def ask_source_plate_filename():
    # Create tkinter window in background to allow us to make dialog boxes.
    window = tkinter.Tk()
    window.withdraw()
    # Open dialog boxes asking user for plate map.
    source_plate_filename = filedialog.askopenfilename(
        title="Select plate map",
        filetypes=(("CSV files", "*.CSV"), ("all files", "*.*")),
    )
    return source_plate_filename


# - Image Preprocessing Functionality

# Blur slightly (improves background subtraction and colony detection).


def blur(image, blur_radius):
    return image.filter(ImageFilter.GaussianBlur(radius=blur_radius))


def brightness_contrast(image, brightness, contrast):
    # Adjust brightness and contrast to improve detection
    image = ImageEnhance.Contrast(image).enhance(contrast)
    image = ImageEnhance.Brightness(image).enhance(brightness)
    return image


def blend(images, blur_radius):
    average = blur(images[0], blur_radius)
    for i in range(1, len(images)):
        img = blur(images[i], blur_radius)
        average = Image.blend(average, img, 1.0 / float(i + 1))
    return average


# Processes images with various functions to improve colony detection. Saves to temp_folder_path.
def preprocess_images(
    image_filenames,
    temp_folder_path,
    inverted=False,
    blur_radius=0.0,
    brightness=1.0,
    contrast=1.0,
    background_filenames=None,
):
    preprocessed_image_filenames = []
    for image_filename in image_filenames:
        image = Image.open(image_filename)
        image = blur(image, blur_radius)
        image = brightness_contrast(image, brightness, contrast)
        if background_filenames:
            background_images = [Image.open(x) for x in background_filenames]
            average_background = blend(background_images, blur_radius)
            if inverted:
                image = ImageChops.subtract(average_background, image)
            else:
                image = ImageChops.subtract(image, average_background)
        # Save in temporary folder.
        preprocessed_image_filename = (
            temp_folder_path + "/" + os.path.basename(image_filename)
        )
        # Absolute filenames are important for opencfu step.
        absolute_filename = os.path.abspath(preprocessed_image_filename)
        image.save(absolute_filename)
        preprocessed_image_filenames.append(absolute_filename)
    return preprocessed_image_filenames


# ------------------- Colony Location Finding Functionality --------------------
def generate_plates(
    preprocessed_image_filenames, source_plate_filename, plate_locations
):
    # Generates a list of plates, their images filenames and source plate (map)
    # filenames, and their locations within their source images.
    plates_per_image = len(plate_locations)
    plates = []
    plate_index = 0
    for preprocessed_image_filename in preprocessed_image_filenames:
        for i in range(0, plates_per_image):
            if plate_index < 1:
                plates.append(
                    {
                        "image_filename": preprocessed_image_filename,
                        "source_plate_filename": source_plate_filename,
                        "location_in_image": plate_locations[i],
                    }
                )
                plate_index += 1
    return plates


def run_opencfu(opencfu_folder_path, image_filenames, arg_string):
    # Run opencfu for an image and return the result as a dictionary keyed by
    # image filenames.
    opencfu_outputs = {}
    for image_filename in image_filenames:
        shell_command = 'cd "{0}/bin" && opencfu -i "{1}" {2}'.format(
            opencfu_folder_path, image_filename, arg_string
        )
        raw_opencfu_output = subprocess.check_output(args=shell_command, shell=True)
        f = StringIO(raw_opencfu_output.decode("utf-8"))
        opencfu_outputs[image_filename] = list(csv.DictReader(f, delimiter=","))
    return opencfu_outputs


def get_relative_locations(
    opencfu_output,
    plate_location,
    rotate,
    pixels_per_mm,
    plate_origin,
):
    # converts opencfu output (locations in px coordinates) into mm coordinates
    # relative to origin.
    relative_locations = []
    for row in opencfu_output:
        if row["IsValid"] == "1":
            x = float(row["X"])
            y = float(row["Y"])
            translated_x = x - plate_location["x"]
            translated_y = y - plate_location["y"]
            cosine = math.cos(math.radians(rotate))
            sine = math.sin(math.radians(rotate))
            rotated_x = translated_x * cosine - translated_y * sine
            rotated_y = translated_y * cosine + translated_x * sine
            mm_x = rotated_x / pixels_per_mm
            mm_y = rotated_y / pixels_per_mm
            adjusted_x = mm_x - plate_origin["x"]
            adjusted_y = mm_y - plate_origin["y"]
            relative_locations.append({"x": adjusted_x, "y": adjusted_y})
    return relative_locations


def get_image_location(x, y, plate_location, rotate, pixels_per_mm, plate_origin):
    # converts coordinates in mm relative to origin into locations in px coordinates on image
    adjusted_x = x + plate_origin["x"]
    adjusted_y = y + plate_origin["y"]
    px_x = adjusted_x * pixels_per_mm
    px_y = adjusted_y * pixels_per_mm
    cosine = math.cos(math.radians(-rotate))
    sine = math.sin(math.radians(-rotate))
    rotated_x = px_x * cosine - px_y * sine
    rotated_y = px_y * cosine + px_x * sine
    translated_x = rotated_x + plate_location["x"]
    translated_y = rotated_y + plate_location["y"]
    return (translated_x, translated_y)


def draw_previews(opencfu_outputs, preview_path):
    # Intakes a list of opencfu outputs (DictReaders) keyed by image filename
    # and draws previews to temp_folder_path.
    for image_filename, opencfu_output in opencfu_outputs.items():
        # Create preview image of colony picking
        original = Image.open(image_filename)
        colonies_image = original.copy()
        draw = ImageDraw.Draw(colonies_image)
        for row in opencfu_output:
            x = float(row["X"])
            y = float(row["Y"])
            if row["IsValid"] == "1":
                # draw green circle
                draw.ellipse((x - 4, y - 4, x + 4, y + 4), outline=(0, 255, 0, 255))
            else:
                # draw red circle
                draw.ellipse((x - 4, y - 4, x + 4, y + 4), outline=(255, 0, 0, 255))
        preview_filename = (
            preview_path + "/preview_colonies_" + os.path.basename(image_filename)
        )
        # Save image preview
        colonies_image.save(preview_filename)
        return preview_filename


def draw_regions(
    preview_path,
    preview_filename,
    plate_location,
    rotate,
    pixels_per_mm,
    colony_regions,
    plate_origin,
):
    # Draws the colony regions and saves output in temp folder.
    # Open source image
    regions_image = Image.open(preview_filename)
    draw = ImageDraw.Draw(regions_image)
    # Draw (different for circles vs rectangles)
    for i in range(0, colony_regions["rows"]):
        for j in range(0, colony_regions["columns"]):
            if colony_regions["type"] == "circle":
                mm_x = (
                    colony_regions["x"]
                    + j * colony_regions["x_spacing"]
                    - plate_origin["x"]
                )
                mm_y = (
                    colony_regions["y"]
                    + i * colony_regions["y_spacing"]
                    - plate_origin["y"]
                )
                px_x, px_y = get_image_location(
                    mm_x, mm_y, plate_location, rotate, pixels_per_mm, plate_origin
                )
                px_r = colony_regions["r"] * pixels_per_mm
                draw.ellipse(
                    (px_x - px_r, px_y - px_r, px_x + px_r, px_y + px_r),
                    outline=(255, 0, 0, 255),
                )
            elif colony_regions["type"] == "rectangle":
                mm_x_min = (
                    colony_regions["x_1"]
                    + j * colony_regions["x_spacing"]
                    - plate_origin["x"]
                )
                mm_x_max = (
                    colony_regions["x_2"]
                    + j * colony_regions["x_spacing"]
                    - plate_origin["x"]
                )
                mm_y_min = (
                    colony_regions["y_1"]
                    + i * colony_regions["y_spacing"]
                    - plate_origin["y"]
                )
                mm_y_max = (
                    colony_regions["y_2"]
                    + i * colony_regions["y_spacing"]
                    - plate_origin["y"]
                )
                px_x_min, px_y_min = get_image_location(
                    mm_x_min,
                    mm_y_min,
                    plate_location,
                    rotate,
                    pixels_per_mm,
                    plate_origin,
                )
                px_x_max, px_y_max = get_image_location(
                    mm_x_max,
                    mm_y_max,
                    plate_location,
                    rotate,
                    pixels_per_mm,
                    plate_origin,
                )
                draw.rectangle(
                    [(px_x_min, px_y_min), (px_x_max, px_y_max)],
                    outline=(255, 0, 0, 255),
                )
            else:
                raise ValueError(
                    "Invalid colony_regions type: {0}".format(colony_regions["type"])
                )

    # Save
    new_preview_filename = (
        preview_path + "/preview_regions_" + os.path.basename(preview_filename)
    )
    regions_image.save(new_preview_filename)


def measure_colony_distances(colony_list):
    # Find the minimum distance from other colonies for each colony
    colonies_with_distances = []
    for colony_1 in colony_list:
        colonies_with_distances.append(colony_1)
        colonies_with_distances[-1]["dist"] = 10000
        for colony_2 in colony_list:
            if not colony_1 == colony_2:
                dist = (
                    (colony_2["x"] - colony_1["x"]) ** 2
                    + (colony_2["y"] - colony_1["y"]) ** 2
                ) ** 0.5
                if dist < colonies_with_distances[-1]["dist"]:
                    colonies_with_distances[-1]["dist"] = dist
    return colonies_with_distances


def get_plasmid_name(source_plate_filename, row, column):
    # Get name of the plasmid by reading user-supplied plate map.
    with open(source_plate_filename, newline="", encoding="utf-8-sig") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=",", quotechar='"')
        try:
            plasmid_name = list(csvreader)[row][column]
        except:
            plasmid_name = ""
    return plasmid_name


def get_colonies_in_region(colony_locations, colony_regions, plate_origin, i, j):
    # Returns a list of only the colonies which are inside colony region i, j.
    colonies_in_region = []
    if colony_regions["type"] == "circle":
        for colony in colony_locations:
            target_x = (
                colony_regions["x"]
                + j * colony_regions["x_spacing"]
                - plate_origin["x"]
            )
            target_y = (
                colony_regions["y"]
                + i * colony_regions["y_spacing"]
                - plate_origin["y"]
            )
            delta_x = colony["x"] - target_x
            delta_y = colony["y"] - target_y
            if (delta_x ** 2 + delta_y ** 2) ** 0.5 < colony_regions["r"]:
                colonies_in_region.append(colony)
    elif colony_regions["type"] == "rectangle":
        for colony in colony_locations:
            x_min = (
                colony_regions["x_1"]
                + j * colony_regions["x_spacing"]
                - plate_origin["x"]
            )
            x_max = (
                colony_regions["x_2"]
                + j * colony_regions["x_spacing"]
                - plate_origin["x"]
            )
            y_min = (
                colony_regions["y_1"]
                + i * colony_regions["y_spacing"]
                - plate_origin["y"]
            )
            y_max = (
                colony_regions["y_2"]
                + i * colony_regions["y_spacing"]
                - plate_origin["y"]
            )
            if (
                colony["x"] > x_min
                and colony["x"] < x_max
                and colony["y"] > y_min
                and colony["y"] < y_max
            ):
                colonies_in_region.append(colony)
    else:
        raise ValueError(
            "Invalid colony_regions type: {0}".format(colony_regions["type"])
        )
    return colonies_in_region


def pick_colonies(
    plates,
    colony_regions,
    colonies_to_pick,
    block_rows,
    block_columns,
    calibration_point_location,
):
    # Tracking output block number, row, and column.
    n = 0
    i = 0
    j = 0
    culture_blocks_dict = {}
    culture_blocks_dict["culture_block_0"] = []
    culture_blocks_dict["culture_block_0"].append([])
    for plate in plates:
        for row in range(0, colony_regions["rows"]):
            for col in range(0, colony_regions["columns"]):
                plasmid_name = get_plasmid_name(
                    plate["source_plate_filename"], row, col
                )
                if plasmid_name:
                    colonies = get_colonies_in_region(
                        plate["colony_locations"],
                        colony_regions,
                        calibration_point_location,
                        row,
                        col,
                    )
                    colonies_with_distances = measure_colony_distances(colonies)
                    sorted_colonies = sorted(
                        colonies_with_distances, key=lambda c: c["dist"], reverse=True
                    )
                    selected_colonies = sorted_colonies[:colonies_to_pick]
                    for colony in selected_colonies:
                        colony_dict = {
                            "name": plasmid_name,
                            "source": "{0}".format(
                                os.path.splitext(
                                    os.path.basename(plate["source_plate_filename"])
                                )[0]
                            ),
                            "x": colony["x"],
                            # INVERT COLONY Y FOR LOWER-LEFT-ORIGIN OPENTRONS LABWARE COORDINATE SYSTEM
                            "y": -colony["y"],
                        }
                        try:
                            culture_blocks_dict["culture_block_{0}".format(n)][
                                i
                            ].append(colony_dict)
                        except IndexError:
                            culture_blocks_dict["culture_block_{0}".format(n)].append(
                                [colony_dict]
                            )
                        if i == block_rows - 1:
                            if j == block_columns - 1:
                                n += 1
                                j = 0
                            else:
                                j += 1
                            i = 0
                        else:
                            i += 1
    return culture_blocks_dict


def delete_temp_files(temp_folder_path):
    # Deletes all files in folder.
    temp_files = [file for file in os.listdir(temp_folder_path)]
    for file in temp_files:
        os.remove(os.path.join(temp_folder_path, file))


# ---------------------------- Output File Handling ----------------------------
def create_block_maps(culture_blocks_dict, output_folder_path):
    for block_name, block_map in culture_blocks_dict.items():
        with open(
            output_folder_path + "/" + "{0}.csv".format(block_name), "w+", newline=""
        ) as block_map_file:
            writer = csv.writer(block_map_file)
            for row in block_map:
                newrow = []
                newrow.append("Control")
                for x in row:
                    newrow.append(x["name"])
                writer.writerow(newrow)


def create_protocol(culture_blocks_dict, protocol_template_path, output_folder_path):
    # Get the contents of colony_pick_template.py, which contains the body of the protocol.

    with open(protocol_template_path) as template_file:
        template_string = template_file.read()
    with open(
        output_folder_path + "/" + "colony_pick_protocol.py", "w+"
    ) as protocol_file:
        # Paste colony locations dictionary into output file.
        protocol_file.write(
            "culture_blocks_dict = " + json.dumps(culture_blocks_dict) + "\n\n"
        )
        # Paste the rest of the protocol.
        protocol_file.write(template_string)


if __name__ == "__main__":
    main()
