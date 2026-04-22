### Slidemaker

Turn a folder of photos (or a folder tree) into PowerPoint slides. Includes fingerprint-based dedup, so you can let it loose on a huge folder of old photos and have a nice slide show in minutes for your next wedding reception or funeral.

```
.avif, .bmp, .gif, .j2k, .jp2, .jpx, .pcx, .tiff, .tif, .jpg, .jpeg, .png, .webp
```

Automatically scales photos proportionately to fit the background of a slide. Fills in the background with the color of your choice, or a blurred/stretched version of the photo. (Like how those vertical videos get letterboxed on YouTube or Instagram.)

Default slide size is PowerPoint's default of 13.333 by 7.5 inches, with a 16:9 aspect ratio. Adjust the width/height arguments to get the desired aspect ratio for your application.

Images are saved in the PowerPoint presentation using JPEG compression. Set the `--image_quality` argument to 90 or more if you have lots of screenshots and line art, to avoid compression artifacts. Photographs are usually ok at the default setting of 75. You can also set that value lower to decrease resulting file size.

**Examples**:

  * For 1920x1200 screens with a 16:10 aspect ratio, you can set --height to 8.333.
  * For 1280x960 screens or other older 4:3 projectors, you can set --width to 10.
  * For 1280x1024 screens which have a 5:4 aspect ration, you can set -width to 10 and --height to 8.

Generally speaking, you're almost never going to see anything but 16:9 on a computer. But some places still have the older 4:3 stuff kicking around.

Also, even if you have a newer projector, you might have an older screen which is squareish. Setting the projector to a 4:3 or 5:4 aspect ratio might be preferable in that case as well, if the hardware supports the older video modes.

#### How To Use

```
# Make a slideshow from the images in the "imgs" directory
# with blurred image backgrounds and wipe transitions.
# Remove duplicates.

python slidemaker.py --input_dir ./imgs --deduplicate --transition wipe --blurry_background
```

#### CLI Arguments

Slide Layout:  
  `--width`: Width for slides. Default: 13.333".  
  `--height`: Height for slides. Default: 7.5".  
  `--bgcolor`: Background color (in RGB hex) for the slides.  
  &ensp;&ensp;&ensp;&ensp;- Default is "#FFFFFF" (white).  
  &ensp;&ensp;&ensp;&ensp;- 3-character shorthand (#FFF) is supported.  
  &ensp;&ensp;&ensp;&ensp;- Case insensitive.  
  &ensp;&ensp;&ensp;&ensp;- '#' is optional.  
  `--blurry_background`: Instead of using the bgcolor, the script will insert a stretched and heavily blurred version of the image behind itself.  
  &ensp;&ensp;&ensp;&ensp;- This will significantly increase file size, since there are now two copies of all the pictures instead of one.  
  &ensp;&ensp;&ensp;&ensp;- Title slides will use the background color specified by `--bgcolor`.  

Slideshow Settings:  
  `--duration`: Delay between each slide transition, in seconds. Defaults to 5s.  
  `--transition`: Select transition type. [none|fade|wipe|push|ripple].  
  `--titles`: Inserts a title slide before each folder's images, using the name of the folder as the title.  
  `--captions_file`: Specify a filename for photo captions.  
  &ensp;&ensp;&ensp;&ensp;- Captions will be in a textbox.  
  &ensp;&ensp;&ensp;&ensp;- The background of the textbox will match `--bgcolor`.  
  &ensp;&ensp;&ensp;&ensp;- Text will be black or white to best contrast the background color.  

Presentation Output:  
  `--output_file`: Output file name. Defaults to 'Presentation.pptx'.  
  `--overwrite`: Overwrite existing file if present.  

Image Selection:  
  `--input_dir`: Folder full of images. Defaults to current directory.  
  `--subfolders`: Instead of only looking in `input_dir` for images, looks recursively in subfolders also.  
  `--deduplicate`: Find and omit similar-looking images based on similarity threshold. This will also save a JSON full of duplicate image info.  
  `--threshold`: Minimum "Hamming Distance" between two photos for duplicate detection. (Does nothing unless --deduplicate is also set, defaults to 12.)

Image Quality:  
  `--auto_adjust`: Applies an auto-levels to each photo, and a gamma adjustment to the ones that are too dark.  
  `--image_quality`: Level of JPEG compression to use when saving slides. Defaults to 75.  
  &ensp;&ensp;&ensp;&ensp;- Allowed range is 1-100.  
  &ensp;&ensp;&ensp;&ensp;- Bigger numbers mean bigger files but higher image quality.  
  `--resample`: Downsamples images if the effective DPI is higher than the number specified. (0 disables.)  
  `--auto_contrast`: Execute an auto contrast action on the images when adding them to the slideshow.  
  
Other Settings:
  `--logfile`: Use a log file instead of stdout. If you do not provide an argument, a default file name 'slidemaker.log' is used.  

#### Captions File:

Captions file basically is a yaml file full of key/value pairs, which looks like this:

```
# captions.yaml
photo1.jpg: 'This is the caption for photo1'
photo2.jpg: 'This is a different caption.'
photo3.jpg: 'Also a caption for photo3.'
...
```

As each image/slide is prepared, the caption file will be checked, and if the filename has a caption specified, it will be placed in the lower left of the slide.
  * The caption will obscure some of the image.  
  * You do not have to provide captions for all of the photos.  

#### Memory Use

Python normally does a pretty good job managing its own memory use, but in this case, the total amount of RAM in use can get pretty big pretty quickly.

Although it slows things down a bit, I manually added garbage collection calls to more aggressively shed unneeded data. However, in the end, the application still builds the entire powerpoint presentation in memory before writing it.

So, if you don't have enough RAM you may encounter issues with sets of photos exceeding your RAM amount. (Or which exceed 4GB, assuming you for some reason are using a 32-bit version of Python.)

You can decrease the amount of RAM used by using the `--resample` and `--image_quality` arguments; lower resolution and lower quality images use less memory and storage space.

#### Deduplicating and the Hamming Distance

If you enable image deduplication with the `--deduplicate` flag, the script will automatically detect duplicate pictures, keep the image with the largest file size (usually that's the highest quality one) and omit the rest when creating the slide show. However, this adds non-trivial processing time to the process of generating the slideshow, so be prepared to wait a little bit.

How does it work? It's math. I actually _do_ know how it works, believe it or not, but here's the tl;dr version:

The script first generates a fingerprint for each image via a method called "difference hashing." More math. Just think of it as a series of numbers that represent the "gist" of what the image looks like.

The Hamming Distance (named after [Richard Hamming](https://en.wikipedia.org/wiki/Richard_Hamming) of Bell Labs) is then a measure of how different the two hashes are: the higher the number, the less similar the images are.

  * Generally speaking, two copies of the same image will have a distance of 0, or a very low single digit number, even if they've been resized, resampled, and/or stretched.
  * Small changes, like retouching to remove red-eye or a pimple, or slight cropping to remove fuzzies or background from a scanned image, will also not have much effect.
  * With enough editing, or with pictures that are just not the same, the number will be pretty large.

This is great for filtering duplicates out of a large library of scanned photos. Because when your grandpa dropped that box of slides off at Walgreens in 1997, they didn't pick out the duplicates either, and now you have twelve CD-Rs with six slightly different high resolution scans of the same photo of your dad on prom night, May 1976, in a powder blue tuxedo and a mullet. Let's face it, he was cooler than you.

So, for my sets of family photos, I've found that a threshold of 14 was sufficient to find basically all of the duplicates. Higher than 20, and I started getting false positives. Your mileage may vary.
