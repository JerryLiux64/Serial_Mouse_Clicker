import json
from flask import Blueprint, flash, g, redirect, url_for, redirect, render_template, request, current_app, jsonify, session
from werkzeug.exceptions import abort
from auto import AutoClicker

bp = Blueprint('actions', __name__)
actionClicker = []

@bp.route('/')
def index():
    return render_template("index.html")

@bp.route('/getconfig', methods=['POST'])
def getconfig():
    if request.method == 'POST':
        tabledata = request.form.get('tabledata', type=str)
        current_app.logger.debug(tabledata)
        with open(current_app.config['CONFIGJSON'], 'w') as f:
            current_app.logger.debug("File saved to %s" % current_app.config['CONFIGJSON'])
            f.write(tabledata)
    return "", 204

@bp.route('/run_action', methods = ['GET', 'POST'])
def run_action():
    with open(current_app.config['CONFIGJSON'], 'r') as f:
        content = json.load(f)
    autoclicker = AutoClicker(content)
    actionClicker.clear()
    actionClicker.append(autoclicker)
    autoclicker.run()
    return "", 204

@bp.route('/stop_running', methods = ['GET', 'POST'])
def stop_running():
    actionclicker = actionClicker[0]
    actionClicker.clear()
    current_app.logger.debug(actionclicker)
    if actionclicker:
        actionclicker.stop()
    return "", 204
