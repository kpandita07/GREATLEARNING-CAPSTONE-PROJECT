from flask import Flask, jsonify, json, Response, request
from flask_cors import CORS
import safetyEssentialsClient
import logging

# A very basic API created using Flask that has two possible routes for requests.

app = Flask(__name__)
CORS(app)

# The service basepath has a short response just to ensure that healthchecks
# sent to the service root will receive a healthy response.
@app.route("/")
def healthCheckResponse():
    return jsonify({"message" : "Nothing here, used for health check. Try /items instead."})

# Returns the data for all of the Mysfits to be displayed on
# the website.  If no filter query string is provided, all mysfits are retrived
# and returned. If a querystring filter is provided, only those mysfits are queried.
@app.route("/items")
def getItems():

    filterCategory = request.args.get('filter')
    if filterCategory:
        filterValue = request.args.get('value')
        queryParam = {
            'filter': filterCategory,
            'value': filterValue
        }
        # a filter query string was found, query only for those mysfits.
        serviceResponse = safetyEssentialsClient.queryItems(queryParam)
    else:
        # no filter was found, retrieve all mysfits.
        serviceResponse = safetyEssentialsClient.getAllItems()

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    print(flaskResponse)
    return flaskResponse

# retrieve the full details for a specific mysfit with their provided path
# parameter as their ID.
@app.route("/items/<itemId>", methods=['GET'])
def getItem(itemId):
    serviceResponse = safetyEssentialsClient.getItem(itemId)

    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

@app.route("/items/<itemId>/addtocart", methods=['POST'])
def addToCart(itemId):
    req_data = request.get_json()
    logging.info(req_data)
    serviceResponse = safetyEssentialsClient.addToCart(itemId, req_data['email'])
    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

@app.route("/cart", methods=['GET'])
def getCart():
    userEmail = request.args.get('email')
    print('getCart user-email: {}'.format(userEmail))
    serviceResponse = safetyEssentialsClient.getCart(userEmail)
    print('getCart serviceResponse: {}'.format(serviceResponse))
    flaskResponse = Response(serviceResponse)
    flaskResponse.headers["Content-Type"] = "application/json"

    return flaskResponse

# Run the service on the local server it has been deployed to,
# listening on port 8080.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
