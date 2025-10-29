"""Comprehensive test suite pre Claude API wrapper."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from anthropic import APIError, RateLimitError, APIConnectionError
from utils.config import Settings
from services.claude_api import ClaudeClient


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_config():
    """Mock Settings objekt s API key."""
    config = Mock(spec=Settings)
    config.anthropic_api_key = "test-api-key-123"
    return config


@pytest.fixture
def mock_config_no_key():
    """Mock Settings objekt bez API key."""
    config = Mock(spec=Settings)
    config.anthropic_api_key = None
    return config


@pytest.fixture
def client(mock_config):
    """ClaudeClient instance s mock configom."""
    with patch('services.claude_api.Anthropic'):
        return ClaudeClient(mock_config)


@pytest.fixture
def mock_anthropic_response():
    """Mock Anthropic API response."""
    response = Mock()
    response.content = [Mock(text="Test response from Claude")]
    response.usage = Mock(input_tokens=100, output_tokens=200)
    return response


# ============================================================================
# 1. INITIALIZATION TESTS (3 tests)
# ============================================================================

def test_claude_client_init_success(mock_config):
    """Test úspešnej inicializácie ClaudeClient."""
    with patch('services.claude_api.Anthropic') as mock_anthropic:
        client = ClaudeClient(mock_config)
        
        assert client.config == mock_config
        assert client.model == "claude-sonnet-4-5-20250929"
        assert client.max_tokens == 8000
        mock_anthropic.assert_called_once_with(api_key="test-api-key-123")


def test_claude_client_init_missing_api_key(mock_config_no_key):
    """Test inicializácie bez API key - musí vyhodiť ValueError."""
    with pytest.raises(ValueError) as exc_info:
        ClaudeClient(mock_config_no_key)
    
    assert "ANTHROPIC_API_KEY is required" in str(exc_info.value)


def test_claude_client_init_invalid_config():
    """Test inicializácie s neplatným config objektom."""
    invalid_config = Mock()
    # Simuluj že nemá anthropic_api_key attribute
    del invalid_config.anthropic_api_key
    
    with pytest.raises(ValueError):
        ClaudeClient(invalid_config)


# ============================================================================
# 2. SYSTEM PROMPT TESTS (2 tests)
# ============================================================================

def test_get_legal_system_prompt_structure(client):
    """Test že system prompt má správnu štruktúru."""
    prompt = client.get_legal_system_prompt()
    
    assert isinstance(prompt, str)
    assert len(prompt) > 100
    assert "UAE" in prompt
    assert "expert" in prompt.lower()


def test_system_prompt_contains_uae_requirements(client):
    """Test že prompt obsahuje UAE špecifické požiadavky."""
    prompt = client.get_legal_system_prompt()
    
    # Musí obsahovať UAE legal requirements
    assert "UAE" in prompt or "Spojených Arabských Emirátov" in prompt
    assert "Federal Law" in prompt
    assert "slovenčin" in prompt.lower()
    assert "citáci" in prompt.lower() or "cituj" in prompt.lower()


# ============================================================================
# 3. LEGAL ANALYSIS TESTS (5 tests)
# ============================================================================

def test_analyze_legal_case_success(client, mock_anthropic_response):
    """Test úspešnej analýzy právneho prípadu."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    result = client.analyze_legal_case(
        case_context="Test case context",
        legal_context="Test legal context",
        query="Test query"
    )
    
    assert "response" in result
    assert "token_usage" in result
    assert "cost" in result
    assert "model" in result
    assert result["response"] == "Test response from Claude"


