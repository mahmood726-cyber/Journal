import React, { useState } from 'react';
import {
  CheckCircleIcon,
  DocumentTextIcon,
  UserGroupIcon,
  DocumentArrowUpIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

interface ReviewAndSubmitProps {
  data: any;
  updateData: (step: string, data: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const ReviewAndSubmit: React.FC<ReviewAndSubmitProps> = ({ data, onPrev }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [agreedToEthics, setAgreedToEthics] = useState(false);
  const [agreedToOriginality, setAgreedToOriginality] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const navigate = useNavigate();

  const { manuscriptDetails, authors, files } = data;

  const validate = (): boolean => {
    const newErrors: string[] = [];

    if (!agreedToTerms) {
      newErrors.push('You must agree to the submission terms');
    }
    if (!agreedToEthics) {
      newErrors.push('You must confirm ethical compliance');
    }
    if (!agreedToOriginality) {
      newErrors.push('You must confirm originality of work');
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) {
      toast.error('Please complete all required confirmations');
      return;
    }

    setIsSubmitting(true);

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Submit manuscript
      // const response = await api.post('/manuscripts', {
      //   ...manuscriptDetails,
      //   authors,
      //   files
      // });

      toast.success(
        'Manuscript submitted successfully! You will receive a confirmation email shortly.',
        { duration: 5000 }
      );

      // Redirect to dashboard
      setTimeout(() => {
        navigate('/dashboard/manuscripts');
      }, 2000);
    } catch (error) {
      console.error('Submission error:', error);
      toast.error('Failed to submit manuscript. Please try again.');
      setIsSubmitting(false);
    }
  };

  const manuscriptFiles = files?.uploadedFiles?.filter((f: any) => f.type === 'manuscript') || [];
  const figureFiles = files?.uploadedFiles?.filter((f: any) => f.type === 'figure') || [];
  const supplementaryFiles =
    files?.uploadedFiles?.filter((f: any) => f.type === 'supplementary') || [];

  return (
    <div className="space-y-6">
      {/* Instruction Banner */}
      <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200">
        <div className="flex">
          <InformationCircleIcon className="h-5 w-5 text-indigo-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-indigo-900">Review Your Submission</h3>
            <p className="mt-1 text-sm text-indigo-700">
              Please carefully review all information below. You can go back to any step to make
              changes before submitting.
            </p>
          </div>
        </div>
      </div>

      {/* Manuscript Details Section */}
      <div className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <DocumentTextIcon className="h-6 w-6 text-indigo-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Manuscript Details</h3>
          </div>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Title
            </label>
            <p className="mt-1 text-sm text-gray-900">{manuscriptDetails?.title || 'N/A'}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Manuscript Type
              </label>
              <p className="mt-1 text-sm text-gray-900 capitalize">
                {manuscriptDetails?.manuscriptType?.replace('-', ' ') || 'N/A'}
              </p>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Subject Area
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {manuscriptDetails?.subjectArea || 'N/A'}
              </p>
            </div>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Abstract
            </label>
            <p className="mt-1 text-sm text-gray-900 line-clamp-4">
              {manuscriptDetails?.abstract || 'N/A'}
            </p>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Keywords
            </label>
            <div className="mt-1 flex flex-wrap gap-2">
              {manuscriptDetails?.keywords?.map((keyword: string) => (
                <span
                  key={keyword}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                >
                  {keyword}
                </span>
              )) || <span className="text-sm text-gray-900">N/A</span>}
            </div>
          </div>

          {manuscriptDetails?.fundingStatement && (
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Funding
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {manuscriptDetails.fundingStatement}
              </p>
            </div>
          )}

          {manuscriptDetails?.conflictOfInterest && (
            <div>
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                Conflicts of Interest
              </label>
              <p className="mt-1 text-sm text-gray-900">
                {manuscriptDetails.conflictOfInterest}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Authors Section */}
      <div className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <UserGroupIcon className="h-6 w-6 text-indigo-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">
              Authors ({authors?.length || 0})
            </h3>
          </div>
        </div>
        <div className="px-6 py-4">
          <div className="space-y-4">
            {authors?.map((author: any, index: number) => (
              <div
                key={author.id}
                className="flex items-start p-4 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                    <span className="text-sm font-medium text-indigo-600">{index + 1}</span>
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <div className="flex items-center">
                    <p className="text-sm font-medium text-gray-900">
                      {author.firstName} {author.lastName}
                    </p>
                    {author.isCorresponding && (
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                        Corresponding
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{author.email}</p>
                  <p className="text-xs text-gray-600 mt-1">{author.affiliation}</p>
                  {author.orcid && (
                    <p className="text-xs text-gray-500 mt-1">ORCID: {author.orcid}</p>
                  )}
                  {author.contribution && (
                    <p className="text-xs text-gray-600 mt-2 italic">{author.contribution}</p>
                  )}
                </div>
              </div>
            )) || <p className="text-sm text-gray-500">No authors added</p>}
          </div>
        </div>
      </div>

      {/* Files Section */}
      <div className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div className="flex items-center">
            <DocumentArrowUpIcon className="h-6 w-6 text-indigo-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">
              Uploaded Files ({files?.uploadedFiles?.length || 0})
            </h3>
          </div>
        </div>
        <div className="px-6 py-4 space-y-4">
          {/* Manuscript Files */}
          {manuscriptFiles.length > 0 && (
            <div>
              <label className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                Manuscript Files
              </label>
              <div className="mt-2 space-y-2">
                {manuscriptFiles.map((file: any) => (
                  <div
                    key={file.id}
                    className="flex items-center p-3 bg-gray-50 rounded border border-gray-200"
                  >
                    <DocumentTextIcon className="h-5 w-5 text-indigo-600 mr-3" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(file.file.size)}
                      </p>
                    </div>
                    <CheckCircleIcon className="h-5 w-5 text-green-500 ml-2" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Figure Files */}
          {figureFiles.length > 0 && (
            <div>
              <label className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                Figures
              </label>
              <div className="mt-2 space-y-2">
                {figureFiles.map((file: any) => (
                  <div
                    key={file.id}
                    className="flex items-center p-3 bg-gray-50 rounded border border-gray-200"
                  >
                    <DocumentTextIcon className="h-5 w-5 text-indigo-600 mr-3" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.file.name}
                      </p>
                      {file.description && (
                        <p className="text-xs text-gray-600 mt-1">{file.description}</p>
                      )}
                    </div>
                    <CheckCircleIcon className="h-5 w-5 text-green-500 ml-2" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Supplementary Files */}
          {supplementaryFiles.length > 0 && (
            <div>
              <label className="text-xs font-medium text-gray-700 uppercase tracking-wide">
                Supplementary Materials
              </label>
              <div className="mt-2 space-y-2">
                {supplementaryFiles.map((file: any) => (
                  <div
                    key={file.id}
                    className="flex items-center p-3 bg-gray-50 rounded border border-gray-200"
                  >
                    <DocumentTextIcon className="h-5 w-5 text-indigo-600 mr-3" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.file.name}
                      </p>
                      {file.description && (
                        <p className="text-xs text-gray-600 mt-1">{file.description}</p>
                      )}
                    </div>
                    <CheckCircleIcon className="h-5 w-5 text-green-500 ml-2" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {(!files?.uploadedFiles || files.uploadedFiles.length === 0) && (
            <p className="text-sm text-gray-500">No files uploaded</p>
          )}
        </div>
      </div>

      {/* Confirmations */}
      <div className="bg-white border-2 border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Required Confirmations
        </h3>
        <div className="space-y-4">
          <label className="flex items-start">
            <input
              type="checkbox"
              checked={agreedToTerms}
              onChange={(e) => setAgreedToTerms(e.target.checked)}
              className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="ml-3 text-sm text-gray-700">
              I agree to the{' '}
              <a
                href="/submission-terms"
                target="_blank"
                className="text-indigo-600 hover:text-indigo-800 underline"
              >
                submission terms and conditions
              </a>
              , including the copyright and licensing agreement.
            </span>
          </label>

          <label className="flex items-start">
            <input
              type="checkbox"
              checked={agreedToEthics}
              onChange={(e) => setAgreedToEthics(e.target.checked)}
              className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="ml-3 text-sm text-gray-700">
              I confirm that this research complies with all relevant ethical guidelines and has
              received necessary approvals (e.g., IRB, animal ethics).
            </span>
          </label>

          <label className="flex items-start">
            <input
              type="checkbox"
              checked={agreedToOriginality}
              onChange={(e) => setAgreedToOriginality(e.target.checked)}
              className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="ml-3 text-sm text-gray-700">
              I confirm that this manuscript is original work, has not been published elsewhere,
              and is not under consideration by another journal.
            </span>
          </label>
        </div>

        {errors.length > 0 && (
          <div className="mt-4 bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-600 mr-3 flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium text-red-900">
                  Please complete the following:
                </h4>
                <ul className="mt-2 text-sm text-red-700 list-disc list-inside">
                  {errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* What Happens Next */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex">
          <InformationCircleIcon className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-blue-900">What happens next?</h3>
            <ul className="mt-2 text-sm text-blue-700 space-y-1">
              <li>1. You'll receive an email confirmation with your manuscript ID</li>
              <li>2. Our editorial team will perform an initial review (3-5 business days)</li>
              <li>3. Your manuscript will be assigned to reviewers</li>
              <li>4. You'll receive updates via email at each stage</li>
              <li>5. Average review time: 21 days</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-6 border-t-2 border-gray-200">
        <button
          type="button"
          onClick={onPrev}
          disabled={isSubmitting}
          className="px-6 py-2 bg-white text-gray-700 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="px-8 py-3 bg-green-600 text-white rounded-md text-base font-semibold hover:bg-green-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center shadow-lg"
        >
          {isSubmitting ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Submitting...
            </>
          ) : (
            <>
              <CheckCircleIcon className="h-5 w-5 mr-2" />
              Submit Manuscript
            </>
          )}
        </button>
      </div>
    </div>
  );
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
};

export default ReviewAndSubmit;
