from flask import Flask, request, send_file, jsonify
from fast_mail_parser import parse_email, ParseError
import extract_msg
import text_functions
import image_functions
import os

app = Flask(__name__)

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

    # Check file by content
    # Check if it's a .msg file.
    try:
        extract_msg.openMsg(file_path)
        is_msg = True
    except:
        is_msg = False
        pass


    # Check if it's a .eml file.
    try:
        with open(file_path, 'r') as f:
            message_payload = f.read()
    
        _ = parse_email(message_payload)
        is_eml = True

    # UnicodeDecodeError is raised when the file is not a text file (e.g. an .msg file)
    except (ParseError, UnicodeDecodeError): 
        is_eml = False
        pass

    # Extract text from the file
    if is_msg:
        text = text_functions.build_email_text_from_msg(file_path)
    elif is_eml:
        text = text_functions.build_email_text_from_eml(file_path)
    else:
        return jsonify({"error": "File has no supported file type: eml, msg"}), 400
        
    # Write extracted text to image
    output_image_path = os.path.join('/tmp', 'output.jpg')
    image_functions.write_text_to_image(text, output_image_path)

    # Return the image file as a response
    return send_file(output_image_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082) # TODO change port number via params
