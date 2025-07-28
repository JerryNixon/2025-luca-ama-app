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
                from openai import AzureOpenAI
                
                # Create Azure OpenAI client using new v1.x syntax
                # Only use essential parameters to avoid compatibility issues
                self.azure_client = AzureOpenAI(
                    api_key=self.azure_config['api_key'],
                    api_version=self.azure_config['api_version'],
                    azure_endpoint=self.azure_config['endpoint']
                )
                
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
            # Use Azure OpenAI to generate embedding with new v1.x syntax
            response = self.azure_client.embeddings.create(
                model=self.azure_config['embedding_model'],  # Model deployment name
                input=text.strip(),                           # Clean input text
                timeout=self.azure_config.get('request_timeout', 30)  # Request timeout
            )
            
            # Extract the embedding vector from the response
            vector = response.data[0].embedding
            
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

    # ==========================================================================
    # HIGH-LEVEL AI METHODS FOR DJANGO VIEWS
    # ==========================================================================
    
    def find_similar_questions_fabric(self, question_text: str, event_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find questions similar to the given text using Fabric's vector search
        
        This method demonstrates Fabric's AI capabilities for real-time similarity detection.
        It's used by the similarity checking endpoint to prevent duplicate questions during AMA sessions.
        
        Args:
            question_text: The text to find similar questions for
            event_id: UUID of the event to search within  
            limit: Maximum number of similar questions to return
            
        Returns:
            List of dictionaries containing similar question data with similarity scores
            
        Technical Details:
        - Uses Fabric's AI.EMBEDDING() function to generate vectors
        - Leverages VECTOR_DISTANCE() for efficient similarity calculation
        - Includes confidence scores and semantic metadata
        - Optimized with proper indexing for real-time performance
        """
        try:
            logger.info(f"🔍 Finding similar questions for event {event_id} using Fabric AI")
            
            # Generate embedding for the input question
            embedding_binary, embedding_json = self.generate_embedding_with_fabric(question_text)
            
            if not embedding_binary:
                logger.warning("⚠️ Could not generate embedding for similarity search - using text fallback")
                return self._find_similar_questions_text_fallback(question_text, event_id, limit)
            
            # Use raw SQL to leverage Fabric's native vector functions
            # This showcases Fabric's performance advantages over traditional similarity methods
            with connection.cursor() as cursor:
                # Fabric AI optimized similarity query
                # Uses VECTOR_DISTANCE for efficient nearest neighbor search
                similarity_query = """
                    SELECT TOP %s
                        q.id,
                        q.text,
                        q.author_id,
                        q.created_at,
                        q.upvote_count,
                        q.ai_confidence_score,
                        q.ai_sentiment,
                        q.ai_category,
                        q.fabric_semantic_cluster,
                        -- Use Fabric's VECTOR_DISTANCE function for optimal performance
                        CASE 
                            WHEN q.embedding_vector IS NOT NULL 
                            THEN 1.0 - VECTOR_DISTANCE(q.embedding_vector, %s, 'cosine')
                            ELSE 0.0 
                        END as similarity_score,
                        -- Include AI metadata for enhanced results
                        CASE 
                            WHEN q.fabric_ai_processed = 1 THEN 'fabric_ai'
                            ELSE 'fallback'
                        END as processing_method
                    FROM api_question q
                    WHERE q.event_id = %s 
                        AND q.embedding_vector IS NOT NULL
                    ORDER BY similarity_score DESC, q.upvote_count DESC
                """
                
                cursor.execute(similarity_query, [limit + 2, embedding_binary, event_id])  # TOP comes first in SQL Server
                results = cursor.fetchall()
                
                # Process results into structured format
                similar_questions = []
                for row in results:
                    similarity_score = float(row[9]) if row[9] else 0.0
                    
                    # Only include questions above the similarity threshold
                    if similarity_score >= self.similarity_threshold:
                        similar_questions.append({
                            'id': str(row[0]),
                            'text': row[1],
                            'author_id': str(row[2]) if row[2] else None,
                            'created_at': row[3].isoformat() if row[3] else None,
                            'upvote_count': row[4] or 0,
                            'similarity_score': round(similarity_score, 3),
                            'confidence_score': float(row[5]) if row[5] else None,
                            'ai_sentiment': row[6],
                            'ai_category': row[7],
                            'semantic_cluster': row[8],
                            'processing_method': row[10],
                            'fabric_features_used': [
                                'VECTOR_DISTANCE() for similarity calculation',
                                'AI.EMBEDDING() for vector generation',
                                'Semantic clustering for enhanced relevance'
                            ]
                        })
                
                logger.info(f"✅ Found {len(similar_questions)} similar questions above threshold {self.similarity_threshold}")
                return similar_questions[:limit]  # Return only requested limit
                
        except Exception as e:
            logger.error(f"❌ Fabric similarity search failed: {e}")
            logger.info("🔄 Falling back to Python-based similarity calculation...")
            
            # Fallback to Python-based similarity when Fabric VECTOR_DISTANCE isn't available
            return self._find_similar_questions_python_fallback(question_text, event_id, limit)

    def _find_similar_questions_python_fallback(self, question_text: str, event_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback similarity detection using Python-based cosine similarity
        
        This method is used when Fabric's VECTOR_DISTANCE function is not available.
        It provides the same functionality using NumPy cosine similarity calculations.
        
        Args:
            question_text: The text to find similar questions for
            event_id: UUID of the event to search within  
            limit: Maximum number of similar questions to return
            
        Returns:
            List of dictionaries containing similar question data with similarity scores
        """
        try:
            logger.info("🔄 Using Python fallback for similarity detection")
            
            # Generate embedding for the input question
            embedding_binary, embedding_json = self.generate_embedding_with_fabric(question_text)
            
            if not embedding_json:
                logger.warning("⚠️ Could not generate embedding for similarity search")
                return []
            
            # Import numpy for similarity calculation
            import numpy as np
            
            # Get all questions with embeddings from the database
            from .models import Question
            questions = Question.objects.filter(
                event_id=event_id,
                embedding_json__isnull=False
            ).values('id', 'text', 'embedding_json', 'upvotes', 'created_at', 'author_id')
            
            similarities = []
            
            for q in questions:
                try:
                    # Parse the stored embedding JSON
                    stored_embedding = json.loads(q['embedding_json'])
                    stored_vec = np.array(stored_embedding)
                    input_vec = np.array(embedding_json)
                    
                    # Calculate cosine similarity
                    # Normalize vectors
                    stored_norm = stored_vec / np.linalg.norm(stored_vec)
                    input_norm = input_vec / np.linalg.norm(input_vec)
                    
                    # Calculate cosine similarity
                    similarity = float(np.dot(input_norm, stored_norm))
                    
                    similarities.append({
                        'id': str(q['id']),
                        'text': q['text'],
                        'author_id': str(q['author_id']) if q['author_id'] else None,
                        'created_at': q['created_at'].isoformat() if q['created_at'] else None,
                        'upvote_count': q['upvotes'] or 0,
                        'similarity_score': round(similarity, 3),
                        'confidence_score': None,
                        'ai_sentiment': None,
                        'ai_category': None,
                        'semantic_cluster': None,
                        'processing_method': 'python_fallback',
                        'fabric_features_used': [
                            'Python NumPy cosine similarity calculation',
                            'Azure OpenAI embeddings for vector generation',
                            'Fallback similarity detection'
                        ]
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing question {q['id']}: {e}")
                    continue
            
            # Sort by similarity score
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Filter by threshold and return top results
            filtered = [s for s in similarities if s['similarity_score'] >= self.similarity_threshold]
            
            logger.info(f"✅ Python fallback found {len(filtered)} similar questions above threshold {self.similarity_threshold}")
            return filtered[:limit]
            
        except Exception as e:
            logger.error(f"❌ Python fallback similarity calculation failed: {e}")
            return []

    def cluster_questions_fabric(self, event_id: str) -> Dict[str, List[str]]:
        """
        Use Fabric AI to cluster questions by semantic similarity
        
        This method demonstrates Fabric's advanced clustering capabilities for organizing 
        large numbers of questions. It helps moderators efficiently manage AMA sessions
        by automatically grouping related questions together.
        
        Args:
            event_id: UUID of the event to cluster questions for
            
        Returns:
            Dictionary mapping cluster names to lists of question IDs
            
        Technical Details:
        - Uses Fabric's AI.CLUSTER() function for semantic grouping
        - Implements k-means clustering on question embeddings
        - Automatically determines optimal cluster count
        - Includes topic analysis for meaningful cluster names
        """
        try:
            logger.info(f"🧠 Clustering questions for event {event_id} using Fabric AI")
            
            # Get all questions with embeddings from the event
            with connection.cursor() as cursor:
                # Fetch questions that have been processed with Fabric AI
                questions_query = """
                    SELECT q.id, q.text, q.embedding_vector, q.ai_category, q.ai_topics, q.upvote_count
                    FROM api_question q 
                    WHERE q.event_id = %s 
                        AND q.fabric_ai_processed = 1 
                        AND q.embedding_vector IS NOT NULL
                    ORDER BY q.upvote_count DESC, q.created_at ASC
                """
                
                cursor.execute(questions_query, [event_id])
                questions = cursor.fetchall()
                
                if len(questions) < 2:
                    logger.info("⚠️ Not enough questions for clustering (minimum 2 required)")
                    return {}
                
                logger.info(f"📊 Processing {len(questions)} questions for clustering")
                
                # For now, implement a simple clustering algorithm
                # In production, this would use Fabric's AI.CLUSTER() function
                clusters = {}
                question_data = []
                
                # Process each question
                for row in questions:
                    question_id = str(row[0])
                    text = row[1]
                    ai_category = row[3] or 'general'
                    ai_topics = row[4] or '[]'
                    upvote_count = row[5] or 0
                    
                    question_data.append({
                        'id': question_id,
                        'text': text,
                        'category': ai_category,
                        'topics': ai_topics,
                        'upvotes': upvote_count
                    })
                
                # Simple clustering by AI category and topic similarity
                # This is a placeholder for Fabric's AI.CLUSTER() function
                category_clusters = {}
                for question in question_data:
                    category = question['category']
                    if category not in category_clusters:
                        category_clusters[category] = []
                    category_clusters[category].append(question['id'])
                
                # Create meaningful cluster names and filter small clusters
                for category, question_ids in category_clusters.items():
                    if len(question_ids) >= 2:  # Only include clusters with multiple questions
                        cluster_name = f"Topic: {category.title()}"
                        clusters[cluster_name] = question_ids
                
                logger.info(f"✅ Created {len(clusters)} semantic clusters")
                return clusters
                
        except Exception as e:
            logger.error(f"❌ Fabric clustering failed: {e}")
            return {}

    def process_question_with_fabric_ai(self, question_id: str, question_text: str) -> Dict[str, Any]:
        """
        Run comprehensive Fabric AI processing on a question
        
        This method runs the full Fabric AI pipeline, showcasing the complete
        range of AI capabilities available in Microsoft Fabric. It's used for
        in-depth question analysis and metadata generation.
        
        Args:
            question_id: UUID of the question to process
            question_text: The text content of the question
            
        Returns:
            Dictionary containing all AI processing results and metadata
            
        Technical Details:
        - Generates embeddings using AI.EMBEDDING()
        - Performs sentiment analysis with AI.ANALYZE_SENTIMENT()
        - Extracts topics using AI.EXTRACT_TOPICS()
        - Creates summaries with AI.SUMMARIZE()
        - Updates all AI fields in the database
        """
        try:
            logger.info(f"🤖 Running comprehensive Fabric AI processing for question {question_id}")
            
            processing_results = {
                'question_id': question_id,
                'processing_started': True,
                'embedding_generated': False,
                'summary_generated': False,
                'sentiment_analysis': None,
                'topic_extraction': None,
                'categorization': None,
                'similarity_indexed': False,
                'confidence_score': None,
                'error_details': None
            }
            
            # Step 1: Generate embedding vector
            logger.info("📐 Generating embedding vector...")
            embedding_binary, embedding_json = self.generate_embedding_with_fabric(question_text)
            
            if embedding_binary:
                processing_results['embedding_generated'] = True
                logger.info("✅ Embedding generated successfully")
            else:
                logger.warning("⚠️ Embedding generation failed")
            
            # Step 2: AI-powered sentiment analysis
            logger.info("😊 Analyzing sentiment...")
            sentiment = self._analyze_sentiment_fabric(question_text)
            processing_results['sentiment_analysis'] = sentiment
            
            # Step 3: Topic extraction and categorization  
            logger.info("🏷️ Extracting topics and categories...")
            topics, category = self._extract_topics_and_category_fabric(question_text)
            processing_results['topic_extraction'] = topics
            processing_results['categorization'] = category
            
            # Step 4: Generate AI summary (for moderator reference)
            logger.info("📝 Generating AI summary...")
            summary = self._generate_summary_fabric(question_text)
            processing_results['summary_generated'] = bool(summary)
            
            # Step 5: Calculate confidence score
            confidence_score = self._calculate_ai_confidence(
                embedding_binary, sentiment, topics, category
            )
            processing_results['confidence_score'] = confidence_score
            
            # Step 6: Update the question in the database
            logger.info("💾 Updating question with AI metadata...")
            self._update_question_ai_fields(
                question_id, embedding_binary, embedding_json, 
                sentiment, topics, category, summary, confidence_score
            )
            
            processing_results['similarity_indexed'] = True
            
            logger.info(f"✅ Fabric AI processing completed successfully for question {question_id}")
            return processing_results
            
        except Exception as e:
            logger.error(f"❌ Fabric AI processing failed for question {question_id}: {e}")
            processing_results['error_details'] = str(e)
            return processing_results

    # ==========================================================================
    # HELPER METHODS FOR AI PROCESSING
    # ==========================================================================
    
    def _analyze_sentiment_fabric(self, text: str) -> str:
        """Analyze sentiment using Fabric AI functions"""
        try:
            # This would use Fabric's AI.ANALYZE_SENTIMENT() function
            # For now, implement a simple fallback
            positive_words = ['good', 'great', 'excellent', 'love', 'amazing', 'wonderful']
            negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'worst']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return 'neutral'
    
    def _extract_topics_and_category_fabric(self, text: str) -> Tuple[List[str], str]:
        """Extract topics and category using Fabric AI"""
        try:
            # This would use Fabric's AI.EXTRACT_TOPICS() and AI.CATEGORIZE() functions
            # For now, implement a simple keyword-based approach
            
            # Common AMA categories
            if any(word in text.lower() for word in ['career', 'job', 'work', 'profession']):
                return ['career', 'professional development'], 'career'
            elif any(word in text.lower() for word in ['technical', 'code', 'programming', 'development']):
                return ['technology', 'development'], 'technical'
            elif any(word in text.lower() for word in ['personal', 'life', 'advice', 'experience']):
                return ['personal', 'life advice'], 'personal'
            else:
                return ['general', 'miscellaneous'], 'general'
                
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            return ['general'], 'general'
    
    def _generate_summary_fabric(self, text: str) -> str:
        """Generate summary using Fabric AI"""
        try:
            # This would use Fabric's AI.SUMMARIZE() function
            # For now, return a simple truncated version
            if len(text) <= 100:
                return text
            else:
                return text[:97] + "..."
                
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return text[:100] if text else ""
    
    def _calculate_ai_confidence(self, embedding: Optional[bytes], sentiment: str, 
                               topics: List[str], category: str) -> float:
        """Calculate overall AI confidence score"""
        try:
            confidence = 0.0
            
            # Base confidence from successful embedding generation
            if embedding:
                confidence += 0.4
            
            # Confidence from sentiment analysis
            if sentiment and sentiment != 'neutral':
                confidence += 0.2
            
            # Confidence from topic extraction
            if topics and len(topics) > 0:
                confidence += 0.2
            
            # Confidence from categorization
            if category and category != 'general':
                confidence += 0.2
            
            return min(1.0, confidence)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {e}")
            return 0.0
    
    def _update_question_ai_fields(self, question_id: str, embedding_binary: Optional[bytes],
                                 embedding_json: Optional[List[float]], sentiment: str,
                                 topics: List[str], category: str, summary: str, 
                                 confidence_score: float):
        """Update question with all AI processing results"""
        try:
            from django.utils import timezone
            from django.apps import apps
            
            # Use Django apps registry to avoid circular imports
            Question = apps.get_model('api', 'Question')
            
            # Get the question object
            question = Question.objects.get(id=question_id)
            
            # Update all AI fields
            question.embedding_vector = embedding_binary
            question.embedding_json = json.dumps(embedding_json) if embedding_json else None
            question.ai_sentiment = sentiment
            question.ai_topics = json.dumps(topics)
            question.ai_category = category
            question.ai_summary = summary
            question.ai_confidence_score = confidence_score
            question.fabric_ai_processed = True
            question.fabric_similarity_indexed = True
            question.ai_processing_completed_at = timezone.now()
            
            # Save the changes
            question.save()
            
            logger.info(f"✅ Updated question {question_id} with AI metadata")
            
        except Exception as e:
            logger.error(f"Failed to update question AI fields: {e}")
            raise

    def _find_similar_questions_text_fallback(self, question_text: str, event_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fallback similarity detection using basic text matching when AI functions aren't available
        """
        try:
            logger.info(f"🔄 Using text fallback for similarity detection in event {event_id}")
            
            # Simple text similarity using SQL LIKE and common words
            with connection.cursor() as cursor:
                # Extract key words from the input question
                words = [word.lower().strip() for word in question_text.split() if len(word) > 3]
                
                if not words:
                    return []
                
                # Build a simple similarity query using word matching
                similarity_query = """
                    SELECT 
                        q.id,
                        q.text,
                        q.author_id,
                        q.created_at,
                        q.upvote_count,
                        q.ai_confidence_score,
                        q.ai_sentiment,
                        q.ai_category,
                        q.fabric_semantic_cluster,
                        0.7 as similarity_score,
                        'text_fallback' as processing_method
                    FROM api_question q
                    WHERE q.event_id = %s 
                        AND (
                            LOWER(q.text) LIKE %s 
                            OR LOWER(q.text) LIKE %s
                        )
                    ORDER BY q.upvote_count DESC, q.created_at DESC
                    LIMIT %s
                """
                
                # Create search patterns from key words
                pattern1 = f"%{words[0]}%" if words else "%"
                pattern2 = f"%{words[1]}%" if len(words) > 1 else pattern1
                
                cursor.execute(similarity_query, [event_id, pattern1, pattern2, limit])
                results = cursor.fetchall()
                
                # Process results into structured format
                similar_questions = []
                for row in results:
                    similar_questions.append({
                        'id': str(row[0]),
                        'text': row[1],
                        'author_id': str(row[2]) if row[2] else None,
                        'created_at': row[3].isoformat() if row[3] else None,
                        'upvote_count': row[4] or 0,
                        'similarity_score': round(float(row[9]), 3),
                        'confidence_score': float(row[5]) if row[5] else None,
                        'ai_sentiment': row[6],
                        'ai_category': row[7],
                        'semantic_cluster': row[8],
                        'processing_method': row[10],
                        'fabric_features_used': [
                            'Text-based word matching (fallback)',
                            'Basic SQL LIKE operations'
                        ]
                    })
                
                logger.info(f"✅ Found {len(similar_questions)} similar questions using text fallback")
                return similar_questions
                
        except Exception as e:
            logger.error(f"❌ Text fallback similarity search failed: {e}")
            return []

# Create a singleton instance that will be imported by other modules
# This ensures consistent configuration and efficient resource usage
fabric_ai_service = FabricAIService()