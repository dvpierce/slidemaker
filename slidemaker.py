import os
import io
import argparse

from lib.slideshow import slideshow
from lib.validators import validators as v

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--width",
                    help="Slide width, in inches",
                    type=float,
                    required=False,
                    default=13.333)
parser.add_argument("-v", "--height",
                    help="Slide height, in inches",
                    type=float,
                    required=False,
                    default=7.5)
parser.add_argument("-i", "--input_dir",
                    help="Path to files",
                    type=v.validate_is_dir,
                    required=False,
                    default="./")
parser.add_argument("-o", "--output_file",
                    help="Name of output file (pptx)",
                    type=str,
                    required=False,
                    default="Presentation.pptx")
parser.add_argument("-d", "--duration",
                    help="Duration for each slide.",
                    type=float,
                    required=False,
                    default=5)
parser.add_argument("-r", "--overwrite",
                    help="Overwrite existing files?",
                    action="store_true")
parser.add_argument("-c", "--bgcolor",
                    help="RGB code for background color. Default is white.",
                    type=v.validate_is_hex,
                    required=False,
                    default="ffffff")
parser.add_argument("-k", "--threshold",
                    help="Hamming distance for duplicate detection. Default is 12. " +
                    "Smaller numbers are less likely to detect duplicates, larger " +
                    "numbers are more likely to get false positives.",
                    required=False,
                    type=int,
                    default=12)
parser.add_argument("-b", "--blurry_background",
                    help="Blurry Youtube style background.",
                    action="store_true")
parser.add_argument("-e", "--deduplicate",
                    help="Enable duplicate detection and don't include duplicates.",
                    action="store_true")
parser.add_argument("-f", "--add_format",
                    help="Force a specific file extension.",
                    required=False,
                    type=v.validate_is_pilsupported)
parser.add_argument("-t", "--transition",
                    help="Transition type: supports fade, wipe, push, or ripple. Omit for no transition or enter 'none'.",
                    required=False,
                    choices=["fade", "wipe", "push", "ripple", "none"],
                    type=str,
                    default="none")
parser.add_argument("-a", "--auto_contrast",
                    help="Whether to apply auto-contrast to images.",
                    required=False,
                    action="store_true")
parser.add_argument("-s", "--resample",
                    help="Resample large images to [DPI] to save disk space. Set to '0' or omit to disable resampling.",
                    required=False,
                    type=int,
                    default=0)
parser.add_argument("--logfile",
                    help="Save output to log instead.",
                    required=False,
                    action="store_true")
parser.add_argument("--subfolders",
                    help="Scan input directory for subfolders and use those photos too.",
                    required=False,
                    action="store_true")
parser.add_argument("--titles",
                    help="Use folder name(s) as slide titles.",
                    required=False,
                    action="store_true")
parser.add_argument("--captions_file",
                    help="Use captions file [FILENAME].",
                    required=False,
                    type=str,
                    default=None)
args = parser.parse_args()


if __name__ == "__main__":
    # slideshow.stdout_output = False
    slideshowmaker = slideshow(input_dir=args.input_dir,
                           output_file=args.output_file,
                           slide_w=args.width,
                           slide_h=args.height,
                           slide_duration_sec=args.duration,
                           overwrite=args.overwrite,
                           bgcolor=args.bgcolor,
                           duplicate_threshold=args.threshold,
                           blurbg=args.blurry_background,
                           deduplicate=args.deduplicate,
                           transition=args.transition,
                           auto_contrast=args.auto_contrast,
                           resample=args.resample,
                           logfile=args.logfile,
                           subfolders=args.subfolders,
                           titles=args.titles,
                           captions_file=args.captions_file)
    slideshowmaker.create_image_slideshow()
