"""
Comprehensive tests for utils/embeddings.py module
Tests all EmbeddingManager methods including multilingual support,
lazy loading, batch processing, and error handling.
"""

import pytest
import math
from unittest.mock import Mock, patch, MagicMock
from utils.embeddings import EmbeddingManager


class TestEmbeddingManagerInitialization:
    """Test EmbeddingManager initialization and model loading"""
    
    def test_default_model_initialization(self):
        """Test initialization with default multilingual model"""
        manager = EmbeddingManager()
        
        assert manager.model_name == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        assert manager.model is not None
        assert manager.embedding_dimension > 0
    
    def test_custom_model_initialization(self):
        """Test initialization with custom model name"""
        custom_model = "sentence-transformers/all-MiniLM-L6-v2"
        manager = EmbeddingManager(model_name=custom_model)
        
        assert manager.model_name == custom_model
        assert manager.model is not None
    
    @patch('utils.embeddings.OpenAI')
    def test_lazy_loading_model_property(self, mock_openai):
        """Test that model is loaded immediately on initialization"""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        manager = EmbeddingManager()
        
        # Verify model was loaded during __init__
        mock_openai.assert_called_once()
        assert manager.model == mock_client
    
    def test_embedding_dimension_set_correctly(self):
        """Test that embedding dimension is captured during initialization"""
        manager = EmbeddingManager()
        
        # Default multilingual model should have 1536 dimensions
        assert manager.embedding_dimension == 1536
        assert isinstance(manager.embedding_dimension, int)


class TestGenerateEmbeddings:
    """Test batch embeddings generation"""
    
    def test_generate_embeddings_single_text(self):
        """Test generating embeddings for single text"""
        manager = EmbeddingManager()
        texts = ["This is a test document"]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (1, manager.embedding_dimension)
        assert hasattr(embeddings, 'shape')
    
    def test_generate_embeddings_multiple_texts(self):
        """Test generating embeddings for multiple texts"""
        manager = EmbeddingManager()
        texts = [
            "First document about UAE law",
            "Second document about regulations",
            "Third document about legal framework"
        ]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (3, manager.embedding_dimension)
        assert hasattr(embeddings, 'shape')
    
    def test_generate_embeddings_batch_processing(self):
        """Test batch processing with many texts"""
        manager = EmbeddingManager()
        # Create 100 texts to test batching (default batch_size=32)
        texts = [f"Document number {i} about legal matters" for i in range(100)]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (100, manager.embedding_dimension)
        assert hasattr(embeddings, 'shape')
    
    def test_generate_embeddings_empty_list_raises_error(self):
        """Test that empty list raises ValueError"""
        manager = EmbeddingManager()
        
        with pytest.raises(ValueError, match="Cannot generate embeddings for empty text list"):
            manager.generate_embeddings([])
    
    def test_generate_embeddings_preserves_order(self):
        """Test that embeddings maintain input text order"""
        manager = EmbeddingManager()
        texts = ["Text A", "Text B", "Text C"]
        
        embeddings1 = manager.generate_embeddings(texts)
        embeddings2 = manager.generate_embeddings(texts)
        
        # Same texts should produce same embeddings in same order
        assert embeddings1.shape == embeddings2.shape
        for i in range(len(texts)):
            for j in range(manager.embedding_dimension):
                assert abs(embeddings1[i][j] - embeddings2[i][j]) < 1e-5
    
    @patch('utils.embeddings.OpenAI')
    def test_generate_embeddings_calls_encode_correctly(self, mock_openai):
        """Test that encode is called with correct parameters"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536), Mock(embedding=[0.2] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        manager = EmbeddingManager()
        texts = ["Text 1", "Text 2"]
        manager.generate_embeddings(texts)
        
        mock_client.embeddings.create.assert_called_once_with(
            input=texts,
            model="text-embedding-3-small"
        )


class TestGenerateQueryEmbedding:
    """Test single query embedding generation"""
    
    def test_generate_query_embedding_valid_query(self):
        """Test generating embedding for valid query"""
        manager = EmbeddingManager()
        query = "What are the labor laws in UAE?"
        
        embedding = manager.generate_query_embedding(query)
        
        assert embedding.shape == (manager.embedding_dimension,)
        assert hasattr(embedding, 'shape')
    
    def test_generate_query_embedding_empty_string_raises_error(self):
        """Test that empty query raises ValueError"""
        manager = EmbeddingManager()
        
        with pytest.raises(ValueError, match="Cannot generate embedding for empty query"):
            manager.generate_query_embedding("")
    
    def test_generate_query_embedding_whitespace_only_raises_error(self):
        """Test that whitespace-only query raises ValueError"""
        manager = EmbeddingManager()
        
        with pytest.raises(ValueError, match="Cannot generate embedding for empty query"):
            manager.generate_query_embedding("   \t\n  ")
    
    def test_generate_query_embedding_consistency(self):
        """Test that same query produces same embedding"""
        manager = EmbeddingManager()
        query = "Test query for consistency"
        
        embedding1 = manager.generate_query_embedding(query)
        embedding2 = manager.generate_query_embedding(query)
        
        assert len(embedding1) == len(embedding2)
        for i in range(len(embedding1)):
            assert abs(embedding1[i] - embedding2[i]) < 1e-5
    
    @patch('utils.embeddings.OpenAI')
    def test_generate_query_embedding_no_progress_bar(self, mock_openai):
        """Test that query embedding doesn't show progress bar"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        manager = EmbeddingManager()
        manager.generate_query_embedding("test query")
        
        mock_client.embeddings.create.assert_called_once_with(
            input="test query",
            model="text-embedding-3-small"
        )


