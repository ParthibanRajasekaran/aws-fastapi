import os, boto3
from fastapi.testclient import TestClient
from moto import mock_aws
import sys

# Set AWS region before importing app
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda-dynamo'))
from app import app  # our FastAPI app for Dynamo

@mock_aws
def test_create_item():
    # Set up mock AWS credentials
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    
    # Set up in-memory DynamoDB
    dynamodb = boto3.resource('dynamodb')
    # Create table that our code will use
    dynamodb.create_table(
        TableName="ItemsTable",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode='PAY_PER_REQUEST'
    )
    os.environ["TABLE_NAME"] = "ItemsTable"
    
    # Reinitialize app's dynamodb resource to use the mock
    import importlib
    import app as app_module
    importlib.reload(app_module)
    
    client = TestClient(app_module.app)
    # Call the POST /items endpoint
    item_data = {"id": "test1", "value": "hello"}
    resp = client.post("/items", json=item_data)
    assert resp.status_code == 200
    # Verify the item was written to DynamoDB
    table = dynamodb.Table("ItemsTable")
    result = table.get_item(Key={"id": "test1"})
    assert "Item" in result and result["Item"]["value"] == "hello"

def test_full_flow_localstack():
    """
    This test is designed for LocalStack integration testing.
    To run this test, you need to have LocalStack running on localhost:4566
    and uncomment the code below.
    """
    pass
    # Uncomment below when LocalStack is available:
    # dyn_resource = boto3.resource('dynamodb', endpoint_url="http://localhost:4566")
    # s3_client = boto3.client('s3', endpoint_url="http://localhost:4566")
    # # Set up resources on LocalStack
    # dyn_resource.create_table(
    #     TableName="ItemsTable",
    #     KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
    #     AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
    #     BillingMode='PAYPERREQUEST'
    # )
    # s3_client.create_bucket(Bucket="my-demo-bucket")
    # # Inject env vars so our app uses localstack and resource names
    # os.environ["TABLE_NAME"] = "ItemsTable"
    # os.environ["BUCKET_NAME"] = "my-demo-bucket"
    # client = TestClient(app)
    # # Perform operations
    # client.post("/items", json={"id": "123", "value": "foo"})
    # client.put("/items/123", json={"value": "bar"})