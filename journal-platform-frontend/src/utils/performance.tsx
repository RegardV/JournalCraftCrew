/**
 * Performance Optimization Utilities
 * Phase 4: Performance Optimization
 */

import { useCallback, useMemo, useRef, useEffect, useState } from 'react';
import React from 'react';

// Debounce hook for API calls and search
export function useDebounce<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<number>();

  const debouncedCallback = useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    },
    [callback, delay]
  ) as T;

  return debouncedCallback;
}

// Throttle hook for scroll events and频繁 updates
export function useThrottle<T extends (...args: any[]) => any>(
  callback: T,
  delay: number
): T {
  const lastCallRef = useRef<number>(0);

  const throttledCallback = useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCallRef.current >= delay) {
        lastCallRef.current = now;
        callback(...args);
      }
    },
    [callback, delay]
  ) as T;

  return throttledCallback;
}

// Intersection Observer for lazy loading
export function useIntersectionObserver(
  elementRef: React.RefObject<Element>,
  options: IntersectionObserverInit = {}
) {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsIntersecting(entry.isIntersecting);
        if (entry.isIntersecting && !hasIntersected) {
          setHasIntersected(true);
        }
      },
      {
        threshold: 0.1,
        rootMargin: '50px',
        ...options,
      }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [elementRef, hasIntersected, options]);

  return { isIntersecting, hasIntersected };
}

// Image lazy loading component
export const LazyImage: React.FC<{
  src: string;
  alt: string;
  className?: string;
  placeholder?: string;
}> = React.memo(({ src, alt, className, placeholder = '/placeholder.jpg' }) => {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [imageRef, inView] = useIntersectionObserver();

  useEffect(() => {
    if (inView && src !== imageSrc) {
      const img = new Image();
      img.onload = () => {
        setImageSrc(src);
      };
      img.src = src;
    }
  }, [inView, src, imageSrc]);

  return (
    <img
      ref={imageRef}
      src={imageSrc}
      alt={alt}
      className={className}
      loading="lazy"
    />
  );
});

LazyImage.displayName = 'LazyImage';

// Virtual scrolling helper for large lists
export function useVirtualScrolling<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );

    return items.slice(startIndex, endIndex).map((item, index) => ({
      item,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight,
    }));
  }, [items, scrollTop, itemHeight, containerHeight]);

  const totalHeight = items.length * itemHeight;

  const handleScroll = useCallback(
    (e: React.UIEvent<HTMLDivElement>) => {
      setScrollTop(e.currentTarget.scrollTop);
    },
    []
  );

  return {
    visibleItems,
    totalHeight,
    handleScroll,
  };
}

// Local storage with TTL support
class StorageCache {
  private cache = new Map<string, { data: any; expiry: number }>();

  set(key: string, data: any, ttlMs: number = 5 * 60 * 1000): void {
    const expiry = Date.now() + ttlMs;
    this.cache.set(key, { data, expiry });

    try {
      localStorage.setItem(key, JSON.stringify({ data, expiry }));
    } catch (e) {
      console.warn('LocalStorage write failed:', e);
    }
  }

  get(key: string): any | null {
    // Check memory cache first
    const memoryItem = this.cache.get(key);
    if (memoryItem) {
      if (Date.now() < memoryItem.expiry) {
        return memoryItem.data;
      }
      this.cache.delete(key);
    }

    // Check localStorage
    try {
      const item = localStorage.getItem(key);
      if (item) {
        const parsed = JSON.parse(item);
        if (Date.now() < parsed.expiry) {
          this.cache.set(key, parsed);
          return parsed.data;
        }
        localStorage.removeItem(key);
      }
    } catch (e) {
      console.warn('LocalStorage read failed:', e);
    }

    return null;
  }

  clear(): void {
    this.cache.clear();
    try {
      localStorage.clear();
    } catch (e) {
      console.warn('LocalStorage clear failed:', e);
    }
  }

  size(): number {
    return this.cache.size;
  }
}

export const cache = new StorageCache();

// Resource preloading utility
export function preloadResources(resources: string[]): Promise<void[]> {
  const promises = resources.map(resource => {
    if (resource.endsWith('.js') || resource.endsWith('.css')) {
      return preloadLink(resource, resource.endsWith('.css') ? 'style' : 'script');
    } else if (resource.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
      return preloadImage(resource);
    }
    return Promise.resolve();
  });

  return Promise.all(promises);
}

function preloadLink(href: string, as: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = href;
    link.as = as;
    link.onload = () => resolve();
    link.onerror = reject;
    document.head.appendChild(link);
  });
}

function preloadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve();
    img.onerror = reject;
    img.src = src;
  });
}

// Performance monitoring
export class PerformanceMonitor {
  private static marks = new Map<string, number>();

  static mark(name: string): void {
    this.marks.set(name, performance.now());
  }

  static measure(name: string, startMark?: string): number {
    const endTime = performance.now();
    const startTime = startMark ? this.marks.get(startMark) : this.marks.get(name);

    if (startTime !== undefined) {
      const duration = endTime - startTime;
      console.debug(`Performance: ${name} took ${duration.toFixed(2)}ms`);
      return duration;
    }

    return 0;
  }

  static logMemoryUsage(): void {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      console.debug('Memory usage:', {
        used: `${(memory.usedJSHeapSize / 1048576).toFixed(2)} MB`,
        total: `${(memory.totalJSHeapSize / 1048576).toFixed(2)} MB`,
        limit: `${(memory.jsHeapSizeLimit / 1048576).toFixed(2)} MB`,
      });
    }
  }
}

// Bundle size monitoring
export function logBundleSize(): void {
  if (typeof window !== 'undefined' && 'performance' in window) {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    const transferSize = navigation.transferSize || 0;
    const encodedBodySize = navigation.encodedBodySize || 0;

    console.debug('Bundle sizes:', {
      transferSize: `${(transferSize / 1024).toFixed(2)} KB`,
      encodedBodySize: `${(encodedBodySize / 1024).toFixed(2)} KB`,
    });
  }
}