def test_analyze_legal_case_with_history(client, mock_anthropic_response):
    """Test analýzy s conversation history."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    history = [
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"}
    ]
    
    result = client.analyze_legal_case(
        case_context="Test case",
        legal_context="Test legal",
        query="Follow-up query",
        history=history
    )
    
    # Verify history was included in the call
    call_args = client.client.messages.create.call_args
    messages = call_args.kwargs['messages']
    
    assert len(messages) >= 3  # history + new message
    assert messages[0]["content"] == "Previous question"
    assert result["response"] == "Test response from Claude"


def test_analyze_legal_case_empty_context(client, mock_anthropic_response):
    """Test analýzy s prázdnym kontextom - mal by stále fungovať."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    result = client.analyze_legal_case(
        case_context="",
        legal_context="",
        query="Test query"
    )
    
    assert result is not None
    assert "response" in result


def test_analyze_legal_case_api_error(client):
    """Test handlovania API error."""
    client.client.messages.create = Mock(
        side_effect=APIError("API Error")
    )
    
    with pytest.raises(APIError):
        client.analyze_legal_case(
            case_context="Test",
            legal_context="Test",
            query="Test"
        )


def test_analyze_legal_case_rate_limit(client, mock_anthropic_response):
    """Test rate limit handling s retry."""
    # First call fails with rate limit, second succeeds
    client.client.messages.create = Mock(
        side_effect=[
            RateLimitError("Rate limit", response=Mock(status_code=429), body={}),
            mock_anthropic_response
        ]
    )
    
    with patch('time.sleep'):  # Mock sleep to speed up test
        result = client.analyze_legal_case(
            case_context="Test",
            legal_context="Test",
            query="Test"
        )
    
    assert result["response"] == "Test response from Claude"
    assert client.client.messages.create.call_count == 2


# ============================================================================
# 4. ALTERNATIVES GENERATION TESTS (3 tests)
# ============================================================================

def test_generate_alternatives_success(client, mock_anthropic_response):
    """Test úspešného generovania alternatív."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    result = client.generate_alternatives(
        case_summary="Test case summary",
        legal_context="Test legal context"
    )
    
    assert "response" in result
    assert "token_usage" in result
    assert result["response"] == "Test response from Claude"


def test_generate_alternatives_structured_output(client, mock_anthropic_response):
    """Test že alternatívy majú správnu štruktúru v requeste."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    client.generate_alternatives(
        case_summary="Summary",
        legal_context="Context"
    )
    
    call_args = client.client.messages.create.call_args
    messages = call_args.kwargs['messages']
    
    # Verify prompt asks for structured alternatives
    user_message = messages[0]['content']
    assert "3-5" in user_message or "alternatív" in user_message.lower()
    assert "rizik" in user_message.lower() or "risk" in user_message.lower()


def test_generate_alternatives_risk_assessment(client, mock_anthropic_response):
    """Test že prompt požaduje risk assessment."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    client.generate_alternatives(
        case_summary="Summary",
        legal_context="Context"
    )
    
    call_args = client.client.messages.create.call_args
    user_message = call_args.kwargs['messages'][0]['content']
    
    # Verify risk levels are mentioned
    assert "Low" in user_message or "Medium" in user_message or "High" in user_message


# ============================================================================
# 5. API CALL TESTS (4 tests)
# ============================================================================

def test_call_claude_api_success(client, mock_anthropic_response):
    """Test úspešného API call."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    result = client._call_claude_api(
        messages=[{"role": "user", "content": "Test"}],
        system="Test system prompt"
    )
    
    assert result["response"] == "Test response from Claude"
    assert result["token_usage"]["input"] == 100
    assert result["token_usage"]["output"] == 200
    assert result["model"] == "claude-sonnet-4-5-20250929"


def test_call_claude_api_retry_on_error(client, mock_anthropic_response):
    """Test retry mechaniky pri connection error."""
    client.client.messages.create = Mock(
        side_effect=[
            APIConnectionError(),
            mock_anthropic_response
        ]
    )
    
    with patch('time.sleep'):
        result = client._call_claude_api(
            messages=[{"role": "user", "content": "Test"}],
            system="Test system"
        )
    
    assert result["response"] == "Test response from Claude"
    assert client.client.messages.create.call_count == 2


