import React, { useState, useEffect, useRef } from 'react';
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  PhotoIcon,
  DocumentIcon,
  TrashIcon,
  CheckCircleIcon,
  InformationCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface UploadedFile {
  id: string;
  file: File;
  type: 'manuscript' | 'figure' | 'supplementary';
  description?: string;
  uploading?: boolean;
  progress?: number;
  error?: string;
}

interface FileUploadProps {
  data: any;
  updateData: (step: string, data: any) => void;
  onNext: () => void;
  onPrev: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({
  data,
  updateData,
  onNext,
  onPrev,
}) => {
  const [files, setFiles] = useState<UploadedFile[]>(data.files?.uploadedFiles || []);
  const [dragActive, setDragActive] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const manuscriptInputRef = useRef<HTMLInputElement>(null);
  const figureInputRef = useRef<HTMLInputElement>(null);
  const supplementaryInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    updateData('files', { uploadedFiles: files });
  }, [files]);

  const acceptedManuscriptFormats = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/x-latex': ['.tex'],
    'text/x-tex': ['.tex'],
  };

  const acceptedFigureFormats = {
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/tiff': ['.tif', '.tiff'],
    'application/pdf': ['.pdf'],
    'image/svg+xml': ['.svg'],
  };

  const acceptedSupplementaryFormats = {
    'application/pdf': ['.pdf'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'text/csv': ['.csv'],
    'application/zip': ['.zip'],
    'video/mp4': ['.mp4'],
    'video/quicktime': ['.mov'],
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent, type: 'manuscript' | 'figure' | 'supplementary') => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files), type);
    }
  };

  const handleFileInput = (
    e: React.ChangeEvent<HTMLInputElement>,
    type: 'manuscript' | 'figure' | 'supplementary'
  ) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files), type);
    }
  };

  const handleFiles = (fileList: File[], type: 'manuscript' | 'figure' | 'supplementary') => {
    const newFiles: UploadedFile[] = fileList.map((file) => ({
      id: `${Date.now()}-${Math.random()}`,
      file,
      type,
      uploading: true,
      progress: 0,
    }));

    setFiles([...files, ...newFiles]);

    // Simulate upload progress
    newFiles.forEach((uploadedFile) => {
      simulateUpload(uploadedFile.id);
    });
  };

  const simulateUpload = (fileId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setFiles((prevFiles) =>
        prevFiles.map((f) =>
          f.id === fileId
            ? {
                ...f,
                progress,
                uploading: progress < 100,
              }
            : f
        )
      );
      if (progress >= 100) {
        clearInterval(interval);
      }
    }, 200);
  };

  const removeFile = (fileId: string) => {
    setFiles(files.filter((f) => f.id !== fileId));
  };

  const updateFileDescription = (fileId: string, description: string) => {
    setFiles(
      files.map((f) => (f.id === fileId ? { ...f, description } : f))
    );
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileIcon = (type: string) => {
    if (type === 'manuscript') return DocumentTextIcon;
    if (type === 'figure') return PhotoIcon;
    return DocumentIcon;
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    const manuscriptFiles = files.filter((f) => f.type === 'manuscript');
    if (manuscriptFiles.length === 0) {
      newErrors.manuscript = 'Please upload at least one manuscript file';
    }

    const uploadingFiles = files.filter((f) => f.uploading);
    if (uploadingFiles.length > 0) {
      newErrors.uploading = 'Please wait for all files to finish uploading';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validate()) {
      onNext();
    }
  };

  const manuscriptFiles = files.filter((f) => f.type === 'manuscript');
  const figureFiles = files.filter((f) => f.type === 'figure');
  const supplementaryFiles = files.filter((f) => f.type === 'supplementary');

  return (
    <div className="space-y-8">
      {/* Manuscript Files */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Manuscript File <span className="text-red-500">*</span>
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Upload your manuscript in PDF, Word, or LaTeX format
            </p>
          </div>
        </div>

        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-indigo-500 bg-indigo-50'
              : errors.manuscript
              ? 'border-red-300 bg-red-50'
              : 'border-gray-300 hover:border-indigo-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={(e) => handleDrop(e, 'manuscript')}
        >
          <input
            ref={manuscriptInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.doc,.docx,.tex"
            onChange={(e) => handleFileInput(e, 'manuscript')}
          />

          <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            Drag and drop your manuscript file here, or{' '}
            <button
              type="button"
              onClick={() => manuscriptInputRef.current?.click()}
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              browse
            </button>
          </p>
          <p className="mt-1 text-xs text-gray-500">PDF, DOC, DOCX, TEX (max 50MB)</p>
        </div>

        {errors.manuscript && (
          <p className="mt-2 text-sm text-red-600 flex items-center">
            <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
            {errors.manuscript}
          </p>
        )}

        {/* Manuscript Files List */}
        {manuscriptFiles.length > 0 && (
          <div className="mt-4 space-y-2">
            {manuscriptFiles.map((file) => (
              <FileItem
                key={file.id}
                file={file}
                onRemove={removeFile}
                onUpdateDescription={updateFileDescription}
              />
            ))}
          </div>
        )}
      </div>

      {/* Figure Files */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Figures <span className="text-gray-400">(Optional)</span>
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Upload high-resolution figures (PNG, JPEG, TIFF, PDF, SVG)
            </p>
          </div>
        </div>

        <div
          className="relative border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 transition-colors"
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={(e) => handleDrop(e, 'figure')}
        >
          <input
            ref={figureInputRef}
            type="file"
            className="hidden"
            accept=".png,.jpg,.jpeg,.tif,.tiff,.pdf,.svg"
            multiple
            onChange={(e) => handleFileInput(e, 'figure')}
          />

          <PhotoIcon className="mx-auto h-10 w-10 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            <button
              type="button"
              onClick={() => figureInputRef.current?.click()}
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Upload figures
            </button>{' '}
            or drag and drop
          </p>
          <p className="mt-1 text-xs text-gray-500">
            PNG, JPEG, TIFF, PDF, SVG (max 20MB each)
          </p>
        </div>

        {/* Figure Files List */}
        {figureFiles.length > 0 && (
          <div className="mt-4 space-y-2">
            {figureFiles.map((file) => (
              <FileItem
                key={file.id}
                file={file}
                onRemove={removeFile}
                onUpdateDescription={updateFileDescription}
              />
            ))}
          </div>
        )}
      </div>

      {/* Supplementary Files */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Supplementary Materials <span className="text-gray-400">(Optional)</span>
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Upload additional data, videos, or supporting documents
            </p>
          </div>
        </div>

        <div
          className="relative border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 transition-colors"
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={(e) => handleDrop(e, 'supplementary')}
        >
          <input
            ref={supplementaryInputRef}
            type="file"
            className="hidden"
            accept=".pdf,.xls,.xlsx,.csv,.zip,.mp4,.mov"
            multiple
            onChange={(e) => handleFileInput(e, 'supplementary')}
          />

          <DocumentIcon className="mx-auto h-10 w-10 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            <button
              type="button"
              onClick={() => supplementaryInputRef.current?.click()}
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Upload supplementary files
            </button>{' '}
            or drag and drop
          </p>
          <p className="mt-1 text-xs text-gray-500">
            PDF, Excel, CSV, ZIP, Video (max 100MB each)
          </p>
        </div>

        {/* Supplementary Files List */}
        {supplementaryFiles.length > 0 && (
          <div className="mt-4 space-y-2">
            {supplementaryFiles.map((file) => (
              <FileItem
                key={file.id}
                file={file}
                onRemove={removeFile}
                onUpdateDescription={updateFileDescription}
              />
            ))}
          </div>
        )}
      </div>

      {/* Help Box */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex">
          <InformationCircleIcon className="h-5 w-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">File Upload Guidelines:</p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>Manuscript files should be in their final, proofread version</li>
              <li>Figures should be high-resolution (minimum 300 DPI for print)</li>
              <li>Number your figures in the order they appear in the text</li>
              <li>Include descriptive captions for all figures</li>
              <li>Supplementary materials should be clearly labeled</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Upload Status Error */}
      {errors.uploading && (
        <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
          <p className="text-sm text-yellow-800 flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            {errors.uploading}
          </p>
        </div>
      )}

      {/* Summary */}
      {files.length > 0 && (
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-sm text-green-800">
            <strong>{files.length}</strong> file{files.length !== 1 ? 's' : ''} uploaded
            {' • '}
            {manuscriptFiles.length} manuscript
            {manuscriptFiles.length !== 1 ? 's' : ''}, {figureFiles.length} figure
            {figureFiles.length !== 1 ? 's' : ''}, {supplementaryFiles.length} supplementary
          </p>
        </div>
      )}

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
          Next: Review & Submit
        </button>
      </div>
    </div>
  );
};

// File Item Component
interface FileItemProps {
  file: UploadedFile;
  onRemove: (fileId: string) => void;
  onUpdateDescription: (fileId: string, description: string) => void;
}

const FileItem: React.FC<FileItemProps> = ({ file, onRemove, onUpdateDescription }) => {
  const Icon = file.type === 'figure' ? PhotoIcon : DocumentTextIcon;

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <div className="flex items-start flex-1 min-w-0">
          <Icon className="h-10 w-10 text-indigo-600 flex-shrink-0" />
          <div className="ml-3 flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">{file.file.name}</p>
            <p className="text-xs text-gray-500">{formatFileSize(file.file.size)}</p>

            {file.uploading && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${file.progress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Uploading... {file.progress}%</p>
              </div>
            )}

            {!file.uploading && (
              <div className="mt-2">
                <CheckCircleIcon className="h-5 w-5 text-green-500 inline mr-1" />
                <span className="text-xs text-green-600">Uploaded successfully</span>
              </div>
            )}

            {(file.type === 'figure' || file.type === 'supplementary') && !file.uploading && (
              <input
                type="text"
                placeholder="Add a description or caption..."
                value={file.description || ''}
                onChange={(e) => onUpdateDescription(file.id, e.target.value)}
                className="mt-2 w-full px-2 py-1 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            )}
          </div>
        </div>

        <button
          type="button"
          onClick={() => onRemove(file.id)}
          className="ml-4 p-1 text-gray-400 hover:text-red-600 rounded-md hover:bg-red-50"
          title="Remove file"
        >
          <TrashIcon className="h-5 w-5" />
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

export default FileUpload;
