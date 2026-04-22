import os
import io
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import re
import json
import datetime
import threading

class my_logger:
    log_lock = threading.Lock()

    def __init__(self, file=None):
        self.use_file = file
        return

    def _get_time(self):
        return str(datetime.datetime.now(datetime.UTC).isoformat(timespec='seconds'))

    def logit(self, *args, **kwargs):
        with my_logger.log_lock:
            if self.use_file:
                with open(self.use_file, "a") as f:
                    value = kwargs.pop('end', None)
                    value = kwargs.pop('flush', None)
                    print(self._get_time(), *args, **kwargs, file=f, flush=True)
            else:
                print(self._get_time(), *args, **kwargs)

class imghandler:
    def __init__(self, img_path, slide_w=13.333, slide_h=7.5):
        self.image = img_path
        self.filename = os.path.basename(self.image)
        self.slide_w = slide_w
        self.slide_h = slide_h
        self.image_data = Image.open(self.image)
        self.lim_w = None
        self.lim_h = None

    def get_imagesize(self):
        w, h = self.image_data.size
        return w, h

    def get_limits(self):
        # Compute (once, and save) the maximum image size in inches.
        if not self.lim_w and not self.lim_h:
            w, h = self.get_imagesize()
            scalefactor = max([(w/self.slide_w), (h/self.slide_h)])
            self.lim_w = w/scalefactor
            self.lim_h = h/scalefactor
        return self.lim_w, self.lim_h

    def get_is_largeimage(self, maxres=300):
        # Return whether or not the image is higher res than it needs
        # to be in order to be [maxres] DPI @ get_limits() height/width.
        w, h = self.image_data.size
        lim_w, lim_h = self.get_limits()
        return w > (lim_w * maxres)

    def resample(self, maxres=300):
        # Resample image to [maxres] dpi if it's higher res than needed.
        if self.get_is_largeimage():
            lim_w, lim_h = self.get_limits()
            new_w = int(lim_w * maxres)
            new_h = int(lim_h * maxres)
            self.image_data = self.image_data.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)
            return True
        else:
            return False

    def get_offsets(self):
        iw, ih = self.get_limits()
        xoffset = (self.slide_w - iw)/2
        yoffset = (self.slide_h - ih)/2
        return xoffset, yoffset

    def blur_stretch(self):
        original = self.image_data
        stretched = original.resize((int(self.slide_w*100), int(self.slide_h*100)))
        blurred_bg = stretched.filter(ImageFilter.GaussianBlur(radius=20))
        image_stream = io.BytesIO()
        blurred_bg.save(image_stream, format='JPEG')
        image_stream.seek(0)
        return image_stream

    def get_image(self):
        image_stream = io.BytesIO()
        self.image_data.save(image_stream, format='JPEG')
        image_stream.seek(0)
        return image_stream

    def get_autocontrast(self):
        image_stream = io.BytesIO()
        mod_image = self.image_data.convert("RGB")
        ImageOps.autocontrast(mod_image, cutoff=3).save(image_stream, format='JPEG')
        image_stream.seek(0)
        return image_stream

    @staticmethod
    def convert_RGB(hexstring):
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
        return (r, g, b)

    @staticmethod
    def get_appropriate_text_color(hexstring):
        r, g, b = imghandler.convert_RGB(hexstring)
        luminance = (0.299 * r) + (0.587 * g) + (0.114 * b)
        if luminance >= 128:
            return 0, 0, 0
        else:
            return 255, 255, 255


