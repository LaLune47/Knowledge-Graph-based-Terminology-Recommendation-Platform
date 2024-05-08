from flask import jsonify,request
from .json_params import JsonBaseResponse
from .. import app

@app.errorhandler(400)
def csrf_error(reason):
    print("request.is_json: ",request.is_json,    request.method)
    print(request.is_json)
    json_params = JsonBaseResponse()
    return json_params.toJson(code=400, message=str(reason))