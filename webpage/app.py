import os
import sys
import webbrowser
import actions
from flask import Flask, flash, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename



def create_app(test_config=None):
    # print(template_folder)
    # create and configure the app
    if hasattr(sys, '_MEIPASS'):
        # Chnage template_folder path referance since pyinstaller change to app.exe to '_MEIPASS'
        # See https://stackoverflow.com/questions/32149892/flask-application-built-using-pyinstaller-not-rendering-index-html, 
        # second answer:'If you are trying to create a --onefile executable you will also need to add the directories in the spec file....'
        # Remember to use --add-data "templates;templates" for pyinstaller so it will copy the templates folder to its designated path.
        # pyinstaller --onefile --add-data "templates;templates" app.py

        base_dir = os.path.join(sys._MEIPASS)
        template_folder=os.path.join(base_dir, 'templates')
        app = Flask(__name__, template_folder = template_folder) #Use designated path to template_folder 
    else:
        app = Flask(__name__, instance_relative_config=True) 

    app.config.from_mapping(
        SECRET_KEY='dev',
        CONFIGJSON=os.path.join(app.instance_path, 'config.json'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    app.register_blueprint(actions.bp)
    app.add_url_rule('/', endpoint='index')

    return app

if __name__ == "__main__":
    app = create_app()
    webbrowser.open('http://127.0.0.1:5000')
    app.run(port=5000, debug=True, threaded=True)