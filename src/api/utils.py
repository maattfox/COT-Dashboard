import os
import re
import shutil
import requests
import zipfile
import io
import pandas as pd

import config



def createFolder(rootPath, folderName):
    try:
        os.mkdir(rootPath + "/" +folderName)
    except OSError:
        print("Creation of the directory %s failed" % folderName)
    else:
        print("Successfully created the directory %s " % folderName)



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

    # DOWNLOAD ALL DATA

    for source in config.SOURCES:
        print(source)
        createFolder(config.DATA_FOLDER, source["directory"])
        current_working_directory = config.DATA_FOLDER + source["directory"] + "/"

        for url_part in source["url_parts"]:

            for i in range(url_part["from_year"], url_part["to_year"] + 1):
                item_url_full_part = url_part["url"] + str(i) + config.SOURCE_FILE_TYPE

                print("Downloading {}, year: {}, url_part: {}".format(source["name"], i, item_url_full_part))

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

                print("parsing: {}".format(os.path.join(current_folder, filename)))



def parseData():

    data_frame_list = []

    for source in config.SOURCES:
        current_folder = config.DATA_FOLDER + source["directory"]
        output_data_folder = current_folder + "/extracted/"

        list = []

        for subdir, dirs, files in os.walk(output_data_folder):
            if len(files) == 1:
                print("Parsing {} file {}".format(subdir, list[0]))

                df = pd.read_csv(subdir + "/"+files[0], index_col=None, header=0)
                list.append(df)

        frame = pd.concat(list, axis=0, ignore_index=True)
        data_frame_list.append({"source_name": source["name"], "data": frame})

    return data_frame_list



def buildDB():
    pass



