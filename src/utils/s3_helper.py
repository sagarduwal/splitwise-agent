import os
import logging
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import uuid
from datetime import datetime
from typing import Optional, Tuple
from PIL import Image
import io


class S3Helper:
    def __init__(self):
        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Validate required environment variables
        self.bucket_name = os.getenv("AWS_S3_BUCKET")
        if not self.bucket_name:
            raise ValueError("AWS_S3_BUCKET environment variable is required")

        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1"),
            )
            # Verify credentials and bucket access
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "403":
                raise ValueError(f"No permission to access bucket: {self.bucket_name}")
            elif error_code == "404":
                raise ValueError(f"Bucket does not exist: {self.bucket_name}")
            else:
                raise ValueError(f"Failed to initialize S3 client: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to initialize S3 client: {str(e)}")

    def optimize_image(self, image_data: bytes, max_size: int = 1024) -> bytes:
        """
        Optimize image for upload by resizing and compressing

        Args:
            image_data: Raw image bytes
            max_size: Maximum dimension size (width or height)

        Returns:
            bytes: Optimized image data
        """
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGB if needed
        if image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
        ):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background

        # Resize if needed
        width, height = image.size
        if width > max_size or height > max_size:
            ratio = min(max_size / width, max_size / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Save with optimal quality
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        return buffer.getvalue()

    def validate_image(self, image_data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate image data before upload

        Args:
            image_data: Raw image bytes

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not image_data:
            return False, "Image data cannot be empty"

        try:
            # Try to open the image to verify it's valid
            image = Image.open(io.BytesIO(image_data))

            # Check image format
            if image.format not in ["PNG", "JPEG", "JPG"]:
                return False, f"Unsupported image format: {image.format}"

            # Check image size (max 10MB)
            if len(image_data) > 10 * 1024 * 1024:
                return False, "Image size exceeds 10MB limit"

            # Check dimensions (max 4000x4000)
            width, height = image.size
            if width > 4000 or height > 4000:
                return (
                    False,
                    f"Image dimensions ({width}x{height}) exceed maximum allowed (4000x4000)",
                )

            return True, None

        except Exception as e:
            return False, f"Invalid image data: {str(e)}"

    def upload_image(self, image_data: bytes) -> str:
        """
        Upload an image to S3 and return its URL

        Args:
            image_data: Raw image bytes

        Returns:
            str: Public URL of the uploaded image

        Raises:
            ValueError: If image_data is invalid
            Exception: If upload fails
        """
        # Validate and optimize image
        is_valid, error_message = self.validate_image(image_data)
        if not is_valid:
            self.logger.error(f"Invalid image data: {error_message}")
            raise ValueError(error_message)

        # Optimize image before upload
        try:
            self.logger.info("Optimizing image for upload...")
            image_data = self.optimize_image(image_data)
            self.logger.info(f"Image optimized, size: {len(image_data)} bytes")

        except Exception as e:
            self.logger.error(f"Image optimization failed: {str(e)}")
            raise ValueError(f"Failed to optimize image: {str(e)}")

        try:
            # Generate a unique filename using UUID and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())
            filename = f"receipts/{timestamp}_{unique_id}.png"
            self.logger.info(f"Generated filename: {filename}")

            # Upload the file with public-read ACL
            self.logger.info(f"Uploading to bucket: {self.bucket_name}")
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=image_data,
                ContentType="image/png",
                ACL="public-read",
                Metadata={
                    "upload_timestamp": timestamp,
                    "content_type": "receipt_image",
                    "id": unique_id
                },
            )
            self.logger.info(f"Upload to S3 successful for key: {filename}")

            # Generate and verify the URL
            # Format: https://{bucket}.s3.{region}.amazonaws.com/{key}
            region = os.getenv("AWS_REGION", "us-east-1")
            
            # Use the correct URL format for S3 objects
            # This format is compatible with the VisionTool
            url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com/{filename}"
            
            # Log the URL and ensure it's properly formatted for vision tools
            self.logger.info(f"Successfully uploaded image to {url}")
            
            # Verify the URL is accessible
            if not self.verify_image_url(url):
                self.logger.warning(f"Uploaded image URL verification failed: {url}")
                # Try an alternative URL format if verification failed
                alt_url = f"https://s3.{region}.amazonaws.com/{self.bucket_name}/{filename}"
                self.logger.info(f"Trying alternative URL format: {alt_url}")
                if self.verify_image_url(alt_url):
                    self.logger.info(f"Alternative URL format verified: {alt_url}")
                    return alt_url
            
            return url

        except ClientError as e:
            error_msg = f"Failed to upload image to S3: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error uploading image: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def verify_image_url(self, url: str) -> bool:
        """
        Verify if an image URL exists in the S3 bucket

        Args:
            url: S3 URL to verify

        Returns:
            bool: True if image exists and is accessible
        """
        try:
            # Extract key from URL - handle different URL formats
            # Format could be either:
            # - https://{bucket}.s3.amazonaws.com/{key}
            # - https://{bucket}.s3.{region}.amazonaws.com/{key}
            if ".s3.amazonaws.com/" in url:
                key = url.split(".s3.amazonaws.com/")[1]
            elif ".s3." in url and ".amazonaws.com/" in url:
                # Extract the part after amazonaws.com/
                key = url.split(".amazonaws.com/")[1]
            else:
                self.logger.error(f"Invalid S3 URL format: {url}")
                return False

            # Check if object exists
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            self.logger.info(f"Successfully verified image URL: {url}")
            return True

        except (ClientError, IndexError, BotoCoreError) as e:
            self.logger.error(f"Failed to verify image URL {url}: {str(e)}")
            return False
