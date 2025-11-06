import React, { useState, useEffect } from 'react';
import { InformationCircleIcon } from '@heroicons/react/24/outline';

interface ManuscriptDetailsProps {
  data: any;
  updateData: (step: string, data: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const ManuscriptDetails: React.FC<ManuscriptDetailsProps> = ({
  data,
  updateData,
  onNext,
}) => {
  const [formData, setFormData] = useState({
    title: data.manuscriptDetails?.title || '',
    abstract: data.manuscriptDetails?.abstract || '',
    keywords: data.manuscriptDetails?.keywords || [],
    manuscriptType: data.manuscriptDetails?.manuscriptType || '',
    subjectArea: data.manuscriptDetails?.subjectArea || '',
    fundingStatement: data.manuscriptDetails?.fundingStatement || '',
    conflictOfInterest: data.manuscriptDetails?.conflictOfInterest || '',
  });

  const [keywordInput, setKeywordInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const manuscriptTypes = [
    { value: 'original-research', label: 'Original Research Article' },
    { value: 'review', label: 'Review Article' },
    { value: 'systematic-review', label: 'Systematic Review' },
    { value: 'meta-analysis', label: 'Meta-Analysis' },
    { value: 'case-study', label: 'Case Study' },
    { value: 'short-communication', label: 'Short Communication' },
    { value: 'letter', label: 'Letter to Editor' },
  ];

  const subjectAreas = [
    'Biochemistry',
    'Bioinformatics',
    'Biophysics',
    'Cell Biology',
    'Genetics',
    'Immunology',
    'Microbiology',
    'Molecular Biology',
    'Neuroscience',
    'Pharmacology',
    'Physiology',
    'Structural Biology',
  ];

  useEffect(() => {
    // Auto-save data
    updateData('manuscriptDetails', formData);
  }, [formData]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const addKeyword = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && keywordInput.trim()) {
      e.preventDefault();
      if (!formData.keywords.includes(keywordInput.trim())) {
        setFormData((prev) => ({
          ...prev,
          keywords: [...prev.keywords, keywordInput.trim()],
        }));
      }
      setKeywordInput('');
    }
  };

  const removeKeyword = (keyword: string) => {
    setFormData((prev) => ({
      ...prev,
      keywords: prev.keywords.filter((k: string) => k !== keyword),
    }));
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length < 10) {
      newErrors.title = 'Title must be at least 10 characters';
    }

    if (!formData.abstract.trim()) {
      newErrors.abstract = 'Abstract is required';
    } else if (formData.abstract.length < 150) {
      newErrors.abstract = 'Abstract must be at least 150 characters';
    } else if (formData.abstract.length > 3000) {
      newErrors.abstract = 'Abstract must not exceed 3000 characters';
    }

    if (formData.keywords.length < 3) {
      newErrors.keywords = 'Please add at least 3 keywords';
    } else if (formData.keywords.length > 10) {
      newErrors.keywords = 'Maximum 10 keywords allowed';
    }

    if (!formData.manuscriptType) {
      newErrors.manuscriptType = 'Please select a manuscript type';
    }

    if (!formData.subjectArea) {
      newErrors.subjectArea = 'Please select a subject area';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validate()) {
      onNext();
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Manuscript Title <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
            errors.title ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Enter the full title of your manuscript"
        />
        {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
        <p className="mt-1 text-xs text-gray-500">
          {formData.title.length} characters (minimum 10)
        </p>
      </div>

      {/* Manuscript Type */}
      <div>
        <label htmlFor="manuscriptType" className="block text-sm font-medium text-gray-700 mb-1">
          Manuscript Type <span className="text-red-500">*</span>
        </label>
        <select
          id="manuscriptType"
          name="manuscriptType"
          value={formData.manuscriptType}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
            errors.manuscriptType ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">Select manuscript type</option>
          {manuscriptTypes.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
        {errors.manuscriptType && (
          <p className="mt-1 text-sm text-red-600">{errors.manuscriptType}</p>
        )}
      </div>

      {/* Subject Area */}
      <div>
        <label htmlFor="subjectArea" className="block text-sm font-medium text-gray-700 mb-1">
          Primary Subject Area <span className="text-red-500">*</span>
        </label>
        <select
          id="subjectArea"
          name="subjectArea"
          value={formData.subjectArea}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
            errors.subjectArea ? 'border-red-500' : 'border-gray-300'
          }`}
        >
          <option value="">Select subject area</option>
          {subjectAreas.map((area) => (
            <option key={area} value={area}>
              {area}
            </option>
          ))}
        </select>
        {errors.subjectArea && (
          <p className="mt-1 text-sm text-red-600">{errors.subjectArea}</p>
        )}
      </div>

      {/* Abstract */}
      <div>
        <label htmlFor="abstract" className="block text-sm font-medium text-gray-700 mb-1">
          Abstract <span className="text-red-500">*</span>
        </label>
        <textarea
          id="abstract"
          name="abstract"
          rows={10}
          value={formData.abstract}
          onChange={handleChange}
          className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
            errors.abstract ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Enter your abstract here. Include background, methods, results, and conclusions."
        />
        {errors.abstract && <p className="mt-1 text-sm text-red-600">{errors.abstract}</p>}
        <p className="mt-1 text-xs text-gray-500">
          {formData.abstract.length} characters (150-3000 recommended)
        </p>
      </div>

      {/* Keywords */}
      <div>
        <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 mb-1">
          Keywords <span className="text-red-500">*</span>
        </label>
        <div className="flex flex-wrap gap-2 mb-2">
          {formData.keywords.map((keyword: string) => (
            <span
              key={keyword}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800"
            >
              {keyword}
              <button
                type="button"
                onClick={() => removeKeyword(keyword)}
                className="ml-2 inline-flex items-center justify-center w-4 h-4 text-indigo-600 hover:text-indigo-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <input
          type="text"
          id="keywords"
          value={keywordInput}
          onChange={(e) => setKeywordInput(e.target.value)}
          onKeyDown={addKeyword}
          className={`w-full px-4 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
            errors.keywords ? 'border-red-500' : 'border-gray-300'
          }`}
          placeholder="Type a keyword and press Enter"
        />
        {errors.keywords && <p className="mt-1 text-sm text-red-600">{errors.keywords}</p>}
        <p className="mt-1 text-xs text-gray-500">
          {formData.keywords.length} keywords (3-10 required)
        </p>
      </div>

      {/* Funding Statement */}
      <div>
        <label htmlFor="fundingStatement" className="block text-sm font-medium text-gray-700 mb-1">
          Funding Statement
        </label>
        <textarea
          id="fundingStatement"
          name="fundingStatement"
          rows={3}
          value={formData.fundingStatement}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="List funding sources and grant numbers (if applicable)"
        />
        <p className="mt-1 text-xs text-gray-500">
          Provide details of all funding sources for this research
        </p>
      </div>

      {/* Conflict of Interest */}
      <div>
        <label
          htmlFor="conflictOfInterest"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Conflict of Interest Statement
        </label>
        <textarea
          id="conflictOfInterest"
          name="conflictOfInterest"
          rows={3}
          value={formData.conflictOfInterest}
          onChange={handleChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          placeholder="Declare any conflicts of interest or state 'None'"
        />
        <p className="mt-1 text-xs text-gray-500">
          All authors must disclose any potential conflicts of interest
        </p>
      </div>

      {/* Help Box */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex">
          <InformationCircleIcon className="h-5 w-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Writing Tips:</p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>Write a clear, descriptive title that accurately reflects your research</li>
              <li>Your abstract should be self-contained and summarize key findings</li>
              <li>Choose keywords that researchers would use to find your article</li>
              <li>Be specific about funding sources and potential conflicts</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-end pt-4">
        <button
          type="button"
          onClick={handleNext}
          className="px-6 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors duration-200"
        >
          Next: Add Authors
        </button>
      </div>
    </div>
  );
};

export default ManuscriptDetails;
