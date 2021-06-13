import Binance
import boto3
import datetime
import requests
import json
import time

api = Binance.Binance()

def handler(event, context):
    try:
        accValue = api.getAccountValue()
        accPerformance = api.getAccountPerformance()
        performanceHistory = api.get10DayPerformance()
        response = {"accValue": accValue, "accPerformance": accPerformance, "performanceHistory": performanceHistory}
        return {
                'statusCode': 200,
                'headers': { "Content-Type": "application/json" },
                'body': json.dumps(response)
            }
    except Exception as e:
        return {
                'statusCode': 500,
                'headers': { "Content-Type": "application/json" },
                'body': json.dumps({"error": str(e)})
            }