from pydantic import BaseModel, Field, StrictStr


class OCRModel(BaseModel):
    """Model for correct OCR results."""

    transcription: StrictStr = Field(
        ...,
        description="The full text extracted from the image.",
    )


class TranscriptionModel(BaseModel):
    """Model for transcription results."""

    transcribed_pages: list[OCRModel] = Field(
        ...,
        description="List of transcribed pages.",
    )
