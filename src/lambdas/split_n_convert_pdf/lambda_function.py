# from time import sleep
# import hashlib
# import unicodedata

import io
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote_plus

import boto3
import fitz
from loguru import logger
from PIL import Image

from aws.S3 import S3

# Configure Loguru to only log errors
logger.configure(handlers=[{"sink": sys.stderr, "level": "DEBUG"}])

s3_client = S3()
sqs_client = boto3.client("sqs")
KNOWLEDGE_BASE_BUCKET_NAME = "caristeo-ai-knowledge-base-bucket"
PAGE_OCR_SQS_QUEUE_URL = os.environ.get("PAGE_OCR_SQS_QUEUE_URL")


def generate_ascii_group_id(folder_name: str) -> str:
    """
    Generate an ASCII-compliant MessageGroupId for SQS.

    Args:
        folder_name (str): The name of the folder to convert.

    Returns:
        str: An ASCII-compliant version of the folder name.
    """
    folder_name = (
        unicodedata.normalize("NFKD", folder_name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    # Remove any character not allowed by SQS MessageGroupId
    folder_name = re.sub(
        r'[^a-zA-Z0-9!"#$%&\'()*+,-./:;<=>?@[\\\]^_`{|}~]', "", folder_name
    )
    return folder_name[:128]


def lambda_handler(event, context):
    # Initialize S3 client
    logger.info("Lambda function started")
    event = json.loads(event["Records"][0]["body"])
    logger.info(f"Event: {event}")
    min_width = 100
    min_height = 100

    try:
        object_key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
        # id = hashlib.md5(object_key.encode("utf-8")).hexdigest()[:8]
        logger.info(f"Processing object key: {object_key}")

        folder_name = Path(object_key).stem
        logger.debug(f"Folder name: {folder_name}")

        logger.debug("Getting PDF from S3")

        pdf_bytes = s3_client.get_object(
            bucket_name=KNOWLEDGE_BASE_BUCKET_NAME, file_key=object_key
        )
        logger.info(
            f"PDF object retrieved, byte length: {len(pdf_bytes) if pdf_bytes else 'None'}"
        )

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            extracted_images = []

            for page_num, page in enumerate(doc):
                logger.debug(f"Processing page {page_num + 1}/{len(doc)}")
                s3_key = (
                    f"transcribed_books/{folder_name}/pages/page_{page_num + 1}.jpg"
                )

                sqs_message = {
                    "file_key": s3_key,
                    "page_num": page_num + 1,
                    "document_name": folder_name,
                }

                image_list = page.get_images(full=True)
                logger.debug(f"Found {len(image_list)} images on page {page_num + 1}")

                if not image_list:
                    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
                    # upload the image to S3
                    logger.info(f"Uploading to S3: {s3_key}")

                    with io.BytesIO() as buffer:
                        pix.save(buffer, format="jpeg")
                        # Save the image to S3
                        buffer.seek(0)

                        s3_client.upload_fileobj(
                            bucket_name=KNOWLEDGE_BASE_BUCKET_NAME,
                            file_key=s3_key,
                            fileobj=buffer,
                        )

                        extracted_images.append(s3_key)

                        sqs_client.send_message(
                            QueueUrl=PAGE_OCR_SQS_QUEUE_URL,
                            MessageBody=json.dumps(sqs_message),
                        )

                    del buffer, pix

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)

                    if base_image:
                        image_bytes = base_image["image"]
                        try:
                            image = Image.open(io.BytesIO(image_bytes))
                            width, height = image.size
                            # if width < min_width or height < min_height:
                            #     logger.debug(
                            #         f"Image {img_index + 1} on page {page_num + 1} is too small: {width}x{height}"
                            #     )
                            #     continue

                            image = image.convert("L")  # Convert to grayscale

                            # put image in s3, use the same s3_key as above, and i only want "page_{page_num + 1}.jpg" in the name
                            with io.BytesIO() as buffer:
                                image.save(buffer, format="JPEG")
                                buffer.seek(0)
                                s3_client.upload_fileobj(
                                    bucket_name=KNOWLEDGE_BASE_BUCKET_NAME,
                                    file_key=s3_key,
                                    fileobj=buffer,
                                )
                                extracted_images.append(s3_key)

                                sqs_client.send_message(
                                    QueueUrl=PAGE_OCR_SQS_QUEUE_URL,
                                    MessageBody=json.dumps(sqs_message),
                                    MessageGroupId=generate_ascii_group_id(folder_name),
                                )

                            del buffer, image

                            logger.info(
                                f"Extracted page {page_num + 1} as image {img_index + 1} to S3: {s3_key} (dimensions: {width}x{height})"
                            )
                        except Exception as e:
                            logger.error(
                                f"Error processing page {page_num + 1} as image {img_index + 1}: {str(e)}",
                                exc_info=True,
                            )
                            continue
        except Exception as e:
            logger.error(f"Error processing PDF with PyMuPDF: {str(e)}", exc_info=True)
            print(f"Error processing PDF with PyMuPDF: {str(e)}")
            raise
        finally:
            # Clean up the PDF document
            if "doc" in locals():
                doc.close()
                logger.debug("PDF document closed")

    except Exception as e:
        logger.error(f"Lambda function error: {str(e)}", exc_info=True)
        print(f"Lambda function error: {str(e)}")
        raise

    logger.info("Lambda function completed")
    return {"statusCode": 200, "body": "PDF processing completed"}
