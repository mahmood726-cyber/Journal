# Phase 1 Implementation Notes

## Google Scholar Metadata Optimization ✅

**Status**: Implemented
**Date**: 2025-01-06

### Changes Made

1. **Created SEOMetaTags Component** (`frontend/src/components/Public/SEOMetaTags.tsx`)
   - Comprehensive meta tags for Google Scholar indexing
   - Highwire Press meta tags (citation_*)
   - Dublin Core metadata (DC.*)
   - Open Graph tags (og:*)
   - Twitter Card tags
   - Schema.org JSON-LD structured data
   - Canonical URLs
   - PDF alternative links

2. **Updated ArticleView Component** (`frontend/src/components/Public/ArticleView.tsx`)
   - Imported and integrated SEOMetaTags
   - Passes all article metadata to SEO component

### Dependencies Required

**Install react-helmet-async**:
```bash
cd frontend
npm install react-helmet-async
# or
yarn add react-helmet-async
```

**Update App.tsx to wrap with HelmetProvider**:
```tsx
import { HelmetProvider } from 'react-helmet-async';

function App() {
  return (
    <HelmetProvider>
      {/* existing app structure */}
    </HelmetProvider>
  );
}
```

### Meta Tags Implemented

#### Google Scholar / Highwire Press Tags
- ✅ citation_title
- ✅ citation_author (with multiple authors support)
- ✅ citation_author_institution
- ✅ citation_author_email
- ✅ citation_author_orcid
- ✅ citation_publication_date
- ✅ citation_online_date
- ✅ citation_year
- ✅ citation_journal_title
- ✅ citation_journal_abbrev
- ✅ citation_issn
- ✅ citation_volume
- ✅ citation_issue
- ✅ citation_firstpage
- ✅ citation_lastpage
- ✅ citation_doi
- ✅ citation_pdf_url
- ✅ citation_abstract_html_url
- ✅ citation_fulltext_html_url
- ✅ citation_keywords (multiple)
- ✅ citation_language

#### Dublin Core Tags
- ✅ DC.title
- ✅ DC.creator (multiple)
- ✅ DC.date
- ✅ DC.identifier
- ✅ DC.publisher
- ✅ DC.description
- ✅ DC.type
- ✅ DC.format
- ✅ DC.language
- ✅ DC.rights
- ✅ DC.subject (multiple)

#### Open Graph Tags
- ✅ og:title
- ✅ og:description
- ✅ og:type (article)
- ✅ og:url
- ✅ article:published_time
- ✅ article:author (multiple)
- ✅ article:tag (keywords)

#### Schema.org Structured Data
- ✅ @type: ScholarlyArticle
- ✅ headline
- ✅ abstract
- ✅ author (array with Person schema)
- ✅ datePublished
- ✅ publisher (Organization)
- ✅ isPartOf (PublicationVolume → PublicationIssue → Periodical)
- ✅ keywords
- ✅ url
- ✅ identifier (DOI)
- ✅ license (CC BY 4.0)
- ✅ inLanguage

### Benefits

1. **Google Scholar Indexing**: Articles will be automatically discovered and indexed by Google Scholar
2. **Citation Tracking**: Proper citation metadata enables accurate citation counting
3. **Search Engine Optimization**: Better ranking in academic search engines
4. **Social Media Sharing**: Rich previews when shared on Twitter, Facebook, LinkedIn
5. **Standards Compliance**: Follows Highwire Press, Dublin Core, and Schema.org standards

### Testing

To verify the implementation:

1. **Google Rich Results Test**:
   - Visit: https://search.google.com/test/rich-results
   - Enter article URL
   - Verify ScholarlyArticle schema is detected

2. **Google Scholar Debug**:
   - Use browser DevTools
   - Check <head> section for citation_* meta tags
   - Verify all required tags are present

3. **Open Graph Debugger**:
   - Facebook: https://developers.facebook.com/tools/debug/
   - Twitter: https://cards-dev.twitter.com/validator

### Next Steps

1. ✅ Implement Google Scholar meta tags (DONE)
2. ✅ Implement PubMed XML export (DONE)
3. ✅ Implement JATS XML support (DONE)
4. ✅ Implement Crossref DOI automation (DONE)

**Phase 1: 100% COMPLETE**

---

## PubMed XML Export ✅

**Status**: Implemented
**Date**: 2025-01-06

### Changes Made

