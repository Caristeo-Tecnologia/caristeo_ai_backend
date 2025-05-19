import asyncio
import os

import boto3
import streamlit as st

from src.core.config import boto3_params
from src.genai.Bedrock import BedrockAgent
from src.genai.Prompts import Prompts

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Caristeo AI Assistant", layout="wide", initial_sidebar_state="expanded"
)
st.title("Caristeo AI Assistant")

# Initialize session state for message history and AWS credentials
if "messages" not in st.session_state:
    st.session_state.messages = []
if "aws_credentials" not in st.session_state:
    st.session_state.aws_credentials = {
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "AWS_REGION": os.environ.get("AWS_REGION", "us-east-1"),
    }

# AWS Credentials Configuration in Sidebar
with st.sidebar:
    st.header("AWS Credentials")
    st.write("Configure AWS credentials for Bedrock access")

    aws_access_key = st.text_input(
        "AWS Access Key ID",
        value=st.session_state.aws_credentials["AWS_ACCESS_KEY_ID"],
        type="password"
        if st.session_state.aws_credentials["AWS_ACCESS_KEY_ID"]
        else "default",
    )

    aws_secret_key = st.text_input(
        "AWS Secret Access Key",
        value=st.session_state.aws_credentials["AWS_SECRET_ACCESS_KEY"],
        type="password",
    )

    if st.button("Update AWS Credentials"):
        st.session_state.aws_credentials = {
            "AWS_ACCESS_KEY_ID": aws_access_key,
            "AWS_SECRET_ACCESS_KEY": aws_secret_key,
            # Always use default region
            "AWS_REGION": "us-east-1",
        }
        st.success("AWS credentials updated!")
        # Set environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
        os.environ["AWS_REGION"] = "us-east-1"
        st.rerun()  # Rerun the app to apply changes

    if st.button("Export Credentials as .env File"):
        env_content = f"""AWS_ACCESS_KEY_ID={st.session_state.aws_credentials["AWS_ACCESS_KEY_ID"]}
AWS_SECRET_ACCESS_KEY={st.session_state.aws_credentials["AWS_SECRET_ACCESS_KEY"]}
AWS_REGION=us-east-1
"""
        st.download_button(
            label="Download .env File",
            data=env_content,
            file_name=".env",
            mime="text/plain",
        )

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Initialize Bedrock client with current credentials
current_boto3_params = boto3_params.copy()
if (
    st.session_state.aws_credentials["AWS_ACCESS_KEY_ID"]
    and st.session_state.aws_credentials["AWS_SECRET_ACCESS_KEY"]
):
    current_boto3_params.update({
        "aws_access_key_id": st.session_state.aws_credentials["AWS_ACCESS_KEY_ID"],
        "aws_secret_access_key": st.session_state.aws_credentials[
            "AWS_SECRET_ACCESS_KEY"
        ],
        "region_name": st.session_state.aws_credentials["AWS_REGION"],
    })

client = boto3.client("bedrock-agent-runtime", **current_boto3_params)
bedrock = BedrockAgent(boto3_params=current_boto3_params)


# Function to process retrieval and generate response
async def process_query(user_query):
    # Retrieve relevant information from knowledge base
    response = client.retrieve(
        knowledgeBaseId="DUAAO5INIR",  # Replace with your knowledge base ID
        retrievalQuery={"text": user_query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 5,
            }
        },
    )

    # Format the retrieved chunks
    chunks = [
        {
            "text": chunk["content"]["text"],
            "location": chunk["location"]["s3Location"]["uri"],
        }
        for chunk in response["retrievalResults"]
    ]

    formatted_context = "\n".join(
        f"[{i + 1}] {chunk['text']}" for i, chunk in enumerate(chunks)
    )

    references_block = "\n".join(
        f"[{i + 1}]: [{chunk['location']}]({chunk['location']})"
        for i, chunk in enumerate(chunks)
    )

    # Format the prompt with the retrieved context
    prompt = Prompts.QNA_PROMPT.format(
        query=user_query,
        context=formatted_context,
        references=references_block,
    )

    # Create agent and process the response
    agent = bedrock.create_agent()
    return await bedrock.run_stream(
        agent=agent,
        prompt_template=prompt,
        invoke_params={
            "query": user_query,
            "context": formatted_context,
            "references": references_block,
        },
        model_settings={
            "max_tokens": 16384,
            "temperature": 0.0,
        },
    )


# Async generator function to stream tokens from the response
async def stream_response(user_query):
    # First yield a loading message that will be replaced
    yield "Thinking..."

    # Get the streaming response from Bedrock
    async with await process_query(user_query) as result:
        # Clear the "Thinking..." message by yielding an empty string
        yield ""
        # Stream the actual response
        response_text = ""
        async for message in result.stream_text(delta=True):
            response_text += message
            yield response_text


# Create a synchronous wrapper for the async streaming function
def get_response_generator(query):
    async_gen = stream_response(query)

    # This will be called by write_stream
    def sync_generator():
        loop = asyncio.new_event_loop()
        try:
            while True:
                try:
                    # Get the next value from the async generator
                    value = loop.run_until_complete(async_gen.__anext__())
                    yield value
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

    return sync_generator()


# Handle user input
user_query = st.chat_input("Ask me something...")

if user_query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)

    # Display assistant response with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # Use write_stream to display streaming response
        for response_chunk in get_response_generator(user_query):
            if response_chunk:  # Skip empty chunks
                full_response = response_chunk
                response_placeholder.markdown(full_response)

    # Add the complete response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
