import os
import logging
from imagekitio import ImageKit

logger = logging.getLogger(__name__)

IMAGEKIT_PRIVATE_KEY = "private_FvDlJoR4PuXb1GwdQ825AVRW5mw="
IMAGEKIT_PUBLIC_KEY = "public_O7WjPSWLMefzfR/6gxk4MTQOGQs="
IMAGEKIT_URL_ENDPOINT = "https://ik.imagekit.io/oluth2qgo"


class ImageKitService:
    """Service to upload/manage media files via ImageKit (v5 SDK)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # v5 SDK only needs private_key for server-side ops
            cls._instance._ik = ImageKit(private_key=IMAGEKIT_PRIVATE_KEY)
        return cls._instance

    def upload_file(self, file_path: str, file_name: str) -> dict:
        """
        Upload a local file to ImageKit.

        Returns:
            dict with keys:
              - success (bool)
              - url (str): public ImageKit URL
              - file_id (str): ImageKit file ID (for deletion)
              - error (str): error message if success is False
        """
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            # Keep original filename but let ImageKit handle uniqueness
            result = self._ik.files.upload(
                file=file_bytes,
                file_name=file_name,
                folder="/whatsapp_campaigns/",
                is_private_file=False,
                use_unique_file_name=False,
            )

            # v5 returns a Pydantic model – access as attributes
            url = result.url
            file_id = result.file_id if hasattr(result, 'file_id') else getattr(result, 'fileId', '')

            logger.info(f"Uploaded '{file_name}' to ImageKit: {url}")
            return {"success": True, "url": url, "file_id": file_id}

        except Exception as e:
            logger.error(f"ImageKit upload failed for '{file_name}': {e}")
            return {"success": False, "error": str(e)}

    def delete_file(self, file_id: str) -> None:
        """Delete a file from ImageKit by its file ID."""
        try:
            self._ik.files.delete(file_id)
            logger.info(f"Deleted ImageKit file: {file_id}")
        except Exception as e:
            logger.warning(f"Could not delete ImageKit file '{file_id}': {e}")

    @staticmethod
    def get_public_url(path: str) -> str:
        """Build a public ImageKit URL from a path (without uploading)."""
        return f"{IMAGEKIT_URL_ENDPOINT.rstrip('/')}/{path.lstrip('/')}"
