from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
import json
import h2o
import sys
import traceback


@app.route('/predict', methods=['POST'])
def predict():
    if 1==1:
        try:
            json_ = json.dumps(request.json)
            print(json_)

            prediction = score(json_)

            return prediction

        except:

            return jsonify({'trace': traceback.format_exc()})
    else:
        print ('Train the model first')
        return ('No model here to use')


if __name__ == '__main__':
    try:
        port = int(sys.argv[1]) # This is for a command-line input
    except:
        port = 12345 # If you don't provide any port the port will be set to 12345

    '''
    # keep for sklearn models
    lr = joblib.load("Models\\model.pkl") # Load "model.pkl"
    print ('Model loaded')
    model_columns = joblib.load("Models\\model_columns.pkl") # Load "model_columns.pkl"
    print ('Model columns loaded')
    '''
    app.run(port=port, debug=True)