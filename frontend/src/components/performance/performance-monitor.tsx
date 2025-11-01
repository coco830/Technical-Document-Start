"use client"

import { useEffect, useRef, useState } from "react"
import { performance } from "perf_hooks"

interface PerformanceMetrics {
  fcp: number // First Contentful Paint
  lcp: number // Largest Contentful Paint
  fid: number // First Input Delay
  cls: number // Cumulative Layout Shift
  ttfb: number // Time to First Byte
  loadTime: number // 页面加载时间
  renderTime: number // 渲染时间
  memoryUsage: number // 内存使用量
  bundleSize: number // 包大小
}

interface PerformanceEntry {
  name: string
  value: number
  threshold: number
  status: "good" | "needs-improvement" | "poor"
}

export function PerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const observerRef = useRef<PerformanceObserver | null>(null)
  
  useEffect(() => {
    // 只在生产环境或开发模式下启用
    if (process.env.NODE_ENV === "production" || process.env.NEXT_PUBLIC_ENABLE_PERFORMANCE_MONITORING === "true") {
      initializePerformanceMonitoring()
    }
  }, [])
  
  const initializePerformanceMonitoring = () => {
    // 监控页面加载性能
    monitorPageLoad()
    
    // 监控Core Web Vitals
    monitorCoreWebVitals()
    
    // 监控资源加载
    monitorResourceLoading()
    
    // 监控内存使用
    monitorMemoryUsage()
    
    // 监控长任务
    monitorLongTasks()
  }
  
  const monitorPageLoad = () => {
    window.addEventListener("load", () => {
      const navigation = performance.getEntriesByType("navigation")[0] as PerformanceNavigationTiming
      
      if (navigation) {
        const loadTime = navigation.loadEventEnd - navigation.navigationStart
        const ttfb = navigation.responseStart - navigation.requestStart
        const domContentLoaded = navigation.domContentLoadedEventEnd - navigation.navigationStart
        
        setMetrics(prev => ({
          ...prev!,
          loadTime,
          ttfb,
          renderTime: domContentLoaded
        }))
      }
    })
  }
  
  const monitorCoreWebVitals = () => {
    // 使用web-vitals库监控Core Web Vitals
    import("web-vitals").then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS((metric) => {
        setMetrics(prev => ({ ...prev!, cls: metric.value }))
      })
      
      getFID((metric) => {
        setMetrics(prev => ({ ...prev!, fid: metric.value }))
      })
      
      getFCP((metric) => {
        setMetrics(prev => ({ ...prev!, fcp: metric.value }))
      })
      
      getLCP((metric) => {
        setMetrics(prev => ({ ...prev!, lcp: metric.value }))
      })
      
      getTTFB((metric) => {
        setMetrics(prev => ({ ...prev!, ttfb: metric.value }))
      })
    }).catch(err => {
      console.warn("Failed to load web-vitals library:", err)
    })
  }
  
  const monitorResourceLoading = () => {
    if ("PerformanceObserver" in window) {
      observerRef.current = new PerformanceObserver((list) => {
        const resources = list.getEntries()
        let totalSize = 0
        
        resources.forEach((resource) => {
          if ("transferSize" in resource) {
            totalSize += (resource as any).transferSize
          }
        })
        
        setMetrics(prev => ({ ...prev!, bundleSize: totalSize }))
      })
      
      observerRef.current.observe({ entryTypes: ["resource"] })
    }
  }
  
  const monitorMemoryUsage = () => {
    if ("memory" in performance) {
      const updateMemoryUsage = () => {
        const memory = (performance as any).memory
        setMetrics(prev => ({ 
          ...prev!, 
          memoryUsage: Math.round(memory.usedJSHeapSize / 1048576) // MB
        }))
      }
      
      // 初始更新
      updateMemoryUsage()
      
      // 定期更新
      const interval = setInterval(updateMemoryUsage, 5000)
      
      return () => clearInterval(interval)
    }
  }
  
  const monitorLongTasks = () => {
    if ("PerformanceObserver" in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry) => {
          if (entry.duration > 50) { // 超过50ms的任务
            console.warn("Long task detected:", {
              name: entry.name,
              duration: entry.duration,
              startTime: entry.startTime
            })
          }
        })
      })
      
      observer.observe({ entryTypes: ["longtask"] })
    }
  }
  
  const getPerformanceStatus = (value: number, thresholds: { good: number, poor: number }) => {
    if (value <= thresholds.good) return "good"
    if (value <= thresholds.poor) return "needs-improvement"
    return "poor"
  }
  
  const performanceEntries: PerformanceEntry[] = [
    {
      name: "First Contentful Paint (FCP)",
      value: metrics?.fcp || 0,
      threshold: 1.8, // 秒
      status: metrics ? getPerformanceStatus(metrics.fcp, { good: 1.0, poor: 3.0 }) : "good"
    },
    {
      name: "Largest Contentful Paint (LCP)",
      value: metrics?.lcp || 0,
      threshold: 2.5, // 秒
      status: metrics ? getPerformanceStatus(metrics.lcp, { good: 1.2, poor: 4.0 }) : "good"
    },
    {
      name: "First Input Delay (FID)",
      value: metrics?.fid || 0,
      threshold: 100, // 毫秒
      status: metrics ? getPerformanceStatus(metrics.fid, { good: 50, poor: 300 }) : "good"
    },
    {
      name: "Cumulative Layout Shift (CLS)",
      value: metrics?.cls || 0,
      threshold: 0.1,
      status: metrics ? getPerformanceStatus(metrics.cls, { good: 0.025, poor: 0.25 }) : "good"
    },
    {
      name: "Time to First Byte (TTFB)",
      value: metrics?.ttfb || 0,
      threshold: 800, // 毫秒
      status: metrics ? getPerformanceStatus(metrics.ttfb, { good: 400, poor: 1600 }) : "good"
    },
    {
      name: "页面加载时间",
      value: metrics?.loadTime || 0,
      threshold: 3000, // 毫秒
      status: metrics ? getPerformanceStatus(metrics.loadTime, { good: 1500, poor: 4000 }) : "good"
    },
    {
      name: "内存使用量",
      value: metrics?.memoryUsage || 0,
      threshold: 50, // MB
      status: metrics ? getPerformanceStatus(metrics.memoryUsage, { good: 20, poor: 80 }) : "good"
    }
  ]
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case "good": return "text-green-600"
      case "needs-improvement": return "text-yellow-600"
      case "poor": return "text-red-600"
      default: return "text-gray-600"
    }
  }
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "good": return "✅"
      case "needs-improvement": return "⚠️"
      case "poor": return "❌"
      default: return "❓"
    }
  }
  
  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setIsVisible(!isVisible)}
        className="bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700 transition-colors"
        aria-label="Toggle performance monitor"
      >
        📊
      </button>
      
      {isVisible && (
        <div className="bg-white rounded-lg shadow-xl p-4 w-80 max-h-96 overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">性能监控</h3>
            <button
              onClick={() => setIsVisible(false)}
              className="text-gray-500 hover:text-gray-700"
              aria-label="Close performance monitor"
            >
              ✕
            </button>
          </div>
          
          {metrics ? (
            <div className="space-y-3">
              {performanceEntries.map((entry, index) => (
                <div key={index} className="border-b pb-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{entry.name}</span>
                    <span className={`text-sm ${getStatusColor(entry.status)}`}>
                      {getStatusIcon(entry.status)} {entry.value.toFixed(2)}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    阈值: {entry.threshold}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-4">
              性能数据收集中...
            </div>
          )}
          
          <div className="mt-4 pt-2 border-t">
            <button
              onClick={() => {
                // 发送性能数据到分析服务
                if (metrics) {
                  fetch("/api/analytics/performance", {
                    method: "POST",
                    headers: {
                      "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                      url: window.location.href,
                      userAgent: navigator.userAgent,
                      timestamp: new Date().toISOString(),
                      metrics,
                    }),
                  }).catch(err => {
                    console.error("Failed to send performance data:", err)
                  })
                }
              }}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition-colors"
            >
              发送性能数据
            </button>
          </div>
        </div>
      )}
    </div>
  )
}