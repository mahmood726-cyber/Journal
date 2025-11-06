/**
 * SEO Service
 *
 * Comprehensive SEO optimization:
 * - Meta tags generation
 * - Structured data (Schema.org)
 * - Open Graph tags
 * - Twitter Cards
 * - Canonical URLs
 * - XML sitemaps
 * - SEO score calculation
 * - Keyword optimization
 */

export interface SEOMetadata {
  title: string;
  description: string;
  keywords: string[];
  canonicalUrl: string;
  ogType: 'website' | 'article';
  ogImage?: string;
  ogImageAlt?: string;
  twitterCard: 'summary' | 'summary_large_image';
  author?: string;
  publishedDate?: string;
  modifiedDate?: string;
  section?: string;
  tags?: string[];
}

export interface ArticleSEO extends SEOMetadata {
  doi: string;
  journal: string;
  volume?: number;
  issue?: number;
  pages?: string;
  authors: Array<{ name: string; orcid?: string }>;
  citationKeywords: string[];
  abstract: string;
}

export interface SEOScore {
  overall: number; // 0-100
  categories: {
    technical: number;
    content: number;
    userExperience: number;
    mobile: number;
  };
  issues: SEOIssue[];
  recommendations: string[];
}

export interface SEOIssue {
  severity: 'critical' | 'warning' | 'info';
  category: string;
  message: string;
  fix?: string;
}

class SEOService {
  /**
   * Generate complete SEO metadata for article
   */
  generateArticleMetadata(article: {
    id: string;
    title: string;
    abstract: string;
    keywords: string[];
    authors: Array<{ name: string; orcid?: string }>;
    doi: string;
    publishedDate: string;
    modifiedDate?: string;
    section?: string;
    coverImage?: string;
  }): ArticleSEO {
    // Clean and optimize title (max 60 chars)
    const seoTitle = this.optimizeTitle(article.title);

    // Generate meta description (max 160 chars)
    const description = this.generateMetaDescription(article.abstract);

    // Extract keywords
    const keywords = this.extractKeywords(article);

    return {
      title: seoTitle,
      description,
      keywords,
      canonicalUrl: `https://journal.example.com/articles/${article.id}`,
      ogType: 'article',
      ogImage: article.coverImage || `https://journal.example.com/og-image.jpg`,
      ogImageAlt: seoTitle,
      twitterCard: 'summary_large_image',
      author: article.authors[0]?.name,
      publishedDate: article.publishedDate,
      modifiedDate: article.modifiedDate,
      section: article.section,
      tags: article.keywords,
      doi: article.doi,
      journal: 'Journal Name',
      authors: article.authors,
      citationKeywords: keywords,
      abstract: article.abstract,
    };
  }

  /**
   * Generate HTML meta tags
   */
  generateMetaTags(metadata: SEOMetadata): string {
    const tags: string[] = [];

    // Basic meta tags
    tags.push(`<title>${this.escapeHtml(metadata.title)}</title>`);
    tags.push(`<meta name="description" content="${this.escapeHtml(metadata.description)}">`);
    tags.push(`<meta name="keywords" content="${metadata.keywords.join(', ')}">`);
    tags.push(`<link rel="canonical" href="${metadata.canonicalUrl}">`);

    // Open Graph tags
    tags.push(`<meta property="og:title" content="${this.escapeHtml(metadata.title)}">`);
    tags.push(`<meta property="og:description" content="${this.escapeHtml(metadata.description)}">`);
    tags.push(`<meta property="og:type" content="${metadata.ogType}">`);
    tags.push(`<meta property="og:url" content="${metadata.canonicalUrl}">`);
    if (metadata.ogImage) {
      tags.push(`<meta property="og:image" content="${metadata.ogImage}">`);
      tags.push(`<meta property="og:image:alt" content="${this.escapeHtml(metadata.ogImageAlt || metadata.title)}">`);
    }

    // Twitter Card tags
    tags.push(`<meta name="twitter:card" content="${metadata.twitterCard}">`);
    tags.push(`<meta name="twitter:title" content="${this.escapeHtml(metadata.title)}">`);
    tags.push(`<meta name="twitter:description" content="${this.escapeHtml(metadata.description)}">`);
    if (metadata.ogImage) {
      tags.push(`<meta name="twitter:image" content="${metadata.ogImage}">`);
    }

    // Article-specific tags
    if (metadata.ogType === 'article') {
      if (metadata.author) {
        tags.push(`<meta name="author" content="${this.escapeHtml(metadata.author)}">`);
      }
      if (metadata.publishedDate) {
        tags.push(`<meta property="article:published_time" content="${metadata.publishedDate}">`);
      }
      if (metadata.modifiedDate) {
        tags.push(`<meta property="article:modified_time" content="${metadata.modifiedDate}">`);
      }
      if (metadata.section) {
        tags.push(`<meta property="article:section" content="${this.escapeHtml(metadata.section)}">`);
      }
      if (metadata.tags) {
        metadata.tags.forEach((tag) => {
          tags.push(`<meta property="article:tag" content="${this.escapeHtml(tag)}">`);
        });
      }
    }

    return tags.join('\n');
  }

