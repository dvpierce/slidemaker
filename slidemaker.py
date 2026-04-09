import os
import io
import argparse

from lib.slideshow import slideshow

parser = argparse.ArgumentParser()
parser.add_argument("--width", help="Slide width, in inches", type=float, required=False, default=13.333)
parser.add_argument("--height", help="Slide height, in inches", type=float, required=False, default=7.5)
parser.add_argument("--input_dir", help="Path to files", type=str, required=False, default="./")
parser.add_argument("--output_file", help="Name of output file (pptx)", type=str, required=False, default="Presentation.pptx")
parser.add_argument("--duration", help="Duration for each slide.", type=float, required=False, default=5)
parser.add_argument("--overwrite", help="Overwrite existing files?", action="store_true")
parser.add_argument("--bgcolor", help="RGB code for background color. Default is black.", required=False, default="000000")
parser.add_argument("--threshold", help="Hamming distance for duplicate detection. Default is 12. Smaller numbers are less likely to detect duplicates, larger numbers are more likely to get false positives.", required=False, type=int, default=12)
parser.add_argument("--blurry_background", help="Blurry Youtube style background.", action="store_true")
parser.add_argument("--deduplicate", help="Enable duplicate detection and don't include duplicates.", action="store_true")
parser.add_argument("--add_format", help="Force a specific file extension.", required=False, type=str)
parser.add_argument("--transition", help="Transition type", required=False, type=int, default=0)
args = parser.parse_args()


if __name__ == "__main__":
    slideshow.create_image_slideshow(input_dir=args.input_dir,
                           output_file=args.output_file,
                           slide_w=args.width,
                           slide_h=args.height,
                           slide_duration_sec=args.duration,
                           overwrite=args.overwrite,
                           bgcolor=args.bgcolor,
                           duplicate_threshold=args.threshold,
                           blurbg=args.blurry_background,
                           deduplicate=args.deduplicate,
                           transition=args.transition)
