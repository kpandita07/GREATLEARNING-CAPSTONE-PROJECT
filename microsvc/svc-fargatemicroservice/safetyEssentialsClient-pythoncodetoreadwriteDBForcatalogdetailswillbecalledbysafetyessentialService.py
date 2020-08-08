import boto3
import json
import uuid
import logging
from collections import defaultdict
import argparse

# create a DynamoDB client using boto3. The boto3 library will automatically
# use the credentials associated with our ECS task role to communicate with
# DynamoDB, so no credentials need to be stored/managed at all by our code!
client = boto3.client('dynamodb')

def getItemsJson(items):
    # loop through the returned mysfits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    itemList = defaultdict(list)

    for item in items:
        safetyItem = {}

        safetyItem["itemId"] = item["ItemId"]["S"]
        safetyItem["name"] = item["Name"]["S"]
        safetyItem["description"] = item["Description"]["S"]
        safetyItem["price"] = int(item["Price"]["N"])
        safetyItem["category"] = item["Category"]["S"]
        safetyItem["thumbImageUri"] = item["ThumbImageUri"]["S"]
        safetyItem["profileImageUri"] = item["ProfileImageUri"]["S"]
      
        itemList["items"].append(safetyItem)

    return itemList

def getCartJson(items):
    # loop through the returned mysfits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    itemCount = defaultdict(list)  
    itemCount["count"] = len(items)

    return itemCount

def getAllItems():
    # Retrieve all Mysfits from DynamoDB using the DynamoDB scan operation.
    # Note: The scan API can be expensive in terms of latency when a DynamoDB
    # table contains a high number of records and filters are applied to the
    # operation that require a large amount of data to be scanned in the table
    # before a response is returned by DynamoDB. For high-volume tables that
    # receive many requests, it is common to store the result of frequent/common
    # scan operations in an in-memory cache. DynamoDB Accelerator (DAX) or
    # use of ElastiCache can provide these benefits. But, because out Mythical
    # Mysfits API is low traffic and the table is very small, the scan operation
    # will suit our needs for this workshop.
    response = client.scan(
        TableName='BravoSafetyEssentials'
    )

    logging.info(response["Items"])

    # loop through the returned mysfits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    itemList = getItemsJson(response["Items"])

    return json.dumps(itemList)

def queryItemsList(filter, value):
    # Use the DynamoDB API Query to retrieve mysfits from the table that are
    # equal to the selected filter values.
    response = client.query(
        TableName='BravoSafetyEssentials',
        IndexName=filter+'Index',
        KeyConditions={
            filter: {
                'AttributeValueList': [
                    {
                        'S': value
                    }
                ],
                'ComparisonOperator': "EQ"
            }
        }
    )

    # loop through the returned mysfits and add their attributes to a new dict
    # that matches the JSON response structure expected by the frontend.
    itemList = getItemsJson(response["Items"])

    # convert the create list of dicts in to JSON
    return json.dumps(itemList)

def getCart(userEmail):
    response = client.query(
        TableName='BravoSafetyEssentialsCart',
        IndexName='UserIndex',
        KeyConditions={
            'User': {
                'AttributeValueList': [
                    {
                        'S': userEmail
                    }
                ],
                'ComparisonOperator': "EQ"
            }
        }
    )

    itemList = getCartJson(response["Items"])

    # convert the create list of dicts in to JSON
    return json.dumps(itemList)

def queryItems(queryParam):

    logging.info(json.dumps(queryParam))

    filter = queryParam['filter']
    value = queryParam['value']

    return queryItemsList(filter, value)


def addToCart(itemId, userEmail):
    logging.info(itemId, userEmail)

    item = {}
    item["cartId"] = {
        "S": str(uuid.uuid4())
        }
    item["User"] = {
        "S": userEmail
        }
    item["itemId"] = {
        "S": itemId
        }

    client.put_item(
        TableName="BravoSafetyEssentialsCart",
        Item=item
        )

    response = {}
    response["headers"] = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"}
    response["statusCode"] = 200
    responseBody = {}
    responseBody["status"] = "success"
    response["body"] =  json.dumps(responseBody)
    logging.info(response)
    return response
# Retrive a single mysfit from DynamoDB using their unique mysfitId
def getItem(itemId):

    # use the DynamoDB API GetItem, which gives you the ability to retrieve
    # a single item from a DynamoDB table using its unique key with super
    # low latency.
    response = client.get_item(
        TableName='BravoSafetyEssentials',
        Key={
            'ItemId': {
                'S': itemId
            }
        }
    )

    item = response["Item"]

    safetyItem = {}
    safetyItem["itemId"] = item["ItemId"]["S"]
    safetyItem["name"] = item["Name"]["S"]
    safetyItem["description"] = item["Description"]["S"]
    safetyItem["price"] = int(item["Price"]["N"])
    safetyItem["category"] = item["Category"]["S"]
    safetyItem["thumbImageUri"] = item["ThumbImageUri"]["S"]
    safetyItem["profileImageUri"] = item["ProfileImageUri"]["S"]

    return json.dumps(safetyItem)

# So we can test from the command line
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filter')
    parser.add_argument('-v', '--value')
    args = parser.parse_args()

    filter = args.filter
    value = args.value

    if args.filter and args.value:
        print('filter is '+args.filter)
        print('value is '+args.value)

        print("Getting filtered values")
        items = queryItemsList(args.filter, args.value)
    else:
        print("Getting all values")
        items = getAllItems()

    print(items)
