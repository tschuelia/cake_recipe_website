import PIL
import PIL.ExifTags


def _image_exif_data(pil_image):
    if pil_image._getexif():
        return {
            PIL.ExifTags.TAGS[k]: v
            for k, v in pil_image._getexif().items()
            if k in PIL.ExifTags.TAGS
        }


def get_image_size(image):
    """
    Returns the size of the image. The image size depends whether the image is rotated.
    This is indicated by the exif "Orientation" key.
    6 means the image is rotated by 90 degrees
    8 means the image is rotated by 270 degrees
    In both cases height and width of the image need to be flipped.
    """
    pil_image = PIL.Image.open(image)
    exif = _image_exif_data(pil_image)
    # check if image has exif data
    if (
        exif
        and "Orientation" in exif.keys()
        and (exif["Orientation"] == 6 or exif["Orientation"] == 8)
    ):
        # (height, width)
        return (pil_image.size[0], pil_image.size[1])

    return (pil_image.size[1], pil_image.size[0])