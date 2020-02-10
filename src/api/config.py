import os


ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
DEBUG = ENVIRONMENT == "dev"
HOST = '0.0.0.0' if ENVIRONMENT == "prod" else 'localhost'


STARTUP = {"DOWNLOAD": True,
           "EXTRACT": True,
           "PARSE": True,
           "REBUILD_DB": True}


DATA_FOLDER = './data/'


SOURCE_URL = "https://www.cftc.gov/files/dea/history/"
SOURCE_FILE_TYPE = ".zip"

SOURCES = [{ "name": "Disaggregated Futures",
             "directory": "disaggregated_futures",
             "url_parts": [{"url":"fut_disagg_txt_", "from_year": 2010, "to_year": 2020}]},

            { "name": "Disaggregated Futures and Options",
              "directory": "disaggregated_futures_options",
              "url_parts": [{"url":"com_disagg_txt_", "from_year": 2010, "to_year": 2020}]},

            { "name": "Financial Futures",
              "directory": "financial_futures",
              "url_parts": [{"url":"fut_fin_txt_", "from_year": 2010, "to_year": 2020}]},

            { "name": "Financial Futures and Options",
              "directory": "financial_futures_options",
              "url_parts": [{"url":"com_fin_txt_", "from_year": 2010, "to_year": 2020}]},

            { "name": "COT Legacy Futures",
              "directory": "cot_legacy_futures",
              "url_parts": [{"url":"deacot", "from_year": 1986, "to_year": 2020}]}


           ]
"""
SOURCES = [
            { "name": "COT Legacy Futures and Options",
              "directory": "cot_legacy_futures_options",
              "url_parts": [{"url":"deahistfo", "from_year": 1995, "to_year": 2003},
                            {"url":"deahistfo_", "from_year": 2004, "to_year": 2020}]}
           ]
"""
