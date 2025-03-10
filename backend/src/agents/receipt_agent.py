from crewai import Agent, Task
from crewai_tools import VisionTool
from .base_agent import BaseAgent
from ..utils.s3_helper import S3Helper
from PIL import Image
import io
import json
from typing import List, Dict, Optional, Any, Union
from datetime import datetime


class ReceiptAgent(BaseAgent):
    """Agent responsible for processing receipt images and extracting information"""

    def __init__(self):
        super().__init__(
            name="Receipt Analyzer", role="Expert Receipt Analyst and Data Extractor"
        )
        self.s3_helper = S3Helper()

    def create_agent(self) -> Agent:
        # Define tools
        tools = [
            {
                "name": "process_receipt",
                "description": "Process a receipt image and extract information",
                "function": self.process_receipt,
            },
            {
                "name": "categorize_items",
                "description": "Categorize receipt items and add expense categories",
                "function": self.categorize_items,
            },
            {
                "name": "suggest_split",
                "description": "Suggest how to split an expense",
                "function": self.suggest_split,
            },
        ]

        # Create the agent with tools
        return self.create_base_agent(
            backstory=(
                "I am an expert financial analyst specializing in receipt processing. "
                "I have extensive experience in extracting and organizing financial data "
                "from receipts, including complex items, discounts, and tax calculations. "
                "I ensure high accuracy in identifying vendors, dates, items, and totals. "
                "I can handle various receipt formats and understand complex billing structures. "
                "I use advanced OCR and image processing to extract text from receipt images."
            ),
            tools=tools,
        )

    def process_receipt(self, image_data: bytes) -> Dict:
        """
        Process a receipt image and extract detailed information using GPT-4

        Args:
            image_data: Raw image bytes

        Returns:
            Dict: Extracted receipt information including items, prices, and total
        """
        try:
            # Upload image to S3
            image_url = self.s3_helper.upload_image(image_data)

            print(f"Processing receipt with image URL: {image_url}")
            # Create the task with the vision tool
            text_task = self.create_receipt_task(
                description=(
                    "Extract all visible text from the receipt image, maintaining the original "
                    "layout and structure as much as possible. Pay special attention to:\n"
                    "1. Header information (vendor, date, location)\n"
                    "2. Item listings and their format\n"
                    "3. Footer information (totals, taxes, payment details)\n\n"
                    f"Image URL: {image_url}"
                ),
                expected_output="A string containing all visible text from the receipt image",
                vision_url=image_url,
            )

            # Extract raw text using a crew
            raw_text = self.execute_single_task(text_task)
            print(raw_text)

            # Format the raw text nicely
            raw_text_formatted = raw_text.strip()

            # Detailed analysis task
            analysis_task = self.create_receipt_task(
                description=(
                    "Analyze the following receipt text and extract information in JSON format:\n\n"
                    "Receipt Text:\n"
                    "```\n"
                    f"{raw_text_formatted}\n"
                    "```\n\n"
                    "Extract and structure the following information:\n"
                    "1. vendor: {name, address, phone (if available), category}\n"
                    "2. transaction: {date (ISO format), time, receipt_number}\n"
                    "3. items: [{name, quantity, unit_price, total_price, category}]\n"
                    "4. summary: {subtotal, tax_details: [{type, amount}], discounts: [{description, amount}], total}\n"
                    "5. payment: {method, card_last_4 (if available), status}\n"
                    "\nEnsure all numerical values are formatted as numbers, not strings."
                ),
                expected_output=(
                    "A JSON object containing structured receipt data with vendor, transaction, "
                    "items, summary, and payment information"
                ),
                vision_url=image_url,
            )

            try:
                # Execute analysis and parse result using a crew
                result = self.execute_single_task(analysis_task)
                parsed_result = json.loads(result)
                print(parsed_result)

                # Validate and standardize dates
                if "transaction" in parsed_result and parsed_result["transaction"].get(
                    "date"
                ):
                    try:
                        # Ensure date is in ISO format
                        date = datetime.fromisoformat(
                            parsed_result["transaction"]["date"]
                        )
                        parsed_result["transaction"]["date"] = date.isoformat()
                    except ValueError:
                        pass  # Keep original format if parsing fails

                return parsed_result

            except json.JSONDecodeError:
                # Fallback task for unstructured response
                fallback_task = self.create_receipt_task(
                    description=(
                        "The previous analysis returned unstructured data. Please analyze this text "
                        "and return ONLY a valid JSON object with the following structure:\n"
                        '{ "vendor": { "name": string },\n'
                        '  "items": [{ "name": string, "total_price": number }],\n'
                        '  "summary": { "total": number },\n'
                        '  "error": "Partial extraction only" }'
                    ),
                    expected_output=(
                        "A simplified JSON object containing basic receipt information with vendor "
                        "name, items, and total"
                    ),
                    vision_url=image_url,
                )

                try:
                    fallback_result = self.execute_single_task(fallback_task)
                    return json.loads(fallback_result)
                except:
                    return {
                        "raw_text": raw_text,
                        "error": "Failed to parse receipt data",
                        "items": [],
                        "summary": {"total": 0.0},
                    }

        except Exception as e:
            print(e)
            raise Exception(f"Failed to process receipt: {str(e)}")

    def categorize_items(self, items: List[Dict]) -> List[Dict]:
        """
        Categorize receipt items and add expense categories using GPT-4

        Args:
            items: List of items from receipt

        Returns:
            List[Dict]: Items with added categories and split suggestions
        """
        if not items:
            return items

        categorization_task = self.create_receipt_task(
            description=(
                "Analyze these receipt items and enhance them with the following information:\n"
                "1. Add an 'expense_category' field (e.g., 'food', 'transport', 'entertainment')\n"
                "2. Add a 'split_suggestion' field (e.g., 'personal', 'shared', 'business')\n"
                "3. Add 'notes' field for any special considerations\n\n"
                f"Items: {json.dumps(items, indent=2)}"
            ),
            expected_output=(
                "A JSON array of receipt items enhanced with expense categories, split "
                "suggestions, and notes"
            ),
            tools=[VisionTool()],
        )

        try:
            result = self.execute_single_task(categorization_task)
            categorized_items = json.loads(result)

            # Ensure all original fields are preserved
            for i, item in enumerate(categorized_items):
                if i < len(items):
                    item.update({k: v for k, v in items[i].items() if k not in item})

            return categorized_items
        except Exception as e:
            # Preserve original items if categorization fails
            return [
                {
                    **item,
                    "error": f"Categorization failed: {str(e)}",
                    "expense_category": "uncategorized",
                }
                for item in items
            ]

    def create_receipt_task(
        self,
        description: str,
        expected_output: Optional[str] = None,
        agent: Optional[Agent] = None,
        tools: Optional[List[Any]] = None,
        vision_url: Optional[str] = None,
    ) -> Task:
        """
        Create a new task for the receipt agent with optional vision capabilities

        Args:
            description: Task description
            expected_output: Expected format and structure of the output
            agent: Optional agent to use for the task
            tools: Optional tools to use for the task
            vision_url: Optional URL to an image to analyze with vision tools

        Returns:
            Task: Configured task instance

        Raises:
            Exception: If task creation fails
        """
        try:
            # Initialize task tools and context
            task_tools = tools or []

            # Add vision tool if URL is provided
            if vision_url:
                vision_tool = VisionTool(image_path_url=vision_url)
                if vision_tool not in task_tools:
                    task_tools.append(vision_tool)

            # Call the parent class's create_task method with our modifications
            return super().create_task(
                description=description,
                expected_output=expected_output,
                agent=agent,
                tools=task_tools,
            )
        except Exception as e:
            # Log the error for debugging
            print(f"Error creating receipt task: {str(e)}")
            raise Exception(f"Failed to create receipt task: {str(e)}")

    def suggest_split(self, receipt_data: Dict) -> Dict:
        """
        Analyze receipt data and suggest how to split the expense

        Args:
            receipt_data: Processed receipt data

        Returns:
            Dict: Split suggestions and reasoning
        """
        split_task = self.create_receipt_task(
            description=(
                "Analyze this receipt data and suggest how to split the expense:\n"
                "1. Determine if this is likely a personal, shared, or business expense\n"
                "2. If shared, suggest how to split it fairly\n"
                "3. Provide reasoning for the suggestion\n\n"
                f"Receipt data: {json.dumps(receipt_data, indent=2)}"
            ),
            expected_output=(
                "A JSON object containing split type (personal/shared/business), split ratios "
                "if shared, and detailed reasoning"
            ),
            tools=[VisionTool()],
        )

        try:
            result = self.execute_single_task(split_task)
            return json.loads(result)
        except Exception as e:
            return {
                "split_type": "unknown",
                "error": f"Failed to suggest split: {str(e)}",
                "default_split": "equal",
            }
