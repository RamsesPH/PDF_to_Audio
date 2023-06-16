from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import PyPDF2
import pyttsx3

# ----- /variables area / -----

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = "uploads/"
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MBi
app.config['ALLOWED_EXTENSIONS'] = ['.pdf', '.text']


# ----- / Functions Area / -----

@app.route('/', methods=['GET', 'POST'])
def index():
    files = os.listdir(app.config['UPLOAD_DIRECTORY'])
    list_pdf = []

    for file in files:
        extension = os.path.splitext(file)[1].lower()
        if extension in app.config['ALLOWED_EXTENSIONS']:
            list_pdf.append(file)

    return render_template('index.html', list_pdf=list_pdf)


@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1].lower()
        # saving the file securely
        if file:
            if extension not in app.config['ALLOWED_EXTENSIONS']:
                return 'FILE IS NOT A PDF OR TEXT FILE'

            file.save(os.path.join(
              app.config['UPLOAD_DIRECTORY'],
              secure_filename(file.filename))
            )
    except RequestEntityTooLarge:
        return 'File is larger than 10 MB limit'
    return redirect('/')

@app.route('/serve_pdf/<filename>', methods=['GET'])
def serve_pdf(filename):
    return send_from_directory(app.config['UPLOAD_DIRECTORY'], filename)

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    selected_file = request.form['file']
    pdf_path = os.path.join(app.config['UPLOAD_DIRECTORY'], selected_file)
    with open(pdf_path, 'rb') as book:
        pdf_reader = PyPDF2.PdfReader(book)
        num_pages = len(pdf_reader.pages)
        #checking number of pages in the book
        print("Number of pages : ", num_pages)
        page_number = 7
        page = pdf_reader.pages[page_number]

        book = page.extract_text()
        print(book)  # checking if it is reading the correct page
        num_characters = len(book)  # checking the number of char in the selected page
        print("Number of characters:", num_characters)
        truncated_text = book[:470]  # truncating the size of the page to be read , for testing
        print(truncated_text)

    # ----- / text to Audio Area / -----

    speaker = pyttsx3.init()

    # ----- / VOICE / -----
    voices = speaker.getProperty('voices')  # getting details of current voice
    speaker.setProperty('voice', voices[33].id)
    # index 33, for an acceptable female voice,
    # index 7, is an acceptable male voice.
    # ----- / RATE / -----
    rate = speaker.getProperty('rate')  # setting details of current rate.
    print("the original rate is: ", rate)
    speaker.setProperty('rate', 170)  # reducing the voice speed 30%
    print("The used rate is :", rate)
    #
    # ----- / CHANGING VOLUME / -----
    volume = speaker.getProperty('volume')
    print("the original volume is: ", volume)
    speaker.setProperty('volume', 0.7)
    print("the volume level is :", volume)
    #
    speaker.say(truncated_text)
    speaker.runAndWait()
    return 'PDF processing and audio conversion completed'

if __name__ == '__main__':
    app.run()
