### Slidemaker

Turn a folder of photos into PowerPoint slides. Includes fingerprint-based dedup, so you can let it loose on a huge folder of old photos and have a nice slide show in minutes for your next wedding reception or funeral.

```
.avif, .bmp, .gif, .j2k, .jp2, .jpx, .pcx, .tiff, .tif, .jpg, .jpeg, .png, .webp
```

Automatically scales photos proportionately to fit the background of a slide. Fills in the background with the color of your choice, or a blurred/stretched version of the photo. (Like how those vertical videos get letterboxed on YouTube or Instagram.)

Default slide size is PowerPoint's default of 13.333 by 7.5 inches, with a 16:9 aspect ratio. Adjust the width/height arguments to get the desired aspect ratio for your application.

**A Note About File Size**: Pictures are big, and they're usually not able to be compressed any more than they already are. So if you have a gigabyte of photographs, you're probably going to end up with a gigabyte of powerpoint slides. There is often a difference, logistically, between dealing with five hundred 2MB files, and a single 1000MB file.

**Examples**:

  * For 1920x1200 screens with a 16:10 aspect ratio, you can set --height to 8.333.
  * For 1280x960 screens or other older 4:3 projectors, you can set --width to 10.
  * For 1280x1024 screens which have that rare 5:4 aspect ration, you can set -width to 10 and --height to 8.

Generally speaking, you're almost never going to see anything but 16:9 on a computer. But some places still have the older 4:3 stuff kicking around.

#### Use

```
python slidemaker.py --input_dir imgs --deduplicate --transition 2 --blurry_background
```

#### CLI arguments:

  `--width`: Width for slides. Default: 13.333".  
  `--height`: Height for slides. Default: 7.5".  
  
  `--input_dir`: Folder full of images. Defaults to current directory.  
  `--output_file`: Output file name. Defaults to 'Presentation.pptx'.  
  `--overwrite`: Overwrite existing file if present.  
  `--add_format`: Force the script to attempt to process files ending in this file extension. (e.g., `.blp` or something.)  
  &ensp;&ensp;&ensp;&ensp;- The image type still needs to be [supported by Pillow](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).  

  `--duration`: Delay between each slide transition, in seconds. Defaults to 5s.  
  `--transition`: Select transition type. 0 = none, 1 = fade, 2 = wipe, 3 = push, 4 = ripple.  
  `--bgcolor`: Background color (in RGB hex) for the slides. Default is "FFFFFF" (white). 3-character shorthand (#FFF) is supported.
  `--blurry_background`: Instead of using the bgcolor, the script will insert a stretched and heavily blurred version of the image behind itself.  
  &ensp;&ensp;&ensp;&ensp;- This will significantly increase file size, since there are now two copies of all the pictures instead of one.  

  `--deduplicate`: Find and omit similar-looking images based on similarity threshold.  
  `--threshold`: Minimum "Hamming Distance" between two photos for duplicate detection. (Does nothing unless --deduplicate is also set, defaults to 12.)

#### Truth Bomb

Google AI wrote like half of this. And then I had to rewrite basically all of it. But somehow I still feel guilty.

#### Deduplicating and the Hamming Distance

If you enable image deduplication with the `--deduplicate` flag, the script will automatically detect duplicate pictures, keep the image with the largest file size (usually that's the highest quality one) and omit the rest when creating the slide show. However, this adds non-trivial processing time to the process of generating the slideshow, so be prepared to wait a little bit.

How does it work? It's math. I actually _do_ know how it works, believe it or not, but here's the tl;dr version:

The script first generates a fingerprint for each image via a method called "difference hashing." More math. Just think of it as a series of numbers that represent the "gist" of what the image looks like.

The Hamming Distance (named after [Richard Hamming](https://en.wikipedia.org/wiki/Richard_Hamming) of Bell Labs) is then a measure of how different the two hashes are: the higher the number, the less similar the images are.

  * Generally speaking, two copies of the same image will have a distance of 0, or a very low single digit number, even if they've been resized, resampled, and/or stretched.
  * Small changes, like retouching to remove red-eye or a pimple, or slight cropping to remove fuzzies or background from a scanned image, will also not have much effect.
  * With enough editing, or with pictures that are just not the same, the number will be pretty large.

This is great for filtering duplicates out of a large library of scanned photos. Because when your grandpa dropped that box of slides off at Walgreens in 1997, they didn't pick out the duplicates either, and now you have four CD-Rs with six slightly different high resolution scans of your dad on prom night in a powder blue tuxedo and a mullet.

So, for my sets of family photos, I've found that a threshold of 14 was sufficient to find basically all of the duplicates. Higher than 20, and I started getting false positives. Your mileage may vary.