# Free AI Setup with Ollama

## Why Ollama?

**Cost Comparison:**

| Solution | Setup Cost | Monthly Cost (1000 submissions) | Privacy |
|----------|------------|--------------------------------|---------|
| **OpenAI API** | $0 | $50-200+ | ❌ Data sent to OpenAI |
| **Anthropic Claude** | $0 | $75-250+ | ❌ Data sent to Anthropic |
| **Ollama (Recommended)** | **$0** | **$0** | ✅ All data on your server |

**Ollama Advantages:**
- ✅ **100% Free** - No API costs, no usage limits
- ✅ **Privacy** - All data stays on your server
- ✅ **No internet required** - Works offline
- ✅ **No rate limits** - Process unlimited manuscripts
- ✅ **GDPR compliant** - Data never leaves your infrastructure
- ✅ **Fast** - Local processing, no network latency

**Only Requirement:** Extra RAM (4-8GB recommended)

---

## What AI Features Get Enabled?

### 1. Intelligent Reviewer Matching
**Without AI:** Manual assignment based on keywords
**With Ollama:**
- Semantic understanding of manuscript content
- Matches reviewers based on expertise similarity
- Analyzes abstracts, keywords, and references
- Ranks reviewers by relevance score

**Example:**
```
Manuscript: "Deep Learning for Protein Folding Prediction"
Top Match: Dr. Smith (89% match) - Published 12 papers on ML in biology
```

### 2. Plagiarism Detection
**Without AI:** Basic text matching
**With Ollama:**
- Semantic similarity detection (catches paraphrasing)
- Identifies similar concepts even with different wording
- Cross-references with published literature
- Generates similarity reports

### 3. Abstract Quality Analysis
**Without AI:** Manual review
**With Ollama:**
- Checks structure (background, methods, results, conclusion)
- Identifies missing sections
- Suggests improvements
- Readability scoring

### 4. Manuscript Classification
**Without AI:** Author-selected categories
**With Ollama:**
- Automatic subject classification
- Identifies related disciplines
- Suggests appropriate keywords
- Detects methodology types

### 5. Citation Analysis
**Without AI:** Manual verification
**With Ollama:**
- Checks citation relevance
- Identifies missing key references
- Detects citation biases
- Suggests additional citations

---

## Installation Guide

### Prerequisites

**Server Requirements:**
- Ubuntu 22.04 (or any Linux distro)
- **Minimum:** 8GB RAM total (4GB for Ollama)
- **Recommended:** 16GB RAM (8GB for Ollama)
- **Optional:** GPU with CUDA for faster processing

**For Small Journals (<500 submissions/year):**
- 8GB RAM Digital Ocean Droplet: $48/month
- Can run Ollama + Journal together

**For Large Journals (>1000 submissions/year):**
- 16GB RAM Digital Ocean Droplet: $96/month
- Or separate 8GB droplet for Ollama: $48/month

---

## Step 1: Install Ollama (2 minutes)

### Automatic Installation (Easiest)

SSH into your server:
```bash
ssh root@your-server-ip
```

Install Ollama with one command:
```bash
curl https://ollama.ai/install.sh | sh
```

**That's it!** Ollama is now installed and running.

### Manual Installation (Alternative)

If you prefer manual control:

```bash
# Download Ollama
curl -L https://ollama.ai/download/ollama-linux-amd64 -o /usr/local/bin/ollama

# Make executable
chmod +x /usr/local/bin/ollama

# Create service user
useradd -r -s /bin/false -m -d /usr/share/ollama ollama

# Create systemd service
cat > /etc/systemd/system/ollama.service << 'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

# Start service
systemctl daemon-reload
systemctl enable ollama
systemctl start ollama
```

### Verify Installation

Check Ollama is running:
```bash
systemctl status ollama
```

Should see: **"Active: active (running)"**

---

## Step 2: Download AI Models (5-15 minutes)

