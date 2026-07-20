# Ollama Provider Debug Report - Sprint 20.16

## Investigated File
`backend/app/infrastructure/ai_providers/ollama_provider.py`

---

## 1. `_generate()` Implementation (Lines 219-242)

```python
async def _generate(self, prompt: str) -> str:
    """Generate content using Ollama API."""
    try:
        response = await self._client.generate(
            model=self.model,
            prompt=prompt,
        )
        raw_response = response.get("response", "") or ""
        # TEMPORARY DEBUG LOGGING - TRACE FULL API RESPONSE
        logger.info(f"OllamaProvider._generate - FULL API RESPONSE OBJECT: {response}")
        return raw_response
    except ollama.ResponseError as e:
        logger.error(f"Ollama API response error: {e}")
        raise
    except Exception as e:
        logger.error(f"Ollama API call failed: {e}")
        raise
```

### Key Observations:
- Line 233: Uses `response.get("response", "")` - if key doesn't exist, returns empty string
- Line 240-242: All exceptions are re-raised (no local handling)
- The timeout for the ollama client is passed in `__init__` (line 39)

---

## 2. Client Initialization (Lines 27-39)

```python
def __init__(
    self,
    host: str = DEFAULT_HOST,
    model: str = DEFAULT_MODEL,
    prompt_builder: PromptBuilder | None = None,
    timeout: float = DEFAULT_TIMEOUT,
):
    self.host = host.rstrip("/")
    self.model = model
    self.prompt_builder = prompt_builder or PromptBuilder()
    self.timeout = timeout
    # Initialize ollama client with custom host
    self._client = ollama.AsyncClient(host=self.host, timeout=timeout)
```

### Timeout Values:
- Line 25: `DEFAULT_TIMEOUT = 60.0` (60 seconds)
- Line 32: Timeout is passed to `ollama.AsyncClient(host=self.host, timeout=timeout)`

---

## 3. Timeout Configuration Analysis

### Current State:
- **Line 25**: Class-level default timeout is `60.0` seconds
- **Line 32**: Constructor parameter `timeout: float = DEFAULT_TIMEOUT`
- **Line 39**: `ollama.AsyncClient(host=self.host, timeout=timeout)`

### Issue:
The `timeout` parameter is passed to `AsyncClient`, but the ollama library's timeout behavior may differ:

1. The ollama Python client (`ollama.AsyncClient`) passes timeout to httpx
2. httpx's timeout can be:
   - A float (total timeout) - passed as-is
   - A `Timeout(timeout)` object or dict with connect/read/write values
3. If ollama is not running, httpx raises `httpx.ReadTimeout` or `httpx.ConnectError`

---

## 4. JSON Parsing Logic (Lines 244-273)

```python
def _parse_json_response(self, response: str) -> dict[str, Any] | None:
    """Parse JSON response from Ollama."""
    response = response.strip()

    # Remove markdown code block wrappers if present
    if response.startswith("```json"):
        response = response[7:]
    if response.startswith("```"):
        response = response[3:]
    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    if not response:
        logger.warning("Empty response from LLM")
        return None

    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON response: {e}")
        return None
```

### Key Observations:
- Lines 255-261: Strips markdown code block wrappers
- Lines 265-267: Returns `None` if response is empty after stripping
- Lines 269-273: Returns `None` if JSON parsing fails
- The method catches all JSON errors and returns `None` (no exception raised)

---

## 5. response.response Handling Analysis

### The Problem Path:
When Ollama returns a response:

1. The API returns: `{"response": "...", "done": true}` (typical structure)
2. Line 233 extracts: `raw_response = response.get("response", "") or ""`
3. If Ollama returns empty string or no JSON, parsing returns `None`
4. Line 73 in `summarize_conversation`: `raise ValueError("LLM returned empty or invalid JSON response")`

### Why Different Behaviors?

| Agent | Error Observed | Root Cause |
|-------|---------------|------------|
| ConversationAgent | `ValueError: LLM returned empty or invalid JSON response` | Ollama responded but returned empty/invalid JSON (line 73 raises ValueError) |
| TaskAgent | `httpx.ReadTimeout` | Ollama timed out (not running/slow) before returning response |

---

## Root-Cause Analysis

### Issue 1: Inconsistent Error Handling Between Agents
**Location**: `conversation_agent.py` lines 77-86 vs `task_agent.py` lines 71-77

Both agents have similar try/except patterns in their `process()` methods, catching exceptions and falling back. However, the diagnostic script calls the provider methods directly, bypassing the agent's exception handling.

### Issue 2: Ollama Not Responding / Running
The `httpx.ReadTimeout` error indicates the Ollama server is not reachable or not responding:

- Connection timeout occurs before any response is received
- The default timeout of 60 seconds may not be sufficient for model loading
- Model `llama3.2:latest` may need to be pulled/downloaded first

### Issue 3: Empty Response When Ollama Returns Non-JSON
When Ollama returns a non-JSON response (plain text), `_parse_json_response()` returns `None` (line 267 or 273), causing `ValueError` to be raised (line 73).

---

## Recommended Minimal Code Changes

### Option A: Handle timeouts gracefully in the provider
**File**: `backend/app/infrastructure/ai_providers/ollama_provider.py`

**Change 1 (Lines 240-242)** - Better exception handling:
```python
# BEFORE:
except ollama.ResponseError as e:
    logger.error(f"Ollama API response error: {e}")
    raise
except Exception as e:
    logger.error(f"Ollama API call failed: {e}")
    raise

# AFTER:
except ollama.ResponseError as e:
    logger.error(f"Ollama API response error: {e}")
    raise
except httpx.ReadTimeout as e:
    logger.warning(f"Ollama request timed out: {e}")
    raise TimeoutError(f"Ollama request timed out after {self.timeout}s")
except httpx.ConnectError as e:
    logger.warning(f"Could not connect to Ollama: {e}")
    raise ConnectionError(f"Could not connect to Ollama at {self.host}")
except Exception as e:
    logger.error(f"Ollama API call failed: {e}")
    raise
```

**Change 2 (Line 17)** - Add httpx import:
```python
# ADD:
import httpx
```

### Option B: Increase default timeout for model loading
**File**: `backend/app/infrastructure/ai_providers/ollama_provider.py`

**Change (Line 25)**:
```python
# BEFORE:
DEFAULT_TIMEOUT = 60.0

# AFTER:
DEFAULT_TIMEOUT = 120.0  # Increased for model cold-start
```

### Option C: Add retry logic with exponential backoff
This would be a larger change but would help with cold-start scenarios.

---

## Summary

| Component | Current Behavior | Issue |
|-----------|------------------|-------|
| `_generate()` timeout | 60s default | May be insufficient for cold-start |
| `_generate()` exception handling | Re-raises all | No specific handling for `httpx.ReadTimeout` |
| `_parse_json_response()` | Returns None on failure | Causes ValueError in caller |
| Agent fallback | Catches exceptions | Works, but script bypasses it |

The diagnostic script calls `provider.extract_tasks()` directly, which raises `httpx.ReadTimeout` when Ollama doesn't respond within the timeout. The agent's `process()` method catches this and falls back, but the direct provider call in the script does not.