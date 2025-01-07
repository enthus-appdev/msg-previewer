from fast_mail_parser import parse_email
from bs4 import BeautifulSoup
import extract_msg
import textwrap
import re

def convert_html_to_text(html_content):
    """Converts HTML content to plain text using BeautifulSoup."""
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text()

def build_email_text_from_msg(msg_file_path):
    """Extracts content from a .msg file and format the resulting text."""

    msg = extract_msg.openMsg(msg_file_path)

    # Wrap message body
    msg.body = wrap_text(msg.body, 160)

    # Build text from the content of the email
    text = u'Datum: ' + msg.date.strftime("%d.%m.%Y") + '\nVon: ' + msg.sender + '\nAn: ' + msg.to + '\nBetreff: ' + msg.subject + '\n\nNachricht:\n' + msg.body[:1000]

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

def build_email_text_from_eml(eml_file_path):
    """Extracts content from a .eml file and format the resulting text."""

    with open(eml_file_path, 'r') as f:
        message_payload = f.read()

    msg = parse_email(message_payload)

    # Wrap message body
    body = wrap_text(msg.text_plain[0], 160)

    # Build text from the content of the email
    text = u'Datum: ' + msg.date + '\nBetreff: ' + msg.subject + '\n\nNachricht:\n' + body[:1000]

    # Get Attachment Filenames add to email text
    attachmentFilenames = ''
    for attachment in msg.attachments:
        attachmentFilenames += attachment.filename + '\n'
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