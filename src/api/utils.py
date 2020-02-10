import os
import re
import shutil
import requests
import zipfile
import io
import pandas as pd
from pymongo import MongoClient
import logging

#import src.api.config as config
import config

logger = logging.getLogger('__main__.' + __name__)



def setup_logger():
    """ Prints logger info to terminal"""

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Change this to DEBUG if you want a lot more info
    ch = logging.StreamHandler()

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def createFolder(rootPath, folderName):

    try:
        os.mkdir(rootPath + "/" + folderName)
    except OSError:
        logger.debug("Creation of the directory %s failed" % folderName)
    else:
        logger.debug("Successfully created the directory %s " % folderName)



def removeContentsFromPath(rootPath):
    for root, dirs, files in os.walk(rootPath):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))



def downloadAllData():
    # TODO: Thread the downloading of items to speed up function
    # TODO: Fix download of COT Legacy FO, zip is bad zip

    # REMOVE ALL DATA FROM DATA FOLDER!

    removeContentsFromPath(config.DATA_FOLDER)
    createFolder('.', 'data')
    # DOWNLOAD ALL DATA

    for source in config.SOURCES:
        logger.debug(source)
        createFolder(config.DATA_FOLDER, source["directory"])
        current_working_directory = config.DATA_FOLDER + source["directory"] + "/"

        for url_part in source["url_parts"]:

            for i in range(url_part["from_year"], url_part["to_year"] + 1):
                item_url_full_part = url_part["url"] + str(i) + config.SOURCE_FILE_TYPE

                logger.debug("Downloading {}, year: {}, url_part: {}".format(source["name"], i, item_url_full_part))

                url = config.SOURCE_URL + item_url_full_part

                r = requests.get(url, stream=True)
                with open(current_working_directory + item_url_full_part, 'w+b') as f:
                    f.write(r.content)
                    f.close()



def extractData():

    for source in config.SOURCES:

        current_folder = config.DATA_FOLDER + source["directory"]
        createFolder(current_folder, "extracted")
        output_data_folder = current_folder + "/extracted/"

        # clear each extracted folder
        removeContentsFromPath(output_data_folder)

        # for each file in folder
        directory = os.fsencode(current_folder)

        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            if filename.endswith(".zip"):
                with zipfile.ZipFile(current_folder + "/"+ filename, "r") as zip:
                    zip.extractall(output_data_folder + re.sub("[^0-9]", "", filename))

                logger.debug("parsing: {}".format(os.path.join(current_folder, filename)))



def parseData():

    data_frame_list = []

    for source in config.SOURCES:
        current_folder = config.DATA_FOLDER + source["directory"]
        output_data_folder = current_folder + "/extracted/"

        list = []

        for subdir, dirs, files in os.walk(output_data_folder):
            if len(files) == 1:
                logger.debug("Parsing {} file {}".format(subdir, files[0]))

                df = pd.read_csv(subdir + "/"+files[0], index_col=None, header=0)
                list.append(df)

        frame = pd.concat(list, axis=0, ignore_index=True)
        data_frame_list.append({"source_name": source["name"], "data": frame})

    return data_frame_list



def buildDB(importedData):

    # TODO: Sort out Pandas df to mongodb collection

    dbClient = MongoClient('mongodb', 27017)
    db = dbClient.cotdata

    # Change column names in Legacy Reports to match disagg reports, and strip market and exchange names to separate fields
    for list in importedData:
        if (list["source_name"] == "COT Legacy Futures") or (list["source_name"] == "COT Legacy Futures and Options"):

            logger.debug("Editing {}".format(list["source_name"]))

            list["data"].rename(columns={'Market and Exchange Names': 'Market_and_Exchange_Names',
                                         'CFTC Contract Market Code': 'CFTC_Contract_Market_Code',
                                         'CFTC Market Code in Initials': 'CFTC_Market_Code',
                                         'CFTC Region Code': 'CFTC_Region_Code',
                                         'CFTC Commodity Code': 'CFTC_Commodity_Code',
                                         'As of Date in Form YYMMDD': 'As_of_Date_In_Form_YYMMDD',
                                         'CFTC Contract Market Code (Quotes)': 'CFTC_Contract_Market_Code_Quotes',
                                         'CFTC Market Code in Initials (Quotes)': 'CFTC_Market_Code_Quotes',
                                         'CFTC Commodity Code (Quotes)': 'CFTC_Commodity_Code_Quotes'},
                                inplace=True)

        list["data"]['Market_Name'] = list["data"].apply(lambda row: row['Market_and_Exchange_Names'].rsplit(' - ', 1)[0], axis=1)
        list["data"]['Exchange_Name'] = list["data"].apply(lambda row: row['Market_and_Exchange_Names'].rsplit(' - ', 1)[1], axis=1)


        # Create Market Information Collections

        name = list["source_name"]
        print(name)

        if name in db.list_collection_names():
            db[name].drop()

        sourceCollection = db[name]
        print(sourceCollection)
        data = list["data"].to_dict(orient='records')
        logger.debug("Creating collection '{}'".format(name))
        sourceCollection.insert_many(data)




