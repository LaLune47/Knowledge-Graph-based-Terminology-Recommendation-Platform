from flask import jsonify
import decimal
import json

class DecimalEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,decimal.Decimal):
            return float(o)

class JsonBaseResponse:
    def __init__(self,message="",data={}):
        self.code = 200
        self.message = message
        self.data = {}

    def toJson(self,code='',message = "",data={}):
        if code:
            self.code = code
        if message:
            self.message = message
        if data:
            self.data = data

        if self.code == 200 and not self.message:
            self.message = "success"

        j = json.dumps(self.__dict__, cls=DecimalEncoder)
        return jsonify(json.loads(j))

    def toDict(self,code='',message = "",data={}):
        if code:
            self.code = code
        if message:
            self.message = message
        if data:
            self.data = data

        if self.code == 200 and not self.message:
            self.message = "success"

        j = json.dumps(self.__dict__, cls=DecimalEncoder)
        return json.loads(j)

    def set_msg(self,code,msg):
        self.code = code
        self.message = msg