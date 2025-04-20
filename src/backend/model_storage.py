"""
Model storage implementation for RAG-LLM Framework.
Supports local and cloud storage options for LLM models.
"""
import os
import logging
import tempfile
import shutil
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelStorage:
    """
    Model storage manager for LLM models.
    Supports local and cloud storage options.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the model storage manager with configuration.
        
        Args:
            config: Configuration dictionary with storage settings
        """
        self.config = config
        self.storage_type = self._get_storage_type()
        self.cache_dir = self._get_cache_dir()
        self.cloud_provider = self._get_cloud_provider()
        self.cloud_client = None
        
        if self.storage_type == "cloud":
            self._initialize_cloud_client()
        
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_storage_type(self) -> str:
        """Get the storage type from config or environment variable."""
        env_storage_type = os.environ.get("OLLAMA_STORAGE_TYPE")
        if env_storage_type:
            return env_storage_type.lower()
        
        storage_config = self.config.get("storage", {})
        return storage_config.get("type", "local").lower()
    
    def _get_cache_dir(self) -> str:
        """Get the cache directory from config or environment variable."""
        env_cache_dir = os.environ.get("OLLAMA_CACHE_DIR")
        if env_cache_dir:
            return env_cache_dir
        
        storage_config = self.config.get("storage", {})
        cache_config = storage_config.get("cache", {})
        return cache_config.get("dir", "/tmp/ollama_cache")
    
    def _get_cloud_provider(self) -> Optional[str]:
        """Get the cloud provider from config or environment variable."""
        if self.storage_type != "cloud":
            return None
        
        env_provider = os.environ.get("OLLAMA_CLOUD_PROVIDER")
        if env_provider:
            return env_provider.lower()
        
        storage_config = self.config.get("storage", {})
        cloud_config = storage_config.get("cloud", {})
        return cloud_config.get("provider", "s3").lower()
    
    def _initialize_cloud_client(self):
        """Initialize the appropriate cloud storage client."""
        if self.cloud_provider == "s3":
            self._initialize_s3_client()
        elif self.cloud_provider == "gcs":
            self._initialize_gcs_client()
        elif self.cloud_provider == "azure":
            self._initialize_azure_client()
        elif self.cloud_provider == "nfs":
            self._initialize_nfs_client()
        else:
            logger.warning(f"Unsupported cloud provider: {self.cloud_provider}")
    
    def _initialize_s3_client(self):
        """Initialize the S3 client."""
        try:
            import boto3
            
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            s3_config = cloud_config.get("s3", {})
            
            access_key = os.environ.get("S3_ACCESS_KEY") or s3_config.get("access_key")
            secret_key = os.environ.get("S3_SECRET_KEY") or s3_config.get("secret_key")
            region = os.environ.get("S3_REGION") or s3_config.get("region")
            
            if access_key and secret_key:
                self.cloud_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name=region
                )
                logger.info("Initialized S3 client for model storage")
            else:
                self.cloud_client = boto3.client('s3', region_name=region)
                logger.info("Initialized S3 client with instance profile")
        except ImportError:
            logger.error("boto3 is required for S3 storage. Install with: pip install boto3")
            raise
        except Exception as e:
            logger.error(f"Error initializing S3 client: {str(e)}")
            raise
    
    def _initialize_gcs_client(self):
        """Initialize the Google Cloud Storage client."""
        try:
            from google.cloud import storage
            
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            gcs_config = cloud_config.get("gcs", {})
            
            credentials_file = os.environ.get("GCS_CREDENTIALS_FILE") or gcs_config.get("credentials_file")
            
            if credentials_file:
                self.cloud_client = storage.Client.from_service_account_json(credentials_file)
            else:
                self.cloud_client = storage.Client()
            
            logger.info("Initialized GCS client for model storage")
        except ImportError:
            logger.error("google-cloud-storage is required for GCS storage. Install with: pip install google-cloud-storage")
            raise
        except Exception as e:
            logger.error(f"Error initializing GCS client: {str(e)}")
            raise
    
    def _initialize_azure_client(self):
        """Initialize the Azure Blob Storage client."""
        try:
            from azure.storage.blob import BlobServiceClient
            
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            azure_config = cloud_config.get("azure", {})
            
            account = os.environ.get("AZURE_STORAGE_ACCOUNT") or azure_config.get("account")
            key = os.environ.get("AZURE_STORAGE_KEY") or azure_config.get("key")
            
            if account and key:
                connection_string = f"DefaultEndpointsProtocol=https;AccountName={account};AccountKey={key};EndpointSuffix=core.windows.net"
                self.cloud_client = BlobServiceClient.from_connection_string(connection_string)
                logger.info("Initialized Azure Blob Storage client for model storage")
            else:
                logger.error("Azure Storage account and key are required")
                raise ValueError("Azure Storage account and key are required")
        except ImportError:
            logger.error("azure-storage-blob is required for Azure storage. Install with: pip install azure-storage-blob")
            raise
        except Exception as e:
            logger.error(f"Error initializing Azure Blob Storage client: {str(e)}")
            raise
    
    def _initialize_nfs_client(self):
        """Initialize the NFS client (just a path mapping)."""
        try:
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            nfs_config = cloud_config.get("nfs", {})
            
            nfs_path = os.environ.get("NFS_PATH") or nfs_config.get("path")
            
            if nfs_path:
                self.cloud_client = {"path": nfs_path}
                logger.info(f"Using NFS path for model storage: {nfs_path}")
            else:
                logger.error("NFS path is required")
                raise ValueError("NFS path is required")
        except Exception as e:
            logger.error(f"Error initializing NFS client: {str(e)}")
            raise
    
    def get_model_path(self, model_name: str) -> str:
        """
        Get the path to the model file.
        If using cloud storage, downloads the model if not in cache.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Path to the model file
        """
        if self.storage_type == "local":
            return model_name
        
        cache_path = os.path.join(self.cache_dir, model_name)
        if os.path.exists(cache_path):
            if self._is_cache_expired(cache_path):
                logger.info(f"Cache expired for model {model_name}, downloading from cloud storage")
                self._download_model_from_cloud(model_name, cache_path)
            else:
                logger.info(f"Using cached model {model_name}")
        else:
            logger.info(f"Model {model_name} not in cache, downloading from cloud storage")
            self._download_model_from_cloud(model_name, cache_path)
        
        return cache_path
    
    def _is_cache_expired(self, cache_path: str) -> bool:
        """
        Check if the cached model is expired.
        
        Args:
            cache_path: Path to the cached model
            
        Returns:
            True if cache is expired, False otherwise
        """
        storage_config = self.config.get("storage", {})
        cache_config = storage_config.get("cache", {})
        ttl_hours = float(cache_config.get("ttl", "24h").rstrip("h"))
        
        mtime = os.path.getmtime(cache_path)
        age_hours = (time.time() - mtime) / 3600
        
        return age_hours > ttl_hours
    
    def _download_model_from_cloud(self, model_name: str, cache_path: str):
        """
        Download a model from cloud storage to local cache.
        
        Args:
            model_name: Name of the model
            cache_path: Path to save the model
        """
        if self.cloud_provider == "s3":
            self._download_from_s3(model_name, cache_path)
        elif self.cloud_provider == "gcs":
            self._download_from_gcs(model_name, cache_path)
        elif self.cloud_provider == "azure":
            self._download_from_azure(model_name, cache_path)
        elif self.cloud_provider == "nfs":
            self._copy_from_nfs(model_name, cache_path)
        else:
            logger.error(f"Unsupported cloud provider: {self.cloud_provider}")
            raise ValueError(f"Unsupported cloud provider: {self.cloud_provider}")
    
    def _download_from_s3(self, model_name: str, cache_path: str):
        """
        Download a model from S3.
        
        Args:
            model_name: Name of the model
            cache_path: Path to save the model
        """
        try:
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            s3_config = cloud_config.get("s3", {})
            
            bucket = os.environ.get("S3_BUCKET") or s3_config.get("bucket")
            prefix = os.environ.get("S3_PREFIX") or s3_config.get("prefix", "models/")
            
            if not prefix.endswith("/"):
                prefix += "/"
            
            key = f"{prefix}{model_name}"
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            self.cloud_client.download_file(bucket, key, temp_path)
            
            shutil.move(temp_path, cache_path)
            
            logger.info(f"Downloaded model {model_name} from S3 bucket {bucket}")
        except Exception as e:
            logger.error(f"Error downloading model from S3: {str(e)}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            raise
    
    def _download_from_gcs(self, model_name: str, cache_path: str):
        """
        Download a model from Google Cloud Storage.
        
        Args:
            model_name: Name of the model
            cache_path: Path to save the model
        """
        try:
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            gcs_config = cloud_config.get("gcs", {})
            
            bucket_name = os.environ.get("GCS_BUCKET") or gcs_config.get("bucket")
            prefix = os.environ.get("GCS_PREFIX") or gcs_config.get("prefix", "models/")
            
            if not prefix.endswith("/"):
                prefix += "/"
            
            blob_name = f"{prefix}{model_name}"
            
            bucket = self.cloud_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.download_to_filename(cache_path)
            
            logger.info(f"Downloaded model {model_name} from GCS bucket {bucket_name}")
        except Exception as e:
            logger.error(f"Error downloading model from GCS: {str(e)}")
            raise
    
    def _download_from_azure(self, model_name: str, cache_path: str):
        """
        Download a model from Azure Blob Storage.
        
        Args:
            model_name: Name of the model
            cache_path: Path to save the model
        """
        try:
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            azure_config = cloud_config.get("azure", {})
            
            container_name = os.environ.get("AZURE_CONTAINER") or azure_config.get("container")
            prefix = os.environ.get("AZURE_PREFIX") or azure_config.get("prefix", "models/")
            
            if not prefix.endswith("/"):
                prefix += "/"
            
            blob_name = f"{prefix}{model_name}"
            
            container_client = self.cloud_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            
            with open(cache_path, "wb") as file:
                data = blob_client.download_blob()
                file.write(data.readall())
            
            logger.info(f"Downloaded model {model_name} from Azure container {container_name}")
        except Exception as e:
            logger.error(f"Error downloading model from Azure: {str(e)}")
            raise
    
    def _copy_from_nfs(self, model_name: str, cache_path: str):
        """
        Copy a model from NFS mount.
        
        Args:
            model_name: Name of the model
            cache_path: Path to save the model
        """
        try:
            nfs_path = self.cloud_client["path"]
            
            if not nfs_path.endswith("/"):
                nfs_path += "/"
            
            source_path = f"{nfs_path}{model_name}"
            
            shutil.copy2(source_path, cache_path)
            
            logger.info(f"Copied model {model_name} from NFS path {nfs_path}")
        except Exception as e:
            logger.error(f"Error copying model from NFS: {str(e)}")
            raise
    
    def list_available_models(self) -> List[str]:
        """
        List available models in cloud storage.
        
        Returns:
            List of model names
        """
        if self.storage_type == "local":
            return []
        
        if self.cloud_provider == "s3":
            return self._list_models_s3()
        elif self.cloud_provider == "gcs":
            return self._list_models_gcs()
        elif self.cloud_provider == "azure":
            return self._list_models_azure()
        elif self.cloud_provider == "nfs":
            return self._list_models_nfs()
        else:
            logger.error(f"Unsupported cloud provider: {self.cloud_provider}")
            return []
    
    def _list_models_s3(self) -> List[str]:
        """
        List available models in S3.
        
        Returns:
            List of model names
        """
        try:
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            s3_config = cloud_config.get("s3", {})
            
            bucket = os.environ.get("S3_BUCKET") or s3_config.get("bucket")
            prefix = os.environ.get("S3_PREFIX") or s3_config.get("prefix", "models/")
            
            if not prefix.endswith("/"):
                prefix += "/"
            
            response = self.cloud_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            
            models = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    key = obj["Key"]
                    if key.startswith(prefix):
                        model_name = key[len(prefix):]
                        if model_name:
                            models.append(model_name)
            
            return models
        except Exception as e:
            logger.error(f"Error listing models from S3: {str(e)}")
            return []
    
    def _list_models_gcs(self) -> List[str]:
        """
        List available models in Google Cloud Storage.
        
        Returns:
            List of model names
        """
        try:
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            gcs_config = cloud_config.get("gcs", {})
            
            bucket_name = os.environ.get("GCS_BUCKET") or gcs_config.get("bucket")
            prefix = os.environ.get("GCS_PREFIX") or gcs_config.get("prefix", "models/")
            
            if not prefix.endswith("/"):
                prefix += "/"
            
            bucket = self.cloud_client.bucket(bucket_name)
            
            blobs = bucket.list_blobs(prefix=prefix)
            
            models = []
            for blob in blobs:
                if blob.name.startswith(prefix):
                    model_name = blob.name[len(prefix):]
                    if model_name:
                        models.append(model_name)
            
            return models
        except Exception as e:
            logger.error(f"Error listing models from GCS: {str(e)}")
            return []
    
    def _list_models_azure(self) -> List[str]:
        """
        List available models in Azure Blob Storage.
        
        Returns:
            List of model names
        """
        try:
            storage_config = self.config.get("storage", {})
            cloud_config = storage_config.get("cloud", {})
            azure_config = cloud_config.get("azure", {})
            
            container_name = os.environ.get("AZURE_CONTAINER") or azure_config.get("container")
            prefix = os.environ.get("AZURE_PREFIX") or azure_config.get("prefix", "models/")
            
            if not prefix.endswith("/"):
                prefix += "/"
            
            container_client = self.cloud_client.get_container_client(container_name)
            
            blobs = container_client.list_blobs(name_starts_with=prefix)
            
            models = []
            for blob in blobs:
                if blob.name.startswith(prefix):
                    model_name = blob.name[len(prefix):]
                    if model_name:
                        models.append(model_name)
            
            return models
        except Exception as e:
            logger.error(f"Error listing models from Azure: {str(e)}")
            return []
    
    def _list_models_nfs(self) -> List[str]:
        """
        List available models in NFS mount.
        
        Returns:
            List of model names
        """
        try:
            nfs_path = self.cloud_client["path"]
            
            if not nfs_path.endswith("/"):
                nfs_path += "/"
            
            models = []
            for file in os.listdir(nfs_path):
                file_path = os.path.join(nfs_path, file)
                if os.path.isfile(file_path):
                    models.append(file)
            
            return models
        except Exception as e:
            logger.error(f"Error listing models from NFS: {str(e)}")
            return []
