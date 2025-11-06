/**
 * Performance Monitor Component
 * Phase 4: Performance Optimization
 */

import React, { useEffect, useState } from 'react';
import { PerformanceMonitor, logBundleSize } from '@/utils/performance';

interface PerformanceMetrics {
  memoryUsage?: {
    used: string;
    total: string;
    limit: string;
  };
  bundleSize?: {
    transferSize: string;
    encodedBodySize: string;
  };
  renderTime?: number;
  cacheSize?: number;
}

const PerformanceMonitor: React.FC<{ enabled?: boolean }> = ({ enabled = process.env.NODE_ENV === 'development' }) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({});
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!enabled) return;

    const measurePerformance = () => {
      PerformanceMonitor.mark('performance-check');

      // Measure memory usage
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        setMetrics(prev => ({
          ...prev,
          memoryUsage: {
            used: `${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`,
            total: `${(memory.totalJSHeapSize / 1048576).toFixed(2)} MB`,
            limit: `${(memory.jsHeapSizeLimit / 1048576).toFixed(2)} MB`,
          },
        }));
      }

      // Measure render time
      const renderTime = PerformanceMonitor.measure('performance-check');
      if (renderTime > 0) {
        setMetrics(prev => ({
          ...prev,
          renderTime,
        }));
      }

      // Get bundle size
      logBundleSize();
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        setMetrics(prev => ({
          ...prev,
          bundleSize: {
            transferSize: `${(navigation.transferSize / 1024).toFixed(2)} KB`,
            encodedBodySize: `${(navigation.encodedBodySize / 1024).toFixed(2)} KB`,
          },
        }));
      }
    };

    // Initial measurement
    measurePerformance();

    // Set up periodic measurements
    const interval = setInterval(measurePerformance, 5000);

    return () => clearInterval(interval);
  }, [enabled]);

  // Keyboard shortcut to toggle visibility (Ctrl+Shift+P)
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'P') {
        setIsVisible(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  if (!enabled || !isVisible) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={() => setIsVisible(true)}
          className="bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-50 hover:opacity-100 transition-opacity"
        >
          📊
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 bg-gray-900 text-white text-xs p-4 rounded-lg shadow-lg max-w-sm">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-bold text-green-400">Performance Monitor</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-gray-400 hover:text-white"
        >
          ✕
        </button>
      </div>

      <div className="space-y-2">
        {metrics.memoryUsage && (
          <div>
            <div className="text-gray-400">Memory Usage:</div>
            <div className="text-xs">
              <div>Used: {metrics.memoryUsage.used}</div>
              <div>Total: {metrics.memoryUsage.total}</div>
              <div>Limit: {metrics.memoryUsage.limit}</div>
            </div>
          </div>
        )}

        {metrics.bundleSize && (
          <div>
            <div className="text-gray-400">Bundle Size:</div>
            <div className="text-xs">
              <div>Transfer: {metrics.bundleSize.transferSize}</div>
              <div>Encoded: {metrics.bundleSize.encodedBodySize}</div>
            </div>
          </div>
        )}

        {metrics.renderTime && (
          <div>
            <div className="text-gray-400">Last Render:</div>
            <div className="text-xs">{metrics.renderTime.toFixed(2)}ms</div>
          </div>
        )}

        <div className="pt-2 border-t border-gray-700">
          <button
            onClick={() => PerformanceMonitor.logMemoryUsage()}
            className="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-xs mr-2"
          >
            Log Memory
          </button>
          <button
            onClick={() => logBundleSize()}
            className="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs"
          >
            Log Bundle
          </button>
        </div>

        <div className="text-gray-500 text-xs mt-2">
          Press Ctrl+Shift+P to toggle
        </div>
      </div>
    </div>
  );
};

export default PerformanceMonitor;