  /**
   * Generate Schema.org JSON-LD structured data
   */
  generateSchemaOrgData(article: ArticleSEO): string {
    const schema = {
      '@context': 'https://schema.org',
      '@type': 'ScholarlyArticle',
      headline: article.title,
      description: article.description,
      abstract: article.abstract,
      identifier: `https://doi.org/${article.doi}`,
      doi: article.doi,
      url: article.canonicalUrl,
      datePublished: article.publishedDate,
      dateModified: article.modifiedDate,
      author: article.authors.map((author) => ({
        '@type': 'Person',
        name: author.name,
        ...(author.orcid && { '@id': `https://orcid.org/${author.orcid}` }),
      })),
      publisher: {
        '@type': 'Organization',
        name: article.journal,
        logo: {
          '@type': 'ImageObject',
          url: 'https://journal.example.com/logo.png',
        },
      },
      isPartOf: {
        '@type': 'PublicationIssue',
        ...(article.issue && { issueNumber: article.issue.toString() }),
        isPartOf: {
          '@type': 'PublicationVolume',
          ...(article.volume && { volumeNumber: article.volume.toString() }),
          isPartOf: {
            '@type': 'Periodical',
            name: article.journal,
            issn: '1234-5678', // Replace with actual ISSN
          },
        },
      },
      ...(article.ogImage && {
        image: article.ogImage,
      }),
      ...(article.keywords.length > 0 && {
        keywords: article.keywords.join(', '),
      }),
      ...(article.pages && {
        pageStart: article.pages.split('-')[0],
        pageEnd: article.pages.split('-')[1] || article.pages.split('-')[0],
      }),
    };

    return `<script type="application/ld+json">\n${JSON.stringify(schema, null, 2)}\n</script>`;
  }

