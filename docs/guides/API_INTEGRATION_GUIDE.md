# Modulus API Integration Guide for 3rd Party Applications

## Overview

Modulus provides a REST API for deterministic, exact mathematical computation. This guide shows how to integrate Modulus into your applications.

---

## 🚀 Quick Start

### Base URL
```
http://localhost:8000
```

### API Documentation
Interactive docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 Endpoints

### 1. `/solve_v2` - Advanced Solver (Recommended)

**POST** `/solve_v2`

Full PAT-first pipeline with Grok router, validation, and machine-checkable certificates.

#### Request Body
```json
{
  "question": "string",           // Natural language problem description
  "context": "string (optional)"  // Additional context or constraints
}
```

#### Response
```json
{
  "answer": "string",              // Human-readable answer
  "confidence": 0.0-1.0,           // Confidence score
  "trace_id": "string",            // Unique trace identifier
  "fallback_used": false,          // Whether fallback was triggered
  
  "router": {
    "confidence": 0.0-1.0,
    "explanation": "string",
    "raw_response": {
      "problem_id": "string",
      "domains": ["array"],
      "equations": ["array"],
      "symbols": {},
      "objective": {}
    }
  },
  
  "validation": {
    "accepted": true,
    "messages": []
  },
  
  "execution": {
    "proof": {},                   // Machine-checkable proof
    "raw_solution": {},
    "serialized_package": {}       // Complete solution package
  },
  
  "solution_package": {
    "solution": {},
    "certificate": {},
    "trace": {}                    // Detailed execution trace
  }
}
```

#### Example: Python
```python
import requests

response = requests.post(
    "http://localhost:8000/solve_v2",
    json={"question": "What is the orbital velocity at 400km altitude?"}
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']}")
print(f"Trace ID: {result['trace_id']}")
```

#### Example: JavaScript/Node.js
```javascript
const axios = require('axios');

async function solveWithModulus(question) {
  const response = await axios.post('http://localhost:8000/solve_v2', {
    question: question
  });
  
  return {
    answer: response.data.answer,
    confidence: response.data.confidence,
    trace: response.data.solution_package?.trace
  };
}

// Usage
solveWithModulus("Calculate escape velocity from Earth")
  .then(result => console.log(result));
```

#### Example: cURL
```bash
curl -X POST http://localhost:8000/solve_v2 \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Solve the heat equation for a 1D rod",
    "context": "Length 1m, initial temp 100C at center"
  }'
```

---

### 2. `/solve` - Legacy Endpoint

**POST** `/solve`

Direct solver access without router pipeline.

#### Request Body
```json
{
  "question": "string",
  "proof": false,                  // Include proof steps
  "n_samples": 5,                  // Number of samples for voting
  "backend": "pat",                // "pat" or "modulus"
  "temperature": 0.7
}
```

#### Response
```json
{
  "answer": "string",
  "confidence": 0.0-1.0,
  "proof_steps": [],               // If proof=true
  "samples": [],
  "execution_time_ms": 0.0
}
```

#### Example: Python
```python
response = requests.post(
    "http://localhost:8000/solve",
    json={
        "question": "2x + 5 = 15",
        "backend": "pat",
        "proof": True
    }
)
```

---

## 🔧 Integration Patterns

### Pattern 1: Simple Q&A Integration

```python
class ModulusClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def solve(self, question: str, context: str = None):
        """Simple solve with automatic retry."""
        response = requests.post(
            f"{self.base_url}/solve_v2",
            json={"question": question, "context": context},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def solve_with_validation(self, question: str):
        """Solve and validate the result."""
        result = self.solve(question)
        
        if not result.get("validation", {}).get("accepted"):
            raise ValueError(f"Invalid problem: {result['validation']['messages']}")
        
        if result["confidence"] < 0.5:
            print("Warning: Low confidence result")
        
        return result["answer"]

# Usage
client = ModulusClient()
answer = client.solve_with_validation("What is the speed of light?")
```

### Pattern 2: Batch Processing

```python
def batch_solve(questions: List[str], max_workers: int = 5):
    """Solve multiple problems in parallel."""
    from concurrent.futures import ThreadPoolExecutor
    
    client = ModulusClient()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(client.solve, q) for q in questions]
        results = [f.result() for f in futures]
    
    return results

# Usage
questions = [
    "Calculate orbital period at 400km",
    "Solve x^2 - 4 = 0",
    "What is the escape velocity?"
]
results = batch_solve(questions)
```

### Pattern 3: Streaming Long-Running Computations

```python
def solve_with_progress(question: str, callback=None):
    """Solve with progress updates."""
    import time
    
    # Start computation
    response = requests.post(
        "http://localhost:8000/solve_v2",
        json={"question": question},
        stream=False  # For now, no streaming
    )
    
    result = response.json()
    
    # Extract trace for progress
    trace = result.get("solution_package", {}).get("trace", {})
    if callback:
        callback(trace)
    
    return result

# Usage
def progress_callback(trace):
    print(f"Stages completed: {len(trace.get('nodes', []))}")

solve_with_progress("Simulate 1000 timesteps", callback=progress_callback)
```

