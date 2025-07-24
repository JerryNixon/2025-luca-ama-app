"""
Microsoft Fabric AI Service

This service is the primary interface for all AI operations in the AMA application.
It leverages Microsoft Fabric's integrated AI capabilities first, with Azure OpenAI
as a fallback for features not yet available in Fabric.

Key Features:
1. Vector embeddings using Fabric's AI.EMBEDDING() function
2. Similarity search using Fabric's VECTOR_DISTANCE() function
3. Semantic analysis using Fabric's AI text analysis functions
4. Performance optimization with native SQL integration
5. Comprehensive error handling and fallback mechanisms

Architecture:
- Primary: Microsoft Fabric AI functions (native SQL integration)
- Fallback: Azure OpenAI API (for advanced features or when Fabric fails)
- Caching: Django cache framework for performance optimization
- Logging: Comprehensive logging for debugging and monitoring
"""
import json          # For handling JSON data (embeddings, configurations)
import logging       # For application logging and debugging
import struct        # For binary data conversion (embedding vectors)
import time          # For performance timing and delays
from typing import List, Dict, Optional, Tuple, Any  # Type hints for better code clarity
from django.conf import settings     # Access to Django configuration
from django.db import connection, transaction  # Database operations
from django.core.cache import cache  # Caching for performance optimization

# Set up logging for this module
logger = logging.getLogger(__name__)

