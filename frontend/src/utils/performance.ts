/**
 * Performance Monitoring and Optimization Utilities
 * Implements performance monitoring and optimization techniques to meet <2s load time goal
 */

// Performance monitoring
export const measurePerformance = (name: string, fn: () => any) => {
  if (typeof window !== 'undefined' && 'performance' in window) {
    performance.mark(`${name}-start`);
    const result = fn();
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);

    const measure = performance.getEntriesByName(name)[0];
    console.log(`Performance measurement for ${name}: ${measure.duration.toFixed(2)}ms`);

    return result;
  } else {
    return fn();
  }
};

// Debounce utility for performance
export const debounce = <T extends (...args: any[]) => any>(func: T, wait: number) => {
  let timeout: NodeJS.Timeout;
  return ((...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  }) as T;
};

// Memoize utility for performance
export const memoize = <T extends (...args: any[]) => any>(func: T) => {
  const cache = new Map<string, ReturnType<T>>();
  return (...args: Parameters<T>): ReturnType<T> => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key)!;
    }
    const result = func(...args);
    cache.set(key, result);
    return result;
  };
};

// Image optimization helper
export const getImageOptimizedUrl = (url: string, width: number, height: number) => {
  // For Next.js Image optimization, we would typically use the next/image component
  // This is a helper for external image optimization
  if (url.includes('unsplash.com')) {
    return `${url}&w=${width}&h=${height}&fit=crop&auto=format`;
  }
  return url;
};

// Preload resources
export const preloadResource = (url: string, as: 'script' | 'style' | 'image' | 'font') => {
  if (typeof document !== 'undefined') {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = as;
    document.head.appendChild(link);
  }
};

// Lazy load components with error boundary
export const lazyLoadWithRetry = async <T>(
  importFn: () => Promise<{ default: T }>,
  retries = 3
): Promise<{ default: T }> => {
  for (let i = 0; i < retries; i++) {
    try {
      return await importFn();
    } catch (error) {
      if (i === retries - 1) throw error;
      // Wait progressively longer between retries
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
  throw new Error('Failed to load module after retries');
};

// Performance observer for long tasks
export const setupLongTaskObserver = () => {
  if ('PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.duration > 50) { // Long task threshold
          console.warn('Long task detected:', entry);
        }
      });
    });
    observer.observe({ entryTypes: ['longtask'] });
  }
};

// Initialize performance monitoring
export const initPerformanceMonitoring = () => {
  if (typeof window !== 'undefined') {
    // Track initial page load time
    window.addEventListener('load', () => {
      const pageLoadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
      console.log(`Page load time: ${pageLoadTime}ms`);

      // Report to analytics if needed
      if (pageLoadTime > 2000) {
        console.warn(`⚠️ Page load time exceeded 2s: ${pageLoadTime}ms`);
      } else {
        console.log(`✅ Page load time under 2s: ${pageLoadTime}ms`);
      }
    });
  }
};