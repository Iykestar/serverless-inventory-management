# Check-Stock Lambda Function
# Author: Ikechukwu Enuosa
# Monitors inventory levels and sends SNS alerts

import json, boto3

def lambda_handler(event, context):
    """
    Triggered by DynamoDB Streams
    Checks inventory levels and sends SNS notification when stock is zero
    """
    print("Event received: " + json.dumps(event, indent=2))
    
    # Process each record from DynamoDB stream
    for record in event['Records']:
        newImage = record['dynamodb'].get('NewImage', None)
        
        if newImage:      
            count = int(record['dynamodb']['NewImage']['Count']['N'])
            
            # Check if item is out of stock
            if count == 0:
                store = record['dynamodb']['NewImage']['Store']['S']
                item = record['dynamodb']['NewImage']['Item']['S']
                
                # Construct notification message
                message = f"{store} is out of stock of {item}"
                print(message)
                
                # Send SNS notification
                sns = boto3.client('sns')
                alertTopic = 'NoStock'
                snsTopicArn = [t['TopicArn'] for t in sns.list_topics()['Topics']
                              if t['TopicArn'].lower().endswith(':' + alertTopic.lower())][0]
                
                sns.publish(
                    TopicArn=snsTopicArn,
                    Message=message,
                    Subject='Inventory Alert!',
                    MessageStructure='raw'
                )
    
    return f'Successfully processed {len(event["Records"])} records.'
