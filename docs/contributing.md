# Contributing Guide

We welcome contributions from researchers, developers, and enthusiasts! This project thrives on community collaboration and innovation.

## 🎯 Ways to Contribute

### 🔧 Code Contributions
- **New Features**: Implement additional signal processing algorithms, visualization modes, or application integrations
- **Performance Optimization**: Improve real-time processing efficiency and reduce latency
- **Platform Support**: Enhance compatibility with different operating systems and hardware configurations
- **Bug Fixes**: Identify and resolve issues in existing codebase
- **Documentation**: Improve code comments, API documentation, and user guides

### 🔬 Research Contributions  
- **Algorithm Development**: Contribute advanced signal processing and machine learning algorithms
- **Validation Studies**: Provide empirical validation of sensor accuracy and system performance
- **Application Examples**: Share novel use cases and domain-specific implementations
- **Benchmarking**: Establish performance baselines and comparison metrics

### 🤝 Community Support
- **Issue Reporting**: Help identify bugs and suggest improvements
- **User Support**: Assist other users with setup and troubleshooting
- **Testing**: Validate new features across different platforms and configurations
- **Feedback**: Provide insights from real-world usage and applications

## 🛠️ Development Environment Setup

### Prerequisites
```bash
# Install core dependencies
pip install -r requirements.txt

```

### Git Workflow
```bash
# 1. Clone the repo
git clone https://github.com/ultimaterobotics/uMyo_python_tools.git
cd uMyo_python_tools

# 2. Create development branch
git checkout -b feature/your-feature-name

# 3. Make your changes
# ... edit files ...

# 5. Commit changes
git add .
git commit -m "feat: add new signal processing algorithm"

# 5. Push and create pull request
git push origin feature/your-feature-name
```

## 📋 Development Guidelines

### Code Style Standards
```python
"""
Follow Google Python Style Guide with project-specific adaptations:
- Line length: 160 characters (configured in setup.cfg)
- Use type hints for all function parameters and return values
- Include comprehensive docstrings for all public functions and classes
- Prefer explicit imports over wildcard imports
- Use meaningful variable names that reflect the domain (EMG, quaternion, etc.)
"""

# Example: Well-documented function
def calculate_emg_rms(signal_data: List[int], window_size: int = 50) -> float:
    """Calculate root mean square (RMS) of EMG signal.
    
    Args:
        signal_data: List of EMG signal samples (16-bit signed integers)
        window_size: Number of samples for RMS calculation window
        
    Returns:
        RMS value of the signal over the specified window
        
    Raises:
        ValueError: If window_size is larger than signal_data length
        
    Example:
        >>> emg_samples = [100, -150, 200, -80, 120]
        >>> rms_value = calculate_emg_rms(emg_samples, window_size=5)
        >>> print(f"RMS: {rms_value:.2f}")
        RMS: 138.74
    """
    if len(signal_data) < window_size:
        raise ValueError(f"Window size {window_size} exceeds data length {len(signal_data)}")
    
    # Use recent window for RMS calculation
    recent_samples = signal_data[-window_size:]
    squared_sum = sum(sample ** 2 for sample in recent_samples)
    return math.sqrt(squared_sum / window_size)
```

### Performance Optimization Guidelines
```python
"""
Real-time EMG processing requires careful performance optimization:
"""

# ✅ Good: Use efficient data structures
from collections import deque
signal_buffer = deque(maxlen=1000)  # Automatic size limiting

# ❌ Avoid: Inefficient list operations
signal_list = []
if len(signal_list) > 1000:
    signal_list = signal_list[-1000:]  # Expensive slice operation

# ✅ Good: Vectorized operations with numpy
import numpy as np
def efficient_filtering(data):
    return np.convolve(data, np.ones(5)/5, mode='valid')  # Moving average

# ❌ Avoid: Python loops for numerical computation
def slow_filtering(data):
    filtered = []
    for i in range(4, len(data)):
        avg = sum(data[i-4:i+1]) / 5
        filtered.append(avg)
    return filtered
```

## 📝 Issue Reporting Template

```markdown
**Bug Report**
- OS: macOS 12.6
- Python: 3.9.7
- uMyo Tools Version: 1.0.0
- Hardware: uMyo sensor v2, USB base station

**Steps to Reproduce:**
1. Run `python umyo_mouse.py`
2. Complete calibration sequence
3. Attempt to move cursor with arm movement
4. Cursor moves erratically

**Expected Behavior:**
Smooth cursor movement proportional to arm orientation

**Actual Behavior:**
Cursor jumps randomly, sometimes moves in wrong direction

**Additional Information:**
- Problem started after OS update
- Works correctly on Windows 10 machine
- Sensor battery level: 3.8V
- RSSI: 45dB

**Logs/Output:**
[Include relevant console output or error messages]
```

## 🌟 Community Guidelines

### Code of Conduct
- **Respectful Communication**: Professional and inclusive interactions
- **Constructive Feedback**: Focus on improvement and learning
- **Knowledge Sharing**: Help others learn and succeed
- **Attribution**: Credit original authors and sources
- **Safety First**: Prioritize user safety and responsible development

### Getting Help
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community help
- **Documentation**: Comprehensive guides and API reference
- **Email Support**: support@ultimaterobotics.com for critical issues

Thank you for contributing to the uMyo Python Tools project! 🎉
