import os
from enum import Enum


class Settings:
    KNOWLEDGE_BASE_BUCKET_NAME = os.environ.get("KNOWLEDGE_BASE_BUCKET_NAME")
    MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")


class Boto3Params:
    def __init__(self):
        self.AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
        self.AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
        self.AWS_SESSION_TOKEN = os.environ.get("AWS_SESSION_TOKEN", "")
        self.AWS_REGION = os.environ.get("AWS_REGION")

    def get_params(self):
        params = {}
        if self.AWS_ACCESS_KEY_ID:
            params["aws_access_key_id"] = self.AWS_ACCESS_KEY_ID
        if self.AWS_SECRET_ACCESS_KEY:
            params["aws_secret_access_key"] = self.AWS_SECRET_ACCESS_KEY
        if self.AWS_SESSION_TOKEN:
            params["aws_session_token"] = self.AWS_SESSION_TOKEN
        params["region_name"] = self.AWS_REGION
        return params


boto3_params = Boto3Params().get_params()
settings = Settings()


class AllowedLLM(Enum):
    ANTHROPIC_CLAUDE_SONNET_V3_7 = (
        "us.anthropic.claude-3-7-sonnet-20250219-v1:0".lower()
    )
    MISTRAL_PIXTRAL_12B_2409 = "pixtral-12b-2409".lower()


settings = Settings()
