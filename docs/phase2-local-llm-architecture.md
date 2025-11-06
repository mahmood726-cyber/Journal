# Phase 2: Local LLM Architecture - Llama Integration

**Status**: Planning
**Date**: January 6, 2025
**Architecture**: Local Llama (No Paid APIs)

---

## Overview

Phase 2 will implement **5 advanced features** using a **local Llama installation** instead of paid AI services. This approach provides:

- ✅ **Zero API costs** - No OpenAI, Anthropic, or iThenticate fees
- ✅ **Complete privacy** - All data stays on-premises
- ✅ **Customization** - Fine-tune models for academic publishing
- ✅ **Scalability** - No rate limits or usage caps
- ✅ **Independence** - No dependency on external services

---

## Local LLM Stack

### Option 1: Ollama (Recommended for Development)
**Best for**: Quick setup, Docker deployment, API compatibility

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.1 8B (fast, good quality)
ollama pull llama3.1:8b

# Pull Llama 3.1 70B (slower, best quality)
ollama pull llama3.1:70b

# Pull embedding model
ollama pull nomic-embed-text

# Start server (runs on http://localhost:11434)
ollama serve
```

**Features**:
- OpenAI-compatible API
- Built-in model management
- Automatic GPU acceleration
- Docker support
- REST API

### Option 2: llama.cpp (Lightweight)
**Best for**: Resource-constrained environments, maximum control

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Run server
./server -m models/llama-3.1-8b.gguf --port 8080 --host 0.0.0.0
```

### Option 3: vLLM (Production)
**Best for**: High-throughput production deployments

```bash
pip install vllm

# Start server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --port 8000
```

---

## Architecture Design

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Python)                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │         AI Services Layer                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │  │
│  │  │ Plagiarism  │  │  Reviewer   │  │  Email   │ │  │
│  │  │  Detection  │  │  Matching   │  │Template  │ │  │
│  │  └──────┬──────┘  └──────┬──────┘  └────┬─────┘ │  │
│  └─────────┼────────────────┼──────────────┼───────┘  │
│            └────────────────┼──────────────┘           │
│                             │                           │
│  ┌─────────────────────────▼──────────────────────┐   │
│  │        LLM Service Manager                      │   │
│  │  - Connection pooling                           │   │
│  │  - Request queuing                              │   │
│  │  - Caching                                      │   │
│  │  - Error handling                               │   │
│  └─────────────────────────┬──────────────────────┘   │
└──────────────────────────┬─┴──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│           Local Llama Server (Ollama/llama.cpp)         │
│                                                          │
│  ┌──────────────────┐     ┌──────────────────┐         │
│  │ Llama 3.1 8B/70B │     │ nomic-embed-text │         │
│  │ (Text Generation)│     │   (Embeddings)   │         │
│  └──────────────────┘     └──────────────────┘         │
│                                                          │
│  GPU: CUDA/ROCm/Metal (optional but recommended)        │
└──────────────────────────────────────────────────────────┘
```

---

## Phase 2 Features with Local LLM

### 1. Local LLM-Based Plagiarism Detection ✨

**Replaces**: iThenticate/Turnitin (saves $1-3 per submission)

**Approach**: Semantic similarity detection using embeddings + document fingerprinting

**Implementation**:

```python
# backend/services/plagiarism_service.py