  /**
   * Calculate SEO score for page
   */
  calculateSEOScore(pageData: {
    title: string;
    description: string;
    headings: { h1: number; h2: number; h3: number };
    wordCount: number;
    images: Array<{ hasAlt: boolean; altText?: string }>;
    links: { internal: number; external: number };
    hasCanonical: boolean;
    hasStructuredData: boolean;
    loadTime: number;
    mobileResponsive: boolean;
    httpsEnabled: boolean;
  }): SEOScore {
    const issues: SEOIssue[] = [];
    let technicalScore = 100;
    let contentScore = 100;
    let uxScore = 100;
    let mobileScore = 100;

    // Technical SEO
    if (!pageData.hasCanonical) {
      issues.push({
        severity: 'warning',
        category: 'technical',
        message: 'Missing canonical URL',
        fix: 'Add a canonical link tag to prevent duplicate content issues',
      });
      technicalScore -= 15;
    }

    if (!pageData.hasStructuredData) {
      issues.push({
        severity: 'warning',
        category: 'technical',
        message: 'Missing structured data (Schema.org)',
        fix: 'Add JSON-LD structured data for better search engine understanding',
      });
      technicalScore -= 10;
    }

    if (!pageData.httpsEnabled) {
      issues.push({
        severity: 'critical',
        category: 'technical',
        message: 'Site not using HTTPS',
        fix: 'Enable HTTPS for security and SEO benefits',
      });
      technicalScore -= 25;
    }

    if (pageData.loadTime > 3000) {
      issues.push({
        severity: 'warning',
        category: 'technical',
        message: 'Slow page load time',
        fix: 'Optimize images, minify CSS/JS, use CDN',
      });
      technicalScore -= 15;
    }

    // Content SEO
    if (pageData.title.length < 30 || pageData.title.length > 60) {
      issues.push({
        severity: 'warning',
        category: 'content',
        message: 'Title length not optimal (30-60 chars recommended)',
        fix: `Current length: ${pageData.title.length} characters`,
      });
      contentScore -= 10;
    }

    if (pageData.description.length < 120 || pageData.description.length > 160) {
      issues.push({
        severity: 'warning',
        category: 'content',
        message: 'Meta description length not optimal (120-160 chars)',
        fix: `Current length: ${pageData.description.length} characters`,
      });
      contentScore -= 10;
    }

    if (pageData.headings.h1 === 0) {
      issues.push({
        severity: 'critical',
        category: 'content',
        message: 'Missing H1 heading',
        fix: 'Add exactly one H1 heading that describes the page content',
      });
      contentScore -= 20;
    } else if (pageData.headings.h1 > 1) {
      issues.push({
        severity: 'warning',
        category: 'content',
        message: 'Multiple H1 headings found',
        fix: 'Use only one H1 heading per page',
      });
      contentScore -= 15;
    }

    if (pageData.wordCount < 300) {
      issues.push({
        severity: 'warning',
        category: 'content',
        message: 'Low word count (300+ recommended)',
        fix: `Current word count: ${pageData.wordCount}`,
      });
      contentScore -= 15;
    }

    const imagesWithoutAlt = pageData.images.filter((img) => !img.hasAlt).length;
    if (imagesWithoutAlt > 0) {
      issues.push({
        severity: 'warning',
        category: 'content',
        message: `${imagesWithoutAlt} images missing alt text`,
        fix: 'Add descriptive alt text to all images for accessibility and SEO',
      });
      contentScore -= Math.min(imagesWithoutAlt * 5, 20);
    }

    // User Experience SEO
    if (pageData.links.internal < 3) {
      issues.push({
        severity: 'info',
        category: 'ux',
        message: 'Few internal links',
        fix: 'Add more internal links to improve site navigation',
      });
      uxScore -= 10;
    }

    // Mobile SEO
    if (!pageData.mobileResponsive) {
      issues.push({
        severity: 'critical',
        category: 'mobile',
        message: 'Site not mobile responsive',
        fix: 'Implement responsive design for mobile devices',
      });
      mobileScore -= 40;
    }

    const overall =
      technicalScore * 0.3 +
      contentScore * 0.3 +
      uxScore * 0.2 +
      mobileScore * 0.2;

    // Generate recommendations
    const recommendations: string[] = [];
    if (overall >= 90) {
      recommendations.push('Excellent SEO! Keep monitoring and maintaining your current practices.');
    } else if (overall >= 70) {
      recommendations.push('Good SEO foundation. Focus on addressing warnings to improve further.');
    } else {
      recommendations.push('Significant SEO improvements needed. Prioritize critical issues first.');
    }

    return {
      overall: Math.max(0, Math.round(overall)),
      categories: {
        technical: Math.max(0, Math.round(technicalScore)),
        content: Math.max(0, Math.round(contentScore)),
        userExperience: Math.max(0, Math.round(uxScore)),
        mobile: Math.max(0, Math.round(mobileScore)),
      },
      issues,
      recommendations,
    };
  }

  /**
   * Generate XML sitemap
   */
  generateSitemap(pages: Array<{
    url: string;
    lastModified: Date;
    priority: number;
    changeFrequency: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  }>): string {
    const xml: string[] = [];
    xml.push('<?xml version="1.0" encoding="UTF-8"?>');
    xml.push('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">');

    pages.forEach((page) => {
      xml.push('  <url>');
      xml.push(`    <loc>${this.escapeXml(page.url)}</loc>`);
      xml.push(`    <lastmod>${page.lastModified.toISOString()}</lastmod>`);
      xml.push(`    <changefreq>${page.changeFrequency}</changefreq>`);
      xml.push(`    <priority>${page.priority.toFixed(1)}</priority>`);
      xml.push('  </url>');
    });

    xml.push('</urlset>');
    return xml.join('\n');
  }

  /**
   * Generate robots.txt
   */
  generateRobotsTxt(config: {
    sitemap: string;
    allowedPaths: string[];
    disallowedPaths: string[];
  }): string {
    const lines: string[] = [];
    lines.push('User-agent: *');

    config.allowedPaths.forEach((path) => {
      lines.push(`Allow: ${path}`);
    });

    config.disallowedPaths.forEach((path) => {
      lines.push(`Disallow: ${path}`);
    });

    lines.push('');
    lines.push(`Sitemap: ${config.sitemap}`);

    return lines.join('\n');
  }