def test_call_claude_api_max_retries_exceeded(client):
    """Test že po max retries sa vyhodí exception."""
    client.client.messages.create = Mock(
        side_effect=APIConnectionError()
    )
    
    with patch('time.sleep'):
        with pytest.raises(APIConnectionError):
            client._call_claude_api(
                messages=[{"role": "user", "content": "Test"}],
                system="Test system"
            )
    
    assert client.client.messages.create.call_count == 3


def test_call_claude_api_token_tracking(client, mock_anthropic_response):
    """Test správneho trackovania tokenov."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    result = client._call_claude_api(
        messages=[{"role": "user", "content": "Test"}],
        system="Test system"
    )
    
    assert result["token_usage"]["input"] == 100
    assert result["token_usage"]["output"] == 200
    assert result["token_usage"]["total"] == 300


# ============================================================================
# 6. COST CALCULATION TESTS (3 tests)
# ============================================================================

def test_calculate_cost_basic(client):
    """Test základného výpočtu nákladov."""
    # Claude Sonnet 4.5: $3/M input, $15/M output
    cost = client.calculate_cost(input_tokens=1000, output_tokens=1000)
    
    expected = (1000 / 1_000_000) * 3 + (1000 / 1_000_000) * 15
    assert cost == pytest.approx(expected, rel=1e-9)


def test_calculate_cost_zero_tokens(client):
    """Test výpočtu s nulovými tokenmi."""
    cost = client.calculate_cost(input_tokens=0, output_tokens=0)
    assert cost == 0.0


def test_calculate_cost_large_numbers(client):
    """Test výpočtu s veľkými číslami tokenov."""
    cost = client.calculate_cost(input_tokens=1_000_000, output_tokens=500_000)
    
    # 1M input = $3, 500k output = $7.5, total = $10.5
    expected = 3.0 + 7.5
    assert cost == pytest.approx(expected, rel=1e-9)


# ============================================================================
# 7. INTEGRATION TESTS (3 tests)
# ============================================================================

def test_full_legal_analysis_workflow(client, mock_anthropic_response):
    """Test komplétneho workflow právnej analýzy."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    # Analyze case
    result1 = client.analyze_legal_case(
        case_context="Employment dispute",
        legal_context="UAE Labor Law",
        query="What are employee rights?"
    )
    
    # Generate alternatives based on analysis
    result2 = client.generate_alternatives(
        case_summary=result1["response"],
        legal_context="UAE Labor Law"
    )
    
    assert result1 is not None
    assert result2 is not None
    assert client.client.messages.create.call_count == 2


def test_conversation_history_management(client, mock_anthropic_response):
    """Test manažmentu conversation history."""
    client.client.messages.create = Mock(return_value=mock_anthropic_response)
    
    history = []
    
    # First query
    result1 = client.analyze_legal_case(
        case_context="Case 1",
        legal_context="Law 1",
        query="Query 1",
        history=history
    )
    
    # Add to history
    history.append({"role": "user", "content": "Query 1"})
    history.append({"role": "assistant", "content": result1["response"]})
    
    # Second query with history
    result2 = client.analyze_legal_case(
        case_context="Case 1",
        legal_context="Law 1",
        query="Follow-up query",
        history=history
    )
    
    assert len(history) == 2
    assert result2 is not None


def test_slovak_output_validation(client):
    """Test že system prompt vyžaduje slovenský output."""
    prompt = client.get_legal_system_prompt()
    
    # Verify Slovak language requirement
    assert "slovenčin" in prompt.lower() or "slovak" in prompt.lower()
    
    # Verify prompt is used in analysis
    with patch.object(client, '_call_claude_api') as mock_call:
        mock_call.return_value = {
            "response": "Test",
            "token_usage": {"input": 100, "output": 200, "total": 300},
            "cost": 0.01,
            "model": "test"
        }
        
        client.analyze_legal_case(
            case_context="Test",
            legal_context="Test",
            query="Test"
        )
        
        # Verify system prompt was passed
        call_args = mock_call.call_args
        assert call_args.kwargs['system'] == prompt