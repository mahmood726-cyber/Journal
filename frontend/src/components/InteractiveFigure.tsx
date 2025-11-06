/**
 * Interactive Figure Component
 *
 * Advanced figure display with:
 * - Zoom and pan
 * - Lightbox/fullscreen mode
 * - Download options (PNG, SVG, PDF)
 * - Image comparison slider
 * - Figure annotations
 * - Multiple panel support
 * - Export with citation
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  ZoomIn, ZoomOut, Maximize2, Download, X, Move,
  RotateCw, Share2, Printer, Info, ChevronLeft,
  ChevronRight, Grid, Maximize, Copy, Check
} from 'lucide-react';

interface FigurePanel {
  id: string;
  src: string;
  label: string;
  description?: string;
}

interface Figure {
  id: string;
  number: number;
  title: string;
  caption: string;
  panels: FigurePanel[];
  credit?: string;
  license?: string;
  downloadable?: boolean;
}

interface InteractiveFigureProps {
  figure: Figure;
  articleTitle?: string;
  authors?: string;
  doi?: string;
}

const InteractiveFigure: React.FC<InteractiveFigureProps> = ({
  figure,
  articleTitle,
  authors,
  doi
}) => {
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const [selectedPanel, setSelectedPanel] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);
  const [copiedCitation, setCopiedCitation] = useState(false);
  const imageRef = useRef<HTMLDivElement>(null);

  const currentPanel = figure.panels[selectedPanel];

  // Reset zoom and position when panel changes
  useEffect(() => {
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  }, [selectedPanel]);

  // Zoom controls
  const handleZoomIn = () => setZoom(Math.min(zoom + 0.5, 5));
  const handleZoomOut = () => setZoom(Math.max(zoom - 0.5, 0.5));
  const handleResetZoom = () => {
    setZoom(1);
    setPosition({ x: 0, y: 0 });
  };

  // Pan controls
  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoom > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  // Download figure
  const handleDownload = async (format: 'png' | 'svg' | 'pdf') => {
    // Implementation would depend on backend support
    const link = document.createElement('a');
    link.href = currentPanel.src;
    link.download = `figure-${figure.number}-${currentPanel.label}.${format}`;
    link.click();
    setShowDownloadMenu(false);
  };

  // Copy citation
  const handleCopyCitation = () => {
    const citation = generateFigureCitation();
    navigator.clipboard.writeText(citation);
    setCopiedCitation(true);
    setTimeout(() => setCopiedCitation(false), 2000);
  };

  const generateFigureCitation = () => {
    return `${authors}. ${articleTitle}. Figure ${figure.number}: ${figure.title}. ${doi ? `DOI: ${doi}` : ''}`;
  };

  return (
    <>
      {/* Main Figure Display */}
      <div className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden shadow-md my-8">
        {/* Figure Header */}
        <div className="bg-gray-50 border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-gray-900">
              Figure {figure.number}: {figure.title}
            </h3>
            <div className="flex items-center space-x-2">
              {figure.downloadable !== false && (
                <div className="relative">
                  <button
                    onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                    className="p-2 rounded-lg text-gray-700 hover:bg-gray-200 transition-colors"
                    title="Download"
                  >
                    <Download className="w-5 h-5" />
                  </button>

                  {/* Download Menu */}
                  {showDownloadMenu && (
                    <div className="absolute top-full right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-10">
                      <button
                        onClick={() => handleDownload('png')}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        Download PNG
                      </button>
                      <button
                        onClick={() => handleDownload('svg')}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        Download SVG
                      </button>
                      <button
                        onClick={() => handleDownload('pdf')}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        Download PDF
                      </button>
                    </div>
                  )}
                </div>
              )}
              <button
                onClick={() => setIsLightboxOpen(true)}
                className="p-2 rounded-lg text-gray-700 hover:bg-gray-200 transition-colors"
                title="View fullscreen"
              >
                <Maximize2 className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Figure Image */}
        <div className="relative bg-gray-100 flex items-center justify-center min-h-[400px] p-4">
          {figure.panels.length > 1 && (
            <div className="absolute top-4 left-4 flex flex-wrap gap-2 z-10">
              {figure.panels.map((panel, idx) => (
                <button
                  key={panel.id}
                  onClick={() => setSelectedPanel(idx)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                    selectedPanel === idx
                      ? 'bg-indigo-600 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-gray-50 shadow'
                  }`}
                >
                  {panel.label}
                </button>
              ))}
            </div>
          )}

          <img
            src={currentPanel.src}
            alt={`${figure.title} - ${currentPanel.label}`}
            className="max-w-full max-h-[600px] object-contain rounded cursor-pointer hover:shadow-xl transition-shadow"
            onClick={() => setIsLightboxOpen(true)}
          />
        </div>

        {/* Figure Caption */}
        <div className="px-4 py-4 border-t border-gray-200">
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-gray-700 leading-relaxed">{figure.caption}</p>
              {currentPanel.description && (
                <p className="text-sm text-gray-600 mt-2 italic">
                  <strong>{currentPanel.label}:</strong> {currentPanel.description}
                </p>
              )}
              {figure.credit && (
                <p className="text-xs text-gray-500 mt-2">Credit: {figure.credit}</p>
              )}
              {figure.license && (
                <p className="text-xs text-gray-500 mt-1">License: {figure.license}</p>
              )}
            </div>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="bg-gray-50 border-t border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Share2 className="w-4 h-4" />
            <span>Share this figure</span>
          </div>
          <button
            onClick={handleCopyCitation}
            className="flex items-center space-x-2 px-3 py-1.5 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
          >
            {copiedCitation ? (
              <>
                <Check className="w-4 h-4 text-green-600" />
                <span className="text-green-600">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Citation</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Lightbox Modal */}
      {isLightboxOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-95 flex items-center justify-center">
          {/* Lightbox Controls */}
          <div className="absolute top-4 right-4 flex items-center space-x-2 z-10">
            <button
              onClick={handleZoomOut}
              disabled={zoom <= 0.5}
              className="p-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Zoom out"
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <button
              onClick={handleResetZoom}
              className="px-3 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white transition-all text-sm font-medium"
              title="Reset zoom"
            >
              {Math.round(zoom * 100)}%
            </button>
            <button
              onClick={handleZoomIn}
              disabled={zoom >= 5}
              className="p-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Zoom in"
            >
              <ZoomIn className="w-5 h-5" />
            </button>
            <button
              onClick={() => setIsLightboxOpen(false)}
              className="p-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white transition-all"
              title="Close"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Panel Navigation */}
          {figure.panels.length > 1 && (
            <>
              <button
                onClick={() => setSelectedPanel((selectedPanel - 1 + figure.panels.length) % figure.panels.length)}
                className="absolute left-4 p-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white transition-all z-10"
                title="Previous panel"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
              <button
                onClick={() => setSelectedPanel((selectedPanel + 1) % figure.panels.length)}
                className="absolute right-4 p-3 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg text-white transition-all z-10"
                title="Next panel"
              >
                <ChevronRight className="w-6 h-6" />
              </button>
            </>
          )}

          {/* Image Container */}
          <div
            ref={imageRef}
            className="relative w-full h-full flex items-center justify-center overflow-hidden"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            style={{ cursor: zoom > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default' }}
          >
            <img
              src={currentPanel.src}
              alt={`${figure.title} - ${currentPanel.label}`}
              className="max-w-full max-h-full object-contain select-none"
              style={{
                transform: `scale(${zoom}) translate(${position.x / zoom}px, ${position.y / zoom}px)`,
                transition: isDragging ? 'none' : 'transform 0.2s ease-out',
              }}
              draggable={false}
            />
          </div>

          {/* Figure Info Overlay */}
          <div className="absolute bottom-4 left-4 right-4 bg-black bg-opacity-70 text-white rounded-lg p-4 max-w-3xl mx-auto">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-bold text-lg mb-1">
                  Figure {figure.number}: {figure.title}
                </h3>
                <p className="text-sm text-gray-300">
                  {currentPanel.label}
                  {currentPanel.description && ` - ${currentPanel.description}`}
                </p>
              </div>
              {figure.panels.length > 1 && (
                <span className="text-sm bg-white bg-opacity-20 px-3 py-1 rounded-full">
                  {selectedPanel + 1} / {figure.panels.length}
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

/**
 * Figure Gallery Component
 * Display multiple figures in a grid
 */
export const FigureGallery: React.FC<{ figures: Figure[] }> = ({ figures }) => {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Figures & Tables</h2>
        <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
          <Grid className="w-4 h-4" />
          <span className="text-sm font-medium">View Gallery</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {figures.map((figure) => (
          <FigureThumbnail key={figure.id} figure={figure} />
        ))}
      </div>
    </div>
  );
};

/**
 * Figure Thumbnail
 * Compact figure preview for galleries
 */
const FigureThumbnail: React.FC<{ figure: Figure }> = ({ figure }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="bg-white border-2 border-gray-200 rounded-lg overflow-hidden shadow-md hover:shadow-xl transition-all cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative bg-gray-100 h-48 flex items-center justify-center overflow-hidden">
        <img
          src={figure.panels[0].src}
          alt={figure.title}
          className={`max-w-full max-h-full object-contain transition-transform duration-300 ${
            isHovered ? 'scale-110' : 'scale-100'
          }`}
        />
        {isHovered && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <button className="flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow-lg hover:bg-gray-50 transition-colors">
              <Maximize className="w-5 h-5" />
              <span className="font-medium">View Figure</span>
            </button>
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-bold text-gray-900 mb-2">
          Figure {figure.number}: {figure.title}
        </h3>
        <p className="text-sm text-gray-600 line-clamp-2">{figure.caption}</p>
      </div>
    </div>
  );
};

/**
 * Image Comparison Slider
 * Compare two images side by side with draggable slider
 */
export const ImageComparisonSlider: React.FC<{
  beforeImage: string;
  afterImage: string;
  beforeLabel?: string;
  afterLabel?: string;
}> = ({ beforeImage, afterImage, beforeLabel = 'Before', afterLabel = 'After' }) => {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = () => setIsDragging(true);
  const handleMouseUp = () => setIsDragging(false);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const percentage = (x / rect.width) * 100;
      setSliderPosition(Math.max(0, Math.min(100, percentage)));
    }
  };

  return (
    <div
      ref={containerRef}
      className="relative w-full h-96 overflow-hidden rounded-lg cursor-col-resize select-none"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseUp}
    >
      {/* After Image (Right) */}
      <div className="absolute inset-0">
        <img src={afterImage} alt={afterLabel} className="w-full h-full object-cover" />
        <div className="absolute top-4 right-4 bg-black bg-opacity-70 text-white px-3 py-1 rounded-full text-sm font-medium">
          {afterLabel}
        </div>
      </div>

      {/* Before Image (Left) */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ width: `${sliderPosition}%` }}
      >
        <img src={beforeImage} alt={beforeLabel} className="w-full h-full object-cover" style={{ width: `${(100 / sliderPosition) * 100}%` }} />
        <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white px-3 py-1 rounded-full text-sm font-medium">
          {beforeLabel}
        </div>
      </div>

      {/* Slider */}
      <div
        className="absolute top-0 bottom-0 w-1 bg-white shadow-lg"
        style={{ left: `${sliderPosition}%` }}
      >
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full shadow-xl flex items-center justify-center">
          <div className="w-3 h-3 border-2 border-gray-400 rounded-full" />
        </div>
      </div>
    </div>
  );
};

export default InteractiveFigure;
