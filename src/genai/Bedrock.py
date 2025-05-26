from typing import Dict, List, Optional, Type, Union

import boto3
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.bedrock import BedrockConverseModel
from pydantic_ai.providers.bedrock import BedrockProvider

# import stricy string type from pydantic
# from src.core.config import boto3_params


class BedrockAgent:
    def __init__(
        self,
        model_name: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        result_type: Optional[Union[Type[BaseModel], Type[str]]] = str,
        boto3_params: Optional[Dict[str, str]] = None,
    ):
        self.model_name = model_name
        self.result_type = result_type
        self.client = boto3.client("bedrock-runtime", **boto3_params)

    def create_agent(self):
        return Agent(
            BedrockConverseModel(
                model_name=self.model_name,
                provider=BedrockProvider(bedrock_client=self.client),
            ),
            result_type=self.result_type,
        )

    def get_inference(
        self,
        prompt_template: str,
        agent: Agent,
        model_settings: Dict[str, Union[float, int]] = None,
        invoke_params: Dict[str, str] = None,
        image_content: Optional[Union[bytes, List[bytes]]] = None,
        image_media_type: str = "image/jpeg",
    ) -> str:
        if invoke_params:
            prompt_template = prompt_template.format(**invoke_params)

        # Create message content for the agent
        message_content = []

        # Add text prompt
        message_content.append(prompt_template)

        # Add image if provided
        if image_content:
            if isinstance(image_content, bytes):
                image_content = [image_content]
            for image in image_content:
                message_content.append(
                    BinaryContent(
                        data=image,
                        media_type=image_media_type,
                    )
                )

        # Run the agent with the content
        response = agent.run_sync(
            user_prompt=message_content if image_content else prompt_template,
            model_settings=model_settings,
        )
        return response.output

    async def run_stream(
        self,
        prompt_template: str,
        agent: Agent,
        model_settings: Dict[str, Union[float, int]] = None,
        invoke_params: Dict[str, str] = None,
    ):
        if invoke_params:
            prompt_template = prompt_template.format(**invoke_params)

        # Return the full response object to support streaming operations
        return agent.run_stream(
            user_prompt=prompt_template,
            model_settings=model_settings,
        )
