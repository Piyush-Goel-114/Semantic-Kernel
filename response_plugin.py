from semantic_kernel.functions import kernel_function
from typing import Annotated
from pydantic import BaseModel

class EmailResponse(BaseModel):
    
    subject: str
    body: str

class EmailResponsePlugin:

    @kernel_function(description="Generates email response draft for out-of-stock items")
    def generate_email_response(
        self, 
        email_thread: Annotated[str, "The original email thread"],
        summary: Annotated[str, "The email summary"]
    ) -> Annotated[str, "Returns draft email response"]:
        return f"Based on this email thread: {email_thread} and summary: {summary}, generate a professional email response informing the customer that their ordered items are out of stock. Include appropriate apology and next steps."
    