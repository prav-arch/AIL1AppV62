import os

# Flask configuration
DEBUG = True
SECRET_KEY = os.environ.get("SESSION_SECRET", "super-secret-key")

# LLM API configuration
LLM_API_BASE_URL = "http://127.0.0.1:8080"
VERIFY_SSL = False  # Skip SSL verification as requested

# MinIO configuration
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = False  # HTTP instead of HTTPS
MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "aiapp-storage")

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

# NIFI configuration
NIFI_API_URL = os.environ.get("NIFI_API_URL", "http://localhost:8080/nifi-api")

# Airflow configuration
AIRFLOW_API_URL = os.environ.get("AIRFLOW_API_URL", "http://localhost:8080/api/v1")
AIRFLOW_USERNAME = os.environ.get("AIRFLOW_USERNAME", "admin")
AIRFLOW_PASSWORD = os.environ.get("AIRFLOW_PASSWORD", "admin")

# Upload configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'csv', 'pcap'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# FAISS configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "faiss_index"
