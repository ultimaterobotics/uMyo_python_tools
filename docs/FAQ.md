## 🛠️ Troubleshooting

### Common Issues

#### "No module named 'serial'"
```bash
pip install pyserial
```

#### Device Not Found
1. Check USB cable connection
2. Verify uMyo sensor is powered on
3. Try different USB port
4. Check device manager (Windows) or `lsusb` (Linux)

#### Slow Performance
1. Close other serial applications
2. Use USB 3.0 port if available
3. Increase Python process priority
4. Consider using numpy for better performance