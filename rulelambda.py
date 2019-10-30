import datetime
import boto3

sns = boto3.client('sns')
dynamoDB = boto3.client('dynamodb')
topic = "IoTSNStopic"
content = "Your door is open now during the midnight"

def handler(event,context):
    print(event)
    ## put the item into DDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('IoTWorkshopDDB')
    response = table.put_item(
        Item={
            'ThingName': event['thing'],
            'Timestamp': event['timestamp'],
            'status': event['status']
        }
    )
    print(response)
    accountId = context.invoked_function_arn.split(":")[4]
    #take action if it is from GMT 22:00 - 1:00 (AEST 9:00 - 12:00 for testing)
    currentHour = datetime.datetime.now().hour
    topicArn = "arn:aws:sns:us-east-1:" + accountId + ":IoTSNStopic"
    print(currentHour)
    if (currentHour >= 22 or currentHour <= 1) and event['status'] == '1' :
        result = sns.publish(TopicArn=topicArn, Message=content)
        print("sent alarm")
    return
