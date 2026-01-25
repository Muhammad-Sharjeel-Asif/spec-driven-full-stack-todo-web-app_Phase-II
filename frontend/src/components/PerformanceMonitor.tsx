'use client';

import { useEffect } from 'react';
import {
  initPerformanceMonitoring,
  setupLongTaskObserver
} from '@/utils/performance';

interface PerformanceMonitorProps {
  children: React.ReactNode;
}

/**
 * Performance Monitor Component
 * Tracks and reports performance metrics to help ensure <2s load times
 */
export default function PerformanceMonitor({ children }: PerformanceMonitorProps) {
  useEffect(() => {
    // Initialize performance monitoring
    initPerformanceMonitoring();

    // Set up long task observer
    setupLongTaskObserver();

    // Track when component mounts as a performance milestone
    if (typeof performance !== 'undefined') {
      performance.mark('component-mount-start');
    }

    return () => {
      if (typeof performance !== 'undefined') {
        performance.mark('component-unmount');
        performance.measure('component-lifecycle', 'component-mount-start', 'component-unmount');
      }
    };
  }, []);

  return <>{children}</>;
}