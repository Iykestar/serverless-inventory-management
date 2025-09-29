# Load-Inventory Lambda function
# Author: Ikechukwu Enuosa
# This function processes inventory files uploaded to S3
import json, urllib, boto3, csv

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')
inventoryTable = dynamodb.Table('Inventory')

def lambda_handler(event, context):
    print("Event received: " + json.dumps(event, indent=2))
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    localFilename = '/tmp/inventory.txt'
    
    try:
        s3.meta.client.download_file(bucket, key, localFilename)
    except Exception as e:
        print(f'Error getting object {key} from bucket {bucket}: {e}')
        raise e
    
    with open(localFilename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        rowCount = 0
        
        for row in reader:
            rowCount += 1
            try:
                inventoryTable.put_item(
                    Item={
                        'Store': row['store'],
                        'Item': row['item'],
                        'Count': int(row['count'])
                    }
                )
            except Exception as e:
                print(f"Unable to insert data: {e}")
    
    return f"{rowCount} records processed successfully"