class dedup:
    def __init__(self, directory=".", hash_size=8, hamming_diff=12, out_log=None, forcetype=None):
        self.directory = directory
        self.hash_size = hash_size
        self.hamming_diff = hamming_diff
        self.file_database = dict()
        self.ddlist = None
        self.force = forcetype
        self.out_log = out_log

    def output(self, *args, **kwargs):
        if not self.out_log:
            value = kwargs.pop('flush', None)
            print(*args, **kwargs, flush=True)
        else:
            self.out_log.logit(*args, **kwargs)

    def set_scandir(self, new_directory):
        if os.path.isdir(new_directory):
            self.directory = new_directory
            return self.directory
        else:
            raise Exception(f"{new_directory} is not a directory.")

    def scandir(self):
        valid_extensions = ('.avif', '.bmp', '.gif', '.j2k', '.jp2', '.jpx', '.pcx', '.tiff', '.tif', '.jpg', '.jpeg', '.png', '.webp')
        if self.force:
            if not self.force.startswith("."):
                self.force = f".{self.force}"
            valid_extensions.add(self.force.lower())
        count = 0
        files = [ file for file in os.listdir(self.directory) if file.lower().endswith(valid_extensions) ]
        for file in files:
            count += 1
            img_path = f"{os.path.abspath(self.directory)}{os.sep}{file}"
            self.file_database[img_path] = dict()
            self.file_database[img_path]['fingerprint'] = self._get_imagefingerprint(img_path)
            self.file_database[img_path]['duplicates'] = list()
            self.file_database[img_path]['duplicates'].append(img_path)
            self.output(f"Generating signatures for image {count} of {len(files)}...", end="\r", flush=True)
        self.output("")
        self.output("Signature generation complete.")

    def _get_imagefingerprint(self, image_path):
        with Image.open(image_path) as img:
            img = img.convert('L')
            img = img.resize((self.hash_size + 1, self.hash_size), Image.Resampling.LANCZOS)
            pixels = np.array(img)
            diff = pixels[:, 1:] > pixels[:, :-1]

            decimal_value = 0
            hex_string = []
            for index, value in enumerate(diff.flatten()):
                if value:
                    decimal_value += 2**(index % self.hash_size)
                if (index % self.hash_size) == self.hash_size-1:
                    hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
                    decimal_value = 0

            return "".join(hex_string)

    def _hamming_distance(self, hex_hash1, hex_hash2):
        # 1. Convert hex strings to integers
        val1 = int(hex_hash1, 16)
        val2 = int(hex_hash2, 16)

        # 2. XOR the two values
        # Bits that are different will result in a 1
        xor_result = val1 ^ val2

        # 3. Count the number of set bits (1s) in the binary result
        return bin(xor_result).count('1')

    def find_duplicates(self):
        self.output("Scanning for duplicates...")
        count = 0
        for img_path in self.file_database.keys():
            count += 1
            self.output(f"Checking image {count} of {len(self.file_database.keys())} against {len(self.file_database.keys())-1} fingerprints", end="\r", flush=True)
            for other_file in self.file_database.keys():
                if other_file == img_path:
                    continue
                if self._hamming_distance(self.file_database[img_path]['fingerprint'], self.file_database[other_file]['fingerprint']) <= self.hamming_diff:
                    self.file_database[img_path]['duplicates'].append(other_file)
        self.output("")
        with open("file_database", "w") as f:
            f.write(json.dumps(self.file_database, indent=4))
        self.output("Scan complete. Refer to 'file_database' for results.", flush=True)
        return

    def generate_deduplicated_file_list(self):
        # Generate image fingerprints (scandir()) and cross reference them (find_duplicates)
        # Data is saved in self.file_database
        self.scandir()
        self.find_duplicates()

        image_paths = self.file_database.keys()
        if self.ddlist:
            del self.ddlist
        self.ddlist = list()
        for image_path in image_paths:
            biggest_file = max([file for file in list(set(self.file_database[image_path]['duplicates'])) ], key=lambda file: os.path.getsize(file))
            self.ddlist.append(biggest_file)
        self.ddlist = sorted(list(set(self.ddlist)))
        return self.ddlist

    def get_deduplicated_file_list(self):
        if self.ddlist != None:
            return self.ddlist
        else:
            return self.generate_deduplicated_file_list()
