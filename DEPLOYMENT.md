# DeepDoc Deployment Guide

## 🚀 Quick Start

### 1. Environment Setup

First, create your environment configuration:

```bash
# Copy the environment template
cp .env.example .env

# Edit with your actual values
nano .env
```

**Required Environment Variables:**
```bash
GOOGLE_API_KEY=your_actual_google_api_key_here  # ⚠️ CRITICAL: Replace this!
DATABASE_PATH=./database
COLLECTION_NAME=pdf_embeddings
```

### 2. Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p database logs backups

# Set environment variables (or use .env file)
export GOOGLE_API_KEY="your_api_key_here"

# Run the Streamlit app
streamlit run app.py

# OR run the Flask API
python api_enhanced.py
```

### 3. Docker Deployment (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f deepdoc-app

# Stop services
docker-compose down
```

Access the application at `http://localhost:8501`

---

## 🔒 Security Setup

### 1. API Key Security
```bash
# Get your Google API key from Google Cloud Console
# Enable the Generative AI API
# Add it to your .env file
echo "GOOGLE_API_KEY=your_actual_key_here" >> .env
```

### 2. Production Security Checklist
- [ ] Replace default SECRET_KEY
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Enable rate limiting
- [ ] Set up monitoring
- [ ] Configure backup strategy

---

## 🐳 Docker Deployment Options

### Option 1: Simple Docker Run
```bash
# Build the image
docker build -t deepdoc .

# Run with environment file
docker run -p 8501:8501 --env-file .env -v $(pwd)/database:/app/database deepdoc
```

### Option 2: Docker Compose (Full Stack)
```bash
# Start all services (app + redis + backup)
docker-compose up -d

# Scale the application (if needed)
docker-compose up -d --scale deepdoc-app=2
```

### Option 3: Docker Compose (Production)
```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## ☁️ Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)
```bash
# 1. Push to ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
docker build -t deepdoc .
docker tag deepdoc:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/deepdoc:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/deepdoc:latest

# 2. Create ECS task definition and service
# Use the provided task-definition.json
```

#### Using EC2
```bash
# 1. Launch EC2 instance
# 2. Install Docker and Docker Compose
# 3. Clone your repository
# 4. Set up environment variables
# 5. Run docker-compose up -d
```

### Google Cloud Platform

#### Using Cloud Run
```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/your-project-id/deepdoc

# 2. Deploy to Cloud Run
gcloud run deploy deepdoc \
  --image gcr.io/your-project-id/deepdoc \
  --set-env-vars GOOGLE_API_KEY=your_key_here
```

### Azure Deployment

#### Using Container Instances
```bash
# Create resource group
az group create --name deepdoc-rg --location eastus

# Deploy container
az container create \
  --resource-group deepdoc-rg \
  --restart-policy Always
```

---

## 🔧 Configuration Options

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Generative AI API key | - | ✅ |
| `DATABASE_PATH` | ChromaDB storage path | `./database` | |
| `COLLECTION_NAME` | Vector collection name | `pdf_embeddings` | |
| `SIMILARITY_THRESHOLD` | Minimum similarity for retrieval | `0.3` | |
| `MAX_RETRIES` | API retry attempts | `3` | |
| `LOG_LEVEL` | Logging level | `INFO` | |
| `MAX_FILE_SIZE` | Max upload file size (bytes) | `10485760` | |
| `REDIS_HOST` | Redis server host | `localhost` | |
| `SECRET_KEY` | Flask secret key | - | Production |

### Performance Tuning

#### For High Traffic:
```bash
# Increase worker processes
export STREAMLIT_SERVER_MAX_UPLOAD_SIZE=100
export STREAMLIT_SERVER_MAX_MESSAGE_SIZE=100

# Use Redis caching
export REDIS_HOST=your-redis-host
export REDIS_PORT=6379
```

#### For Large Documents:
```bash
# Increase chunk size and overlap
export MAX_CHUNK_SIZE=800
export CHUNK_OVERLAP=100
export MAX_CHUNKS_PER_QUERY=10
```

---

## 📊 Monitoring & Logging

### Application Logs
```bash
# View Docker logs
docker-compose logs -f deepdoc-app

# View application logs in container
docker exec -it deepdoc-app tail -f /app/logs/app.log
```

### Health Monitoring
```bash
# Health check endpoint
curl http://localhost:8501/_stcore/health

# API health check
curl http://localhost:5000/health
```

### Prometheus Metrics (Optional)
Add to `docker-compose.yml`:
```yaml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

---

## 🔄 Backup & Recovery

### Database Backup
```bash
# Manual backup
cp -r ./database ./backups/database_$(date +%Y%m%d_%H%M%S)

# Automated backup (runs in Docker Compose)
docker-compose exec backup ls -la /app/backups
```

### Restore from Backup
```bash
# Stop services
docker-compose down

# Restore database
cp -r ./backups/database_20240315_120000 ./database

# Start services
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Error
```bash
# Check if API key is set
docker-compose exec deepdoc-app env | grep GOOGLE_API_KEY

# Test API key
docker-compose exec deepdoc-app python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
print('API key is working!')
"
```

#### 2. Database Connection Issues
```bash
# Check database directory permissions
ls -la ./database

# Reset database
rm -rf ./database
mkdir ./database
docker-compose restart deepdoc-app
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats deepdoc-app

# Increase Docker memory limit
# Add to docker-compose.yml:
mem_limit: 2g
```

#### 4. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep 8501

# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use different external port
```

### Performance Issues

#### Slow Response Times
1. Enable Redis caching
2. Increase similarity threshold
3. Reduce max chunks per query
4. Use faster embedding models

#### High Memory Usage
1. Reduce batch size for embeddings
2. Implement pagination for large results
3. Use streaming responses for large documents

---

## 📋 Production Checklist

Before deploying to production:

- [ ] **Security**
  - [ ] Change default SECRET_KEY
  - [ ] Set strong GOOGLE_API_KEY
  - [ ] Configure HTTPS/SSL
  - [ ] Set up firewall rules
  - [ ] Enable rate limiting

- [ ] **Performance**
  - [ ] Configure Redis caching
  - [ ] Set appropriate resource limits
  - [ ] Optimize chunk sizes
  - [ ] Set up load balancing

- [ ] **Monitoring**
  - [ ] Set up application logs
  - [ ] Configure health checks
  - [ ] Set up alerts
  - [ ] Monitor resource usage

- [ ] **Backup**
  - [ ] Configure automated backups
  - [ ] Test restore procedures
  - [ ] Set up off-site backup storage

- [ ] **Documentation**
  - [ ] Update environment variables
  - [ ] Document custom configurations
  - [ ] Create runbooks for common issues

---

## 🆘 Support

For additional help:
1. Check the troubleshooting section above
2. Review application logs
3. Create an issue in your project repository
4. Check environment variable configuration

**Useful Commands:**
```bash
# Check system status
docker-compose ps

# View all logs
docker-compose logs

# Restart specific service
docker-compose restart deepdoc-app

# Update and rebuild
docker-compose down
docker-compose up --build -d
```
