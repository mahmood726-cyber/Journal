/**
 * One-Click PDF Submission Component
 *
 * Drag & drop PDF → Auto-extract metadata → Submit
 * Reduces 30-minute 8-step process to 2 minutes.
 */
import React, { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader, ArrowRight } from 'lucide-react';

interface ExtractedMetadata {
  title: string;
  authors: Array<{ name: string; affiliation: string; email?: string; orcid?: string }>;
  abstract: string;
  keywords: string[];
  references: string[];
  email?: string;
  confidence_scores: {
    title: number;
    authors: number;
    abstract: number;
  };
}

interface OneClickSubmissionProps {
  onSubmit?: (data: ExtractedMetadata & { file: File }) => void;
  onCancel?: () => void;
}

const OneClickSubmission: React.FC<OneClickSubmissionProps> = ({ onSubmit, onCancel }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [metadata, setMetadata] = useState<ExtractedMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const extractMetadata = async (pdfFile: File) => {
    setIsExtracting(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', pdfFile);

      const response = await fetch('/api/v1/ai/extract-metadata', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to extract metadata');
      }

      const data: ExtractedMetadata = await response.json();
      setMetadata(data);
    } catch (err) {
      console.error('Metadata extraction failed:', err);
      setError(err instanceof Error ? err.message : 'Extraction failed');
    } finally {
      setIsExtracting(false);
    }
  };

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const droppedFile = e.dataTransfer.files[0];
      if (!droppedFile) return;

      if (droppedFile.type !== 'application/pdf') {
        setError('Please upload a PDF file');
        return;
      }

      setFile(droppedFile);
      await extractMetadata(droppedFile);
    },
    []
  );

  const handleFileInput = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (!selectedFile) return;

      if (selectedFile.type !== 'application/pdf') {
        setError('Please upload a PDF file');
        return;
      }

      setFile(selectedFile);
      await extractMetadata(selectedFile);
    },
    []
  );

  const handleSubmit = () => {
    if (metadata && file) {
      onSubmit?.({ ...metadata, file });
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High confidence';
    if (score >= 0.6) return 'Medium confidence';
    return 'Low confidence';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900">One-Click Submission</h2>
        <p className="text-gray-600 mt-2">
          Upload your PDF and we'll automatically extract all the metadata
        </p>
        <div className="mt-2 flex items-center space-x-2 text-sm text-indigo-600">
          <span>📄 Upload PDF</span>
          <ArrowRight className="w-4 h-4" />
          <span>🤖 AI Extraction</span>
          <ArrowRight className="w-4 h-4" />
          <span>✅ Submit</span>
        </div>
      </div>

      {!file && !isExtracting && !metadata && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-3 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer
            ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400 hover:bg-gray-50'}
          `}
        >
          <Upload className="w-16 h-16 mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">
            Drop your PDF manuscript here
          </h3>
          <p className="text-gray-500 mb-4">or click to browse</p>
          <input
            type="file"
            accept="application/pdf"
            onChange={handleFileInput}
            className="hidden"
            id="pdf-upload"
          />
          <label
            htmlFor="pdf-upload"
            className="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 cursor-pointer transition-colors"
          >
            Choose PDF File
          </label>

          <div className="mt-6 text-sm text-gray-500">
            <p className="font-medium mb-2">✨ What we extract automatically:</p>
            <ul className="space-y-1">
              <li>• Title, authors, and affiliations</li>
              <li>• Abstract and keywords</li>
              <li>• References and citations</li>
              <li>• Email addresses and ORCID IDs</li>
            </ul>
          </div>
        </div>
      )}

      {isExtracting && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader className="w-12 h-12 animate-spin text-indigo-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Extracting metadata...</h3>
          <p className="text-gray-600">Our AI is analyzing your manuscript</p>
          <div className="mt-6 space-y-2 text-sm text-gray-500">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-indigo-600 rounded-full mr-2 animate-pulse"></div>
              Extracting title and authors...
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-indigo-600 rounded-full mr-2 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
              Finding abstract and keywords...
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-indigo-600 rounded-full mr-2 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              Parsing references...
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-red-900">Extraction Error</h4>
            <p className="text-red-800 text-sm mt-1">{error}</p>
            <button
              onClick={() => {
                setFile(null);
                setError(null);
                setMetadata(null);
              }}
              className="mt-3 text-sm text-red-700 hover:text-red-900 underline"
            >
              Try again
            </button>
          </div>
        </div>
      )}

      {metadata && file && !isExtracting && (
        <div className="space-y-6">
          {/* Success Banner */}
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start">
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 mr-3 flex-shrink-0" />
            <div className="flex-1">
              <h4 className="font-semibold text-green-900">Metadata extracted successfully!</h4>
              <p className="text-green-800 text-sm mt-1">
                Review the extracted information below and submit
              </p>
            </div>
          </div>

          {/* Extracted Metadata */}
          <div className="space-y-4">
            {/* Title */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Title</label>
                <span className={`text-xs ${getConfidenceColor(metadata.confidence_scores.title)}`}>
                  {getConfidenceLabel(metadata.confidence_scores.title)}
                </span>
              </div>
              <input
                type="text"
                value={metadata.title}
                onChange={(e) => setMetadata({ ...metadata, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            {/* Authors */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Authors ({metadata.authors.length})</label>
                <span className={`text-xs ${getConfidenceColor(metadata.confidence_scores.authors)}`}>
                  {getConfidenceLabel(metadata.confidence_scores.authors)}
                </span>
              </div>
              <div className="space-y-2">
                {metadata.authors.map((author, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border border-gray-200">
                    <div className="font-medium text-gray-900">{author.name}</div>
                    <div className="text-sm text-gray-600">{author.affiliation}</div>
                    {author.email && <div className="text-sm text-gray-500">{author.email}</div>}
                    {author.orcid && (
                      <div className="text-sm text-indigo-600">ORCID: {author.orcid}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Abstract */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Abstract</label>
                <span className={`text-xs ${getConfidenceColor(metadata.confidence_scores.abstract)}`}>
                  {getConfidenceLabel(metadata.confidence_scores.abstract)}
                </span>
              </div>
              <textarea
                value={metadata.abstract}
                onChange={(e) => setMetadata({ ...metadata, abstract: e.target.value })}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>

            {/* Keywords */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                Keywords ({metadata.keywords.length})
              </label>
              <div className="flex flex-wrap gap-2">
                {metadata.keywords.map((keyword, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>

            {/* References */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                References ({metadata.references.length})
              </label>
              <div className="text-sm text-gray-600">
                {metadata.references.length > 0 ? (
                  `${metadata.references.length} references extracted`
                ) : (
                  'No references found'
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-4 pt-4 border-t">
            <button
              onClick={handleSubmit}
              className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors"
            >
              Submit Manuscript
            </button>
            <button
              onClick={() => {
                setFile(null);
                setMetadata(null);
                setError(null);
                onCancel?.();
              }}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium transition-colors"
            >
              Cancel
            </button>
          </div>

          {/* Time Saved Banner */}
          <div className="p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <div className="flex items-center">
              <FileText className="w-5 h-5 text-indigo-600 mr-3" />
              <div>
                <p className="text-indigo-900 font-medium">
                  ⚡ You just saved ~28 minutes compared to traditional submission!
                </p>
                <p className="text-indigo-700 text-sm mt-1">
                  No more filling out 8 separate forms manually
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OneClickSubmission;
