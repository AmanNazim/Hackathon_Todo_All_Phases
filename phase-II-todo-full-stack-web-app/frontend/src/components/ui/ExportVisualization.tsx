'use client';

import React, { useRef } from 'react';
import Button from '../ui/Button';

interface ExportVisualizationProps {
  elementId: string;
  filename?: string;
  title?: string;
  className?: string;
}

export default function ExportVisualization({
  elementId,
  filename = 'visualization',
  title = 'Export Visualization',
  className = '',
}: ExportVisualizationProps) {
  const exportToPNG = async () => {
    const element = document.getElementById(elementId);
    if (!element) {
      alert('Element not found');
      return;
    }

    try {
      // Use html2canvas library (would need to be installed)
      // For now, using a canvas-based approach
      const canvas = await htmlToCanvas(element);
      const dataUrl = canvas.toDataURL('image/png');

      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = `${filename}-${new Date().toISOString().split('T')[0]}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Failed to export PNG:', error);
      alert('Failed to export as PNG');
    }
  };

  const exportToSVG = () => {
    const element = document.getElementById(elementId);
    if (!element) {
      alert('Element not found');
      return;
    }

    try {
      const svgData = elementToSVG(element);
      const blob = new Blob([svgData], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = `${filename}-${new Date().toISOString().split('T')[0]}.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export SVG:', error);
      alert('Failed to export as SVG');
    }
  };

  const exportToPDF = async () => {
    const element = document.getElementById(elementId);
    if (!element) {
      alert('Element not found');
      return;
    }

    try {
      // This would use jsPDF library in production
      // For now, print to PDF using browser's print dialog
      const printWindow = window.open('', '_blank');
      if (!printWindow) {
        alert('Please allow popups to export PDF');
        return;
      }

      const styles = Array.from(document.styleSheets)
        .map((styleSheet) => {
          try {
            return Array.from(styleSheet.cssRules)
              .map((rule) => rule.cssText)
              .join('\n');
          } catch (e) {
            return '';
          }
        })
        .join('\n');

      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>${filename}</title>
            <style>${styles}</style>
            <style>
              @media print {
                body { margin: 0; padding: 20px; }
                @page { margin: 0; }
              }
            </style>
          </head>
          <body>
            ${element.outerHTML}
          </body>
        </html>
      `);
      printWindow.document.close();

      setTimeout(() => {
        printWindow.print();
      }, 250);
    } catch (error) {
      console.error('Failed to export PDF:', error);
      alert('Failed to export as PDF');
    }
  };

  const copyToClipboard = async () => {
    const element = document.getElementById(elementId);
    if (!element) {
      alert('Element not found');
      return;
    }

    try {
      const canvas = await htmlToCanvas(element);
      canvas.toBlob(async (blob) => {
        if (!blob) {
          throw new Error('Failed to create blob');
        }

        await navigator.clipboard.write([
          new ClipboardItem({ 'image/png': blob }),
        ]);

        alert('Copied to clipboard!');
      });
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      alert('Failed to copy to clipboard');
    }
  };

  // Helper function to convert HTML element to canvas
  const htmlToCanvas = async (element: HTMLElement): Promise<HTMLCanvasElement> => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('Failed to get canvas context');

    const rect = element.getBoundingClientRect();
    canvas.width = rect.width * 2; // 2x for better quality
    canvas.height = rect.height * 2;
    ctx.scale(2, 2);

    // Draw white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // This is a simplified version - in production, use html2canvas library
    // For now, we'll use a basic approach
    return canvas;
  };

  // Helper function to convert element to SVG
  const elementToSVG = (element: HTMLElement): string => {
    const rect = element.getBoundingClientRect();
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" width="${rect.width}" height="${rect.height}">
        <foreignObject width="100%" height="100%">
          <div xmlns="http://www.w3.org/1999/xhtml">
            ${element.outerHTML}
          </div>
        </foreignObject>
      </svg>
    `;
    return svg;
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-sm text-gray-600 dark:text-gray-400">{title}:</span>

      <Button onClick={exportToPNG} variant="secondary" size="sm">
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        PNG
      </Button>

      <Button onClick={exportToSVG} variant="secondary" size="sm">
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
          />
        </svg>
        SVG
      </Button>

      <Button onClick={exportToPDF} variant="secondary" size="sm">
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
          />
        </svg>
        PDF
      </Button>

      <Button onClick={copyToClipboard} variant="secondary" size="sm">
        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
        Copy
      </Button>
    </div>
  );
}

// Wrapper component for easy integration with charts and visualizations
interface ExportableVisualizationProps {
  children: React.ReactNode;
  filename?: string;
  title?: string;
  showExportButtons?: boolean;
  className?: string;
}

export function ExportableVisualization({
  children,
  filename = 'visualization',
  title,
  showExportButtons = true,
  className = '',
}: ExportableVisualizationProps) {
  const elementId = `exportable-${filename}-${Date.now()}`;

  return (
    <div className={className}>
      {showExportButtons && (
        <div className="mb-4 flex justify-end">
          <ExportVisualization
            elementId={elementId}
            filename={filename}
            title={title || 'Export'}
          />
        </div>
      )}
      <div id={elementId}>{children}</div>
    </div>
  );
}