### Recommended Models

#### Option A: Small & Fast (4GB RAM)
Perfect for small to medium journals:
```bash
# Download small language model
ollama pull llama2:7b

# Download embedding model (for semantic matching)
ollama pull mxbai-embed-large
```

**Specs:**
- Model size: 3.8GB
- RAM usage: ~4GB
- Speed: ~20 tokens/sec
- Quality: Good for most tasks

#### Option B: Better Quality (8GB RAM)
For larger journals or higher quality:
```bash
# Download medium language model
ollama pull llama2:13b

# Download embedding model
ollama pull mxbai-embed-large
```

**Specs:**
- Model size: 7.3GB
- RAM usage: ~8GB
- Speed: ~10 tokens/sec
- Quality: Excellent

#### Option C: Best Quality (16GB RAM+)
For very large journals or research analysis:
```bash
# Download large language model
ollama pull llama2:70b

# Download embedding model
ollama pull mxbai-embed-large
```

**Specs:**
- Model size: 38GB
- RAM usage: ~16GB
- Speed: ~5 tokens/sec
- Quality: Exceptional

### Specialized Models

For specific use cases:

```bash
# Code analysis (for computer science journals)
ollama pull codellama:13b

# Medical/scientific journals
ollama pull meditron:7b

# Multilingual journals
ollama pull mistral:7b
```

### Download Progress

You'll see download progress:
```
pulling manifest
pulling 8934d96d3f08... 100% ▕████████████████▏ 3.8 GB
pulling 8c17c2ebb0ea... 100% ▕████████████████▏ 7.0 KB
pulling 7c23fb36d801... 100% ▕████████████████▏ 4.8 KB
pulling 2e0493f67d0c... 100% ▕████████████████▏   59 B
pulling fa304d675061... 100% ▕████████████████▏   91 B
pulling 42ba7f8a01dd... 100% ▕████████████████▏  557 B
verifying sha256 digest
writing manifest
success
```

### Verify Models

List installed models:
```bash
ollama list
```

Should show:
```
NAME                    ID              SIZE      MODIFIED
llama2:7b              7896987b      3.8 GB    2 minutes ago
mxbai-embed-large      4f4e2b87      669 MB    1 minute ago
```

---

## Step 3: Configure Journal to Use Ollama (1 minute)

### Update Environment Variables

Edit your journal's `.env` file:
```bash
cd /opt/Journal  # or wherever your journal is installed
nano .env
```

Add these lines (or update if they exist):
```env
# Enable AI Features
AI_ENABLED=true

# Use Ollama (not OpenAI/Anthropic)
AI_PROVIDER=ollama

# Ollama API endpoint (default: localhost)
OLLAMA_API_BASE=http://localhost:11434

# Language model for text generation
OLLAMA_MODEL=llama2:7b

# Embedding model for semantic matching
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large

# Optional: Adjust temperature (0.0 = deterministic, 1.0 = creative)
OLLAMA_TEMPERATURE=0.3

# Optional: Context length (longer = more memory)
OLLAMA_CONTEXT_LENGTH=2048
```

**If Ollama is on a different server:**
```env
# Point to external Ollama server
OLLAMA_API_BASE=http://ollama-server-ip:11434
```

### Restart Journal Services

Apply the configuration:
```bash
# If using Docker
docker-compose -f docker-compose.prod.yml restart backend

# If running directly
systemctl restart journal-backend
```

---

## Step 4: Test AI Features (2 minutes)

### Test from Command Line

