"""
Django settings for ama_backend project.

Generated by 'django-admin startproject' using Django 5.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv()

# Load local environment if it exists (override=True to override .env values)
load_dotenv(BASE_DIR / '.env.local', override=True)

# Check if we should use local Docker database
USE_LOCAL_DB = os.getenv('USE_LOCAL_DB', 'false').lower() == 'true'

print("🔗 Configuring database connection...")
if USE_LOCAL_DB:
    print("🐳 Using LOCAL Docker SQL Server Database")
else:
    print("🔗 Configuring Microsoft Fabric SQL Database connection...")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-p9s89r&2dh=pjh__h7#1tj&ln9ulrpc3(fh@ln1i@71-xl8h%f')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Frontend URL Configuration - Auto-detect or use environment variable
FRONTEND_URL = os.getenv('FRONTEND_URL', None)  # Will auto-detect if not set

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',        # Django REST Framework
    'rest_framework_simplejwt',  # JWT Authentication
    'corsheaders',          # CORS headers for frontend communication
    'api',                  # Your AMA API app
]

AUTH_USER_MODEL = 'api.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware (must be first)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ama_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ama_backend.wsgi.application'


# Microsoft Fabric SQL Database Configuration
# This project uses Microsoft Fabric SQL Database exclusively
print("🔗 Configuring Microsoft Fabric SQL Database connection...")

# Get authentication method from environment
auth_method = os.getenv('AUTH_METHOD', 'ActiveDirectoryIntegrated')
print(f"📡 Using authentication method: {auth_method}")

# Build connection string based on authentication method
if auth_method == 'SqlPassword':
    # SQL Server Authentication with username and password
    extra_params = 'Encrypt=yes;TrustServerCertificate=no;ConnectTimeout=30;Command Timeout=60'
elif auth_method == 'ActiveDirectoryPassword':
    # Azure AD with username and password (no interactive prompt)
    extra_params = 'Authentication=ActiveDirectoryPassword;Encrypt=yes;TrustServerCertificate=no;ConnectTimeout=30;Command Timeout=60'
elif auth_method == 'ActiveDirectoryInteractive':
    # Opens a browser/dialog for Azure AD login (first time)
    extra_params = 'Authentication=ActiveDirectoryInteractive;Encrypt=yes;TrustServerCertificate=no;ConnectTimeout=30;Command Timeout=60'
elif auth_method == 'ActiveDirectoryDefault':
    # Uses cached Azure AD credentials (after first login)
    extra_params = 'Authentication=ActiveDirectoryDefault;Encrypt=yes;TrustServerCertificate=no;ConnectTimeout=30;Command Timeout=60'
elif auth_method == 'ActiveDirectoryIntegrated':
    # Uses Azure AD integrated authentication (not Windows integrated)
    extra_params = 'Authentication=ActiveDirectoryIntegrated;Encrypt=yes;TrustServerCertificate=no;ConnectTimeout=30;Command Timeout=60'
else:
    # Fallback without specific authentication (let SQL Server handle it)
    extra_params = 'Encrypt=yes;TrustServerCertificate=no;ConnectTimeout=30;Command Timeout=60'

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '1433'),
        'USER': os.getenv('DB_USER'),  # Use the actual user from .env
        'PASSWORD': os.getenv('DB_PASSWORD', ''),  # Empty for Azure AD auth
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': extra_params
        },
    }
}

print(f"Database: {DATABASES['default']['NAME']}")
print(f"Host: {DATABASES['default']['HOST']}")
print(f"User: {DATABASES['default']['USER'] or 'Integrated Auth'}")
print(f"Auth: {auth_method}")


# Performance optimizations for Microsoft Fabric SQL Database
print("Applying Fabric SQL performance optimizations...")

# Connection pooling - keep connections alive to reduce latency
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes

# Reduce connection timeout for faster failure detection
if 'OPTIONS' in DATABASES['default'] and 'extra_params' in DATABASES['default']['OPTIONS']:
    # Update the existing extra_params to include shorter timeouts
    current_params = DATABASES['default']['OPTIONS']['extra_params']
    # Replace timeout values if they exist, otherwise add them
    if 'ConnectTimeout=' in current_params:
        import re
        current_params = re.sub(r'ConnectTimeout=\d+', 'ConnectTimeout=10', current_params)
    else:
        current_params += ';ConnectTimeout=10'
    
    if 'Command Timeout=' in current_params:
        current_params = re.sub(r'Command Timeout=\d+', 'Command Timeout=30', current_params)
    else:
        current_params += ';Command Timeout=30'
    
    DATABASES['default']['OPTIONS']['extra_params'] = current_params

# Enable caching to reduce database hits
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'ama-cache',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# Cache sessions to reduce database load
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

print("Performance optimizations applied successfully!")


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration - Allow frontend to communicate with backend
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Next.js default port
    'http://127.0.0.1:3000',  # Alternative localhost
    'http://localhost:3001',  # Alternative port
    'http://127.0.0.1:3001',  # Alternative port
    'http://localhost:3002',  # Alternative port
    'http://127.0.0.1:3002',  # Alternative port
    'http://localhost:3003',  # Alternative port
    'http://127.0.0.1:3003',  # Alternative port
    'http://localhost:3004',  # Alternative port
    'http://127.0.0.1:3004',  # Alternative port
    'http://localhost:3005',  # Alternative port
    'http://127.0.0.1:3005',  # Alternative port
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False  # Security: only allow specific origins

# Additional CORS headers for authentication
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# Microsoft Fabric AI Configuration (Primary AI Engine)
print("🤖 Configuring Microsoft Fabric AI features...")

# Enable Fabric AI as the primary AI engine
# This tells our application to use Fabric's native AI functions first
FABRIC_AI_ENABLED = True  # Always true since Fabric AI is built into Fabric SQL

# Configuration dictionary for Fabric AI capabilities
FABRIC_AI_CONFIG = {
    # Enable vector functions - these are Fabric's built-in AI functions for embeddings
    'use_vector_functions': True,
    
    # Enable semantic functions - these handle text analysis and understanding
    'use_semantic_functions': True,
    
    # Vector dimension size - standard embedding size for most AI models
    # 1536 is the dimension used by OpenAI's text-embedding-ada-002 model
    'vector_dimension': 1536,
    
    # Fabric's built-in similarity function name
    # VECTOR_DISTANCE calculates similarity between embedding vectors
    'similarity_function': 'VECTOR_DISTANCE',
    
    # Enable Fabric's native indexing for vector operations
    # This dramatically improves similarity search performance
    'enable_vector_indexing': True,
    
    # Batch size for processing multiple questions at once
    # Larger batches are more efficient but use more memory
    'batch_processing_size': 50,
    
    # Timeout for AI operations in seconds
    # Fabric AI operations are usually fast, but we set a reasonable timeout
    'ai_operation_timeout': 30,

    # Enable caching of AI results to improve performance
    # This prevents regenerating embeddings for the same text
    'enable_ai_caching': True,
    
    # Cache timeout for AI results (in seconds)
    # 1 hour = 3600 seconds - embeddings don't change so we can cache longer
    'ai_cache_timeout': 3600,
}

# AZURE openAI configuration for advanced features not supported by Fabric
AZURE_OPENAI_ENABLED = os.getenv('AZURE_OPENAI_ENABLED', 'False').lower() == 'true'

# Only configure Azure OpenAI if it's enabled
if AZURE_OPENAI_ENABLED:
    AZURE_OPENAI_CONFIG = {
        # Azure OpenAI service endpoint - replace with your actual endpoint
        'endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
        
        # API key for authentication - keep this secure
        'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
        
        # API version - this determines which features are available
        'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2023-05-15'),
        
        # Model deployment names - these must match your Azure deployments
        'embedding_model': os.getenv('AZURE_OPENAI_EMBEDDING_MODEL', 'text-embedding-ada-002-3'),
        'chat_model': os.getenv('AZURE_OPENAI_CHAT_MODEL', 'gpt-4'),
        
        # Request timeout for Azure OpenAI API calls
        'request_timeout': 30,
        
        # Retry configuration for failed requests
        'max_retries': 3,
        'retry_delay': 1,  # seconds between retries
    }
    print("🔗 Azure OpenAI features enabled with custom configuration")
else:
    AZURE_OPENAI_CONFIG = None
    print("🔗 Azure OpenAI features disabled - using Fabric AI only")

# AI Feature Configuration
# These settings control how the AI features behave

# Primary AI engine selection - Fabric is our main choice for testing
AI_PRIMARY_ENGINE = 'FABRIC'

# Similarity thresholds - these determine when questions are considered "similar"
# Higher values = more strict similarity requirements
# Lower values = more loose similarity matching

# Threshold for grouping questions (moderator feature)
# 0.85 = 85% similarity required - increased for better precision
AI_SIMILARITY_THRESHOLD = float(os.getenv('AI_SIMILARITY_THRESHOLD', '0.85'))

# Threshold for real-time suggestions while typing
# 0.80 = 80% similarity - increased to reduce false positives
AI_REALTIME_THRESHOLD = float(os.getenv('AI_REALTIME_THRESHOLD', '0.80'))

# Maximum number of similar questions to show at once
# Prevents UI clutter while still being helpful
AI_MAX_SIMILAR_QUESTIONS = int(os.getenv('AI_MAX_SIMILAR_QUESTIONS', '5'))



# Performance tuning for Fabric AI operations
# These settings optimize how we interact with Fabric's AI functions

# Name of the vector index in Fabric SQL database
# This index dramatically speeds up similarity searches
FABRIC_VECTOR_INDEX_NAME = 'IX_Question_Embedding_Vector'

# Batch size for AI processing operations
# Process this many questions at once for efficiency
FABRIC_AI_BATCH_SIZE = int(os.getenv('FABRIC_AI_BATCH_SIZE', '50'))

# Enable parallel processing of AI operations when possible
# This can speed up batch operations significantly
FABRIC_AI_PARALLEL_PROCESSING = True

# Maximum number of parallel AI operations
# Too many can overwhelm the database, too few are slow
FABRIC_AI_MAX_PARALLEL_OPERATIONS = 5



# Logging configuration for AI operations
# This helps us debug and monitor AI performance
FABRIC_AI_LOGGING = {
    # Log all AI operations for debugging
    'log_operations': True,
    
    # Log performance metrics for optimization
    'log_performance': True,
    
    # Log errors for troubleshooting
    'log_errors': True,
    
    # Log successful operations (can be noisy, disable in production)
    'log_success': DEBUG,  # Only log success in debug mode
}


# Feature flags for different AI capabilities
# These allow us to enable/disable specific AI features for testing
FABRIC_AI_FEATURES = {
    # Real-time similarity checking while users type
    'realtime_similarity': True,
    
    # Automatic question grouping using AI
    'auto_grouping': True,
    
    # AI-generated summaries for questions
    'ai_summaries': True,
    
    # Semantic clustering of questions
    'semantic_clustering': True,
    
    # Sentiment analysis of questions
    'sentiment_analysis': True,
    
    # Topic extraction from questions
    'topic_extraction': True,
     # Automatic categorization
    'auto_categorization': True,
}

# Print configuration summary for debugging
print(f"✅ AI Engine: {AI_PRIMARY_ENGINE} (Fabric AI primary)")
print(f"✅ Fabric Vector Functions: {FABRIC_AI_CONFIG['use_vector_functions']}")
print(f"✅ Fabric Semantic Functions: {FABRIC_AI_CONFIG['use_semantic_functions']}")
print(f"✅ Vector Dimension: {FABRIC_AI_CONFIG['vector_dimension']}")
print(f"✅ Similarity Threshold: {AI_SIMILARITY_THRESHOLD}")
print(f"✅ Realtime Threshold: {AI_REALTIME_THRESHOLD}")
print(f"✅ Azure OpenAI Supplementary: {AZURE_OPENAI_ENABLED}")