  // ==================== Private Methods ====================

  private optimizeTitle(title: string): string {
    // Truncate to 60 chars if needed
    if (title.length <= 60) {
      return title;
    }

    // Try to break at word boundary
    const truncated = title.substring(0, 57);
    const lastSpace = truncated.lastIndexOf(' ');

    if (lastSpace > 40) {
      return truncated.substring(0, lastSpace) + '...';
    }

    return truncated + '...';
  }

  private generateMetaDescription(abstract: string): string {
    // Remove markdown/HTML if present
    let cleaned = abstract.replace(/<[^>]*>/g, '').replace(/[*_]/g, '');

    // Truncate to 160 chars
    if (cleaned.length <= 160) {
      return cleaned;
    }

    // Break at sentence boundary if possible
    const sentences = cleaned.match(/[^.!?]+[.!?]+/g) || [];
    let description = '';

    for (const sentence of sentences) {
      if (description.length + sentence.length <= 157) {
        description += sentence;
      } else {
        break;
      }
    }

    if (description.length === 0) {
      // No sentence boundary found, truncate at word
      const truncated = cleaned.substring(0, 157);
      const lastSpace = truncated.lastIndexOf(' ');
      description = truncated.substring(0, lastSpace) + '...';
    }

    return description.trim();
  }

  private extractKeywords(article: {
    title: string;
    abstract: string;
    keywords: string[];
  }): string[] {
    // Combine explicit keywords with extracted ones
    const keywords = new Set(article.keywords.map((k) => k.toLowerCase()));

    // Extract from title (simple approach)
    const titleWords = article.title
      .toLowerCase()
      .split(/\s+/)
      .filter((word) => word.length > 4 && !this.isCommonWord(word));

    titleWords.forEach((word) => keywords.add(word));

    // Limit to 10 most relevant keywords
    return Array.from(keywords).slice(0, 10);
  }

  private isCommonWord(word: string): boolean {
    const commonWords = new Set([
      'about', 'above', 'after', 'again', 'against', 'analysis', 'approach',
      'based', 'between', 'could', 'during', 'first', 'however', 'method',
      'other', 'results', 'should', 'study', 'system', 'their', 'there',
      'these', 'using', 'which', 'would',
    ]);
    return commonWords.has(word.toLowerCase());
  }

  private escapeHtml(text: string): string {
    const map: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
  }

  private escapeXml(text: string): string {
    return this.escapeHtml(text);
  }
}

// Singleton instance
export const seoService = new SEOService();

// React Hook
export function useSEO(metadata: SEOMetadata) {
  React.useEffect(() => {
    // Update document title
    document.title = metadata.title;

    // Update meta tags
    updateMetaTag('description', metadata.description);
    updateMetaTag('keywords', metadata.keywords.join(', '));

    // Update Open Graph tags
    updateMetaTag('og:title', metadata.title, 'property');
    updateMetaTag('og:description', metadata.description, 'property');
    updateMetaTag('og:type', metadata.ogType, 'property');
    updateMetaTag('og:url', metadata.canonicalUrl, 'property');

    if (metadata.ogImage) {
      updateMetaTag('og:image', metadata.ogImage, 'property');
    }

    // Update Twitter Card tags
    updateMetaTag('twitter:card', metadata.twitterCard);
    updateMetaTag('twitter:title', metadata.title);
    updateMetaTag('twitter:description', metadata.description);

    if (metadata.ogImage) {
      updateMetaTag('twitter:image', metadata.ogImage);
    }

    // Update canonical link
    updateCanonicalLink(metadata.canonicalUrl);
  }, [metadata]);
}

function updateMetaTag(name: string, content: string, type: 'name' | 'property' = 'name') {
  let element = document.querySelector(`meta[${type}="${name}"]`);

  if (!element) {
    element = document.createElement('meta');
    element.setAttribute(type, name);
    document.head.appendChild(element);
  }

  element.setAttribute('content', content);
}

function updateCanonicalLink(url: string) {
  let link = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;

  if (!link) {
    link = document.createElement('link');
    link.rel = 'canonical';
    document.head.appendChild(link);
  }

  link.href = url;
}

import React from 'react';
export default seoService;
