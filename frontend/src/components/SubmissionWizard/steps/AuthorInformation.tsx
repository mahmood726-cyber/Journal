import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  TrashIcon,
  InformationCircleIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { CheckCircleIcon } from '@heroicons/react/24/solid';

interface Author {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  affiliation: string;
  orcid: string;
  isCorresponding: boolean;
  contribution: string;
}

interface AuthorInformationProps {
  data: any;
  updateData: (step: string, data: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const AuthorInformation: React.FC<AuthorInformationProps> = ({
  data,
  updateData,
  onNext,
  onPrev,
}) => {
  const [authors, setAuthors] = useState<Author[]>(
    data.authors?.length > 0
      ? data.authors
      : [
          {
            id: '1',
            firstName: '',
            lastName: '',
            email: '',
            affiliation: '',
            orcid: '',
            isCorresponding: true,
            contribution: '',
          },
        ]
  );

  const [errors, setErrors] = useState<Record<string, Record<string, string>>>({});

  useEffect(() => {
    updateData('authors', authors);
  }, [authors]);

  const addAuthor = () => {
    const newAuthor: Author = {
      id: Date.now().toString(),
      firstName: '',
      lastName: '',
      email: '',
      affiliation: '',
      orcid: '',
      isCorresponding: false,
      contribution: '',
    };
    setAuthors([...authors, newAuthor]);
  };

  const removeAuthor = (id: string) => {
    if (authors.length > 1) {
      const updatedAuthors = authors.filter((author) => author.id !== id);
      // If removing corresponding author, make first author corresponding
      if (
        authors.find((a) => a.id === id)?.isCorresponding &&
        updatedAuthors.length > 0
      ) {
        updatedAuthors[0].isCorresponding = true;
      }
      setAuthors(updatedAuthors);
      // Clear errors for removed author
      const newErrors = { ...errors };
      delete newErrors[id];
      setErrors(newErrors);
    }
  };

  const updateAuthor = (id: string, field: keyof Author, value: any) => {
    setAuthors(
      authors.map((author) =>
        author.id === id ? { ...author, [field]: value } : author
      )
    );
    // Clear error for this field
    if (errors[id]?.[field]) {
      setErrors({
        ...errors,
        [id]: { ...errors[id], [field]: '' },
      });
    }
  };

  const setCorrespondingAuthor = (id: string) => {
    setAuthors(
      authors.map((author) => ({
        ...author,
        isCorresponding: author.id === id,
      }))
    );
  };

  const moveAuthor = (index: number, direction: 'up' | 'down') => {
    const newAuthors = [...authors];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex >= 0 && targetIndex < authors.length) {
      [newAuthors[index], newAuthors[targetIndex]] = [
        newAuthors[targetIndex],
        newAuthors[index],
      ];
      setAuthors(newAuthors);
    }
  };

  const validateEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validateORCID = (orcid: string): boolean => {
    if (!orcid) return true; // ORCID is optional
    return /^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$/.test(orcid);
  };

  const validate = (): boolean => {
    const newErrors: Record<string, Record<string, string>> = {};
    let isValid = true;

    authors.forEach((author) => {
      const authorErrors: Record<string, string> = {};

      if (!author.firstName.trim()) {
        authorErrors.firstName = 'First name is required';
        isValid = false;
      }

      if (!author.lastName.trim()) {
        authorErrors.lastName = 'Last name is required';
        isValid = false;
      }

      if (!author.email.trim()) {
        authorErrors.email = 'Email is required';
        isValid = false;
      } else if (!validateEmail(author.email)) {
        authorErrors.email = 'Invalid email format';
        isValid = false;
      }

      if (!author.affiliation.trim()) {
        authorErrors.affiliation = 'Affiliation is required';
        isValid = false;
      }

      if (author.orcid && !validateORCID(author.orcid)) {
        authorErrors.orcid = 'Invalid ORCID format (0000-0000-0000-0000)';
        isValid = false;
      }

      if (Object.keys(authorErrors).length > 0) {
        newErrors[author.id] = authorErrors;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleNext = () => {
    if (validate()) {
      onNext();
    }
  };

  return (
    <div className="space-y-6">
      {/* Author List */}
      <div className="space-y-6">
        {authors.map((author, index) => (
          <div
            key={author.id}
            className="bg-gray-50 rounded-lg p-6 border-2 border-gray-200 relative"
          >
            {/* Author Number and Actions */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <UserCircleIcon className="h-6 w-6 text-indigo-600 mr-2" />
                <h3 className="text-lg font-semibold text-gray-900">
                  Author {index + 1}
                  {author.isCorresponding && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800">
                      <CheckCircleIcon className="h-4 w-4 mr-1" />
                      Corresponding
                    </span>
                  )}
                </h3>
              </div>

              <div className="flex items-center space-x-2">
                {/* Move Up/Down */}
                {index > 0 && (
                  <button
                    type="button"
                    onClick={() => moveAuthor(index, 'up')}
                    className="p-1 text-gray-400 hover:text-gray-600"
                    title="Move up"
                  >
                    ↑
                  </button>
                )}
                {index < authors.length - 1 && (
                  <button
                    type="button"
                    onClick={() => moveAuthor(index, 'down')}
                    className="p-1 text-gray-400 hover:text-gray-600"
                    title="Move down"
                  >
                    ↓
                  </button>
                )}

                {/* Remove Author */}
                {authors.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeAuthor(author.id)}
                    className="p-2 text-red-400 hover:text-red-600 rounded-md hover:bg-red-50"
                    title="Remove author"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Author Form Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* First Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={author.firstName}
                  onChange={(e) =>
                    updateAuthor(author.id, 'firstName', e.target.value)
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                    errors[author.id]?.firstName
                      ? 'border-red-500'
                      : 'border-gray-300'
                  }`}
                  placeholder="John"
                />
                {errors[author.id]?.firstName && (
                  <p className="mt-1 text-xs text-red-600">
                    {errors[author.id].firstName}
                  </p>
                )}
              </div>

              {/* Last Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={author.lastName}
                  onChange={(e) =>
                    updateAuthor(author.id, 'lastName', e.target.value)
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                    errors[author.id]?.lastName
                      ? 'border-red-500'
                      : 'border-gray-300'
                  }`}
                  placeholder="Doe"
                />
                {errors[author.id]?.lastName && (
                  <p className="mt-1 text-xs text-red-600">
                    {errors[author.id].lastName}
                  </p>
                )}
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  value={author.email}
                  onChange={(e) =>
                    updateAuthor(author.id, 'email', e.target.value)
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                    errors[author.id]?.email
                      ? 'border-red-500'
                      : 'border-gray-300'
                  }`}
                  placeholder="john.doe@university.edu"
                />
                {errors[author.id]?.email && (
                  <p className="mt-1 text-xs text-red-600">
                    {errors[author.id].email}
                  </p>
                )}
              </div>

              {/* ORCID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ORCID iD
                  <a
                    href="https://orcid.org"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-1 text-xs text-indigo-600 hover:text-indigo-800"
                  >
                    (Get one here)
                  </a>
                </label>
                <input
                  type="text"
                  value={author.orcid}
                  onChange={(e) =>
                    updateAuthor(author.id, 'orcid', e.target.value)
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                    errors[author.id]?.orcid
                      ? 'border-red-500'
                      : 'border-gray-300'
                  }`}
                  placeholder="0000-0000-0000-0000"
                />
                {errors[author.id]?.orcid && (
                  <p className="mt-1 text-xs text-red-600">
                    {errors[author.id].orcid}
                  </p>
                )}
              </div>

              {/* Affiliation */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Affiliation <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={author.affiliation}
                  onChange={(e) =>
                    updateAuthor(author.id, 'affiliation', e.target.value)
                  }
                  className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent ${
                    errors[author.id]?.affiliation
                      ? 'border-red-500'
                      : 'border-gray-300'
                  }`}
                  placeholder="Department of Biology, University Name, City, Country"
                />
                {errors[author.id]?.affiliation && (
                  <p className="mt-1 text-xs text-red-600">
                    {errors[author.id].affiliation}
                  </p>
                )}
              </div>

              {/* Contribution */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contribution to Study
                </label>
                <textarea
                  value={author.contribution}
                  onChange={(e) =>
                    updateAuthor(author.id, 'contribution', e.target.value)
                  }
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="e.g., Designed experiments, analyzed data, wrote manuscript"
                />
              </div>

              {/* Corresponding Author Toggle */}
              {!author.isCorresponding && (
                <div className="md:col-span-2">
                  <button
                    type="button"
                    onClick={() => setCorrespondingAuthor(author.id)}
                    className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                  >
                    Set as Corresponding Author
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Add Author Button */}
      <button
        type="button"
        onClick={addAuthor}
        className="w-full flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:border-indigo-500 hover:text-indigo-600 hover:bg-indigo-50 transition-all duration-200"
      >
        <PlusIcon className="h-5 w-5 mr-2" />
        Add Another Author
      </button>

      {/* Help Box */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex">
          <InformationCircleIcon className="h-5 w-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Author Guidelines:</p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>List authors in the order they should appear in the publication</li>
              <li>All authors must have made substantial contributions to the work</li>
              <li>The corresponding author will handle all communications about the manuscript</li>
              <li>ORCID iDs are highly recommended for better discoverability</li>
              <li>Use drag handles to reorder authors if needed</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-green-50 rounded-lg p-4 border border-green-200">
        <p className="text-sm text-green-800">
          <strong>{authors.length}</strong> author{authors.length !== 1 ? 's' : ''}{' '}
          added •{' '}
          <strong>
            {authors.find((a) => a.isCorresponding)?.firstName}{' '}
            {authors.find((a) => a.isCorresponding)?.lastName}
          </strong>{' '}
          is the corresponding author
        </p>
      </div>

      {/* Navigation */}
      <div className="flex justify-between pt-4">
        <button
          type="button"
          onClick={onPrev}
          className="px-6 py-2 bg-white text-gray-700 border border-gray-300 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors duration-200"
        >
          Previous
        </button>
        <button
          type="button"
          onClick={handleNext}
          className="px-6 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors duration-200"
        >
          Next: Upload Files
        </button>
      </div>
    </div>
  );
};

export default AuthorInformation;