class LocalPlagiarismService:
    """Local LLM-based plagiarism detection."""

    def __init__(self, llm_client: OllamaClient):
        self.llm_client = llm_client
        self.embedding_model = "nomic-embed-text"
        self.similarity_threshold = 0.85

    async def check_plagiarism(
        self,
        manuscript_text: str,
        title: str
    ) -> PlagiarismReport:
        """Check manuscript for potential plagiarism."""

        # 1. Generate embeddings for manuscript sections
        embeddings = await self._generate_embeddings(manuscript_text)

        # 2. Check against internal corpus (previous submissions)
        internal_matches = await self._check_internal_corpus(embeddings)

        # 3. Check against public databases (optional: arXiv, PubMed)
        external_matches = await self._check_external_sources(embeddings)

        # 4. Analyze self-plagiarism (same author previous work)
        self_plagiarism = await self._check_self_plagiarism(embeddings, author_id)

        # 5. Generate detailed report
        return PlagiarismReport(
            overall_similarity=max_similarity,
            matches=internal_matches + external_matches,
            self_plagiarism_detected=self_plagiarism,
            suspicious_sections=suspicious_sections,
            recommendation=self._get_recommendation(max_similarity)
        )

    async def _generate_embeddings(self, text: str) -> List[np.ndarray]:
        """Generate embeddings for text sections."""
        sections = self._split_into_sections(text)
        embeddings = []

        for section in sections:
            response = await self.llm_client.embed(
                model=self.embedding_model,
                text=section
            )
            embeddings.append(np.array(response['embedding']))

        return embeddings

    async def _check_internal_corpus(
        self,
        embeddings: List[np.ndarray]
    ) -> List[Match]:
        """Check against previously submitted manuscripts."""
        matches = []

        # Query vector database (ChromaDB, Qdrant, or PostgreSQL pgvector)
        for embedding in embeddings:
            similar_docs = await self.vector_db.search(
                embedding=embedding,
                threshold=self.similarity_threshold,
                limit=10
            )
            matches.extend(similar_docs)

        return matches

    async def _analyze_with_llm(
        self,
        suspicious_section: str,
        matched_section: str
    ) -> DetailedAnalysis:
        """Use LLM to analyze if match is actual plagiarism."""
        prompt = f"""
        Analyze these two text sections for plagiarism:

        Section A:
        {suspicious_section}

        Section B:
        {matched_section}

        Determine if Section A is plagiarized from Section B.
        Consider:
        - Direct copying
        - Paraphrasing
        - Idea theft
        - Common knowledge vs. plagiarism

        Respond in JSON format:
        {{
            "is_plagiarism": true/false,
            "confidence": 0-1,
            "type": "direct_copy|paraphrase|idea_theft|coincidence",
            "explanation": "brief explanation"
        }}
        """

        response = await self.llm_client.generate(
            model="llama3.1:8b",
            prompt=prompt,
            format="json"
        )

        return DetailedAnalysis(**json.loads(response['response']))
```

**Benefits**:
- **Cost**: $0 vs $1-3 per check
- **Speed**: Near-instant for internal corpus
- **Privacy**: Manuscripts never leave your server
- **Customizable**: Adjust thresholds for your journal

**Vector Database Options**:
1. **ChromaDB** (Recommended) - Python-native, easy setup
2. **Qdrant** - High performance, Docker-ready
3. **PostgreSQL pgvector** - Use existing database

---

### 2. AI-Powered Reviewer Matching 🎯

**Approach**: Semantic matching between manuscript and reviewer expertise

**Implementation**:

```python
# backend/services/reviewer_matching_service.py