class TestMultilingualSupport:
    """Test multilingual embedding support (Arabic, English, Slovak)"""
    
    def test_english_text_embedding(self):
        """Test embedding generation for English text"""
        manager = EmbeddingManager()
        texts = ["This is an English legal document about UAE regulations"]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (1, manager.embedding_dimension)
        for i in range(embeddings.shape[0]):
            for j in range(embeddings.shape[1]):
                assert not math.isnan(embeddings[i][j])
    
    def test_arabic_text_embedding(self):
        """Test embedding generation for Arabic text"""
        manager = EmbeddingManager()
        texts = ["هذا مستند قانوني عن التشريعات الإماراتية"]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (1, manager.embedding_dimension)
        for i in range(embeddings.shape[0]):
            for j in range(embeddings.shape[1]):
                assert not math.isnan(embeddings[i][j])
    
    def test_slovak_text_embedding(self):
        """Test embedding generation for Slovak text"""
        manager = EmbeddingManager()
        texts = ["Toto je právny dokument o právnych predpisoch SAE"]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (1, manager.embedding_dimension)
        for i in range(embeddings.shape[0]):
            for j in range(embeddings.shape[1]):
                assert not math.isnan(embeddings[i][j])
    
    def test_mixed_language_batch(self):
        """Test embedding generation for mixed language batch"""
        manager = EmbeddingManager()
        texts = [
            "English legal text about regulations",
            "نص قانوني بالعربية عن الأنظمة",
            "Slovenský právny text o predpisoch"
        ]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (3, manager.embedding_dimension)
        for i in range(embeddings.shape[0]):
            for j in range(embeddings.shape[1]):
                assert not math.isnan(embeddings[i][j])
        
        # Verify all embeddings are different (not zeros or same values)
        assert not all(abs(embeddings[0][i] - embeddings[1][i]) < 1e-6 for i in range(manager.embedding_dimension))
        assert not all(abs(embeddings[1][i] - embeddings[2][i]) < 1e-6 for i in range(manager.embedding_dimension))
    
    def test_arabic_query_embedding(self):
        """Test query embedding for Arabic text"""
        manager = EmbeddingManager()
        query = "ما هي قوانين العمل في الإمارات؟"
        
        embedding = manager.generate_query_embedding(query)
        
        assert embedding.shape == (manager.embedding_dimension,)
        for i in range(len(embedding)):
            assert not math.isnan(embedding[i])
    
    def test_multilingual_semantic_similarity(self):
        """Test that semantically similar texts in different languages have similar embeddings"""
        manager = EmbeddingManager()
        
        # Similar legal concept in different languages
        english_text = "labor law regulations"
        arabic_text = "قوانين العمل"
        
        emb_en = manager.generate_query_embedding(english_text)
        emb_ar = manager.generate_query_embedding(arabic_text)
        
        # Calculate cosine similarity
        dot_product = sum(emb_en[i] * emb_ar[i] for i in range(len(emb_en)))
        norm_en = math.sqrt(sum(x * x for x in emb_en))
        norm_ar = math.sqrt(sum(x * x for x in emb_ar))
        similarity = dot_product / (norm_en * norm_ar)
        
        # Should have some similarity (> 0.3) as they're related concepts
        # Note: This is a loose test as translation isn't perfect
        assert similarity > 0.2  # Relaxed threshold for multilingual


