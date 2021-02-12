# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 14:18:16 2021

@author: Spyro
"""

from flask import  send_from_directory, Flask, abort
from flask_restful import Api, Resource
from flask_cors import CORS, cross_origin


import os

import sys
import api_calls

app = Flask(__name__)
api = Api(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.route("/")
@cross_origin()

def heyWelt():
    return "Hello cross origin world"

class Visualization(Resource):

    def get(self, action):
        if action == "getGraphls":
            result_dict = {"data":[["biosource_name1",[["tf_name1","path1"], ["tf_name2","path2"]]],["biosource_name2",[["tf_name1","path1"], ["tf_name2","path2"]]]]}
                                 #[['GM12878', [['ARID3A_ENCFF003VDB', '0'], ['ARID3A_ENCFF003VDB', '1']]],['GMNEXT', [['ARID3A_ENCFF003VDB', '0'], ['ARID3A_ENCFF003VDB', '1']]] ]
            #return api_scripts.parse_result_csv()
            return result_dict

api.add_resource(Visualization, "/<string:action>")


if __name__ == "__main__":

    app.run(debug=True)