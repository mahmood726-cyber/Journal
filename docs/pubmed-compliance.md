# PubMed and MEDLINE Compliance Guide

This document outlines the requirements for PubMed Central (PMC) and MEDLINE indexing compliance.

## Overview

To be indexed in PubMed and MEDLINE, your journal must meet specific scientific, editorial, and technical standards set by the National Library of Medicine (NLM).

## Scientific and Editorial Quality Requirements

### 1. Scope and Content
- **Peer Review**: All research articles must undergo rigorous peer review
- **Scientific Quality**: Articles must meet high standards of scientific merit
- **Biomedical Scope**: Content must be relevant to biomedicine or life sciences
- **Regular Publication**: Maintain a consistent publication schedule

### 2. Editorial Board
- **Qualified Editors**: Editor-in-chief and editorial board must have recognized expertise
- **Geographic Diversity**: International representation on editorial board
- **Clear Responsibilities**: Defined roles for editorial board members
- **Public Listing**: Editorial board must be publicly listed with affiliations

### 3. Editorial Policies
- **Ethics Guidelines**: Clear policies on research ethics, informed consent, and animal welfare
- **Conflict of Interest**: Disclosure requirements for authors, reviewers, and editors
- **Retraction Policy**: Clear procedures for handling corrections and retractions
- **Plagiarism Detection**: Use of plagiarism detection tools
- **Data Sharing**: Policies on data availability and sharing

### 4. Author Guidelines
- **Clear Instructions**: Comprehensive author guidelines
- **Manuscript Format**: Standardized format requirements
- **Authorship Criteria**: Clear definition of authorship (e.g., ICMJE criteria)
- **References**: Standardized citation format (preferably NLM style)

## Technical Requirements

### 1. JATS XML Format
All articles must be submitted to PMC in JATS (Journal Article Tag Suite) XML format:

#### Required JATS Elements:
```xml
<article>
  <front>
    <journal-meta>
      <!-- Journal information -->
      <journal-id journal-id-type="pmc">JournalID</journal-id>
      <journal-title-group>
        <journal-title>Journal Name</journal-title>
      </journal-title-group>
      <issn pub-type="ppub">1234-5678</issn>
      <issn pub-type="epub">8765-4321</issn>
      <publisher>
        <publisher-name>Publisher Name</publisher-name>
      </publisher>
    </journal-meta>

    <article-meta>
      <!-- Article metadata -->
      <article-id pub-id-type="doi">10.xxxx/xxxxx</article-id>
      <title-group>
        <article-title>Article Title</article-title>
      </title-group>
      <contrib-group>
        <!-- Authors with ORCID -->
        <contrib contrib-type="author">
          <name>
            <surname>LastName</surname>
            <given-names>FirstName</given-names>
          </name>
          <contrib-id contrib-id-type="orcid">0000-0000-0000-0000</contrib-id>
          <email>author@email.com</email>
        </contrib>
      </contrib-group>
      <abstract>
        <p>Abstract text</p>
      </abstract>
      <kwd-group>
        <kwd>Keyword1</kwd>
        <kwd>Keyword2</kwd>
      </kwd-group>
    </article-meta>
  </front>

  <body>
    <!-- Article content -->
  </body>

  <back>
    <!-- References -->
    <ref-list>
      <ref id="ref1">
        <element-citation publication-type="journal">
          <!-- Reference details -->
        </element-citation>
      </ref>
    </ref-list>
  </back>
</article>
```

### 2. Metadata Requirements
- **DOI**: Each article must have a unique DOI
- **ISSN**: Journal must have valid ISSN (print and/or electronic)
- **ORCID**: Author ORCID identifiers (highly recommended)
- **Dates**: Submission, acceptance, and publication dates
- **Copyright**: Clear copyright and licensing information
- **Affiliations**: Complete author affiliations with addresses

### 3. File Formats
- **XML**: JATS XML (version 1.2 or later recommended)
- **PDF**: High-quality PDF for archival
- **Figures**: TIFF, EPS, or high-resolution JPEG
- **Tables**: Part of XML or separate files

### 4. Submission to PMC
Articles are submitted via FTP to PMC:

```python
# FTP Submission Details
Host: ftp.ncbi.nlm.nih.gov
Port: 21
Path: /upload/<journal-specific-directory>
```

Files to submit:
- JATS XML file (required)
- PDF file (recommended)
- Figure files (if separate)
- Supplementary materials

## Journal Registration Requirements

### 1. ISSN Registration
- Register with ISSN International Centre
- Obtain separate ISSNs for print and electronic versions if applicable
- ISSN format: XXXX-XXXX

### 2. DOI Registration
Register with a DOI Registration Agency:

#### Option 1: Crossref
- Non-profit DOI registration agency
- Widely used for scholarly publishing
- Provides citation linking services
- Cost: Annual membership + per-article fees