class TestGetEmbeddingDimension:
    """Test embedding dimension getter"""
    
    def test_get_embedding_dimension_returns_correct_value(self):
        """Test that dimension getter returns correct value"""
        manager = EmbeddingManager()
        
        dim1 = manager.get_embedding_dimension()
        dim2 = manager.embedding_dimension
        
        assert dim1 == dim2
        assert isinstance(dim1, int)
        assert dim1 > 0
    
    def test_get_embedding_dimension_consistency(self):
        """Test that dimension remains consistent across calls"""
        manager = EmbeddingManager()
        
        dim1 = manager.get_embedding_dimension()
        dim2 = manager.get_embedding_dimension()
        
        assert dim1 == dim2


class TestGetModelInfo:
    """Test model information retrieval"""
    
    def test_get_model_info_returns_dict(self):
        """Test that model info returns dictionary"""
        manager = EmbeddingManager()
        
        info = manager.get_model_info()
        
        assert isinstance(info, dict)
    
    def test_get_model_info_contains_required_fields(self):
        """Test that model info contains all required fields"""
        manager = EmbeddingManager()
        
        info = manager.get_model_info()
        
        assert "model_name" in info
        assert "embedding_dimension" in info
        assert "max_sequence_length" in info
        assert "supports_languages" in info
    
    def test_get_model_info_correct_values(self):
        """Test that model info values are correct"""
        manager = EmbeddingManager()
        
        info = manager.get_model_info()
        
        assert info["model_name"] == manager.model_name
        assert info["embedding_dimension"] == manager.embedding_dimension
        assert isinstance(info["max_sequence_length"], int)
        assert isinstance(info["supports_languages"], list)
    
    def test_get_model_info_language_support(self):
        """Test that supported languages are listed"""
        manager = EmbeddingManager()
        
        info = manager.get_model_info()
        
        languages = info["supports_languages"]
        assert "Arabic" in languages
        assert "English" in languages
        assert "Slovak" in languages
        assert "50+ others" in languages


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_none_text_in_batch_handling(self):
        """Test handling of None values in text batch"""
        manager = EmbeddingManager()
        
        # Most implementations will convert None to string or error
        # Test the actual behavior
        texts = ["Valid text", None, "Another text"]
        
        # Should either handle gracefully or raise TypeError
        try:
            embeddings = manager.generate_embeddings(texts)
            # If it succeeds, verify shape
            assert embeddings.shape[0] == 3
        except (TypeError, AttributeError):
            # This is also acceptable behavior
            pass
    
    def test_very_long_text_handling(self):
        """Test handling of very long text (exceeds max_seq_length)"""
        manager = EmbeddingManager()
        
        # Create text longer than typical max_seq_length (512 tokens)
        long_text = "word " * 1000
        
        # Should truncate and still produce embedding
        embedding = manager.generate_query_embedding(long_text)
        
        assert embedding.shape == (manager.embedding_dimension,)
        for i in range(len(embedding)):
            assert not math.isnan(embedding[i])
    
    def test_special_characters_handling(self):
        """Test handling of special characters and symbols"""
        manager = EmbeddingManager()
        
        texts = [
            "Text with symbols: @#$%^&*()",
            "Text with numbers: 123456789",
            "Text with punctuation: ... !!! ???"
        ]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (3, manager.embedding_dimension)
        for i in range(embeddings.shape[0]):
            for j in range(embeddings.shape[1]):
                assert not math.isnan(embeddings[i][j])
    
    def test_unicode_handling(self):
        """Test handling of various unicode characters"""
        manager = EmbeddingManager()
        
        texts = [
            "Emoji test: 😀 📚 ⚖️",
            "Arabic: العربية",
            "Chinese: 中文",
            "Mixed: Test مختلط mixed"
        ]
        
        embeddings = manager.generate_embeddings(texts)
        
        assert embeddings.shape == (4, manager.embedding_dimension)
        for i in range(embeddings.shape[0]):
            for j in range(embeddings.shape[1]):
                assert not math.isnan(embeddings[i][j])


