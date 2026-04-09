### Slidemaker

Turn a folder of photos (JPEG or PNG) into PowerPoint slides. Includes fingerprint-based dedup, so you can let it loose on a huge folder of old photos and have a nice slide show in minutes for your next wedding reception or funeral.

Automatically scales photos proportionately to fit the background of a slide. Fills in the background with the color of your choice.

Default slide size is 16:9. Adjust the width/height arguments to a suitable aspect ration for your application.

#### CLI arguments:

`--width`: Width of slides. Default: 13.333".

`--height`: Height of slides. Default: 7.5".

`--input_dir`: Folder full of images. Defaults to current directory.

`--output_file`: Output file name. Defaults to 'Presentation.pptx'.

`--duration`: Delay between each slide transition, in seconds. Defaults to 5s.

`--overwrite`: Overwrite existing file if present.

`--bgcolor`: Background color (in RGB hex) for the slides. 

`--threshold`: Minimum "Hamming Distance" between two photos for duplicate warning.

`--blurry_background`: Instead of using the bgcolor, the script will insert a stretched and heavily blurred version of the image behind itself.

#### Truth Bomb

Google AI wrote like half of this. So it's not really mine.

#### Hamming Distance (--threshold parameter)

It's math. I actually _do_ know how it works, but it's largely unimportant.

Basically, the script will detect images that look similar to each other, based on an image fingerprinting technique called "difference hashing." There's math there too. Same caveat applies as above.

The Hamming Distance is essentially the number of differences between two fingerprints. The higher the number, the less similar the images are. Generally speaking, two copies of the same image will have a distance of 0, even if they've been resized/resampled. Small changes, like retouching to remove red-eye or a pimple, or slight cropping to remove fuzzies or background from a scanned image, will also be inconsequential.

This is great for filtering duplicates out of a large library of scanned photos. Because when your grandpa dropped that box of slides off at Walgreens in 2008, they didn't pick out the duplicates then, and now you have seven slightly different scans of your dad's engagement photo and his horrible, horrible '70s hair.

So, for my sets of family photos, I've found that a threshold of 14 was sufficient to find basically all of the duplicates. Higher than 20, and I started getting false positives. Your mileage may vary. But I think it's a useful feature.
