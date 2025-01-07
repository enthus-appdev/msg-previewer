from PIL import Image, ImageDraw, ImageFont

def write_text_to_image(text, output_image_path):
    """Writes given text to an image."""
    image_width = 1920
    image_height = 1080

    # We need a hardcoded font because the default font doesn't support all characters
    font = ImageFont.truetype("Arial.ttf", 20)

    # Create the image
    image = create_image((image_width, image_height), 'white', text, font, 'black')

    # Save the image as .jpg
    image.save(output_image_path, 'JPEG')

    print(f"Image saved as: {output_image_path}")

def create_image(size, bgColor, text, font, fontColor):
    """
    Creates an image with the specified size, background color, message, font, and font color.

    Args:
        size (tuple): The size of the image in pixels, specified as a tuple (width, height).
        bgColor (str): The background color of the image in RGB format.
        message (str): The message to be displayed on the image.
        font (PIL.ImageFont): The font to be used for the message.
        fontColor (str): The color of the message in RGB format.

    Returns:
        PIL.Image.Image: The created image.
    """
    W, H = size
    image = Image.new('RGB', size, bgColor)
    draw = ImageDraw.Draw(image)

    # Draw the given text anchored to the center of the image, with the given font and color.
    draw.text((W/2, H/2), text, anchor="mm", font=font, fill=fontColor)

    return image