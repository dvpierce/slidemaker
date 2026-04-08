import os
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--width", help="Slide width, in inches", type=float, required=False, default=13.333)
parser.add_argument("--height", help="Slide height, in inches", type=float, required=False, default=7.5)
parser.add_argument("--input_dir", help="Path to files", type=str, required=False, default="./")
parser.add_argument("--output_file", help="Name of output file (pptx)", type=str, required=False, default="Presentation.pptx")
parser.add_argument("--duration", help="Duration for each slide.", type=float, required=False, default=5)
parser.add_argument("--overwrite", help="Overwrite existing files?", type=bool, action="store_true")
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

def create_image_slideshow(input_dir=None, output_file=None, slide_duration_sec=5, overwrite=False):
    # Initialize presentation
    prs = Presentation()
    
    prs.slide_width = Inches(slide_w)
    prs.slide_height = Inches(slide_h)

    valid_extensions = ('.jpg', '.jpeg', 'png')
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_extensons)]
    image_files.sort()

    if (not image_files) or (len(image_files) == 0):
        print("No images found in the specified folder.")
        return

    for img_name in image_files:
        # Use a blank slide layout (index 6 is usually blank)
        slide_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(slide_layout)
        
        img_path = os.path.join(image_folder, img_name)
        
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
                print(f"{output_file} exists. Overwriting per user instructions. (--overwrite selected.)")
            prs.save(output_file)
            print(f"Successfully created: {output_file}")
    except Exception as e:
        print("Error writing output file.")
        raise e

if __name__ == "__main__":
    create_image_slideshow(input_dir=args.input_dir, output_file=args.output_file, slide_duration_sec=args.duration, overwrite=args.overwrite)