import React from 'react';
import { Helmet } from 'react-helmet-async';

interface Author {
  firstName: string;
  lastName: string;
  affiliation: string;
  orcid?: string;
  email?: string;
}

interface SEOMetaTagsProps {
  title: string;
  abstract: string;
  authors: Author[];
  keywords?: string[];
  doi?: string;
  publishedAt: string;
  volume?: number;
  issue?: number;
  pages?: string;
  pdfUrl?: string;
  manuscriptId: string;
  journalTitle?: string;
  journalIssn?: string;
  language?: string;
}

const SEOMetaTags: React.FC<SEOMetaTagsProps> = ({
  title,
  abstract,
  authors,
  keywords = [],
  doi,
  publishedAt,
  volume,
  issue,
  pages,
  pdfUrl,
  manuscriptId,
  journalTitle = 'Diamond Open Access Journal',
  journalIssn = '2XXX-XXXX',
  language = 'en',
}) => {
  const currentUrl = typeof window !== 'undefined' ? window.location.href : '';
  const publishDate = new Date(publishedAt).toISOString().split('T')[0]; // YYYY-MM-DD format
  const publishYear = new Date(publishedAt).getFullYear();

  // Parse page numbers
  const [firstPage, lastPage] = pages ? pages.split('-').map(p => p.trim()) : ['', ''];

  // Generate structured data for Schema.org
  const schemaOrgData = {
    '@context': 'https://schema.org',
    '@type': 'ScholarlyArticle',
    headline: title,
    abstract: abstract.substring(0, 250), // Truncate for schema
    author: authors.map(author => ({
      '@type': 'Person',
      name: `${author.firstName} ${author.lastName}`,
      affiliation: author.affiliation ? {
        '@type': 'Organization',
        name: author.affiliation,
      } : undefined,
      sameAs: author.orcid ? `https://orcid.org/${author.orcid}` : undefined,
    })),
    datePublished: publishDate,
    publisher: {
      '@type': 'Organization',
      name: journalTitle,
    },
    isPartOf: {
      '@type': 'PublicationVolume',
      volumeNumber: volume?.toString(),
      isPartOf: {
        '@type': 'PublicationIssue',
        issueNumber: issue?.toString(),
        isPartOf: {
          '@type': 'Periodical',
          name: journalTitle,
          issn: journalIssn,
        },
      },
    },
    keywords: keywords.join(', '),
    url: currentUrl,
    identifier: doi ? `https://doi.org/${doi}` : currentUrl,
    license: 'https://creativecommons.org/licenses/by/4.0/',
    inLanguage: language,
  };

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title} | {journalTitle}</title>
      <meta name="description" content={abstract.substring(0, 160)} />
      <meta name="keywords" content={keywords.join(', ')} />
      <meta name="language" content={language} />

      {/* Google Scholar / Highwire Press Meta Tags */}
      <meta name="citation_title" content={title} />
      {authors.map((author, index) => (
        <meta
          key={`citation_author_${index}`}
          name="citation_author"
          content={`${author.lastName}, ${author.firstName}`}
        />
      ))}
      {authors.map((author, index) =>
        author.affiliation ? (
          <meta
            key={`citation_author_institution_${index}`}
            name="citation_author_institution"
            content={author.affiliation}
          />
        ) : null
      )}
      {authors.map((author, index) =>
        author.email ? (
          <meta
            key={`citation_author_email_${index}`}
            name="citation_author_email"
            content={author.email}
          />
        ) : null
      )}
      {authors.map((author, index) =>
        author.orcid ? (
          <meta
            key={`citation_author_orcid_${index}`}
            name="citation_author_orcid"
            content={author.orcid}
          />
        ) : null
      )}

      <meta name="citation_publication_date" content={publishDate} />
      <meta name="citation_online_date" content={publishDate} />
      <meta name="citation_year" content={publishYear.toString()} />
      <meta name="citation_journal_title" content={journalTitle} />
      <meta name="citation_journal_abbrev" content={journalTitle} />
      {journalIssn && <meta name="citation_issn" content={journalIssn} />}
      {volume && <meta name="citation_volume" content={volume.toString()} />}
      {issue && <meta name="citation_issue" content={issue.toString()} />}
      {firstPage && <meta name="citation_firstpage" content={firstPage} />}
      {lastPage && <meta name="citation_lastpage" content={lastPage} />}
      {doi && <meta name="citation_doi" content={doi} />}
      {pdfUrl && <meta name="citation_pdf_url" content={pdfUrl} />}
      <meta name="citation_abstract_html_url" content={currentUrl} />
      <meta name="citation_fulltext_html_url" content={currentUrl} />
      {keywords.map((keyword, index) => (
        <meta key={`citation_keywords_${index}`} name="citation_keywords" content={keyword} />
      ))}
      <meta name="citation_language" content={language} />

      {/* Dublin Core Meta Tags */}
      <meta name="DC.title" content={title} />
      {authors.map((author, index) => (
        <meta
          key={`dc_creator_${index}`}
          name="DC.creator"
          content={`${author.firstName} ${author.lastName}`}
        />
      ))}
      <meta name="DC.date" content={publishDate} />
      <meta name="DC.identifier" content={doi ? `doi:${doi}` : currentUrl} />
      <meta name="DC.publisher" content={journalTitle} />
      <meta name="DC.description" content={abstract} />
      <meta name="DC.type" content="Text.Serial.Journal" />
      <meta name="DC.format" content="text/html" />
      <meta name="DC.language" content={language} />
      <meta name="DC.rights" content="https://creativecommons.org/licenses/by/4.0/" />
      {keywords.map((keyword, index) => (
        <meta key={`dc_subject_${index}`} name="DC.subject" content={keyword} />
      ))}

      {/* Open Graph Meta Tags */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={abstract.substring(0, 200)} />
      <meta property="og:type" content="article" />
      <meta property="og:url" content={currentUrl} />
      <meta property="article:published_time" content={new Date(publishedAt).toISOString()} />
      {authors.map((author, index) => (
        <meta
          key={`og_author_${index}`}
          property="article:author"
          content={`${author.firstName} ${author.lastName}`}
        />
      ))}
      {keywords.map((keyword, index) => (
        <meta key={`og_tag_${index}`} property="article:tag" content={keyword} />
      ))}

      {/* Twitter Card Meta Tags */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={abstract.substring(0, 200)} />

      {/* Robots Meta Tags */}
      <meta name="robots" content="index, follow" />
      <meta name="googlebot" content="index, follow" />
      <meta name="google" content="nositelinkssearchbox" />

      {/* Schema.org JSON-LD Structured Data */}
      <script type="application/ld+json">{JSON.stringify(schemaOrgData, null, 2)}</script>

      {/* Canonical URL */}
      <link rel="canonical" href={currentUrl} />

      {/* PDF Alternative */}
      {pdfUrl && (
        <>
          <link rel="alternate" type="application/pdf" href={pdfUrl} />
          <link rel="alternate" media="print" href={pdfUrl} />
        </>
      )}
    </Helmet>
  );
};

export default SEOMetaTags;
