import asyncio
import requests
from semantic_kernel.agents import ChatCompletionAgent, GroupChatOrchestration, RoundRobinGroupChatManager
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.functions import kernel_function, KernelArguments
from summarizer_plugin import SummarizePlugin, EmailSummary
from response_plugin import EmailResponsePlugin, EmailResponse
from feedback_plugin import ModifyEmailPlugin

TEAMS_URL = "TEAMS_WEBHOOK_URL"  # Replace with your actual Teams webhook URL
def get_agents(api_key: str):
    """Create workflow agents similar to the reference pattern"""
    settings_summarizer = OpenAIChatPromptExecutionSettings()
    settings_summarizer.response_format = EmailSummary

    settings_email_generator = OpenAIChatPromptExecutionSettings()
    settings_email_generator.response_format = EmailResponse

    return [
        ChatCompletionAgent(
            name="Summarizer",
            instructions="You are an expert email analyst. Analyze email threads and provide concise, actionable summaries focusing on customer orders, issues, and key details.",
            service=OpenAIChatCompletion(
                api_key=api_key,
                ai_model_id="gpt-4o-2024-08-06"
            ),
            plugins=[SummarizePlugin()],
            arguments=KernelArguments(settings_summarizer)
        ),
        ChatCompletionAgent(
            name="EmailGenerator",
            instructions="You are a professional email writer. Generate courteous, clear email responses for out-of-stock situations. Always include apologies, explanations, and next steps.",
            service=OpenAIChatCompletion(
                api_key=api_key,
                ai_model_id="gpt-4o-2024-08-06"
            ),
            plugins=[EmailResponsePlugin()],
            arguments=KernelArguments(settings_email_generator)
        ),
        ChatCompletionAgent(
            name="EmailRefiner",
            instructions="You are an email quality specialist. Refine and improve email drafts based on human feedback while maintaining professionalism and clarity.",
            service=OpenAIChatCompletion(
                api_key=api_key,
                ai_model_id="gpt-4o-2024-08-06"
            ),
            plugins=[ModifyEmailPlugin()],
        ),
    ]

class WorkflowManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = get_agents(api_key)
        self.runtime = InProcessRuntime()
        
    def trigger_module(self, email_thread: str) -> str:
        """Module 1: Trigger - receives email thread input"""
        print("TRIGGER: Email thread received")
        return email_thread
    
    async def summarizer_module(self, email_thread: str) -> str:
        """Module 2: Summarizer - summarizes email thread using agent"""
        print("SUMMARIZER: Processing email thread...")
        
        summarizer = self.agents[0]
        
        response = await summarizer.get_response(
            f"""
            You are a Nestlé customer service expert responding to a customer inquiry. You have access to:

            CUSTOMER EMAIL THREAD:
            {email_thread}

            INSTRUCTIONS:
            1. Analyze the email thread to understand:
            - What product the customer is asking about
            - Customer's name and preferred communication style
            - Their language preference (English/French/other)
            - Level of urgency and emotional tone
            - Any specific concerns or requirements
            """
        )
        summary = response.content
        
        print(f"Summary generated: {summary}")
        return summary
    
    async def email_response_generator_module(self, email_thread: str, summary: str) -> str:
        """Module 3: Email Response Generator - creates out-of-stock response"""
        print("EMAIL GENERATOR: Creating response draft...")
        
        email_generator = self.agents[1]
        
        response = await email_generator.get_response(
            f"""
            CUSTOMER SERVICE CONTEXT:
            You are a Nestlé customer service expert responding to a customer inquiry. You have access to:

            CUSTOMER EMAIL THREAD:
            {email_thread}

            SUMMARY OF CUSTOMER INQUIRY:
            {summary}

            INSTRUCTIONS:

            1. Generate a professional customer service response that:
            - Matches their communication language and style
            - Addresses their specific situation with empathy
            - Provides clear information about stock status
            - Offers helpful alternatives if needed
            - Includes concrete next steps
            - Maintains Nestlé's brand voice

            2. Write only the email body (no subject line or signatures)

            Generate your response now:
            """
        )
        email_draft = response.content
        
        print("Email draft generated")
        return email_draft
    
    async def human_in_loop_module(self, email_draft: str) -> str:
        """Module 4: Human in the Loop - gets human feedback and iterates"""
        print("HUMAN IN LOOP: Requesting feedback...")

        while True:
            print("\n" + "="*50)
            print("EMAIL DRAFT:")
            print("="*50)
            print(email_draft.content)
            print(type(email_draft.content))
            print("="*50)
            
            payload = {
                "sender_name": "Alex",
                "sender_email": "alex@example.com",
                "subject": "Bulk Order Inquiry",
                "thread_text": email_draft.content
            }

            print(payload)

            feedback = None

            try:
                response = requests.post(TEAMS_URL, json=payload, headers={"Content-Type": "application/json"})

                if response.status_code == 200:
                    try:
                        result = response.json()

                        if result['selected-option'] == 'Approve':
                            return email_draft
                        
                        feedback = result['comment']

                    except ValueError:
                        print("⚠️ Received non-JSON response:")
                        print(response.text)
                        break
                else:
                    print(f"❌ Request failed with status {response.status_code}: {response.text}")
                    break

            except Exception as e:
                print(f"🔥 Error occurred: {e}")
                break
            
            print(f"📝 Modifying email based on feedback: {feedback}")
            email_draft = await self.modify_email_with_agent_feedback(email_draft, feedback)
            print("Email modified. Please review again...")
    
    async def modify_email_with_agent_feedback(self, email_draft: str, feedback: str) -> str:
        """Helper function to modify email based on human feedback using EmailRefiner agent"""
        email_refiner = self.agents[2]
        
        response = await email_refiner.get_response(
            f"Please modify this email: {email_draft} based on this feedback: {feedback}. Keep it professional and address all the feedback points."
        )
        return response.content
    
    def final_output_module(self, final_email: str) -> str:
        """Module 5: Final Output - returns the approved email"""
        print("🎯 FINAL OUTPUT: Returning approved email")
        return final_email
    
    async def run_workflow(self, email_thread: str, custom_prompt: str = None) -> str:
        """Main workflow orchestrator using agents"""
        print("🚀 Starting Email Workflow with Multi-Agent System...")
        
        self.runtime.start()
        
        try:
            # Module 1: Trigger
            triggered_input = self.trigger_module(email_thread)
            
            # Module 2: Summarizer Agent
            summary = await self.summarizer_module(triggered_input)

            # Module 3: Email Response Generator Agent
            email_draft = await self.email_response_generator_module(triggered_input, summary)
            
            # Module 4: Human in the Loop with EmailRefiner Agent
            approved_email = await self.human_in_loop_module(email_draft)
            
            # Module 5: Final Output
            final_email = self.final_output_module(approved_email)
            
            print("\n🎉 Workflow completed successfully!")
            return final_email
            
        finally:
            await self.runtime.stop_when_idle()


async def main(email_thread):

    api_key = "YOUR_OPENAI_API_KEY"
    workflow = WorkflowManager(api_key)
    
    print("=== SEQUENTIAL WORKFLOW ===")
    final_result = await workflow.run_workflow(
        email_thread, 
        custom_prompt="Focus on order details and customer expectations"
    )
    
    print("\n" + "="*50)
    print("FINAL APPROVED EMAIL:")
    print("="*50)
    print(final_result)
    print("="*50)

email_thread = """
    From: customer@email.com
    Subject: Order #12345

    Hi, I placed an order for 5 blue widgets and 3 red gadgets yesterday. 
    When can I expect delivery?

    Thanks,
    John
    """

if __name__ == "__main__":
    asyncio.run(main(email_thread))