import logging
from io import BytesIO

import boto3
from botocore.config import Config as BotoConfig

from app.config import settings

logger = logging.getLogger(__name__)


class PhotoStorageService:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.b2_endpoint_url,
            aws_access_key_id=settings.b2_key_id,
            aws_secret_access_key=settings.b2_application_key,
            config=BotoConfig(retries={"max_attempts": 3, "mode": "adaptive"}),
        )
        self._bucket = settings.b2_bucket_name

    def _build_key(self, user_id: str, distributor_type: str, sku: str, filename: str) -> str:
        return f"{user_id}/{distributor_type}/{sku}/{filename}"

    async def upload_photo(
        self,
        user_id: str,
        distributor_type: str,
        sku: str,
        filename: str,
        data: bytes,
        content_type: str = "image/jpeg",
    ) -> str:
        key = self._build_key(user_id, distributor_type, sku, filename)
        self._client.upload_fileobj(
            BytesIO(data),
            self._bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
        url = f"{settings.b2_endpoint_url}/{self._bucket}/{key}"
        logger.info("Uploaded photo: %s", key)
        return url

    async def delete_photo(self, user_id: str, distributor_type: str, sku: str, filename: str):
        key = self._build_key(user_id, distributor_type, sku, filename)
        self._client.delete_object(Bucket=self._bucket, Key=key)


photo_storage = PhotoStorageService()