class AIReviewerMatchingService:
    """AI-powered reviewer matching using local LLM."""

    async def find_best_reviewers(
        self,
        manuscript: Manuscript,
        num_reviewers: int = 5
    ) -> List[ReviewerMatch]:
        """Find best reviewer matches using semantic similarity."""

        # 1. Generate manuscript embedding
        manuscript_text = f"{manuscript.title}\n\n{manuscript.abstract}"
        manuscript_embedding = await self._get_embedding(manuscript_text)

        # 2. Get reviewer embeddings from database
        reviewers = await self._get_available_reviewers()

        # 3. Calculate semantic similarity
        matches = []
        for reviewer in reviewers:
            # Combine reviewer's expertise keywords, past reviews, publications
            reviewer_text = self._build_reviewer_profile(reviewer)
            reviewer_embedding = await self._get_embedding(reviewer_text)

            similarity = cosine_similarity(
                manuscript_embedding,
                reviewer_embedding
            )

            matches.append(ReviewerMatch(
                reviewer=reviewer,
                similarity_score=similarity,
                match_reasons=[]
            ))

        # 4. Use LLM to explain matches
        top_matches = sorted(matches, key=lambda x: x.similarity_score, reverse=True)[:num_reviewers]

        for match in top_matches:
            match.match_reasons = await self._explain_match(
                manuscript,
                match.reviewer
            )

        return top_matches

    async def _explain_match(
        self,
        manuscript: Manuscript,
        reviewer: User
    ) -> List[str]:
        """Use LLM to explain why reviewer is a good match."""
        prompt = f"""
        Explain why this reviewer is a good match for this manuscript.

        Manuscript:
        Title: {manuscript.title}
        Abstract: {manuscript.abstract[:500]}
        Keywords: {', '.join(manuscript.keywords)}

        Reviewer:
        Name: {reviewer.full_name}
        Expertise: {', '.join(reviewer.specializations)}
        Bio: {reviewer.bio[:300]}

        Provide 3 specific reasons why they match.
        Be concise (one sentence per reason).
        """

        response = await self.llm_client.generate(
            model="llama3.1:8b",
            prompt=prompt
        )

        # Parse reasons from response
        return self._parse_reasons(response['response'])

    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding from local Llama."""
        response = await self.llm_client.embed(
            model="nomic-embed-text",
            text=text
        )
        return np.array(response['embedding'])
```

**Benefits**:
- **Accuracy**: Semantic understanding beyond keyword matching
- **Explainability**: AI explains why each reviewer matches
- **Learning**: Improves over time with feedback
- **Speed**: Near-instant matching for hundreds of reviewers

---

### 3. AI Email Template Generation 📧

**Approach**: Dynamic email generation with local LLM

**Implementation**:

```python
# backend/services/email_template_ai_service.py

class AIEmailTemplateService:
    """AI-powered email template generation using local LLM."""

    async def generate_email(
        self,
        template_type: str,
        context: Dict,
        tone: str = "professional"
    ) -> EmailContent:
        """Generate personalized email using local LLM."""

        prompts = {
            "review_invitation": """
                Generate a professional email inviting a reviewer to review a manuscript.

                Context:
                - Reviewer: {reviewer_name}
                - Manuscript Title: {manuscript_title}
                - Due Date: {due_date}
                - Special note: {special_note}

                Tone: {tone}
                Length: 150-200 words

                Include:
                1. Warm greeting
                2. Manuscript details
                3. Why we chose them
                4. Timeline
                5. Clear accept/decline options
            """,

            "revision_request": """
                Generate an email requesting manuscript revisions.

                Context:
                - Author: {author_name}
                - Manuscript: {manuscript_title}
                - Major concerns: {concerns}
                - Minor concerns: {minor_concerns}
                - Timeline: {timeline}

                Tone: {tone} but encouraging

                Include:
                1. Decision (revisions required)
                2. Summary of reviewer feedback
                3. Clear action items
                4. Timeline for resubmission
                5. Encouraging note
            """,

            "acceptance": """
                Generate an acceptance email for a manuscript.

                Context:
                - Author: {author_name}
                - Manuscript: {manuscript_title}
                - Highlights: {manuscript_highlights}

                Tone: Congratulatory and professional

                Include:
                1. Congratulations
                2. What impressed us
                3. Next steps (copyediting, production)
                4. Publication timeline
            """
        }

        prompt = prompts[template_type].format(**context, tone=tone)

        response = await self.llm_client.generate(
            model="llama3.1:8b",
            prompt=prompt,
            temperature=0.7
        )

        email_body = response['response']
        subject = await self._generate_subject(template_type, context)

        return EmailContent(
            subject=subject,
            body=email_body,
            tone=tone
        )

    async def personalize_template(
        self,
        template: str,
        recipient: User,
        context: Dict
    ) -> str:
        """Personalize template based on recipient profile."""
        prompt = f"""
        Personalize this email template for the recipient.

        Template:
        {template}

        Recipient:
        - Name: {recipient.full_name}
        - Role: {recipient.role}
        - Previous interactions: {context.get('interaction_history', 'None')}

        Make it feel personal but professional.
        """

        response = await self.llm_client.generate(
            model="llama3.1:8b",
            prompt=prompt
        )

        return response['response']
```

**Benefits**:
- **Personalization**: Each email feels handcrafted
- **Consistency**: Maintains journal's voice
- **Multi-language**: Can generate in any language
- **A/B Testing**: Generate variations to test effectiveness

---

### 4. COUNTER Statistics & Article Metrics 📊

**Note**: This feature doesn't require AI, but benefits from AI-powered analytics

**Implementation**:

```python
# backend/services/counter_service.py

class COUNTERStatisticsService:
    """COUNTER R5 compliant article metrics."""

    async def track_event(
        self,
        event_type: str,
        article_id: int,
        user_info: Dict
    ):
        """Track COUNTER-compliant events."""

        # COUNTER R5 metric types
        counter_metrics = {
            "total_item_requests": ["view", "download_pdf", "download_xml"],
            "unique_item_requests": ["unique_view", "unique_download"],
            "total_item_investigations": ["abstract_view", "full_text_view"],
            "unique_item_investigations": ["unique_abstract_view", "unique_full_text_view"]
        }

        # Filter bot traffic (COUNTER requirement)
        if self._is_bot(user_info['user_agent']):
            return

        # Track event
        await self.db.execute(
            """
            INSERT INTO counter_events (
                article_id, event_type, timestamp,
                ip_address, user_agent, country, referrer
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            article_id, event_type, datetime.utcnow(),
            user_info['ip'], user_info['user_agent'],
            user_info.get('country'), user_info.get('referrer')
        )

    async def generate_counter_report(
        self,
        start_date: date,
        end_date: date,
        report_type: str = "TR_J1"  # Journal Requests
    ) -> COUNTERReport:
        """Generate COUNTER R5 compliant report."""

        # Implement COUNTER R5 specifications
        # See: https://www.projectcounter.org/code-of-practice-five-sections/abstract/
        pass
