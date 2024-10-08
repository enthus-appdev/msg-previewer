from flask import Flask, request, send_file, jsonify
import extract_msg
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from email import policy
from email.parser import BytesParser
import os
import textwrap

app = Flask(__name__)

def convert_html_to_text(html_content):
    """Convert HTML content to plain text using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def extract_email_body_from_msg(msg_file_path):
    """Extract body content from a .msg file."""
    msg = extract_msg.Message(msg_file_path)
    
    # Check if the email body is in HTML format
    if msg.body_is_html:
        # Convert HTML body to plain text
        return convert_html_to_text(msg.body)
    else:
        # Use the plain text body
        return msg.body

def extract_email_body_from_eml(eml_file_path):
    """Extract body content from a .eml file."""
    with open(eml_file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

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

def convert_email_to_image(body_content, output_image_path):
    """Convert email body content to an image."""
    # Set up image dimensions
    image_width = 800
    padding = 20
    font = ImageFont.load_default()

    # Text wrapping for proper formatting
    wrapped_text = textwrap.fill(body_content, width=80)

    # Estimate height needed for the text
    dummy_image = Image.new('RGB', (image_width, 1), color=(255, 255, 255))
    draw = ImageDraw.Draw(dummy_image)
    text_height = draw.textsize(wrapped_text, font=font)[1]
    num_lines = len(wrapped_text.split('\n'))
    image_height = padding * 2 + num_lines * text_height

    # Create the actual image
    image = Image.new('RGB', (image_width, image_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Draw the text on the image
    draw.text((padding, padding), wrapped_text, font=font, fill=(0, 0, 0))

    # Save the image as .jpg
    image.save(output_image_path, 'JPEG')
    print(f"Image saved as: {output_image_path}")

@app.route('/converter', methods=['POST'])
def convert_email():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and (file.filename.endswith('.msg') or file.filename.endswith('.eml')):
        filename = file.filename
        file_path = os.path.join('/tmp', filename)
        file.save(file_path)

        # Extract body content based on file type
        if filename.endswith('.msg'):
            body_content = extract_email_body_from_msg(file_path)
        elif filename.endswith('.eml'):
            body_content = extract_email_body_from_eml(file_path)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        # Convert email body to image
        output_image_path = os.path.join('/tmp', 'output.jpg')
        convert_email_to_image(body_content, output_image_path)

        # Return the image file as a response
        return send_file(output_image_path, mimetype='image/jpeg')

    return jsonify({"error": "Unsupported file format"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
