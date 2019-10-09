import os

from flask import Flask, flash, request, render_template, redirect, url_for, send_file
from werkzeug.utils import secure_filename


def create_app(test_config=None):
    # create and configure the app
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

    from . import actions
    app.register_blueprint(actions.bp)
    app.add_url_rule('/', endpoint='index')

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)