Test Ollama is responding:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama2:7b",
  "prompt": "Summarize this abstract: Machine learning has revolutionized protein folding prediction...",
  "stream": false
}'
```

Should return JSON response with generated text.

### Test from Journal

1. **Log in as admin**
2. Navigate to **Settings > AI Configuration**
3. Click **"Test AI Connection"**
4. Should see: ✅ **"Ollama connected successfully"**

### Test Reviewer Matching

1. **Create or select a manuscript**
2. Go to **Assign Reviewers**
3. Click **"AI-Powered Matching"**
4. Should see reviewers ranked by relevance scores

**Example Output:**
```
AI-Powered Reviewer Recommendations:
1. Dr. Jane Smith (92% match)
   - Expertise: Machine Learning, Bioinformatics
   - Recent publications: 15 in related topics
   - Availability: Available

2. Prof. John Doe (87% match)
   - Expertise: Computational Biology, Neural Networks
   - Recent publications: 8 in related topics
   - Availability: Available
```

---

## Performance Optimization

### RAM Usage

Monitor RAM usage:
```bash
# Check overall RAM
free -h

# Check Ollama specifically
systemctl status ollama
```

**If RAM is tight:**
```bash
# Use smaller model
ollama pull llama2:7b

# Or use even smaller
ollama pull tinyllama
```

### Speed Optimization

**Use GPU (if available):**
Ollama automatically uses NVIDIA GPUs:
```bash
# Check GPU is detected
nvidia-smi
```

Ollama will show: **"Using GPU: NVIDIA GeForce RTX 3080"**

**Without GPU:**
- CPU inference is slower but works fine
- Consider upgrading to 13b model only if you have 16GB+ RAM
- 7b model is fast enough for most journals

### Concurrent Requests

Configure how many requests Ollama handles:
```bash
# Edit Ollama service
nano /etc/systemd/system/ollama.service

# Add environment variables
[Service]
Environment="OLLAMA_NUM_PARALLEL=2"  # Number of concurrent requests
Environment="OLLAMA_MAX_LOADED_MODELS=1"  # Keep 1 model in memory

# Restart
systemctl daemon-reload
systemctl restart ollama
```

---

## Advanced Configuration

### Multiple Models

Use different models for different tasks:

```env
# In .env
OLLAMA_MODEL_CLASSIFICATION=llama2:13b  # Better for classification
OLLAMA_MODEL_SUMMARIZATION=llama2:7b    # Fast for summaries
OLLAMA_MODEL_MATCHING=mxbai-embed-large # For semantic matching
```

### Custom System Prompts

Customize AI behavior in admin panel:

**Settings > AI Configuration > System Prompts:**

```
Reviewer Matching Prompt:
"You are an expert in academic peer review. Analyze the manuscript abstract
and reviewer profiles to identify the best matches based on subject expertise,
methodology, and recent publications. Be conservative and only recommend
highly relevant reviewers."

Abstract Analysis Prompt:
"Review this abstract and check for: 1) Clear research question, 2) Methods
described, 3) Results summarized, 4) Conclusions stated. Provide constructive
feedback."
```

### Fine-Tuning for Your Journal

Create custom model for your specific field:

```bash
# Create Modelfile
cat > JournalModelfile << 'EOF'
FROM llama2:7b

# Custom system prompt for your journal
SYSTEM You are an AI assistant for [Your Journal Name], specializing in
[your field]. You understand [specific terminology] and are familiar with
[relevant methodologies].

# Adjust parameters
PARAMETER temperature 0.3
PARAMETER top_p 0.9
EOF

# Create custom model
ollama create my-journal-model -f JournalModelfile

# Use in .env
OLLAMA_MODEL=my-journal-model
```

---

## Monitoring and Maintenance

### Check Ollama Status

```bash
# Service status
systemctl status ollama

# Recent logs
journalctl -u ollama -n 50

# Follow logs in real-time
journalctl -u ollama -f
```

### Monitor Resource Usage

```bash
# Real-time monitoring
htop

# Ollama-specific stats
curl http://localhost:11434/api/ps
```

### Update Ollama

Check for updates monthly:
```bash
# Update Ollama
curl https://ollama.ai/install.sh | sh

