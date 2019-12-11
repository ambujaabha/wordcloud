from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
from wordcloud import *
import os
import code
import slate3k as slate
from os import path

UPLOAD_FOLDER = '/Users/ambujaabha/Documents' # Enter desired upload folder.

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])


def allowed_file(filename):
    return "." in filename and filename.split(".")[1] in ALLOWED_EXTENSIONS


@app.route('/create_wordcloud', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected for uploading'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        current_directory = app.config['UPLOAD_FOLDER']
        if filename.split(".")[1] == "txt":
            text = open(path.join(current_directory, filename)).read()
        else:
            with open(path.join(current_directory, filename),'rb') as f:
                text = "".join(slate.PDF(f))
        wordcloud = WordCloud().generate(text)
        wordcloud.to_file(filename.split(".")[0]+'.jpeg')
        return jsonify({'message': "Successfully saved image to current directory"}), 201
    else:
        return jsonify({'message': 'Allowed file types are txt, pdf'}), 400

@app.route("/search", methods=['POST'])
def search_wordclouds():
    word = request.get_json()['word']
    result_list = []
    for item in os.listdir(os.path.expanduser(app.config['UPLOAD_FOLDER'])):
        if not os.path.isdir(item):
            current_directory = app.config['UPLOAD_FOLDER']
            if item.split(".")[1] == "txt":
                text = open(path.join(current_directory, item)).read()
            else:
                with open(path.join(current_directory, item),'rb') as f:
                    text = "".join(slate.PDF(f))
            if word in text:
                result_list.append(item.split(".")[0] + ".jpeg")
    return jsonify({result_list})
if __name__ == "__main__":
    app.run(port=3000, debug=True)
