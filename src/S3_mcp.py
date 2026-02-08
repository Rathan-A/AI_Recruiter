import os
import boto3
from mcp.server.fastapi import MCPServer
from mcp.types import Tool, ToolResult

# -----------------------
# AWS CONFIG
# -----------------------
AWS_REGION = "us-east-1"
S3_BUCKET = "your-bucket-name"

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# -----------------------
# MCP SERVER
# -----------------------
server = MCPServer("resume-s3-server")


# -------- Tool 1: List resumes ----------
@server.tool()
async def list_resumes() -> ToolResult:
    """
    Lists all resume files in the S3 bucket.
    """
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET)

    files = []
    for obj in response.get("Contents", []):
        files.append(obj["Key"])

    return ToolResult(
        content=[
            {
                "type": "text",
                "text": "\n".join(files) if files else "No resumes found."
            }
        ]
    )


# -------- Tool 2: Fetch a resume ----------
@server.tool()
async def get_resume(file_key: str) -> ToolResult:
    """
    Fetches the content of a resume file from S3.
    """
    obj = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
    text = obj["Body"].read().decode("utf-8", errors="ignore")

    return ToolResult(
        content=[
            {
                "type": "text",
                "text": text
            }
        ]
    )


# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server.app, host="0.0.0.0", port=3333)