# Update models (pulls latest versions)
ollama pull llama2:7b
ollama pull mxbai-embed-large
```

### Backup Models

Models are stored in `/usr/share/ollama/models/`:
```bash
# Backup
tar czf ollama-models-backup.tar.gz /usr/share/ollama/models/

# Restore
tar xzf ollama-models-backup.tar.gz -C /
```

---

## Troubleshooting

### Ollama Service Won't Start

**Check logs:**
```bash
journalctl -u ollama -n 100
```

**Common issues:**

1. **Port 11434 already in use:**
   ```bash
   # Check what's using port
   netstat -tlnp | grep 11434
   # Kill process or change Ollama port
   ```

2. **Out of memory:**
   ```bash
   # Check available RAM
   free -h
   # Use smaller model if needed
   ```

3. **Permission issues:**
   ```bash
   # Fix ownership
   chown -R ollama:ollama /usr/share/ollama
   ```

### Model Download Fails

**Slow/interrupted downloads:**
```bash
# Resume download
ollama pull llama2:7b

# Or download manually
curl -L https://ollama.ai/download/model/llama2:7b -o llama2-7b.bin
```

### Journal Can't Connect to Ollama

**Check connection:**
```bash
# Test API endpoint
curl http://localhost:11434/api/tags

# Should return list of models
```

**If on different servers:**
```bash
# Allow external connections (security risk!)
nano /etc/systemd/system/ollama.service

# Add:
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"

# Better: Use SSH tunnel or VPN
ssh -L 11434:localhost:11434 ollama-server
```

### Slow Performance

**Solutions:**

1. **Use smaller model:**
   ```bash
   ollama pull tinyllama  # Only 1.1GB
   ```

2. **Reduce context length:**
   ```env
   OLLAMA_CONTEXT_LENGTH=1024  # Default: 2048
   ```

3. **Upgrade RAM:**
   - Resize Digital Ocean droplet
   - Or use separate Ollama server

4. **Enable GPU:**
   - Install NVIDIA drivers
   - Ollama automatically uses GPU

### Out of Disk Space

Models can be large:
```bash
# Check disk space
df -h

# Remove unused models
ollama rm unused-model:tag

# Clean up Docker if using
docker system prune -a
```

---

## Security Best Practices

### Firewall Configuration

**If Ollama and Journal on same server:**
```bash
# Ollama should only listen on localhost
# No firewall rules needed
```

**If Ollama on separate server:**
```bash
# On Ollama server, only allow journal server IP
ufw allow from JOURNAL_SERVER_IP to any port 11434

# Or use VPN/SSH tunnel (more secure)
```

### API Authentication (Optional)

Add basic auth to Ollama:
```bash
# Install nginx as reverse proxy
apt-get install -y nginx

# Configure nginx with auth
cat > /etc/nginx/sites-available/ollama << 'EOF'
server {
    listen 11435;
    location / {
        auth_basic "Ollama API";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://localhost:11434;
    }
}
EOF

# Create password
apt-get install -y apache2-utils
htpasswd -c /etc/nginx/.htpasswd journal

# Enable
ln -s /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/
nginx -s reload

