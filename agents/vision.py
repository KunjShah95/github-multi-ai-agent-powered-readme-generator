import os
from core.adk_agent import ADK
from core.a2a_protocol import A2AMessage
import google.generativeai as genai
from PIL import Image


class VisionAgent(ADK):

    # --- AGENT ROLE PROMPT ---
    # You are the VisionAgent. Your role is to:
    # 1. Analyze system diagrams, architecture images, or screenshots provided by the user.
    # 2. Use Google Gemini or similar models to extract and summarize visual information.
    # 3. Generate a detailed, human-readable explanation of the system's architecture, components, and interactions.
    # 4. Integrate the visual analysis into the README, enhancing the documentation with diagrams and explanations.
    # 5. Optionally detect and describe security, scalability, or performance features visible in diagrams.
    # 6. Support multiple image formats and error handling for invalid images.
    #
    # --- FEATURE SUGGESTIONS ---
    # - Add OCR to extract text from diagrams.
    # - Support for multiple images and diagram types (UML, ERD, flowcharts).
    # - Generate Mermaid or PlantUML diagrams from images.
    # - Provide visual summaries for accessibility (alt text, captions).
    # - Integrate with cloud storage for image uploads.
    # - Output a visual changelog if diagrams change over time.
    #
    def __init__(self, model_name="gemini-2.5-flash"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(" GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def analyze_image(self, image_file, context_prompt="Analyze the following system diagram and provide a detailed explanation. Describe the main components, their interactions, and the overall architecture of the system."):
        try:
            image = Image.open(image_file)
            response = self.model.generate_content([context_prompt, image])
            return response.text.strip()
        except Exception as e:
            return f"❌ Error analyzing image: {e}"

    def run(self, image_file, previous_readme_msg: A2AMessage):
        vision_section = self.analyze_image(image_file)

        enhanced_readme = previous_readme_msg.content + f"\n\n---\n\n🧭 **System Overview**\n{vision_section}"

        return A2AMessage(
            from_agent="VisionAgent",
            to_agent="FeedbackAgent",
            message_type="readme_with_vision",
            content=enhanced_readme
        )
