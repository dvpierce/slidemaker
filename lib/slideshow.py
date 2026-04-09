import os
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor

from lib.helpers import dedup, imghandler

class slideshow:
    do_output = True

    def __init__(self):
        return

    @classmethod
    def output(cls, *args, **kwargs):
        if cls.do_output:
            print(*args, **kwargs)

    @classmethod
    def create_image_slideshow(cls, input_dir=None, output_file=None, overwrite=False,
                               slide_w=13.333, slide_h=7.5,
                               bgcolor="000000", slide_duration_sec=5, blurbg=None,
                               deduplicate=False, duplicate_threshold=12):
        prs = Presentation()
        prs.slide_width = Inches(slide_w)
        prs.slide_height = Inches(slide_h)

        if dedup:
            deduper = dedup(directory=input_dir, hash_size=8, hamming_diff=duplicate_threshold, do_output=True)
            image_files = deduper.get_deduplicated_file_list()
        else:
            image_files = [f"{input_dir}{os.sep}{file}" for file in os.listdir(input_dir)]

        count = 0
        for img_path in image_files:
            count += 1
            cls.output(f"Creating slide {count} of {len(image_files)}...", end="\r", flush=True)

            # Use a blank slide layout (index 6 is usually blank)
            slide_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(slide_layout)
            slide.background.fill.solid()

            # Determine desired size and position of image.
            i = imghandler(img_path, slide_w=slide_w, slide_h=slide_h)
            width, height = i.get_limits()
            xoffset, yoffset = i.get_offsets()

            # Insert background on slide.
            if blurbg:
                slide.shapes.add_picture(blur_stretch(img_path, int(slide_w*100), int(slide_h*100)), 0, 0, width=Inches(slide_w), height=Inches(slide_h))
            else:
                r, g, b = imghandler.convert_RGB(bgcolor)
                slide.background.fill.fore_color.rgb = RGBColor(r, g, b)

            # Insert image on slide.
            slide.shapes.add_picture(img_path, Inches(xoffset), Inches(yoffset), width=Inches(width), height=Inches(height))

            # This is supposed to set the slides to autoadvance after slide_duration_sec seconds, but it doesn't work. I'll have to figure out why at some point.
            slide_element = slide.element
            slide_element.set('advClick', '0')  # Don't wait for click
            slide_element.set('advTm', str(slide_duration_sec * 1000))

        cls.output("")
        cls.output(f"Saving {output_file}...")
        if os.path.exists(output_file) and (not overwrite):
            exit(f"{output_file} exists. Can't overwrite. Exiting.")
        else:
            if os.path.exists(output_file):
                cls.output(f"Warning: {output_file} exists and will be overwritten. (--overwrite enabled.)")
            prs.save(output_file)
            cls.output(f"Successfully created: {output_file}")