# Update journal .env
OLLAMA_API_BASE=http://localhost:11435
OLLAMA_API_USER=journal
OLLAMA_API_PASSWORD=your_password
```

### Model Integrity

Verify model checksums:
```bash
# Ollama verifies SHA256 automatically
# You'll see "verifying sha256 digest" during download
```

---

## Cost Analysis

### Total Cost of Ownership (3 Years)

**OpenAI API:**
- Setup: $0
- Monthly (1000 submissions): $100
- 3-year total: **$3,600**
- Plus: Data privacy concerns

**Ollama on 16GB Droplet:**
- Setup: $0
- Monthly (16GB RAM): $96
- 3-year total: **$3,456**
- Bonus: No API costs, unlimited usage, complete privacy

**Ollama on Separate 8GB Droplet:**
- Setup: $0
- Monthly (8GB RAM): $48
- 3-year total: **$1,728**
- Best value: Half the cost of APIs!

**Savings with Ollama:**
- **$1,872-1,944** saved over 3 years vs APIs
- **Unlimited usage** (APIs charge per request)
- **No rate limits** (APIs have quotas)
- **100% private** (APIs see all your data)

---

## Comparison: Ollama vs Cloud APIs

| Feature | Ollama | OpenAI API | Anthropic Claude |
|---------|--------|-----------|------------------|
| **Cost per 1M tokens** | $0 | $60-120 | $75-225 |
| **Privacy** | 100% private | Sent to OpenAI | Sent to Anthropic |
| **Rate limits** | None | 3,500 req/min | 1,000 req/min |
| **Latency** | ~50-200ms | ~500-2000ms | ~500-2000ms |
| **Offline capability** | Yes | No | No |
| **GDPR compliance** | Automatic | Requires BAA | Requires BAA |
| **Setup time** | 5 minutes | Instant | Instant |
| **Customization** | Full control | Limited | Limited |
| **Maintenance** | Low | None | None |

---

## Recommended Setup by Journal Size

### Small Journal (<500 submissions/year)
**Server:** 8GB RAM Digital Ocean Droplet ($48/month)
**Model:** llama2:7b (4GB)
**Cost:** $576/year
**AI Calls:** Unlimited

### Medium Journal (500-2000 submissions/year)
**Server:** 16GB RAM Droplet ($96/month) or separate 8GB for Ollama
**Model:** llama2:13b (8GB)
**Cost:** $576-1,152/year
**AI Calls:** Unlimited

### Large Journal (>2000 submissions/year)
**Server:** Dedicated 16GB RAM Droplet for Ollama ($96/month)
**Model:** llama2:70b with GPU (if high quality needed)
**Cost:** $1,152/year + GPU server
**AI Calls:** Unlimited

---

## Migration from OpenAI/Anthropic

If currently using OpenAI/Anthropic APIs:

1. **Keep both running temporarily**
2. **Install Ollama** (5 minutes)
3. **Enable feature flag:**
   ```env
   AI_PROVIDER=ollama
   AI_FALLBACK_TO_API=true  # Falls back to API if Ollama fails
   ```
4. **Test for 1 week** with real submissions
5. **Compare quality** (reviewer matches, etc.)
6. **Remove API keys** when satisfied

**Expected differences:**
- **Quality:** Ollama 7b ≈ 90% of GPT-3.5 quality
- **Speed:** Ollama faster (local, no network)
- **Cost:** Ollama = $0 vs $100+/month

---

## Support and Resources

### Official Documentation
- Ollama Docs: https://ollama.ai/docs
- Model Library: https://ollama.ai/library
- GitHub: https://github.com/jmorganca/ollama

### Community
- Ollama Discord: https://discord.gg/ollama
- Reddit: r/LocalLLaMA
- GitHub Issues: Report Ollama bugs

### Professional Support
- Ollama setup assistance: $200 one-time
- Custom model fine-tuning: $500-1000
- Performance optimization: $300

Contact: support@diamondoajournal.org

---

## Conclusion

**Ollama is the clear winner for cost-effective AI features:**

✅ **Free forever** - No per-request costs
✅ **Complete privacy** - GDPR compliant by default
✅ **No rate limits** - Process unlimited manuscripts
✅ **Faster** - Local processing, no network latency
✅ **Offline capable** - Works without internet
✅ **Easy setup** - 5 minutes to fully operational
✅ **Professional quality** - 90%+ accuracy vs paid APIs

**Installation time:** 5 minutes
**Cost:** $0 ongoing (just server RAM)
**ROI:** Saves $1,000-3,000/year vs APIs

Start saving money while improving your journal's capabilities!

---

**Last updated:** 2025-01-06
**Ollama version:** 0.1.x
**Maintained by:** Diamond OA Journal Team
