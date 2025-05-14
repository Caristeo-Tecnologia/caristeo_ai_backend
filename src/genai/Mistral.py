from typing import Dict, Optional, Union

from mistralai import Mistral
from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.providers.mistral import MistralProvider

from src.core.config import AllowedLLM, settings


class MistralAgent:
    def __init__(
        self,
        model_name: str = AllowedLLM.MISTRAL_PIXTRAL_12B_2409.value,
        result_type: Optional[BaseModel] = None,
    ):
        self.model_name = model_name
        self.result_type = result_type
        self.client = Mistral(api_key=settings.MISTRAL_API_KEY)

    def create_agent(self):
        return Agent(
            MistralModel(
                model_name=self.model_name,
                provider=MistralProvider(mistral_client=self.client),
            ),
            result_type=self.result_type,
        )

    async def get_inference(
        self,
        prompt_template: str,
        agent: Agent,
        model_settings: Dict[str, Union[float, int]] = None,
        invoke_params: Dict[str, str] = None,
        image_content: Optional[bytes] = None,
        image_media_type: str = "image/png",
    ) -> str:
        if invoke_params:
            prompt_template = prompt_template.format(**invoke_params)

        # Create message content for the agent
        message_content = []

        # Add text prompt
        message_content.append(prompt_template)

        # Add image if provided
        if image_content:
            message_content.append(
                BinaryContent(data=image_content, media_type=image_media_type)
            )

        # Run the agent with the content
        response = await agent.run(
            user_prompt=message_content if image_content else prompt_template,
            model_settings=model_settings,
        )
        return response