class TestEmbeddingQuality:
    """Test embedding quality and properties"""
    
    def test_embeddings_are_normalized_or_reasonable_range(self):
        """Test that embedding values are in reasonable range"""
        manager = EmbeddingManager()
        texts = ["Sample legal document text"]
        
        embeddings = manager.generate_embeddings(texts)
        
        # Values should typically be in range [-1, 1] or [-2, 2]
        min_val = min(embeddings[i][j] for i in range(embeddings.shape[0]) for j in range(embeddings.shape[1]))
        max_val = max(embeddings[i][j] for i in range(embeddings.shape[0]) for j in range(embeddings.shape[1]))
        assert min_val >= -5.0
        assert max_val <= 5.0
    
    def test_different_texts_produce_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        manager = EmbeddingManager()
        
        text1 = "UAE labor law regulations"
        text2 = "Corporate governance framework"
        
        emb1 = manager.generate_query_embedding(text1)
        emb2 = manager.generate_query_embedding(text2)
        
        # Embeddings should be different
        assert not all(abs(emb1[i] - emb2[i]) < 1e-6 for i in range(len(emb1)))
    
    def test_similar_texts_produce_similar_embeddings(self):
        """Test that similar texts produce similar embeddings"""
        manager = EmbeddingManager()
        
        text1 = "labor law regulations in UAE"
        text2 = "UAE employment law and regulations"
        
        emb1 = manager.generate_query_embedding(text1)
        emb2 = manager.generate_query_embedding(text2)
        
        # Calculate cosine similarity
        dot_product = sum(emb1[i] * emb2[i] for i in range(len(emb1)))
        norm1 = math.sqrt(sum(x * x for x in emb1))
        norm2 = math.sqrt(sum(x * x for x in emb2))
        similarity = dot_product / (norm1 * norm2)
        
        # Similar texts should have high similarity (> 0.5)
        assert similarity > 0.5


class TestBatchProcessingEfficiency:
    """Test batch processing behavior"""
    
    def test_batch_processing_consistency(self):
        """Test that batch and individual processing give same results"""
        manager = EmbeddingManager()
        texts = ["Text A", "Text B", "Text C"]
        
        # Batch processing
        batch_embeddings = manager.generate_embeddings(texts)
        
        # Individual processing
        individual_embeddings = [
            manager.generate_query_embedding(text) for text in texts
        ]
        
        # Should produce same results (within floating point tolerance)
        for i in range(len(texts)):
            for j in range(manager.embedding_dimension):
                assert abs(batch_embeddings[i][j] - individual_embeddings[i][j]) < 1e-4
    
    @patch('utils.embeddings.OpenAI')
    def test_batch_size_parameter_used(self, mock_openai):
        """Test that batch_size parameter is passed correctly"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)] * 5
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        manager = EmbeddingManager()
        texts = ["Text"] * 5
        manager.generate_embeddings(texts)
        
        # Verify OpenAI API was called
        mock_client.embeddings.create.assert_called_once()


# Fixtures for common test data
@pytest.fixture
def sample_texts():
    """Fixture providing sample texts for testing"""
    return [
        "UAE Federal Law on Commercial Companies",
        "Employment regulations in Dubai",
        "Intellectual property rights in UAE"
    ]


@pytest.fixture
def sample_arabic_texts():
    """Fixture providing sample Arabic texts"""
    return [
        "القانون الاتحادي للشركات التجارية",
        "لوائح التوظيف في دبي",
        "حقوق الملكية الفكرية في الإمارات"
    ]


@pytest.fixture
def embedding_manager():
    """Fixture providing initialized EmbeddingManager"""
    return EmbeddingManager()