```

**AI Enhancement**: Use local LLM for insights

```python
async def generate_insights(self, article_id: int) -> ArticleInsights:
    """Use AI to analyze article performance and generate insights."""

    stats = await self._get_article_stats(article_id)

    prompt = f"""
    Analyze these article metrics and provide insights:

    Article Statistics:
    - Total views: {stats['views']}
    - Downloads: {stats['downloads']}
    - Geographic distribution: {stats['countries']}
    - Referrers: {stats['top_referrers']}
    - Time trend: {stats['trend_data']}

    Provide:
    1. Performance summary (1 sentence)
    2. Interesting patterns (2-3 observations)
    3. Recommendations to increase visibility
    """

    response = await self.llm_client.generate(
        model="llama3.1:8b",
        prompt=prompt
    )

    return ArticleInsights(insights=response['response'])
```

---

### 5. DataCite DOI Support 🆔

**Note**: Alternative DOI provider (no AI needed)

**Implementation**:

```python
# backend/services/datacite_service.py

class DataCiteService:
    """DataCite DOI registration service."""

    def __init__(self, repository_id: str, password: str, test_mode: bool = True):
        self.repository_id = repository_id
        self.password = password

        if test_mode:
            self.base_url = "https://api.test.datacite.org"
        else:
            self.base_url = "https://api.datacite.org"

    async def register_doi(
        self,
        doi: str,
        manuscript: Manuscript
    ) -> DataCiteResponse:
        """Register DOI with DataCite."""

        metadata = self._generate_datacite_metadata(manuscript)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/dois",
                json=metadata,
                auth=(self.repository_id, self.password)
            )

            response.raise_for_status()
            return DataCiteResponse(**response.json())

    def _generate_datacite_metadata(self, manuscript: Manuscript) -> Dict:
        """Generate DataCite JSON metadata."""
        return {
            "data": {
                "type": "dois",
                "attributes": {
                    "doi": manuscript.doi,
                    "url": f"{settings.JOURNAL_URL}/articles/{manuscript.manuscript_id}",
                    "titles": [{"title": manuscript.title}],
                    "creators": [
                        {
                            "name": f"{author.last_name}, {author.first_name}",
                            "nameType": "Personal",
                            "givenName": author.first_name,
                            "familyName": author.last_name,
                            "nameIdentifiers": [{
                                "nameIdentifier": f"https://orcid.org/{author.orcid}",
                                "nameIdentifierScheme": "ORCID"
                            }] if author.orcid else []
                        }
                        for author in manuscript.authors
                    ],
                    "publicationYear": manuscript.published_at.year,
                    "publisher": settings.JOURNAL_PUBLISHER,
                    "resourceType": "JournalArticle",
                    "subjects": [{"subject": kw} for kw in manuscript.keywords],
                    "descriptions": [{
                        "description": manuscript.abstract,
                        "descriptionType": "Abstract"
                    }],
                    "rightsList": [{
                        "rights": "Creative Commons Attribution 4.0 International",
                        "rightsUri": "https://creativecommons.org/licenses/by/4.0/"
                    }]
                }
            }
        }
