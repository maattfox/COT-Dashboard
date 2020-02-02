
from flask import Flask
app = Flask(__name__)


import config
import utils
import db






@app.route('/')
def hello_world():
    return 'Running Correctly!'






if __name__ == '__main__':

    # STARTUP

    if config.STARTUP["DOWNLOAD"]:
        utils.downloadAllData()

    if config.STARTUP["EXTRACT"]:
        utils.extractData()

    if config.STARTUP["PARSE"]:
        data = utils.parseData()


    #app.run(debug=config.DEBUG, host = config.HOST)
    app.run( host=config.HOST)