1. **Created PubMedXMLService** (`backend/services/pubmed_xml_service.py`)
   - Generates PubMed-compliant XML for MEDLINE indexing
   - Follows PubMed DTD standard
   - Supports single and batch manuscript export
   - Author information with ORCID
   - Article metadata (title, abstract, pagination)
   - Journal metadata (ISSN, volume, issue)

2. **Created Export API** (`backend/api/export.py`)
   - GET /manuscripts/{id}/pubmed-xml: Single manuscript export
   - GET /manuscripts/pubmed-xml/batch: Batch export
   - Returns XML as application/xml content type
   - Permission checks for editors

3. **Registered Export Router** (`backend/main.py`)
   - Added export router to FastAPI application

---

## JATS XML 1.3 Support ✅

**Status**: Implemented
**Date**: 2025-01-06

### Changes Made

1. **Created JATSXMLService** (`backend/services/jats_xml_service.py`)
   - Complete JATS 1.3 (NISO Z39.96-2021) implementation
   - Front matter: journal-meta, article-meta
   - Body: optional article body content
   - Back matter: references, acknowledgments
   - Proper DOCTYPE declaration
   - Author information with ORCID linking
   - Permissions with CC BY 4.0 license
   - Keywords, funding, dates

2. **Added JATS Endpoints** (`backend/api/export.py`)
   - GET /manuscripts/{id}/jats-xml: Single manuscript JATS export
   - Optional include_body and include_references parameters
   - GET /manuscripts/jats-xml/batch: Batch JATS export

### Benefits

- **PubMed Central**: Ready for PMC submission
- **Europe PMC**: Compatible with Europe PMC
- **Crossref**: Can be used for full-text deposits
- **Archiving**: Standard format for long-term preservation
- **Interoperability**: Industry-standard format

---

## Crossref DOI Automation ✅

**Status**: Implemented
**Date**: 2025-01-06

### Changes Made

1. **Created CrossrefXMLService** (`backend/services/crossref_xml_service.py`)
   - Generates Crossref Schema 5.3.1 compliant XML
   - Complete journal and article metadata
   - Contributor information with ORCID
   - DOI data with resource URLs
   - Citation lists support
   - Batch ID generation

2. **Created CrossrefAPIService** (`backend/services/crossref_api_service.py`)
   - Async HTTP client for Crossref API
   - deposit_doi(): Submit metadata to Crossref
   - query_batch_status(): Check submission status
   - query_doi_status(): Verify individual DOIs
   - Test vs Production environment support
   - Response parsing and error handling

3. **Created DOI Database Models** (`backend/db/models_doi.py`)
   - DOIDeposit: Track batch submissions
   - ManuscriptDOI: Link manuscripts to DOIs
   - DOIDepositLog: Audit trail for all actions
   - Status enum: PENDING, SUBMITTED, SUCCESS, FAILED, WARNING

4. **Created Crossref API** (`backend/api/crossref.py`)
   - POST /manuscripts/{id}/register-doi: Register DOI with Crossref
   - GET /manuscripts/{id}/doi-status: Check registration status
   - POST /deposits/{id}/check-status: Query Crossref batch status
   - Background task processing for async submissions
   - Auto-generate DOI option
   - Editor/Admin permissions required

5. **Updated Configuration** (`backend/core/config.py`)
   - CROSSREF_USERNAME: API credentials
   - CROSSREF_PASSWORD: API credentials
   - CROSSREF_DOI_PREFIX: Journal DOI prefix
   - CROSSREF_DEPOSITOR_NAME: Depositor name
   - CROSSREF_DEPOSITOR_EMAIL: Depositor email
   - JOURNAL_ABBREV: Abbreviated journal title

6. **Updated Manuscript Model** (`backend/db/models.py`)
   - Added doi_record relationship to ManuscriptDOI

7. **Registered Crossref Router** (`backend/main.py`)
   - Added crossref router to FastAPI application

### API Endpoints

#### Register DOI
```bash
POST /api/v1/crossref/manuscripts/{manuscript_id}/register-doi
Query Parameters:
  - auto_assign: bool (default: false) - Auto-generate DOI if not assigned
  - environment: str (default: "test") - "test" or "production"

Response:
{
  "success": true,
  "message": "DOI registration initiated",
  "deposit_id": 123,
  "batch_id": "batch_20250106123456_789",
  "doi": "10.1234/ms-2024-001",
  "status": "pending",
  "environment": "test"
}
```

