from fastapi import FastAPI, Response, HTTPException
from mangum import Mangum
import boto3
import os
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError

# Initialize logger with Powertools
logger = Logger(service="s3-api")

app = FastAPI()

# Initialize S3 client outside handler for connection reuse
# This leverages Lambda execution environment reuse for better performance
s3 = boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
bucket_name = os.environ.get("BUCKET_NAME", "my-demo-bucket")
bucket_owner = os.environ.get("BUCKET_OWNER")  # Expected bucket owner account ID

@app.get("/files/{file_key:path}")
def get_file(file_key: str):
    """Retrieve a file from S3 bucket.
    
    Supports bucket owner verification for enhanced security.
    """
    try:
        get_params = {"Bucket": bucket_name, "Key": file_key}
        if bucket_owner:
            get_params["ExpectedBucketOwner"] = bucket_owner
        
        logger.info("Retrieving file from S3", extra={"file_key": file_key, "bucket": bucket_name})
        obj = s3.get_object(**get_params)
        
        # Read file content
        content = obj['Body'].read()
        logger.info("File retrieved successfully", extra={"file_key": file_key, "size": len(content)})
        
        return Response(content, media_type="text/plain")
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchKey':
            logger.info("File not found", extra={"file_key": file_key, "bucket": bucket_name})
            raise HTTPException(status_code=404, detail="File not found")
        else:
            logger.error("S3 client error", extra={"error": str(e), "error_code": error_code, "file_key": file_key})
            raise HTTPException(status_code=500, detail="Failed to retrieve file")
    except Exception as e:
        logger.error("Unexpected error retrieving file", extra={"error": str(e), "file_key": file_key})
        raise HTTPException(status_code=500, detail="Internal server error")

handler = Mangum(app, lifespan="off")  # AWS Lambda entry point with optimized lifespan handling