#### Option 2: DataCite
- Focuses on research data and grey literature
- Also accepts journal articles
- Similar cost structure to Crossref

DOI Format: `10.XXXXX/journal.year.article`

Example: `10.12345/myjournal.2024.001`

### 3. PMC Participation
Apply for PMC participation:
- Submit application to PMC
- Provide sample articles
- Demonstrate compliance with PMC standards
- Approval process takes 3-6 months

### 4. MEDLINE Indexing Application
After publishing for at least one year:
- Submit application via NLM online form
- Provide 3-4 consecutive issues
- Demonstrate consistency in quality
- Review process takes 6-12 months

## Licensing Requirements

### Open Access Licenses
For diamond open access, use Creative Commons licenses:

**Recommended: CC BY 4.0**
- Allows reuse with attribution
- Most compatible with open access principles
- Preferred by many funders

**Alternative: CC BY-NC 4.0**
- Non-commercial use only
- More restrictive, but acceptable

### License Statement Required in Each Article:
```
This is an open access article distributed under the terms of the
Creative Commons Attribution License (CC BY 4.0), which permits
unrestricted use, distribution, and reproduction in any medium,
provided the original author and source are credited.
```

## Ethical Standards

### Research Ethics Compliance
- **IRB Approval**: Human subjects research requires IRB approval
- **Animal Welfare**: Animal research must follow ethical guidelines (e.g., ARRIVE)
- **Clinical Trials**: Registration in clinical trials registry (e.g., ClinicalTrials.gov)
- **Informed Consent**: Documentation of informed consent when applicable

### Publication Ethics
Follow guidelines from:
- **ICMJE** (International Committee of Medical Journal Editors)
- **COPE** (Committee on Publication Ethics)
- **Declaration of Helsinki** (for medical research)

Required policies:
- Authorship disputes
- Data fabrication/falsification
- Image manipulation
- Duplicate publication
- Conflicts of interest

## Quality Control Checklist

Before submitting to PMC, verify:

- [ ] JATS XML validates against JATS DTD 1.2+
- [ ] All required metadata elements present
- [ ] DOI assigned and registered
- [ ] ORCID identifiers included for authors
- [ ] Abstracts present and properly formatted
- [ ] Keywords provided (3-10 recommended)
- [ ] References properly formatted with DOIs when available
- [ ] License information included
- [ ] Author affiliations complete
- [ ] Dates (received, accepted, published) included
- [ ] Figures properly referenced and included
- [ ] Supplementary materials properly linked

## Ongoing Compliance

### Regular Requirements
- **Consistent Publishing**: Maintain regular publication schedule
- **Quality Standards**: Uphold scientific and editorial quality
- **Timely Submission**: Submit articles to PMC within 4 months of publication
- **Updates**: Keep journal metadata current
- **Ethics**: Maintain ethical standards

### Monitoring and Reporting
- Track submission status via PMC portal
- Respond to PMC queries promptly
- Address any compliance issues immediately
- Update journal policies as standards evolve

## Resources

### Official Guidelines
- **PMC**: https://www.ncbi.nlm.nih.gov/pmc/
- **PMC Participation**: https://www.ncbi.nlm.nih.gov/pmc/about/submission-methods/
- **MEDLINE Indexing**: https://www.nlm.nih.gov/medline/medline_overview.html
- **JATS Standard**: https://jats.nlm.nih.gov/
- **ICMJE**: http://www.icmje.org/

### Tools and Validators
- **JATS Validator**: https://jats.nlm.nih.gov/publishing/tag-library/
- **PMC Style Checker**: Available through PMC portal
- **ORCID**: https://orcid.org/
- **Crossref**: https://www.crossref.org/
- **DataCite**: https://datacite.org/

### Best Practices
- Join associations (e.g., OASPA for open access publishers)
- Follow COPE guidelines for publication ethics
- Implement plagiarism detection (e.g., iThenticate)
- Use manuscript tracking system
- Maintain transparent editorial process
- Regular backup and archival of content

## Timeline for New Journals

### Year 0 (Setup)
- Register ISSN
- Register with DOI agency
- Set up journal infrastructure
- Develop editorial policies
- Recruit editorial board
- Create author guidelines
- Build website and submission system

### Year 1 (Launch)
- Publish first articles
- Generate JATS XML for all articles
- Apply for PMC participation
- Build consistent publication record
- Maintain quality standards

### Year 2 (Growth)
- Continue regular publishing
- Apply for MEDLINE indexing
- Build citation record
- Expand editorial board
- Increase visibility

### Year 3+ (Established)
- Maintain PMC compliance
- Monitor MEDLINE review
- Track impact metrics
- Continuous improvement

## Support

For questions about PMC submission:
- Email: pubmedcentral@ncbi.nlm.nih.gov

For MEDLINE indexing questions:
- Email: medlars@nlm.nih.gov

This journal management system includes automated tools to ensure ongoing compliance with all these requirements.