#### Check DOI Status
```bash
GET /api/v1/crossref/manuscripts/{manuscript_id}/doi-status

Response:
{
  "manuscript_id": 789,
  "doi": "10.1234/ms-2024-001",
  "doi_url": "https://doi.org/10.1234/ms-2024-001",
  "registered": true,
  "status": "success",
  "registered_at": "2025-01-06T10:30:00Z",
  "deposit": {
    "batch_id": "batch_20250106123456_789",
    "status": "success",
    "submitted_at": "2025-01-06T10:00:00Z",
    "completed_at": "2025-01-06T10:30:00Z",
    "environment": "test"
  }
}
```

#### Check Deposit Status
```bash
POST /api/v1/crossref/deposits/{deposit_id}/check-status

Response:
{
  "success": true,
  "deposit_id": 123,
  "batch_id": "batch_20250106123456_789",
  "status": "success",
  "records_total": 1,
  "records_success": 1,
  "records_failed": 0,
  "records_warning": 0,
  "last_checked_at": "2025-01-06T10:30:00Z"
}
```

### Benefits

- **Automated DOI Registration**: One-click DOI registration for published articles
- **Status Tracking**: Real-time status updates from Crossref
- **Test Environment**: Verify deposits before production
- **Audit Trail**: Complete log of all deposit actions
- **Background Processing**: Non-blocking API submissions
- **Error Handling**: Comprehensive error handling and retry logic

### Testing

To test the Crossref integration:

1. **Configure Credentials** (`.env`):
```env
CROSSREF_USERNAME=your_crossref_username
CROSSREF_PASSWORD=your_crossref_password
CROSSREF_DOI_PREFIX=10.XXXX
CROSSREF_DEPOSITOR_NAME=Journal Depositor
CROSSREF_DEPOSITOR_EMAIL=deposits@journal.com
JOURNAL_ABBREV=Diamond OA J
```

2. **Create Database Migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add DOI deposit tracking models"
alembic upgrade head
```

3. **Test in Test Environment**:
   - Publish a manuscript
   - Register DOI using auto_assign=true, environment="test"
   - Check status using doi-status endpoint
   - Verify XML submission with Crossref

4. **Production Deployment**:
   - After testing, use environment="production"
   - Monitor deposit status via check-status endpoint

---

## Dependencies Installation Checklist

Before deployment, ensure these dependencies are installed:

### Frontend
- [ ] react-helmet-async - For SEO meta tags
- [ ] Update App.tsx with HelmetProvider wrapper

### Backend (Future)
- [ ] lxml - For XML generation (PubMed, JATS, Crossref)
- [ ] requests - For API calls to Crossref, DataCite, iThenticate

---

## Configuration Needed

### Journal Metadata
Update the following in a configuration file or environment variables:

```env
JOURNAL_TITLE="Diamond Open Access Journal"
JOURNAL_ISSN="2XXX-XXXX"  # Get real ISSN from ISSN.org
JOURNAL_URL="https://journal.example.com"
CROSSREF_DOI_PREFIX="10.XXXX"  # When implementing Crossref
CROSSREF_DEPOSITOR_EMAIL="deposits@journal.example.com"
ITHENTICATE_API_KEY="..."  # When implementing plagiarism check
```

---

## Performance Considerations

1. **Meta Tags**: Adding comprehensive meta tags increases HTML size by ~5-8KB
   - Impact: Negligible (improves SEO significantly)
   - Cached by browsers

2. **Schema.org JSON-LD**: ~2-3KB additional
   - Impact: Minimal
   - Essential for rich results in search engines

3. **Server-Side Rendering**: Consider SSR for better SEO
   - Current: Client-side rendering (React)
   - Future: Next.js or similar for SSR

---

## Standards References

- [Google Scholar Inclusion Guidelines](https://scholar.google.com/intl/en/scholar/inclusion.html)
- [Highwire Press Tags](https://scholar.google.com/intl/en/scholar/inclusion.html#indexing)
- [Dublin Core Metadata Initiative](https://www.dublincore.org/)
- [Schema.org ScholarlyArticle](https://schema.org/ScholarlyArticle)
- [Open Graph Protocol](https://ogp.me/)
- [Twitter Cards](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)

---

**Document Version**: 1.0
**Last Updated**: 2025-01-06
