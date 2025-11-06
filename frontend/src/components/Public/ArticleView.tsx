import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  DocumentTextIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  BookmarkIcon,
  DocumentDuplicateIcon,
  UserCircleIcon,
  CalendarIcon,
  TagIcon,
  ArrowTopRightOnSquareIcon,
} from '@heroicons/react/24/outline';
import { api } from '../../services/api';
import SEOMetaTags from './SEOMetaTags';

interface Article {
  manuscriptId: string;
  title: string;
  abstract: string;
  authors: Array<{
    firstName: string;
    lastName: string;
    affiliation: string;
    orcid?: string;
    email?: string;
  }>;
  keywords: string[];
  doi?: string;
  publishedAt: string;
  volume?: number;
  issue?: number;
  pages?: string;
  pdfUrl?: string;
  citations: number;
  views: number;
  downloads: number;
}

const ArticleView: React.FC = () => {
  const { manuscriptId } = useParams<{ manuscriptId: string }>();

  const { data: article, isLoading } = useQuery<Article>(
    ['article', manuscriptId],
    () => api.get(`/articles/${manuscriptId}`).then((res) => res.data)
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Article not found</h3>
          <p className="mt-1 text-sm text-gray-500">
            The article you're looking for doesn't exist or has been removed.
          </p>
          <div className="mt-6">
            <Link
              to="/"
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Return to Homepage
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const handleCitation = (format: 'apa' | 'mla' | 'chicago' | 'bibtex') => {
    // Generate citation in requested format
    console.log(`Generate ${format} citation`);
  };

  const handleShare = (platform: 'twitter' | 'facebook' | 'linkedin' | 'email') => {
    const url = window.location.href;
    const title = article.title;

    const shareUrls = {
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(
        title
      )}&url=${encodeURIComponent(url)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`,
      email: `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(url)}`,
    };

    window.open(shareUrls[platform], '_blank', 'width=600,height=400');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* SEO Meta Tags for Google Scholar, Dublin Core, Schema.org */}
      <SEOMetaTags
        title={article.title}
        abstract={article.abstract}
        authors={article.authors}
        keywords={article.keywords}
        doi={article.doi}
        publishedAt={article.publishedAt}
        volume={article.volume}
        issue={article.issue}
        pages={article.pages}
        pdfUrl={article.pdfUrl}
        manuscriptId={article.manuscriptId}
      />

      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-800 font-medium">
            ← Back to Journal
          </Link>
        </div>
      </div>

      {/* Article Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Article Type Badge */}
            <div>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                <DocumentTextIcon className="h-4 w-4 mr-1" />
                Research Article
              </span>
            </div>

            {/* Title */}
            <h1 className="text-4xl font-bold text-gray-900 leading-tight">{article.title}</h1>

            {/* Authors */}
            <div className="flex flex-wrap items-center gap-4">
              {article.authors.map((author, index) => (
                <div key={index} className="flex items-center">
                  <UserCircleIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <div>
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-900">
                        {author.firstName} {author.lastName}
                      </span>
                      {author.orcid && (
                        <a
                          href={`https://orcid.org/${author.orcid}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-1"
                          title="ORCID iD"
                        >
                          <ArrowTopRightOnSquareIcon className="h-4 w-4 text-green-600" />
                        </a>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">{author.affiliation}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600 border-t border-b border-gray-200 py-4">
              <div className="flex items-center">
                <CalendarIcon className="h-4 w-4 mr-1" />
                Published: {new Date(article.publishedAt).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </div>
              {article.doi && (
                <div className="flex items-center">
                  <DocumentDuplicateIcon className="h-4 w-4 mr-1" />
                  DOI:{' '}
                  <a
                    href={`https://doi.org/${article.doi}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-1 text-indigo-600 hover:text-indigo-800"
                  >
                    {article.doi}
                  </a>
                </div>
              )}
              {article.volume && (
                <div>
                  Vol. {article.volume}
                  {article.issue && `, Issue ${article.issue}`}
                  {article.pages && `, pp. ${article.pages}`}
                </div>
              )}
            </div>

            {/* License Badge */}
            <div className="bg-green-50 border-l-4 border-green-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-green-700">
                    <strong>Open Access:</strong> This article is freely available under a{' '}
                    <a
                      href="https://creativecommons.org/licenses/by/4.0/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:text-green-900"
                    >
                      Creative Commons CC BY 4.0
                    </a>{' '}
                    license.
                  </p>
                </div>
              </div>
            </div>

            {/* Abstract */}
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Abstract</h2>
              <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                {article.abstract}
              </p>
            </div>

            {/* Keywords */}
            {article.keywords && article.keywords.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <TagIcon className="h-5 w-5 mr-2 text-indigo-600" />
                  Keywords
                </h3>
                <div className="flex flex-wrap gap-2">
                  {article.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 cursor-pointer"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Article Metrics */}
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Article Metrics</h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">{article.views || 0}</p>
                  <p className="text-sm text-gray-600 mt-1">Views</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">{article.downloads || 0}</p>
                  <p className="text-sm text-gray-600 mt-1">Downloads</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-3xl font-bold text-purple-600">{article.citations || 0}</p>
                  <p className="text-sm text-gray-600 mt-1">Citations</p>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Download Section */}
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Download</h3>
              <div className="space-y-3">
                <a
                  href={article.pdfUrl}
                  className="flex items-center justify-center w-full px-4 py-3 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors duration-200 font-medium"
                >
                  <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                  Download PDF
                </a>
                <button className="flex items-center justify-center w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors duration-200">
                  <BookmarkIcon className="h-5 w-5 mr-2" />
                  Save Article
                </button>
              </div>
            </div>

            {/* Share Section */}
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <ShareIcon className="h-5 w-5 mr-2 text-indigo-600" />
                Share
              </h3>
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => handleShare('twitter')}
                  className="px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors duration-200"
                >
                  Twitter
                </button>
                <button
                  onClick={() => handleShare('facebook')}
                  className="px-3 py-2 bg-blue-700 text-white rounded text-sm hover:bg-blue-800 transition-colors duration-200"
                >
                  Facebook
                </button>
                <button
                  onClick={() => handleShare('linkedin')}
                  className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors duration-200"
                >
                  LinkedIn
                </button>
                <button
                  onClick={() => handleShare('email')}
                  className="px-3 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors duration-200"
                >
                  Email
                </button>
              </div>
            </div>

            {/* Citation Section */}
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <DocumentDuplicateIcon className="h-5 w-5 mr-2 text-indigo-600" />
                Cite This Article
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => handleCitation('apa')}
                  className="w-full text-left px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors duration-200"
                >
                  APA Style
                </button>
                <button
                  onClick={() => handleCitation('mla')}
                  className="w-full text-left px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors duration-200"
                >
                  MLA Style
                </button>
                <button
                  onClick={() => handleCitation('chicago')}
                  className="w-full text-left px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors duration-200"
                >
                  Chicago Style
                </button>
                <button
                  onClick={() => handleCitation('bibtex')}
                  className="w-full text-left px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors duration-200"
                >
                  BibTeX
                </button>
              </div>
            </div>

            {/* Related Links */}
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Related Links</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <a
                    href={`/search?keywords=${article.keywords?.[0]}`}
                    className="text-indigo-600 hover:text-indigo-800"
                  >
                    Similar Articles
                  </a>
                </li>
                <li>
                  <a href="/author-guidelines" className="text-indigo-600 hover:text-indigo-800">
                    Submit Your Research
                  </a>
                </li>
                <li>
                  <a href="/contact" className="text-indigo-600 hover:text-indigo-800">
                    Contact Editors
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleView;
