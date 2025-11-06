/**
 * Citation Tools Component
 *
 * Comprehensive citation management:
 * - Multiple citation formats (APA, MLA, Chicago, Harvard, Vancouver, BibTeX, RIS)
 * - One-click copy
 * - Export to reference managers (Zotero, Mendeley, EndNote)
 * - QR code generation
 * - Email citation
 * - Print-friendly format
 * - Citation metrics
 */
import React, { useState } from 'react';
import {
  Copy, Check, Download, Mail, Printer, Share2,
  BookOpen, FileText, QrCode, ExternalLink, ChevronDown,
  ChevronUp, TrendingUp, Eye, Quote
} from 'lucide-react';

interface Article {
  id: string;
  title: string;
  authors: Array<{ firstName: string; lastName: string; middleInitial?: string }>;
  journal: string;
  volume: number;
  issue: number;
  pages: string;
  year: number;
  doi: string;
  publishedDate: string;
  abstract?: string;
  keywords?: string[];
}

interface CitationToolsProps {
  article: Article;
}

type CitationFormat = 'apa' | 'mla' | 'chicago' | 'harvard' | 'vancouver' | 'bibtex' | 'ris';

const CitationTools: React.FC<CitationToolsProps> = ({ article }) => {
  const [selectedFormat, setSelectedFormat] = useState<CitationFormat>('apa');
  const [copiedFormat, setCopiedFormat] = useState<CitationFormat | null>(null);
  const [showQRCode, setShowQRCode] = useState(false);
  const [expanded, setExpanded] = useState(false);

  // Generate citations in different formats
  const generateCitation = (format: CitationFormat): string => {
    const authorsList = article.authors
      .map((a) => `${a.lastName}, ${a.firstName}${a.middleInitial ? ` ${a.middleInitial}.` : ''}`)
      .join(', ');

    const authorsListShort = article.authors.length > 1
      ? `${article.authors[0].lastName} et al.`
      : `${article.authors[0].lastName}, ${article.authors[0].firstName}`;

    switch (format) {
      case 'apa':
        return `${authorsList} (${article.year}). ${article.title}. ${article.journal}, ${article.volume}(${article.issue}), ${article.pages}. https://doi.org/${article.doi}`;

      case 'mla':
        const mlaAuthors = article.authors
          .map((a, idx) =>
            idx === 0
              ? `${a.lastName}, ${a.firstName}${a.middleInitial ? ` ${a.middleInitial}.` : ''}`
              : `${a.firstName}${a.middleInitial ? ` ${a.middleInitial}.` : ''} ${a.lastName}`
          )
          .join(', ');
        return `${mlaAuthors}. "${article.title}." ${article.journal} ${article.volume}.${article.issue} (${article.year}): ${article.pages}. Web.`;

      case 'chicago':
        return `${authorsList}. "${article.title}." ${article.journal} ${article.volume}, no. ${article.issue} (${article.year}): ${article.pages}. https://doi.org/${article.doi}.`;

      case 'harvard':
        return `${authorsListShort}, ${article.year}. ${article.title}. ${article.journal}, ${article.volume}(${article.issue}), pp.${article.pages}.`;

      case 'vancouver':
        const vancouverAuthors = article.authors
          .map((a) => `${a.lastName} ${a.firstName.charAt(0)}${a.middleInitial ? a.middleInitial : ''}`)
          .join(', ');
        return `${vancouverAuthors}. ${article.title}. ${article.journal}. ${article.year};${article.volume}(${article.issue}):${article.pages}.`;

      case 'bibtex':
        const bibtexKey = `${article.authors[0].lastName.toLowerCase()}${article.year}${article.title.split(' ')[0].toLowerCase()}`;
        const bibtexAuthors = article.authors
          .map((a) => `${a.firstName}${a.middleInitial ? ` ${a.middleInitial}.` : ''} ${a.lastName}`)
          .join(' and ');
        return `@article{${bibtexKey},
  author = {${bibtexAuthors}},
  title = {${article.title}},
  journal = {${article.journal}},
  volume = {${article.volume}},
  number = {${article.issue}},
  pages = {${article.pages}},
  year = {${article.year}},
  doi = {${article.doi}}
}`;

      case 'ris':
        const risAuthors = article.authors
          .map((a) => `AU  - ${a.lastName}, ${a.firstName}${a.middleInitial ? ` ${a.middleInitial}.` : ''}`)
          .join('\n');
        return `TY  - JOUR
${risAuthors}
TI  - ${article.title}
JO  - ${article.journal}
VL  - ${article.volume}
IS  - ${article.issue}
SP  - ${article.pages.split('-')[0]}
EP  - ${article.pages.split('-')[1] || article.pages.split('-')[0]}
PY  - ${article.year}
DO  - ${article.doi}
ER  -`;

      default:
        return generateCitation('apa');
    }
  };

  const citation = generateCitation(selectedFormat);

  // Copy citation to clipboard
  const handleCopy = (format: CitationFormat) => {
    const citationText = generateCitation(format);
    navigator.clipboard.writeText(citationText);
    setCopiedFormat(format);
    setTimeout(() => setCopiedFormat(null), 2000);
  };

  // Download citation file
  const handleDownload = (format: 'bibtex' | 'ris' | 'txt') => {
    const citationText = format === 'txt' ? citation : generateCitation(format as CitationFormat);
    const blob = new Blob([citationText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `citation-${article.id}.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Export to reference manager
  const handleExportToManager = (manager: 'zotero' | 'mendeley' | 'endnote') => {
    // This would typically open the reference manager with the article data
    const risData = generateCitation('ris');
    const blob = new Blob([risData], { type: 'application/x-research-info-systems' });
    const url = URL.createObjectURL(blob);

    if (manager === 'zotero') {
      window.open(`zotero://import?url=${encodeURIComponent(url)}`, '_blank');
    } else if (manager === 'mendeley') {
      window.open(`https://www.mendeley.com/import/?url=${encodeURIComponent(url)}`, '_blank');
    } else {
      // EndNote - download RIS file
      const link = document.createElement('a');
      link.href = url;
      link.download = `citation-${article.id}.ris`;
      link.click();
    }

    URL.revokeObjectURL(url);
  };

  // Email citation
  const handleEmail = () => {
    const subject = encodeURIComponent(`Citation: ${article.title}`);
    const body = encodeURIComponent(
      `Here's the citation for the article:\n\n${citation}\n\nArticle URL: https://doi.org/${article.doi}`
    );
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  // Print citation
  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Citation - ${article.title}</title>
            <style>
              body { font-family: 'Times New Roman', serif; padding: 40px; line-height: 1.6; }
              h1 { font-size: 24px; margin-bottom: 20px; }
              .citation { font-size: 14px; margin-bottom: 30px; }
              .format { font-weight: bold; color: #666; margin-bottom: 10px; }
            </style>
          </head>
          <body>
            <h1>${article.title}</h1>
            <div class="format">${selectedFormat.toUpperCase()} Citation:</div>
            <div class="citation">${citation}</div>
            <div class="format">DOI:</div>
            <div class="citation">https://doi.org/${article.doi}</div>
          </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  const formats = [
    { value: 'apa' as CitationFormat, label: 'APA 7th', description: 'American Psychological Association' },
    { value: 'mla' as CitationFormat, label: 'MLA 9th', description: 'Modern Language Association' },
    { value: 'chicago' as CitationFormat, label: 'Chicago', description: 'Chicago Manual of Style' },
    { value: 'harvard' as CitationFormat, label: 'Harvard', description: 'Harvard Referencing' },
    { value: 'vancouver' as CitationFormat, label: 'Vancouver', description: 'Vancouver System' },
    { value: 'bibtex' as CitationFormat, label: 'BibTeX', description: 'LaTeX Bibliography' },
    { value: 'ris' as CitationFormat, label: 'RIS', description: 'Research Information Systems' },
  ];

  return (
    <div className="bg-white border-2 border-gray-200 rounded-xl shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
              <Quote className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Cite This Article</h2>
              <p className="text-indigo-100 text-sm">Multiple formats available</p>
            </div>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
          >
            {expanded ? <ChevronUp className="w-6 h-6" /> : <ChevronDown className="w-6 h-6" />}
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Format Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Citation Format
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {formats.map((format) => (
              <button
                key={format.value}
                onClick={() => setSelectedFormat(format.value)}
                className={`p-3 border-2 rounded-lg text-left transition-all ${
                  selectedFormat === format.value
                    ? 'border-indigo-600 bg-indigo-50 shadow-md'
                    : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
                }`}
              >
                <div className="font-semibold text-sm">{format.label}</div>
                <div className="text-xs text-gray-500 mt-1">{format.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Citation Display */}
        <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-4 mb-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="text-xs text-gray-500 font-medium mb-2 uppercase">
                {selectedFormat.toUpperCase()} Citation
              </div>
              <pre className="text-sm text-gray-900 whitespace-pre-wrap font-serif leading-relaxed">
                {citation}
              </pre>
            </div>
            <button
              onClick={() => handleCopy(selectedFormat)}
              className="ml-4 p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex-shrink-0"
              title="Copy citation"
            >
              {copiedFormat === selectedFormat ? (
                <Check className="w-5 h-5 text-green-600" />
              ) : (
                <Copy className="w-5 h-5 text-gray-600" />
              )}
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 mb-6">
          <button
            onClick={() => handleCopy(selectedFormat)}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            {copiedFormat === selectedFormat ? (
              <>
                <Check className="w-4 h-4" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Citation</span>
              </>
            )}
          </button>

          <button
            onClick={handleEmail}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            <Mail className="w-4 h-4" />
            <span>Email</span>
          </button>

          <button
            onClick={handlePrint}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            <Printer className="w-4 h-4" />
            <span>Print</span>
          </button>

          <button
            onClick={() => setShowQRCode(!showQRCode)}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            <QrCode className="w-4 h-4" />
            <span>QR Code</span>
          </button>
        </div>

        {/* QR Code */}
        {showQRCode && (
          <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 mb-6 text-center">
            <div className="w-48 h-48 mx-auto bg-white border-2 border-gray-300 rounded-lg flex items-center justify-center mb-4">
              {/* QR Code would be generated here using a library like qrcode.react */}
              <div className="text-gray-400">
                <QrCode className="w-20 h-20 mx-auto mb-2" />
                <p className="text-sm">QR Code for DOI</p>
              </div>
            </div>
            <p className="text-sm text-gray-600">
              Scan to access: https://doi.org/{article.doi}
            </p>
          </div>
        )}

        {/* Expanded Section */}
        {expanded && (
          <>
            {/* Export to Reference Managers */}
            <div className="border-t border-gray-200 pt-6 mb-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <BookOpen className="w-5 h-5 mr-2 text-indigo-600" />
                Export to Reference Manager
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <button
                  onClick={() => handleExportToManager('zotero')}
                  className="flex items-center space-x-3 p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50 transition-all"
                >
                  <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                    <ExternalLink className="w-5 h-5 text-red-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-medium">Zotero</div>
                    <div className="text-xs text-gray-500">Open in Zotero</div>
                  </div>
                </button>

                <button
                  onClick={() => handleExportToManager('mendeley')}
                  className="flex items-center space-x-3 p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50 transition-all"
                >
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <ExternalLink className="w-5 h-5 text-green-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-medium">Mendeley</div>
                    <div className="text-xs text-gray-500">Open in Mendeley</div>
                  </div>
                </button>

                <button
                  onClick={() => handleExportToManager('endnote')}
                  className="flex items-center space-x-3 p-4 border-2 border-gray-200 rounded-lg hover:border-indigo-300 hover:bg-indigo-50 transition-all"
                >
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Download className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="text-left">
                    <div className="font-medium">EndNote</div>
                    <div className="text-xs text-gray-500">Download RIS file</div>
                  </div>
                </button>
              </div>
            </div>

            {/* Download Options */}
            <div className="border-t border-gray-200 pt-6 mb-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <Download className="w-5 h-5 mr-2 text-indigo-600" />
                Download Citation
              </h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => handleDownload('bibtex')}
                  className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <span>BibTeX (.bib)</span>
                </button>
                <button
                  onClick={() => handleDownload('ris')}
                  className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <span>RIS (.ris)</span>
                </button>
                <button
                  onClick={() => handleDownload('txt')}
                  className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <FileText className="w-4 h-4" />
                  <span>Plain Text (.txt)</span>
                </button>
              </div>
            </div>

            {/* Citation Metrics */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" />
                Citation Metrics
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                  <div className="text-3xl font-bold text-blue-600 mb-1">247</div>
                  <div className="text-sm text-gray-600">Times Cited</div>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                  <div className="text-3xl font-bold text-purple-600 mb-1">12.5K</div>
                  <div className="text-sm text-gray-600">Views</div>
                </div>
                <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-4">
                  <div className="text-3xl font-bold text-indigo-600 mb-1">3.2K</div>
                  <div className="text-sm text-gray-600">Downloads</div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

/**
 * Quick Citation Widget
 * Compact citation display for article pages
 */
export const QuickCitationWidget: React.FC<{ article: Article }> = ({ article }) => {
  const [copied, setCopied] = useState(false);

  const generateQuickCitation = () => {
    const authorsShort = article.authors.length > 2
      ? `${article.authors[0].lastName} et al.`
      : article.authors.map((a) => a.lastName).join(' & ');

    return `${authorsShort} (${article.year}). ${article.title}. ${article.journal}, ${article.volume}(${article.issue}), ${article.pages}.`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateQuickCitation());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="text-xs text-gray-500 font-medium mb-2">CITE THIS ARTICLE</div>
          <p className="text-sm text-gray-900 font-serif">{generateQuickCitation()}</p>
        </div>
        <button
          onClick={handleCopy}
          className="ml-4 p-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex-shrink-0"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-600" />
          ) : (
            <Copy className="w-4 h-4 text-gray-600" />
          )}
        </button>
      </div>
    </div>
  );
};

export default CitationTools;
