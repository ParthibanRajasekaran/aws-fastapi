from fastapi import FastAPI, HTTPException
from mangum import Mangum
import boto3, os

app = FastAPI()
dynamodb = boto3.resource("dynamodb")  # region will be picked from environment or AWS config
table = dynamodb.Table(os.environ.get("TABLE_NAME", "ItemsTable"))

@app.post("/items")
def create_item(item: dict):
    # Validate input (could use Pydantic model for schema)
    if "id" not in item or "value" not in item:
        raise HTTPException(status_code=400, detail="Invalid item data")
    # Put item into DynamoDB
    table.put_item(Item=item)
    return {"message": f"Item {item['id']} created."}

@app.put("/items/{item_id}")
def update_item(item_id: str, update: dict):
    # Update item in DynamoDB (expects `update` contains attributes to update)
    attrs = {k: {"Value": v, "Action": "PUT"} for k, v in update.items()}
    table.update_item(Key={"id": item_id}, AttributeUpdates=attrs)
    return {"message": f"Item {item_id} updated."}

handler = Mangum(app)  # AWS Lambda entry point
