import os
from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml

from lib.helpers import dedup, imghandler
import datetime

class slideshow:
    no_transition = """<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
    <mc:Choice xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" Requires="p14">
      <p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" p14:dur="0" advClick="0" advTm="{timedelay}"/>
    </mc:Choice>
    <mc:Fallback>
      <p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" advClick="0" advTm="{timedelay}"/>
    </mc:Fallback>
  </mc:AlternateContent>"""
    
    fade_transition = """<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
    <mc:Choice xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" Requires="p14">
      <p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" p14:dur="700" advClick="0" advTm="{timedelay}">
        <p:fade/>
      </p:transition>
    </mc:Choice>
    <mc:Fallback>
      <p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="0" advTm="{timedelay}">
        <p:fade/>
      </p:transition>
    </mc:Fallback>
  </mc:AlternateContent>
"""

    wipe_transition = """<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="slow" advClick="0" advTm="{timedelay}">
        <p:wipe/>
    </p:transition>"""
    
    push_transition = """<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="slow" advClick="0" advTm="{timedelay}">
        <p:push dir="u"/>
    </p:transition>"""
    
    ripple_transition = """<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">
    <mc:Choice xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" Requires="p14">
        <p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="slow" p14:dur="1400" advClick="0" advTm="{timedelay}">
            <p14:ripple/>
        </p:transition>
    </mc:Choice>
    <mc:Fallback>
        <p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="slow" advClick="0" advTm="{timedelay}">
            <p:fade/>
        </p:transition>
    </mc:Fallback>
</mc:AlternateContent>"""
    
    stdout_output = True
    logfile_name = "slideshowmaker.log"
    
    transitions = [
        {"name": "fade", "duration": 700},
        {"name": "ripple", "duration": 2000},
    ]

    def __init__(self):
        return

    @classmethod
    def output(cls, *args, **kwargs):
        def get_time():
            return str(datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds'))
        if cls.stdout_output:
            print(get_time(), *args, **kwargs)
        else:
            with open(cls.logfile_name, "a") as f:
                print(get_time(), *args, **kwargs, file=f)

    @classmethod
    def create_image_slideshow(cls, input_dir=None, output_file=None, overwrite=False,
                               slide_w=13.333, slide_h=7.5,
                               transition="none", auto_contrast=False,
                               bgcolor="ffffff", slide_duration_sec=5, blurbg=None,
                               deduplicate=False, duplicate_threshold=12):

        if os.path.exists(output_file) and not overwrite:
            raise FileExistsError(f"{output_file} already exists. Not set to overwrite.")

        prs = Presentation()
        prs.slide_width = Inches(slide_w)
        prs.slide_height = Inches(slide_h)

        if deduplicate:
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
                slide.shapes.add_picture(i.blur_stretch(), 0, 0, width=Inches(slide_w), height=Inches(slide_h))
            else:
                r, g, b = imghandler.convert_RGB(bgcolor)
                slide.background.fill.fore_color.rgb = RGBColor(r, g, b)

            if auto_contrast:
                slide.shapes.add_picture(i.get_autocontrast(), Inches(xoffset), Inches(yoffset), width=Inches(width), height=Inches(height))
            else:
                slide.shapes.add_picture(i.get_image(), Inches(xoffset), Inches(yoffset), width=Inches(width), height=Inches(height))

            # Add slide transition (or no transition.)
            if transition == "fade":
                transition = cls.fade_transition
            elif transition == "wipe":
                transition = cls.wipe_transition
            elif transition == "push":
                transition = cls.push_transition
            elif transition == "ripple":
                transition = cls.ripple_transition
            else:
                transition = cls.no_transition

            xml = transition.format(timedelay = str(slide_duration_sec * 1000))
            fragment = parse_xml(xml)
            slide.element.insert(-1, fragment)

        cls.output("")
        cls.output(f"Saving {output_file}...")
        if os.path.exists(output_file):
            cls.output(f"Warning: {output_file} exists and will be overwritten. (--overwrite enabled.)")
        prs.save(output_file)
        cls.output(f"Successfully created: {output_file}")
        return True