import json
import sys
from pathlib import Path

from loguru import logger
from models.ocr_model import OCRModel

from aws.S3 import S3
from genai.Bedrock import BedrockAgent
from prompts.Prompts import Prompts

# Configure Loguru to only log errors
logger.configure(handlers=[{"sink": sys.stderr, "level": "DEBUG"}])

s3_client = S3()

KNOWLEDGE_BASE_BUCKET_NAME = "caristeo-ai-knowledge-base-bucket"


def lambda_handler(event, context):
    logger.info(f"Starting OCR processing with event: {event}")
    event = json.loads(event["Records"][0]["body"])
    try:
        file_key = event["file_key"]
        logger.info(f"Processing file: {file_key}")

        logger.debug(f"Retrieving file from S3 bucket: {KNOWLEDGE_BASE_BUCKET_NAME}")
        page_bytes = s3_client.get_object(
            bucket_name=KNOWLEDGE_BASE_BUCKET_NAME,
            file_key=file_key,
        )
        logger.info(
            f"Successfully retrieved file from S3, size: {len(page_bytes)} bytes"
        )

        logger.debug("Initializing Bedrock agent for OCR")
        bedrock = BedrockAgent(result_type=OCRModel)
        agent = bedrock.create_agent()
        logger.info("Bedrock agent initialized")

        logger.debug("Sending image for OCR processing")
        # Call get_inference directly since it's not returning a coroutine
        ocr_response = bedrock.get_inference(
            prompt_template=Prompts.PAGE_OCR_PROMPT,
            agent=agent,
            image_content=page_bytes,
            model_settings={
                "max_tokens": 16384,
                "temperature": 0.0,
            },
        )

        logger.info("OCR processing completed successfully")
        logger.debug(f"OCR response type: {type(ocr_response)}")

        transcription_content = ocr_response.transcription

        transcription_path = f"transcribed_books/{Path(file_key).parts[1]}/transcribed_pages/{Path(file_key).name.replace('.jpg', '.md')}"
        logger.debug(f"Saving transcription to: {transcription_path}")

        put_response = s3_client.put_object(
            bucket_name=KNOWLEDGE_BASE_BUCKET_NAME,
            file_key=transcription_path,
            file_bytes=transcription_content,
        )
        logger.info(f"Transcription saved successfully to path: {transcription_path}")

        return put_response
    except Exception as e:
        logger.error(f"Error in OCR processing: {str(e)}")
        logger.exception("Full exception details:")
        raise  # Re-raise to preserve Lambda error handling
