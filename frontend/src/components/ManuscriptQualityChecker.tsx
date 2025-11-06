/**
 * Manuscript Quality Checker Component
 *
 * Pre-submission quality analysis to reduce desk rejections.
 * Checks structure, length, references, readability, and more.
 */
import React, { useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, TrendingUp, FileText, BookOpen, Users, BarChart3 } from 'lucide-react';

interface QualityCheck {
  category: string;
  score: number;
  status: 'pass' | 'warning' | 'fail';
  message: string;
  details?: string;
  recommendation?: string;
}

interface QualityReport {
  overall_score: number;
  ready_for_submission: boolean;
  checks: QualityCheck[];
  critical_issues: string[];
  warnings: string[];
  recommendations: string[];
}

interface ManuscriptQualityCheckerProps {
  title: string;
  abstract: string;
  fullText: string;
  references: string[];
  onCheckComplete?: (report: QualityReport) => void;
}

const ManuscriptQualityChecker: React.FC<ManuscriptQualityCheckerProps> = ({
  title,
  abstract,
  fullText,
  references,
  onCheckComplete,
}) => {
  const [report, setReport] = useState<QualityReport | null>(null);
  const [isChecking, setIsChecking] = useState(false);

  const checkQuality = async () => {
    setIsChecking(true);

    try {
      const response = await fetch('/api/v1/ai/check-quality', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          title,
          abstract,
          full_text: fullText,
          references,
        }),
      });

      const data: QualityReport = await response.json();
      setReport(data);
      onCheckComplete?.(data);
    } catch (error) {
      console.error('Quality check failed:', error);
    } finally {
      setIsChecking(false);
    }
  };

  const getStatusIcon = (status: 'pass' | 'warning' | 'fail') => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'fail':
        return <XCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  const getCategoryIcon = (category: string) => {
    const lower = category.toLowerCase();
    if (lower.includes('structure')) return <FileText className="w-5 h-5" />;
    if (lower.includes('abstract') || lower.includes('title')) return <BookOpen className="w-5 h-5" />;
    if (lower.includes('reference')) return <Users className="w-5 h-5" />;
    if (lower.includes('readability') || lower.includes('language')) return <BarChart3 className="w-5 h-5" />;
    return <TrendingUp className="w-5 h-5" />;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Manuscript Quality Check</h2>
          <p className="text-sm text-gray-600 mt-1">
            AI-powered analysis to ensure your manuscript meets publication standards
          </p>
        </div>
        <button
          onClick={checkQuality}
          disabled={isChecking || !title || !abstract || !fullText}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isChecking ? 'Analyzing...' : 'Check Quality'}
        </button>
      </div>

      {isChecking && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <span className="ml-4 text-gray-600">Analyzing manuscript quality...</span>
        </div>
      )}

      {report && !isChecking && (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className={`p-6 rounded-lg border-2 ${getScoreBackground(report.overall_score)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Overall Quality Score</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {report.ready_for_submission
                    ? '✓ Ready for submission'
                    : '⚠ Needs improvement before submission'}
                </p>
              </div>
              <div className={`text-5xl font-bold ${getScoreColor(report.overall_score)}`}>
                {report.overall_score}
                <span className="text-2xl">/100</span>
              </div>
            </div>

            {report.ready_for_submission ? (
              <div className="mt-4 p-4 bg-green-100 border border-green-200 rounded-lg">
                <p className="text-green-800 font-medium">
                  🎉 Excellent! Your manuscript meets quality standards and is ready for submission.
                </p>
              </div>
            ) : (
              <div className="mt-4 p-4 bg-red-100 border border-red-200 rounded-lg">
                <p className="text-red-800 font-medium">
                  ⚠ Please address the critical issues below before submitting.
                </p>
              </div>
            )}
          </div>

          {/* Critical Issues */}
          {report.critical_issues.length > 0 && (
            <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded">
              <h4 className="font-semibold text-red-900 flex items-center mb-2">
                <XCircle className="w-5 h-5 mr-2" />
                Critical Issues ({report.critical_issues.length})
              </h4>
              <ul className="space-y-2">
                {report.critical_issues.map((issue, idx) => (
                  <li key={idx} className="text-red-800 text-sm">
                    • {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {report.warnings.length > 0 && (
            <div className="p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
              <h4 className="font-semibold text-yellow-900 flex items-center mb-2">
                <AlertCircle className="w-5 h-5 mr-2" />
                Warnings ({report.warnings.length})
              </h4>
              <ul className="space-y-2">
                {report.warnings.map((warning, idx) => (
                  <li key={idx} className="text-yellow-800 text-sm">
                    • {warning}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Detailed Checks */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Analysis</h3>
            <div className="grid gap-4">
              {report.checks.map((check, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <div className="mt-1">{getCategoryIcon(check.category)}</div>
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900">{check.category}</h4>
                          {getStatusIcon(check.status)}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{check.message}</p>
                        {check.details && (
                          <p className="text-sm text-gray-500 mt-2 italic">{check.details}</p>
                        )}
                        {check.recommendation && (
                          <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                            <p className="text-sm text-blue-900">
                              <strong>Recommendation:</strong> {check.recommendation}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className={`ml-4 text-2xl font-bold ${getScoreColor(check.score)}`}>
                      {check.score}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {report.recommendations.length > 0 && (
            <div className="p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
              <h4 className="font-semibold text-blue-900 flex items-center mb-2">
                <TrendingUp className="w-5 h-5 mr-2" />
                Recommendations for Improvement
              </h4>
              <ul className="space-y-2">
                {report.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-blue-800 text-sm">
                    • {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {!report && !isChecking && (
        <div className="text-center py-12 text-gray-500">
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p>Click "Check Quality" to analyze your manuscript</p>
          <p className="text-sm mt-2">Make sure you've filled in the title, abstract, and main text</p>
        </div>
      )}
    </div>
  );
};

export default ManuscriptQualityChecker;
