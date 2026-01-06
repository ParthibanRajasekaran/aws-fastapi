from fastapi import FastAPI, HTTPException
from mangum import Mangum
import boto3
import os
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths

# Initialize logger with Powertools
logger = Logger(service="dynamodb-api")

app = FastAPI()

# Initialize DynamoDB resource outside handler for connection reuse
# This leverages Lambda execution environment reuse for better performance
# Region is required to be set via AWS_DEFAULT_REGION environment variable
dynamodb = boto3.resource(
    "dynamodb", 
    region_name=os.environ.get("AWS_DEFAULT_REGION") or os.environ.get("AWS_REGION")
)
table = dynamodb.Table(os.environ.get("TABLE_NAME", "ItemsTable"))

@app.post("/items")
def create_item(item: dict):
    """Create a new item in DynamoDB."""
    # Validate input (could use Pydantic model for schema)
    if "id" not in item or "value" not in item:
        logger.error("Invalid item data received", extra={"item": item})
        raise HTTPException(status_code=400, detail="Invalid item data")
    
    # Put item into DynamoDB
    try:
        table.put_item(Item=item)
        logger.info("Item created successfully", extra={"item_id": item['id']})
    except Exception as e:
        logger.error("Failed to create item", extra={"error": str(e), "item_id": item['id']})
        raise HTTPException(status_code=500, detail="Failed to create item")
    
    return {"message": f"Item {item['id']} created."}

@app.put("/items/{item_id}")
def update_item(item_id: str, update: dict):
    """Update an existing item in DynamoDB.
    
    Uses UpdateExpression (best practice) instead of deprecated AttributeUpdates.
    """
    if not update:
        logger.error("Empty update data received", extra={"item_id": item_id})
        raise HTTPException(status_code=400, detail="Update data cannot be empty")
    
    # Build UpdateExpression and ExpressionAttributeValues
    update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update.keys()])
    expression_attribute_names = {f"#{k}": k for k in update.keys()}
    expression_attribute_values = {f":{k}": v for k, v in update.items()}
    
    try:
        table.update_item(
            Key={"id": item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        logger.info("Item updated successfully", extra={"item_id": item_id, "updated_fields": list(update.keys())})
    except Exception as e:
        logger.error("Failed to update item", extra={"error": str(e), "item_id": item_id})
        raise HTTPException(status_code=500, detail="Failed to update item")
    
    return {"message": f"Item {item_id} updated."}

@app.get("/items/{item_id}")
def get_item(item_id: str):
    """Retrieve an item from DynamoDB by ID."""
    try:
        response = table.get_item(Key={"id": item_id})
        if "Item" not in response:
            logger.info("Item not found", extra={"item_id": item_id})
            raise HTTPException(status_code=404, detail="Item not found")
        
        logger.info("Item retrieved successfully", extra={"item_id": item_id})
        return response["Item"]
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve item", extra={"error": str(e), "item_id": item_id})
        raise HTTPException(status_code=500, detail="Failed to retrieve item")

handler = Mangum(app, lifespan="off")  # AWS Lambda entry point with optimized lifespan handling
