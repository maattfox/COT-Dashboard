
from flask import Flask
app = Flask(__name__)

import logging

import config
import utils
import db


logger = utils.setup_logger()






@app.route('/')
def hello_world():
    return 'Running Correctly!'











if __name__ == '__main__':

    if config.STARTUP["DOWNLOAD"]:
        utils.downloadAllData()

    if config.STARTUP["EXTRACT"]:
        utils.extractData()

    if config.STARTUP["PARSE"]:
        data = utils.parseData()

        if config.STARTUP["REBUILD_DB"]:
            utils.buildDB(data)
    #app.run(debug=config.DEBUG, host = config.HOST)
    app.run( host=config.HOST)