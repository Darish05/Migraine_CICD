# 🎨 Streamlit UI for Migraine Prediction System

## Overview
A user-friendly web interface for the Migraine Prediction ML system built with Streamlit.

## Features
- 🔮 **Interactive Prediction Form** - Easy-to-use interface for entering patient data
- 📊 **Visual Results** - Gauge charts and graphs for prediction visualization
- 💡 **Smart Recommendations** - Personalized health advice based on risk factors
- 📥 **Export Reports** - Download prediction results in JSON format
- 📈 **Model Information** - View performance metrics of ML models
- ✅ **Real-time Health Check** - Monitor API and model status

## Quick Start

### Using Docker Compose (Recommended)

1. **Start all services** (API, MLflow, and Streamlit UI):
```bash
sudo docker-compose up -d
```

2. **Access the Streamlit UI**:
   - **UI**: http://localhost:8501
   - **API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs
   - **MLflow**: http://localhost:5000

3. **Stop services**:
```bash
sudo docker-compose down
```

### Using Docker (Streamlit only)

If you want to run only the Streamlit UI:

```bash
# Build the Streamlit image
sudo docker build -f Dockerfile.streamlit -t migraine-streamlit .

# Run the container
sudo docker run -d -p 8501:8501 --name streamlit-ui migraine-streamlit
```

### Local Development

1. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies**:
```bash
pip install -r requirements-streamlit.txt
```

3. **Run Streamlit**:
```bash
streamlit run streamlit_app.py
```

## UI Pages

### 🔮 Prediction Page
- Enter patient demographic information
- Input lifestyle and environmental factors
- Get instant migraine risk predictions
- View severity forecasts
- Receive personalized recommendations

### 📊 Models Info Page
- View top classification models performance
- View top regression models performance
- Check accuracy and metrics

### ℹ️ About Page
- System overview and features
- Technology stack information
- Model types and algorithms used
- Input features explanation

## Screenshots

### Prediction Interface
The prediction page includes:
- Demographics section (Age, Gender)
- Sleep & Lifestyle inputs
- Stress & Habits tracking
- Environmental triggers
- Weather conditions
- Dietary & Physical factors

### Results Display
- **Gauge Charts**: Visual representation of migraine risk probability
- **Severity Meters**: Expected pain severity if migraine occurs
- **Color-coded Alerts**: 
  - 🟢 Green: Low risk (< 33%)
  - 🟡 Yellow: Medium risk (33-66%)
  - 🔴 Red: High risk (> 66%)

## Configuration

### API Endpoint
By default, the UI connects to `http://localhost:8000`. 

To change the API endpoint, modify the `API_URL` variable in `streamlit_app.py`:

```python
API_URL = "http://your-api-endpoint:8000"
```

### Port Configuration
The Streamlit app runs on port `8501` by default. To change it:

**In Docker Compose**:
```yaml
ports:
  - "YOUR_PORT:8501"
```

**In Command Line**:
```bash
streamlit run streamlit_app.py --server.port YOUR_PORT
```

## Troubleshooting

### Cannot connect to API
**Issue**: UI shows "API Offline"

**Solution**:
1. Make sure Docker containers are running:
   ```bash
   sudo docker-compose ps
   ```

2. Check API health:
   ```bash
   curl http://localhost:8000/health
   ```

3. Restart services:
   ```bash
   sudo docker-compose restart
   ```

### Port already in use
**Issue**: Port 8501 is already allocated

**Solution**:
1. Stop the existing container:
   ```bash
   sudo docker stop migraine-streamlit
   ```

2. Or use a different port:
   ```bash
   sudo docker run -d -p 8502:8501 migraine-streamlit
   ```

## Docker Commands

### View logs
```bash
# Streamlit logs
sudo docker logs migraine-streamlit -f

# API logs
sudo docker logs migraine-api -f

# All services
sudo docker-compose logs -f
```

### Rebuild after changes
```bash
# Rebuild only Streamlit
sudo docker-compose build streamlit

# Rebuild and restart
sudo docker-compose up -d --build streamlit
```

### Stop specific service
```bash
sudo docker-compose stop streamlit
```

### Start specific service
```bash
sudo docker-compose start streamlit
```

## Development

### File Structure
```
.
├── streamlit_app.py           # Main Streamlit application
├── Dockerfile.streamlit       # Streamlit Docker configuration
├── requirements-streamlit.txt # UI-specific dependencies
└── docker-compose.yml         # Multi-service orchestration
```

### Adding New Features

1. Edit `streamlit_app.py`
2. Test locally:
   ```bash
   streamlit run streamlit_app.py
   ```
3. Rebuild Docker image:
   ```bash
   sudo docker-compose up -d --build streamlit
   ```

## API Integration

The Streamlit UI makes requests to these API endpoints:

- `GET /health` - Check API health and model status
- `GET /models-info` - Retrieve model performance metrics
- `POST /predict` - Submit prediction request

### Example API Request
```json
{
  "age": 35,
  "gender": 1,
  "sleep_hours": 6.5,
  "stress_level": 8,
  "hydration": 4,
  ...
}
```

## Performance

- **Load Time**: < 2 seconds
- **Prediction Response**: < 1 second
- **Memory Usage**: ~200MB
- **Container Size**: ~1.2GB

## Security Notes

⚠️ **Important**:
- This is a demonstration/educational tool
- Not intended for production medical use
- Always consult healthcare professionals for medical decisions
- Consider adding authentication for production deployments

## Future Enhancements

- [ ] User authentication and session management
- [ ] Historical predictions tracking
- [ ] Batch predictions from CSV upload
- [ ] Advanced visualizations (time series, trends)
- [ ] PDF report generation
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Mobile-responsive improvements

## Support

For issues or questions:
- Create an issue on GitHub
- Check Docker logs for debugging
- Verify all services are running

## License

MIT License - Same as the main project

---

**Made with ❤️ using Streamlit**
