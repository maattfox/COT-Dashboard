
from flask import Flask
import logging
import os

#import src.api.config as config
#import src.api.utils as utils

import config
import utils

app = Flask(__name__)

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