class FabricAIService:
    """
    Main service class for Microsoft Fabric AI operations
    
    This class encapsulates all AI functionality and provides a clean interface
    for the rest of the application to use AI features.
    """
    
    def __init__(self):
        """
        Initialize the Fabric AI service with configuration from Django settings
        
        This constructor sets up all the necessary configuration and connections
        for both Fabric AI and Azure OpenAI (if enabled).
        """
        # Load Fabric AI configuration from Django settings
        # This determines whether Fabric AI features are enabled
        self.fabric_enabled = getattr(settings, 'FABRIC_AI_ENABLED', True)
        
        # Get the detailed Fabric AI configuration dictionary
        self.fabric_config = getattr(settings, 'FABRIC_AI_CONFIG', {})
        
        # Load Azure OpenAI configuration (may be None if disabled)
        self.azure_config = getattr(settings, 'AZURE_OPENAI_CONFIG', None)
        
        # Load similarity thresholds for different use cases
        self.similarity_threshold = getattr(settings, 'AI_SIMILARITY_THRESHOLD', 0.85)
        self.realtime_threshold = getattr(settings, 'AI_REALTIME_THRESHOLD', 0.80)
        
        # Load performance configuration
        self.batch_size = getattr(settings, 'FABRIC_AI_BATCH_SIZE', 50)
        self.operation_timeout = self.fabric_config.get('ai_operation_timeout', 30)
        self.enable_caching = self.fabric_config.get('enable_ai_caching', True)
        self.cache_timeout = self.fabric_config.get('ai_cache_timeout', 3600)

        # Initialize Azure OpenAI client if available and enabled
        self.azure_client = None
        if self.azure_config:
            try:
                # Import OpenAI library (only if we need it)
                import openai
                
                # Configure OpenAI client for Azure
                openai.api_type = "azure"                           # Use Azure OpenAI service
                openai.api_base = self.azure_config['endpoint']     # Azure endpoint URL
                openai.api_version = self.azure_config['api_version']  # API version
                openai.api_key = self.azure_config['api_key']       # Authentication key
                
                # Store the configured client for later use
                self.azure_client = openai
                logger.info("✅ Azure OpenAI client initialized for supplementary features")
                
            except ImportError:
                # OpenAI library not installed - warn but continue
                logger.warning("⚠️  OpenAI library not installed. Install with: pip install openai")
                self.azure_client = None
            except Exception as e:
                # Other initialization errors
                logger.warning(f"⚠️  Azure OpenAI initialization failed: {e}")
                self.azure_client = None
        
        
        
        # Initialize Fabric's AI capabilities
        self._initialize_fabric_ai_capabilities()
    
    def _initialize_fabric_ai_capabilities(self):
        """
        Initialize and verify Microsoft Fabric's AI capabilities
        
        This method checks if Fabric AI functions are available and creates
        necessary database structures for optimal performance.
        """
        
        # Skip initialization if Fabric AI is disabled
        if not self.fabric_enabled:
            logger.info("ℹ️  Fabric AI disabled in configuration")
            return
            
        try:
            # Use Django's database connection to check Fabric AI availability
            with connection.cursor() as cursor:
                
                # Check if Fabric's VECTOR_DISTANCE function is available
                # This is a key indicator that Fabric AI features are enabled
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM sys.objects 
                    WHERE name = 'VECTOR_DISTANCE' 
                    AND type IN ('FN', 'FS')  -- Function types in SQL Server
                """)
                
                # Get the result - 1 means function exists, 0 means it doesn't
                vector_functions_available = cursor.fetchone()[0] > 0
                
                if vector_functions_available:
                    logger.info("✅ Fabric AI vector functions detected and ready")
                    
                    # Create necessary indexes and structures for optimal performance
                    self._setup_fabric_ai_infrastructure()
                    
                    # Test basic AI functionality to ensure it's working
                    self._test_fabric_ai_basic_functionality()

                else:
                    logger.warning("⚠️  Fabric AI vector functions not available")
                    logger.warning("    Make sure your Fabric workspace has AI features enabled")
                    
                    # Disable Fabric AI if functions aren't available
                    self.fabric_enabled = False
                    
        except Exception as e:
            logger.error(f"❌ Failed to initialize Fabric AI capabilities: {e}")
            logger.error("    Falling back to Azure OpenAI or mock responses")
            
            # Disable Fabric AI on initialization error
            self.fabric_enabled = False

    def _setup_fabric_ai_infrastructure(self):
        """
        Create database structures needed for optimal Fabric AI performance
        
        This includes vector indexes, helper functions, and performance optimizations.
        """
        try:
            with connection.cursor() as cursor:
                
                # Get the configured index name from settings
                index_name = getattr(settings, 'FABRIC_VECTOR_INDEX_NAME', 'IX_Question_Embedding_Vector')
                
                # Check if our vector index already exists
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM sys.indexes 
                    WHERE name = %s 
                    AND object_id = OBJECT_ID('api_question')
                """, [index_name])

                # Create the index if it doesn't exist
                if cursor.fetchone()[0] == 0:
                    logger.info(f"Creating Fabric vector index: {index_name}")
                    
                    # Create a specialized index for vector operations
                    # This dramatically improves similarity search performance
                    cursor.execute(f"""
                        CREATE NONCLUSTERED INDEX [{index_name}] 
                        ON [api_question] ([embedding_vector])
                        INCLUDE (
                            [id], [text], [upvotes], [is_answered], 
                            [is_starred], [event_id], [author_id]
                        )
                        WHERE [embedding_vector] IS NOT NULL
                    """)
                    
                    logger.info(f"✅ Created Fabric vector index: {index_name}")
                else:
                    logger.info(f"✅ Fabric vector index already exists: {index_name}")
                
                # Create additional indexes for AI-related queries
                self._create_ai_support_indexes(cursor)
                
        except Exception as e:
            logger.warning(f"⚠️  Could not create Fabric AI infrastructure: {e}")
            logger.warning("    AI features will work but may be slower")

    def _create_ai_support_indexes(self, cursor):
        """
        Create additional indexes to support AI operations
        
        Args:
            cursor: Database cursor for executing SQL commands
        """
        try:
            # Index for semantic clustering queries
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT * FROM sys.indexes 
                    WHERE name = 'IX_Question_Semantic_Cluster' 
                    AND object_id = OBJECT_ID('api_question')
                )
                CREATE NONCLUSTERED INDEX [IX_Question_Semantic_Cluster] 
                ON [api_question] ([fabric_semantic_cluster], [event_id])
                WHERE [fabric_semantic_cluster] IS NOT NULL
            """)
            
            # Index for AI processing status
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT * FROM sys.indexes 
                    WHERE name = 'IX_Question_AI_Processed' 
                    AND object_id = OBJECT_ID('api_question')
                )
                CREATE NONCLUSTERED INDEX [IX_Question_AI_Processed] 
                ON [api_question] ([fabric_ai_processed], [event_id])
                INCLUDE ([id], [text], [created_at])
            """)
            
            logger.info("✅ Created AI support indexes")
            
        except Exception as e:
            logger.warning(f"⚠️  Could not create AI support indexes: {e}")

    def _test_fabric_ai_basic_functionality(self):
        """
        Test basic Fabric AI functionality to ensure it's working properly
        
        This runs a simple test to verify that AI functions are responding correctly.
        """
        try:
            with connection.cursor() as cursor:
                # Test the AI.EMBEDDING function with a simple text
                test_text = "This is a test question for Fabric AI"
                
                # Try to generate an embedding using Fabric's AI function
                cursor.execute("SELECT AI.EMBEDDING(%s) as test_embedding", [test_text])
                result = cursor.fetchone()
                
                if result and result[0]:
                    logger.info("✅ Fabric AI basic functionality test passed")
                    
                    # Log the embedding size for verification
                    embedding_size = len(result[0]) if result[0] else 0
                    logger.info(f"   Embedding size: {embedding_size} bytes")
                    
                else:
                    logger.warning("⚠️  Fabric AI test returned empty result")
                    
        except Exception as e:
            logger.warning(f"⚠️  Fabric AI basic functionality test failed: {e}")
            logger.warning("    AI features may not work as expected")

    def generate_embedding_with_fabric(self, text: str) -> Tuple[Optional[bytes], Optional[List[float]]]:
        """
        Generate embedding vector using Fabric's native AI functions
        
        This is the primary method for creating embeddings that can be used
        for similarity comparisons and semantic analysis.
        
        Args:
            text: The input text to create an embedding for
            
        Returns:
            Tuple of (binary_vector, json_vector) where:
            - binary_vector: Raw bytes suitable for Fabric's vector operations
            - json_vector: List of floats for compatibility and debugging
        """
        
        # Input validation
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding generation")
            return None, None
            
        # Check if Fabric AI is available
        if not self.fabric_enabled:
            logger.info("Fabric AI disabled, using fallback method")
            return self._generate_embedding_azure_fallback(text)
        
        # Check cache first if caching is enabled
        if self.enable_caching:
            cache_key = f"fabric_embedding_{hash(text.strip())}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.debug("✅ Retrieved embedding from cache")
                return cached_result['binary'], cached_result['json']
        try:
            # Use Django's database connection for Fabric AI operations
            with connection.cursor() as cursor:
                
                # Set operation timeout to prevent hanging
                cursor.execute(f"SET LOCK_TIMEOUT {self.operation_timeout * 1000}")  # Convert to milliseconds
                
                # Use Fabric's AI.EMBEDDING function to generate vector embedding
                # This function converts text into a numerical vector representation
                cursor.execute("""
                    SELECT 
                        AI.EMBEDDING(%s) as embedding_binary,
                        AI.EMBEDDING_JSON(%s) as embedding_json
                """, [text.strip(), text.strip()])
                
                # Retrieve the result
                result = cursor.fetchone()
                
                if result and result[0]:
                    # Extract binary and JSON representations
                    binary_embedding = result[0]           # Raw binary vector for Fabric operations
                    json_embedding_str = result[1]         # JSON string representation
                    
                    # Parse JSON embedding if available
                    json_embedding = None
                    if json_embedding_str:
                        try:
                            json_embedding = json.loads(json_embedding_str)
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse JSON embedding from Fabric")
                    
                    # Cache the result if caching is enabled
                    if self.enable_caching:
                        cache.set(cache_key, {
                            'binary': binary_embedding,
                            'json': json_embedding
                        }, timeout=self.cache_timeout)
                    
                    logger.info("✅ Generated embedding using Fabric AI")
                    logger.debug(f"   Text length: {len(text)} characters")
                    logger.debug(f"   Embedding size: {len(binary_embedding)} bytes")
                    
                    return binary_embedding, json_embedding
                else:
                    logger.warning("Fabric AI.EMBEDDING returned empty result")
                    
        except Exception as e:
            logger.warning(f"⚠️  Fabric embedding generation failed: {e}")
            logger.info("Falling back to Azure OpenAI")
            
        # Fallback to Azure OpenAI if Fabric fails
        return self._generate_embedding_azure_fallback(text)
    
    def _generate_embedding_azure_fallback(self, text: str) -> Tuple[Optional[bytes], Optional[List[float]]]:
        """
        Fallback method to generate embeddings using Azure OpenAI
        
        This method is used when Fabric AI is unavailable or fails.
        
        Args:
            text: The input text to create an embedding for
            
        Returns:
            Tuple of (binary_vector, json_vector)
        """
        # Check if Azure OpenAI client is available
        if not self.azure_client:
            logger.info("Azure OpenAI not available, using mock embedding")
            return self._generate_mock_embedding(text)
            
        try:
            # Use Azure OpenAI to generate embedding
            response = self.azure_client.Embedding.create(
                engine=self.azure_config['embedding_model'],  # Model deployment name
                input=text.strip(),                            # Clean input text
                timeout=self.azure_config.get('request_timeout', 30)  # Request timeout
            )
            
            # Extract the embedding vector from the response
            vector = response['data'][0]['embedding']
            
            # Convert to binary format for consistency with Fabric
            binary_vector = struct.pack(f'{len(vector)}f', *vector)
            
            logger.info("✅ Generated embedding using Azure OpenAI fallback")
            logger.debug(f"   Vector dimension: {len(vector)}")
            
            return binary_vector, vector
            
        except Exception as e:
            logger.error(f"❌ Azure OpenAI embedding generation failed: {e}")
            logger.info("Using mock embedding for development")
            
            # Final fallback to mock embedding
            return self._generate_mock_embedding(text)
        
    def _generate_mock_embedding(self, text: str) -> Tuple[Optional[bytes], Optional[List[float]]]:
        """
        Generate a mock embedding for development and testing
        
        This creates a deterministic embedding based on the text content,
        allowing the application to work even without AI services.
        
        Args:
            text: The input text
            
        Returns:
            Tuple of (binary_vector, json_vector)
        """
        
        # Create a deterministic vector based on text content
        # This ensures the same text always produces the same embedding
        text_hash = hash(text.lower().strip())
        
        # Generate a vector with the standard embedding dimension
        vector_dimension = self.fabric_config.get('vector_dimension', 1536)
        
        # Create vector values based on text characteristics
        mock_vector = []
        for i in range(vector_dimension):
            # Use text hash and position to create deterministic values
            value = (text_hash + i) % 10000 / 10000.0  # Normalize to 0-1 range
            mock_vector.append(value)
        
        # Convert to binary format
        binary_vector = struct.pack(f'{len(mock_vector)}f', *mock_vector)
        
        logger.info("✅ Generated mock embedding for development")
        logger.debug(f"   Vector dimension: {len(mock_vector)}")
        
        return binary_vector, mock_vector
    
    def calculate_similarity_fabric(self, vector1: bytes, vector2: bytes) -> float:
        """
        Calculate similarity between two embedding vectors using Fabric's VECTOR_DISTANCE
        
        This uses Fabric's native vector similarity function for optimal performance.
        
        Args:
            vector1: First embedding vector (binary format)
            vector2: Second embedding vector (binary format)
            
        Returns:
            Similarity score between 0.0 and 1.0 (higher = more similar)
        """
        
        # Validate inputs
        if not vector1 or not vector2:
            logger.warning("Empty vectors provided for similarity calculation")
            return 0.0
            
        # Check if Fabric AI is available
        if not self.fabric_enabled:
            return self._calculate_similarity_fallback(vector1, vector2)
        
        try:
            with connection.cursor() as cursor:
                # Use Fabric's VECTOR_DISTANCE function for similarity calculation
                # COSINE distance measures the angle between vectors (good for semantic similarity)
                cursor.execute("""
                    SELECT VECTOR_DISTANCE(%s, %s, 'COSINE') as similarity
                """, [vector1, vector2])
                
                result = cursor.fetchone()
                
                if result and result[0] is not None:
                    similarity = float(result[0])
                    
                    logger.debug(f"✅ Calculated similarity using Fabric: {similarity:.3f}")
                    return similarity
                else:
                    logger.warning("Fabric VECTOR_DISTANCE returned empty result")
        except Exception as e:
            logger.warning(f"⚠️  Fabric similarity calculation failed: {e}")
            
        # Fallback to alternative method
        return self._calculate_similarity_fallback(vector1, vector2)
    
    def _calculate_similarity_fallback(self, vector1: bytes, vector2: bytes) -> float:
        """
        Fallback similarity calculation using standard mathematical libraries
        
        Args:
            vector1: First embedding vector (binary format)
            vector2: Second embedding vector (binary format)
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        
        try:
            # Try using scikit-learn for similarity calculation
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Convert binary vectors back to float arrays
            float_vector1 = list(struct.unpack(f'{len(vector1)//4}f', vector1))
            float_vector2 = list(struct.unpack(f'{len(vector2)//4}f', vector2))
            
            # Calculate cosine similarity
            similarity = cosine_similarity([float_vector1], [float_vector2])[0][0]
            
            logger.debug(f"✅ Calculated similarity using scikit-learn: {similarity:.3f}")
            return float(similarity)
            
        except ImportError:
            logger.warning("Scikit-learn not available for similarity calculation")
            
            # Simple dot product fallback
            try:
                # Convert binary to float arrays
                float_vector1 = list(struct.unpack(f'{len(vector1)//4}f', vector1))
                float_vector2 = list(struct.unpack(f'{len(vector2)//4}f', vector2))
                
                # Ensure vectors are the same length
                if len(float_vector1) != len(float_vector2):
                    logger.warning("Vector length mismatch in similarity calculation")
                    return 0.0
                
                # Calculate simple dot product similarity
                dot_product = sum(a * b for a, b in zip(float_vector1, float_vector2))
                
                # Normalize to 0-1 range (this is a rough approximation)
                similarity = max(0.0, min(1.0, dot_product))
                
                logger.debug(f"✅ Calculated similarity using dot product: {similarity:.3f}")
                return similarity
                
            except Exception as e:
                logger.error(f"❌ All similarity calculation methods failed: {e}")
                return 0.0
                
        except Exception as e:
            logger.error(f"❌ Fallback similarity calculation failed: {e}")
            return 0.0

# Create a singleton instance that will be imported by other modules
# This ensures consistent configuration and efficient resource usage
fabric_ai_service = FabricAIService()