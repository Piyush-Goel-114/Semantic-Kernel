from semantic_kernel.functions import kernel_function
from typing import Annotated
from pydantic import BaseModel

class HumanFeedback(BaseModel):
    approved: bool
    feedback: str = ""

class ModifyEmailPlugin:

    @kernel_function(description="Modifies email based on human feedback")
    def modify_email_with_ai(
        self,
        email_draft: Annotated[str, "Current email draft"],
        feedback: Annotated[str, "Human feedback for modifications"]
    ) -> Annotated[str, "Returns modified email"]:
        return f"Please modify this email: {email_draft} based on this feedback: {feedback}. Keep it professional and address all the feedback points."
