from crewai import Agent
from .base_agent import BaseAgent
from transformers import pipeline
from PIL import Image
import io

class ReceiptAgent(BaseAgent):
    """Agent responsible for processing receipt images and extracting information"""

    def __init__(self):
        super().__init__(
            name="Receipt Processor",
            role="Processes receipt images to extract expense information"
        )
        self.vision_model = pipeline("image-to-text", model="microsoft/git-base")

    def create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            role=self.role,
            goal="Extract accurate expense information from receipt images",
            backstory="I am an expert at processing receipts and extracting relevant "
                     "information like items, prices, and totals.",
            tools=[self.process_receipt]
        )

    def process_receipt(self, image_data: bytes) -> dict:
        """
        Process a receipt image and extract relevant information
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            dict: Extracted receipt information including items, prices, and total
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Get image description from vision model
            result = self.vision_model(image)
            
            # TODO: Implement more sophisticated receipt parsing logic
            # This is a placeholder implementation
            return {
                "raw_text": result[0]["generated_text"],
                "items": [],  # List of items and prices
                "total": 0.0,
                "date": None,
                "vendor": None
            }
        except Exception as e:
            raise Exception(f"Failed to process receipt: {str(e)}")
