from fastapi import FastAPI, Response, HTTPException
from mangum import Mangum
import boto3, os

app = FastAPI()
s3 = boto3.client("s3")  # region will be picked from environment or AWS config
bucket_name = os.environ.get("BUCKET_NAME", "my-demo-bucket")
bucket_owner = os.environ.get("BUCKET_OWNER")  # Expected bucket owner account ID

@app.get("/files/{file_key:path}")
def get_file(file_key: str):
    try:
        get_params = {"Bucket": bucket_name, "Key": file_key}
        if bucket_owner:
            get_params["ExpectedBucketOwner"] = bucket_owner
        obj = s3.get_object(**get_params)
    except s3.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail="File not found")
    # Assuming text file for simplicity; if binary, we might return Base64 or set StreamingResponse
    content = obj['Body'].read()
    return Response(content, media_type="text/plain")

handler = Mangum(app)
