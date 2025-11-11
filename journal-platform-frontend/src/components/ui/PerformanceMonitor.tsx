/**
 * Performance Monitor Component
 * Phase 4: Performance Optimization
 */

import React, { useEffect, useState } from 'react';
// import { PerformanceMonitor as PerfUtils, logBundleSize } from '@/utils/performance';

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

const PerformanceMonitor: React.FC<{ enabled?: boolean }> = ({ enabled = false }) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({});
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!enabled) return;

    // Performance monitoring disabled for now
    return;
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

  // Performance monitor disabled for now
  return null;
};

export default PerformanceMonitor;