```

---

## Infrastructure Requirements

### Hardware Recommendations

#### Development/Testing
- **CPU**: 8+ cores
- **RAM**: 16GB minimum (32GB recommended)
- **GPU**: Optional (CPU inference works)
- **Disk**: 20GB for models

#### Production
- **CPU**: 16+ cores OR
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 3060/4060 or better)
  - Llama 3.1 8B: 8GB VRAM
  - Llama 3.1 70B: 48GB VRAM (or quantized to 24GB)
- **RAM**: 32GB+ (64GB for 70B model)
- **Disk**: 50GB for models and vector database

### Software Stack

```yaml
# docker-compose.yml for local LLM stack

version: '3.8'

services:
  # Ollama LLM Server
  ollama:
    image: ollama/ollama:latest
    container_name: journal-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    command: serve

  # Vector Database (ChromaDB)
  chromadb:
    image: chromadb/chroma:latest
    container_name: journal-chromadb
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]

  # FastAPI Backend (with LLM services)
  backend:
    build: ./backend
    container_name: journal-backend
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_URL=http://ollama:11434
      - CHROMADB_URL=http://chromadb:8000
    depends_on:
      - ollama
      - chromadb

volumes:
  ollama_models:
  chroma_data:
```

---

## Implementation Roadmap

### Week 1-2: LLM Infrastructure
1. ✅ Set up Ollama server
2. ✅ Pull Llama 3.1 models
3. ✅ Set up ChromaDB for embeddings
4. ✅ Create LLM service wrapper
5. ✅ Test inference and embeddings

### Week 3-4: Core AI Features
1. ✅ Implement plagiarism detection service
2. ✅ Implement reviewer matching service
3. ✅ Build vector database for manuscripts
4. ✅ Create plagiarism detection API
5. ✅ Create reviewer matching API

### Week 5: Email & Metrics
1. ✅ Implement AI email template service
2. ✅ Create COUNTER statistics service
3. ✅ Build article metrics dashboard
4. ✅ Add DataCite DOI support

### Week 6: Testing & Optimization
1. ✅ Performance optimization
2. ✅ Caching implementation
3. ✅ Load testing
4. ✅ Documentation

---

## Configuration

```env
# .env

# Local LLM Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Vector Database
CHROMADB_URL=http://localhost:8000
CHROMADB_COLLECTION=manuscripts

# Plagiarism Detection
PLAGIARISM_SIMILARITY_THRESHOLD=0.85
PLAGIARISM_MIN_MATCH_LENGTH=50

# Reviewer Matching
REVIEWER_MATCH_THRESHOLD=0.70
REVIEWER_TOP_K=10

# DataCite
DATACITE_REPOSITORY_ID=your_repo_id
DATACITE_PASSWORD=your_password
DATACITE_DOI_PREFIX=10.XXXX
DATACITE_TEST_MODE=true
```

---

## Cost Analysis

### With Paid APIs (Avoided Costs)
- **iThenticate**: $1-3 per submission
- **OpenAI API**: $0.002-0.02 per 1K tokens
- **Reviewer Matching SaaS**: $500-2000/month

### With Local Llama
- **Initial Setup**: $0 (uses existing hardware)
- **GPU Server** (optional): $500-2000 one-time
- **Electricity**: ~$20-50/month
- **Maintenance**: Minimal

**Savings for 1000 submissions/year**: $5,000 - $10,000+

---

## Next Steps

1. **Install Ollama** and pull Llama 3.1 models
2. **Set up ChromaDB** for vector storage
3. **Implement LLM service wrapper** (backend/services/llm_service.py)
4. **Build plagiarism detection** as first AI feature
5. **Create API endpoints** for AI features

Ready to begin implementation? I'll start with the LLM infrastructure setup! 🚀
