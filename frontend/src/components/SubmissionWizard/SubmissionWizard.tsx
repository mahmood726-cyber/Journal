import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircleIcon } from '@heroicons/react/24/solid';
import { toast } from 'react-hot-toast';

// Step Components
import ManuscriptDetails from './steps/ManuscriptDetails';
import AuthorInformation from './steps/AuthorInformation';
import FileUpload from './steps/FileUpload';
import ReviewAndSubmit from './steps/ReviewAndSubmit';

interface StepConfig {
  id: number;
  name: string;
  description: string;
  component: React.ComponentType<any>;
}

const steps: StepConfig[] = [
  {
    id: 1,
    name: 'Manuscript Details',
    description: 'Basic information about your manuscript',
    component: ManuscriptDetails,
  },
  {
    id: 2,
    name: 'Authors',
    description: 'Add all contributing authors',
    component: AuthorInformation,
  },
  {
    id: 3,
    name: 'Files',
    description: 'Upload manuscript and supplementary materials',
    component: FileUpload,
  },
  {
    id: 4,
    name: 'Review & Submit',
    description: 'Review your submission and submit',
    component: ReviewAndSubmit,
  },
];

const SubmissionWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    manuscriptDetails: {},
    authors: [],
    files: {},
  });
  const navigate = useNavigate();

  const updateFormData = (step: string, data: any) => {
    setFormData((prev) => ({
      ...prev,
      [step]: data,
    }));
  };

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleSubmit = async () => {
    try {
      // Submit manuscript
      toast.success('Manuscript submitted successfully!');
      navigate('/dashboard/manuscripts');
    } catch (error) {
      toast.error('Failed to submit manuscript. Please try again.');
    }
  };

  const CurrentStepComponent = steps[currentStep - 1].component;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Progress Steps */}
      <nav aria-label="Progress" className="mb-8">
        <ol className="flex items-center justify-between">
          {steps.map((step, index) => (
            <li
              key={step.id}
              className={`relative ${
                index !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''
              } flex-1`}
            >
              {index !== steps.length - 1 && (
                <div
                  className="absolute inset-0 flex items-center"
                  aria-hidden="true"
                >
                  <div
                    className={`h-0.5 w-full transition-colors duration-300 ${
                      currentStep > step.id ? 'bg-indigo-600' : 'bg-gray-200'
                    }`}
                  />
                </div>
              )}
              <button
                onClick={() => setCurrentStep(step.id)}
                className={`relative w-full flex flex-col items-center group ${
                  currentStep >= step.id ? 'cursor-pointer' : 'cursor-not-allowed'
                }`}
                disabled={currentStep < step.id}
              >
                <span
                  className={`h-10 w-10 flex items-center justify-center rounded-full transition-colors duration-300 ${
                    currentStep > step.id
                      ? 'bg-indigo-600 hover:bg-indigo-700'
                      : currentStep === step.id
                      ? 'bg-indigo-600 border-2 border-indigo-600'
                      : 'bg-gray-200 border-2 border-gray-300'
                  }`}
                >
                  {currentStep > step.id ? (
                    <CheckCircleIcon className="h-6 w-6 text-white" />
                  ) : (
                    <span
                      className={`text-sm font-medium ${
                        currentStep === step.id ? 'text-white' : 'text-gray-500'
                      }`}
                    >
                      {step.id}
                    </span>
                  )}
                </span>
                <span className="mt-2 text-xs sm:text-sm font-medium text-center">
                  <span
                    className={`${
                      currentStep >= step.id ? 'text-indigo-600' : 'text-gray-500'
                    }`}
                  >
                    {step.name}
                  </span>
                  <span className="block text-xs text-gray-500 mt-0.5 hidden sm:block">
                    {step.description}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ol>
      </nav>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-lg p-6 sm:p-8 mb-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {steps[currentStep - 1].name}
          </h2>
          <p className="mt-1 text-sm text-gray-600">
            {steps[currentStep - 1].description}
          </p>
        </div>

        <CurrentStepComponent
          data={formData}
          updateData={updateFormData}
          onNext={nextStep}
          onPrev={prevStep}
        />
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between items-center bg-white rounded-lg shadow-sm p-4">
        <button
          type="button"
          onClick={prevStep}
          disabled={currentStep === 1}
          className={`px-6 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
            currentStep === 1
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
          }`}
        >
          Previous
        </button>

        <div className="text-sm text-gray-600">
          Step {currentStep} of {steps.length}
        </div>

        {currentStep < steps.length ? (
          <button
            type="button"
            onClick={nextStep}
            className="px-6 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors duration-200"
          >
            Next
          </button>
        ) : (
          <button
            type="button"
            onClick={handleSubmit}
            className="px-6 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 transition-colors duration-200"
          >
            Submit Manuscript
          </button>
        )}
      </div>

      {/* Help Section */}
      <div className="mt-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">Need help?</h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Check our{' '}
                <a href="/author-guidelines" className="font-medium underline">
                  submission guidelines
                </a>{' '}
                or{' '}
                <a href="/contact" className="font-medium underline">
                  contact support
                </a>
                . Your progress is automatically saved as you go.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubmissionWizard;
