/**
 * 3D Cover Flip Display Component
 *
 * Beautiful 3D flip animation for journal issue covers.
 * Hover to see table of contents on the back.
 */
import React, { useState } from 'react';
import { Download, ExternalLink, Calendar, FileText } from 'lucide-react';

interface Article {
  id: number;
  title: string;
  authors: string;
  pages: string;
}

interface Issue {
  id: number;
  volume: number;
  issue: number;
  year: number;
  month: string;
  coverImage: string;
  totalArticles: number;
  articles: Article[];
  pdfUrl?: string;
  publishedDate: string;
}

interface CoverFlipProps {
  issue: Issue;
  size?: 'small' | 'medium' | 'large';
  autoFlip?: boolean;
}

const CoverFlip: React.FC<CoverFlipProps> = ({
  issue,
  size = 'medium',
  autoFlip = false
}) => {
  const [isFlipped, setIsFlipped] = useState(false);

  const sizeClasses = {
    small: 'w-48 h-64',
    medium: 'w-64 h-96',
    large: 'w-80 h-[480px]'
  };

  return (
    <div className="perspective-1000">
      <div
        className={`
          ${sizeClasses[size]}
          relative cursor-pointer transition-transform duration-700 transform-style-3d
          ${isFlipped ? 'rotate-y-180' : ''}
        `}
        onMouseEnter={() => autoFlip && setIsFlipped(true)}
        onMouseLeave={() => autoFlip && setIsFlipped(false)}
        onClick={() => !autoFlip && setIsFlipped(!isFlipped)}
      >
        {/* Front Side - Cover Image */}
        <div className="absolute w-full h-full backface-hidden rounded-lg shadow-2xl overflow-hidden">
          <img
            src={issue.coverImage || '/placeholder-cover.jpg'}
            alt={`Volume ${issue.volume}, Issue ${issue.issue}`}
            className="w-full h-full object-cover"
          />

          {/* Cover Overlay with Issue Info */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-4">
            <div className="text-white">
              <p className="text-sm font-medium opacity-90">
                Volume {issue.volume}, Issue {issue.issue}
              </p>
              <p className="text-xs opacity-75 mt-1">
                {issue.month} {issue.year}
              </p>
              <p className="text-xs opacity-75 mt-1">
                {issue.totalArticles} Articles
              </p>
            </div>
          </div>

          {/* Hover Hint */}
          <div className="absolute top-4 right-4 bg-black/70 text-white text-xs px-3 py-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
            {autoFlip ? 'Hover' : 'Click'} to flip
          </div>
        </div>

        {/* Back Side - Table of Contents */}
        <div className="absolute w-full h-full backface-hidden rotate-y-180 bg-white rounded-lg shadow-2xl overflow-hidden">
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4">
              <h3 className="font-bold text-lg">
                Vol {issue.volume}, Issue {issue.issue}
              </h3>
              <p className="text-sm opacity-90">{issue.month} {issue.year}</p>
            </div>

            {/* Table of Contents */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              <h4 className="font-semibold text-sm text-gray-700 mb-2 flex items-center">
                <FileText className="w-4 h-4 mr-2" />
                Table of Contents
              </h4>

              {issue.articles.map((article, idx) => (
                <div
                  key={article.id}
                  className="text-xs border-b border-gray-200 pb-2 hover:bg-gray-50 p-2 rounded transition-colors cursor-pointer"
                >
                  <p className="font-medium text-gray-900 line-clamp-2">
                    {idx + 1}. {article.title}
                  </p>
                  <p className="text-gray-600 mt-1">{article.authors}</p>
                  <p className="text-gray-500 mt-0.5">Pages {article.pages}</p>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="border-t border-gray-200 p-4 space-y-2">
              <button className="w-full flex items-center justify-center space-x-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium">
                <ExternalLink className="w-4 h-4" />
                <span>View Issue</span>
              </button>

              {issue.pdfUrl && (
                <button className="w-full flex items-center justify-center space-x-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium">
                  <Download className="w-4 h-4" />
                  <span>Download PDF</span>
                </button>
              )}

              <div className="flex items-center justify-center text-xs text-gray-500 mt-2">
                <Calendar className="w-3 h-3 mr-1" />
                Published: {issue.publishedDate}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Issue Grid Display
 * Shows multiple issues with 3D flip
 */
interface IssueGridProps {
  issues: Issue[];
  columns?: 2 | 3 | 4;
}

export const IssueGrid: React.FC<IssueGridProps> = ({
  issues,
  columns = 3
}) => {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  };

  return (
    <div className={`grid ${gridCols[columns]} gap-8`}>
      {issues.map((issue) => (
        <CoverFlip key={issue.id} issue={issue} autoFlip={true} />
      ))}
    </div>
  );
};

/**
 * Featured Issue Display
 * Large 3D flip for current issue on homepage
 */
interface FeaturedIssueProps {
  issue: Issue;
}

export const FeaturedIssue: React.FC<FeaturedIssueProps> = ({ issue }) => {
  return (
    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-8">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Current Issue</h2>
        <p className="text-gray-600 mb-8">
          Volume {issue.volume}, Issue {issue.issue} • {issue.month} {issue.year}
        </p>

        <div className="flex flex-col lg:flex-row items-center lg:items-start gap-8">
          <div className="flex-shrink-0">
            <CoverFlip issue={issue} size="large" />
          </div>

          <div className="flex-1 space-y-6">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                In This Issue
              </h3>

              {/* Featured Articles */}
              <div className="space-y-4">
                {issue.articles.slice(0, 3).map((article, idx) => (
                  <div
                    key={article.id}
                    className="bg-white rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-bold text-sm">
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900 mb-1">
                          {article.title}
                        </h4>
                        <p className="text-sm text-gray-600">{article.authors}</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-xs text-gray-500">
                            Pages {article.pages}
                          </span>
                          <button className="text-xs text-indigo-600 hover:text-indigo-800 font-medium">
                            Read Article →
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {issue.articles.length > 3 && (
                <button className="mt-4 text-indigo-600 hover:text-indigo-800 font-medium text-sm flex items-center">
                  View all {issue.totalArticles} articles
                  <ExternalLink className="w-4 h-4 ml-2" />
                </button>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {issue.totalArticles}
                </div>
                <div className="text-sm text-gray-600">Articles</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {issue.volume}
                </div>
                <div className="text-sm text-gray-600">Volume</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {issue.issue}
                </div>
                <div className="text-sm text-gray-600">Issue</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoverFlip;
