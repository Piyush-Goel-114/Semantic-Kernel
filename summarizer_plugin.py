from semantic_kernel.functions import kernel_function
from typing import Annotated
from pydantic import BaseModel

class EmailSummary(BaseModel):
    
    summary: str
    key_points: list[str]

class SummarizePlugin:
    
    @kernel_function(description="Summarizes an email thread according to specified prompt")
    def summarize_email_thread(
        self, 
        email_thread: Annotated[str, "The full email thread text"],
        prompt: Annotated[str, "Custom summarization prompt"]
    ) -> Annotated[str, "Returns summarized email thread"]:
        return f"Please analyze this email thread and provide a summary: {email_thread}. Focus on: {prompt}"