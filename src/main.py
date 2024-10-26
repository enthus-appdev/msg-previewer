import textwrap
from flask import Flask, request, send_file, jsonify
import extract_msg
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from email import policy
from email.parser import BytesParser
import os
import re

app = Flask(__name__)

def convert_html_to_text(html_content):
    """Convert HTML content to plain text using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def build_email_text_from_msg(msg_file_path):
    """Extract content from a .msg file and format the resulting text."""
    # TODO might have to handle HTML content as well.
    msg = extract_msg.openMsg(msg_file_path)

    # Wrap message body
    msg.body = wrap_text(msg.body, 140)

    # Build text from the content of the email
    text = u'Datum: ' + msg.date.strftime("%d.%m.%Y") + '\nVon: ' + msg.sender + '\nAn: ' + msg.to + '\nBetreff: ' + msg.subject + '\n\nNachricht:\n' + msg.body

    # Get Attachment Filenames add to email text
    attachmentFilenames = ''
    for attachment in msg.attachments:
        attachmentFilenames += attachment.getFilename() + '\n'
    if attachmentFilenames:
        text += '\n\nAnhänge:\n' + attachmentFilenames

    # Remove some special characters that don't get displayed correctly
    text = text.replace('\r', '').replace('\t', '')

    # Remove duplicate spaces
    text = re.sub(' {2,}', ' ', text)

    return convert_html_to_text(text)

def wrap_text(text, width):
    """
    Wraps the given text to the specified width. Preserves existing single line breaks.

    Args:
        text (str): The text to be wrapped.
        width (int): The maximum width of each line.

    Returns:
        str: The wrapped text.

    """
    text = '\n'.join(['\n'.join(textwrap.wrap(line, width,
            break_long_words=False, replace_whitespace=False))
            for line in text.splitlines(keepends=True) if line.strip() != ''])

    return text

def extract_email_text_from_eml(eml_file_path):
    """Extract body content from a .eml file."""
    with open(eml_file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    """
    # Check for HTML or plain text part
    if msg.is_multipart():
        for part in msg.iter_parts():
            if part.get_content_type() == 'text/html':
                return convert_html_to_text(part.get_payload(decode=True).decode())
            elif part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode()
    else:
        # Non-multipart email, directly return text/plain or HTML content
        if msg.get_content_type() == 'text/html':
            return convert_html_to_text(msg.get_payload(decode=True).decode())
        else:
            return msg.get_payload(decode=True).decode()
    """
    return convert_html_to_text(msg.get_payload(decode=True).decode())

def write_text_to_image(text, output_image_path):
    """Write given text to an image."""
    image_width = 1920
    image_height = 1080

    # We need a hardcoded font because the default font doesn't support all characters
    font = ImageFont.truetype("Arial.ttf", 20)
    print(f"Font: {font.getbbox(text)}")

    # Create the image
    image = create_image((image_width, image_height), 'black', text, font, 'white')

    # Save the image as .jpg
    image.save(output_image_path, 'JPEG')

    print(f"Image saved as: {output_image_path}")

def create_image(size, bgColor, text, font, fontColor):
    """
    Create an image with the specified size, background color, message, font, and font color.

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

@app.route('/converter', methods=['POST'])
def convert_email():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file is None:
        return jsonify({"error": "No valid file provided"}), 400

    # Save the file to /tmp
    filename = file.filename
    file_path = os.path.join('/tmp', filename)
    file.save(file_path)

    file_type = ''
    # Check file by extension
    if filename.endswith('.msg'):
        file_type = 'msg'
    elif filename.endswith('.eml'):
        file_type = 'eml'  

    # Check file by content
    # Check if it's a .msg file
    try:
        extract_msg.openMsg(file_path)
        file_type = 'msg'
    except (extract_msg.UnrecognizedMSGTypeError, extract_msg.UnsupportedMSGTypeError):
        pass

    # Check if it's a .eml file
    with open('message.eml', 'r') as f:
        message_payload = f.read()

    # TODO implement (use https://github.com/namecheap/fast_mail_parser)
    try:
        email = parse_email(message_payload)
        file_type = 'eml'
    except: # TODO specify exceptions
        pass

    if file_type == 'msg':
        text = build_email_text_from_msg(file_path)
    elif file_type == 'eml':
        text = extract_email_text_from_eml(file_path) # TODO rewrite function
    else:
        return jsonify({"error": "File has no supported file type: eml, msg"}), 400
        
    # Write extracted text to image
    output_image_path = os.path.join('/tmp', 'output.jpg')
    write_text_to_image(text, output_image_path)

    # Return the image file as a response
    return send_file(output_image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082) # TODO change port number via params

# TODO extract both email types into single interface and use single function to compose text for the image
# TODO split into files