### Pattern 4: Error Handling & Retries

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustModulusClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def solve_with_retry(self, question: str):
        """Solve with automatic retry on failure."""
        try:
            response = requests.post(
                f"{self.base_url}/solve_v2",
                json={"question": question},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Validate result
            if not result.get("answer"):
                raise ValueError("Empty answer received")
            
            return result
            
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            raise
        except ValueError as e:
            print(f"Validation failed: {e}")
            raise

# Usage
client = RobustModulusClient()
result = client.solve_with_retry("Complex physics problem")
```

---

## 🎯 Use Cases

### Use Case 1: Scientific Calculator App

```python
# Mobile app backend
from flask import Flask, request, jsonify

app = Flask(__name__)
modulus = ModulusClient()

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    question = data.get('expression')
    
    try:
        result = modulus.solve(question)
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'trace_id': result['trace_id']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

### Use Case 2: Physics Simulation Engine

```python
class PhysicsSimulator:
    def __init__(self):
        self.client = ModulusClient()
    
    def simulate_orbit(self, altitude_km: float, time_steps: int):
        """Simulate orbital dynamics."""
        question = f"Simulate orbital trajectory at {altitude_km}km altitude for {time_steps} steps"
        
        result = self.client.solve(question)
        
        # Extract trajectory from trace
        trace = result.get("solution_package", {}).get("trace", {})
        return self._parse_trajectory(trace)
    
    def _parse_trajectory(self, trace):
        # Extract position/velocity from trace nodes
        positions = []
        velocities = []
        
        for node in trace.get("nodes", []):
            if node.get("stage") == "solve":
                positions.append(node.get("position"))
                velocities.append(node.get("velocity"))
        
        return {"positions": positions, "velocities": velocities}
```

### Use Case 3: Real-Time Control System (via ROS 2)

```python
# ROS 2 node that uses Modulus for planning
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class ModulusControlNode(Node):
    def __init__(self):
        super().__init__('modulus_control')
        self.client = ModulusClient()
        
        # Subscribe to sensor data
        self.subscription = self.create_subscription(
            Float64MultiArray,
            '/sensor/state',
            self.state_callback,
            10
        )
        
        # Publish control commands
        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/control/command',
            10
        )
    
    def state_callback(self, msg):
        """Process sensor data and compute control."""
        state = msg.data
        
        # Compute optimal control
        question = f"Compute optimal control for state {state}"
        result = self.client.solve(question)
        
        # Publish command
        cmd = Float64MultiArray()
        cmd.data = self._parse_control(result)
        self.publisher.publish(cmd)
```

---

## 🔐 Authentication (Future)

Currently, Modulus API runs locally without authentication. For production deployments:

```python
# Future authentication pattern
headers = {
    "Authorization": f"Bearer {api_key}",
    "X-API-Version": "v2"
}

response = requests.post(
    "https://api.modulus.ai/solve_v2",
    json={"question": "..."},
    headers=headers
)
```

---

## 📊 Rate Limits & Quotas

**Current (Local)**: No limits

**Recommended for Production**:
- **Rate limit**: 100 requests/minute
- **Timeout**: 30 seconds per request
- **Max payload**: 1MB

```python
# Implement client-side rate limiting
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=100, period=60)
def rate_limited_solve(question):
    return modulus_client.solve(question)
```

---

## 🐛 Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process result |
| 400 | Bad Request | Check input format |
| 422 | Validation Error | Fix problem specification |
| 500 | Server Error | Retry with backoff |
| 503 | Service Unavailable | Wait and retry |

### Error Response Format

```json
{
  "detail": "Error description",
  "validation": {
    "accepted": false,
    "messages": ["Specific error messages"]
  }
}
```

### Handling Errors

```python
try:
    result = client.solve(question)
except requests.HTTPError as e:
    if e.response.status_code == 422:
        errors = e.response.json().get("validation", {}).get("messages", [])
        print(f"Validation errors: {errors}")
    elif e.response.status_code == 500:
        print("Server error, retrying...")
        time.sleep(5)
        result = client.solve(question)  # Retry
    else:
        raise
```

---

## 📈 Performance Tips

1. **Batch Similar Requests**: Group similar problems together
2. **Cache Results**: Use trace_id to avoid duplicate computations
3. **Parallel Processing**: Use ThreadPoolExecutor for multiple requests
4. **Timeouts**: Set appropriate timeouts (30s recommended)
5. **Connection Pooling**: Reuse HTTP connections

```python
# Use session for connection pooling
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=100
)
session.mount('http://', adapter)

# All requests use the same session
response = session.post(url, json=data)
```

---

## 🧪 Testing Your Integration

```python
import unittest

class TestModulusIntegration(unittest.TestCase):
    def setUp(self):
        self.client = ModulusClient()
    
    def test_simple_solve(self):
        result = self.client.solve("2 + 2")
        self.assertIsNotNone(result["answer"])
    
    def test_validation_error(self):
        with self.assertRaises(ValueError):
            self.client.solve_with_validation("invalid problem")
    
    def test_batch_processing(self):
        questions = ["x + 1 = 2", "y^2 = 9", "z = 5"]
        results = batch_solve(questions)
        self.assertEqual(len(results), 3)

if __name__ == '__main__':
    unittest.main()
```

---

## 📚 Additional Resources

- **API Docs**: http://localhost:8000/docs
- **Examples**: `/examples/` directory
- **Architecture**: `MODULUS_COMPLETE.md`
- **Production Status**: `PRODUCTION_STATUS.md`

---

## 💡 Best Practices

1. **Always validate** problem specifications before solving
2. **Check confidence** scores in responses
3. **Store trace_id** for debugging and reproducibility
4. **Implement retry logic** with exponential backoff
5. **Monitor performance** using trace data
6. **Cache results** when appropriate
7. **Use batch processing** for multiple problems
8. **Handle errors gracefully** with user-friendly messages

---

## 🆘 Support

**Issues**: Check `/tmp/modulus_api.log` for server logs  
**Documentation**: http://localhost:8000/docs  
**Examples**: Run `./scripts/run_all_tests.sh` to verify setup  

---

**Ready to integrate Modulus into your application!** 🚀


