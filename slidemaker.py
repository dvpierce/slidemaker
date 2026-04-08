import os
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor
from PIL import Image
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("--width", help="Slide width, in inches", type=float, required=False, default=13.333)
parser.add_argument("--height", help="Slide height, in inches", type=float, required=False, default=7.5)
parser.add_argument("--input_dir", help="Path to files", type=str, required=False, default="./")
parser.add_argument("--output_file", help="Name of output file (pptx)", type=str, required=False, default="Presentation.pptx")
parser.add_argument("--duration", help="Duration for each slide.", type=float, required=False, default=5)
parser.add_argument("--overwrite", help="Overwrite existing files?", action="store_true")
parser.add_argument("--bgcolor", help="RGB code for background color. Default is black.", required=False, default="000000")
args = parser.parse_args()

slide_w = args.width
slide_h = args.height


def getSize(image_file):
    w, h = Image.open(image_file).size
    return w, h


def getlimits(image_file):
    w, h = getSize(image_file)
    scalefactor = max([(w/slide_w), (h/slide_h)])
    return (w/scalefactor), (h/scalefactor)


def get_offsets(width, height):
    xoffset = (slide_w - width)/2
    yoffset = (slide_h - height)/2
    return xoffset, yoffset


def getRGB(hexstring):
    pattern = r'^#?([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if not bool(re.match(pattern, hexstring)):
        raise Exception(f"{hexstring} is not a valid RGB color code.")
    hexstring = hexstring.replace("#", "").lower()
    if len(hexstring) == 3:
        r = int(hexstring[0]+hexstring[0], 16)
        g = int(hexstring[1]+hexstring[1], 16)
        b = int(hexstring[2]+hexstring[2], 16)
    elif len(hexstring) == 6:
        r = int(hexstring[0:2], 16)
        g = int(hexstring[2:4], 16)
        b = int(hexstring[4:6], 16)
    else:
        raise Exception(f"{hexstring} is not a valid RGB color code.")
    return RGBColor(r, g, b)


def create_image_slideshow(input_dir=None, output_file=None, slide_duration_sec=5, overwrite=False, bgcolor="000000"):
    # Initialize presentation
    prs = Presentation()

    prs.slide_width = Inches(slide_w)
    prs.slide_height = Inches(slide_h)

    valid_extensions = ('.avif', '.bmp', '.gif', '.j2k', '.jp2', '.jpx', '.pcx', '.tiff', '.tif', '.jpg', '.jpeg', '.png', '.webp')
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_extensions)]
    image_files.sort()

    if not image_files:
        print("No images found in the specified folder.")
        return

    for img_name in image_files:
        # Use a blank slide layout (index 6 is usually blank)
        slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(slide_layout)
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = getRGB(bgcolor)

        img_path = os.path.join(input_dir, img_name)

        width, height = getlimits(img_path)
        xoffset, yoffset = get_offsets(width, height)

        # Add and resize image to fit the 10x7.5 slide exactly
        slide.shapes.add_picture(img_path, Inches(xoffset), Inches(yoffset), width=Inches(width), height=Inches(height))

        # Set timing: Access underlying XML to set 'Advance After' time
        # 'advTm' is in milliseconds
        slide_element = slide.element
        slide_element.set('advClick', '0')  # Don't wait for click
        slide_element.set('advTm', str(slide_duration_sec * 1000))

    try:
        if os.path.exists(output_file) and (not overwrite):
            exit(f"{output_file} exists. Will not overwrite. Exiting.")
        else:
            if os.path.exists(output_file):
                print(f"Warning: {output_file} exists. (--overwrite selected.)")
            prs.save(output_file)
            print(f"Successfully created: {output_file}")
    except Exception as e:
        print("Error writing output file.")
        raise e


if __name__ == "__main__":
    create_image_slideshow(input_dir=args.input_dir,
                           output_file=args.output_file,
                           slide_duration_sec=args.duration,
                           overwrite=args.overwrite,
                           bgcolor=args.bgcolor)
