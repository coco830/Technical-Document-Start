/**
 * 前端错误处理工具模块
 * 提供错误分类、用户友好提示、重试机制和错误监控
 */

import React from 'react';

// 错误严重程度
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// 错误分类
export enum ErrorCategory {
  NETWORK = 'network',
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  VALIDATION = 'validation',
  EXTERNAL_SERVICE = 'external_service',
  INTERNAL = 'internal',
  TIMEOUT = 'timeout',
  RATE_LIMIT = 'rate_limit'
}

// 错误信息接口
export interface ErrorInfo {
  error: Error | AxiosError;
  category: ErrorCategory;
  severity: ErrorSeverity;
  context?: Record<string, any>;
  userMessage?: string;
  timestamp: Date;
  stack?: string;
}

// 错误监控器
export class ErrorMonitor {
  private errors: ErrorInfo[] = [];
  private maxErrors: number = 1000;
  private errorCounts: Record<string, number> = {};
  private errorCountsByCategory: Record<ErrorCategory, number> = {
    [ErrorCategory.NETWORK]: 0,
    [ErrorCategory.AUTHENTICATION]: 0,
    [ErrorCategory.AUTHORIZATION]: 0,
    [ErrorCategory.VALIDATION]: 0,
    [ErrorCategory.EXTERNAL_SERVICE]: 0,
    [ErrorCategory.INTERNAL]: 0,
    [ErrorCategory.TIMEOUT]: 0,
    [ErrorCategory.RATE_LIMIT]: 0
  };
  private errorCountsBySeverity: Record<ErrorSeverity, number> = {
    [ErrorSeverity.LOW]: 0,
    [ErrorSeverity.MEDIUM]: 0,
    [ErrorSeverity.HIGH]: 0,
    [ErrorSeverity.CRITICAL]: 0
  };

  constructor(maxErrors: number = 1000) {
    this.maxErrors = maxErrors;
  }

  recordError(errorInfo: ErrorInfo): void {
    this.errors.push(errorInfo);
    
    // 保持错误列表大小
    if (this.errors.length > this.maxErrors) {
      this.errors.shift();
    }
    
    // 更新计数
    const errorKey = `${errorInfo.error.constructor.name}:${errorInfo.category}`;
    this.errorCounts[errorKey] = (this.errorCounts[errorKey] || 0) + 1;
    this.errorCountsByCategory[errorInfo.category] = 
      (this.errorCountsByCategory[errorInfo.category] || 0) + 1;
    this.errorCountsBySeverity[errorInfo.severity] = 
      (this.errorCountsBySeverity[errorInfo.severity] || 0) + 1;
    
    // 记录到控制台
    const logLevel = {
      [ErrorSeverity.LOW]: 'info',
      [ErrorSeverity.MEDIUM]: 'warn',
      [ErrorSeverity.HIGH]: 'error',
      [ErrorSeverity.CRITICAL]: 'error'
    }[errorInfo.severity] || 'warn';
    
    (console as any)[logLevel]('Error recorded:', errorInfo);
  }

  getErrorSummary(): Record<string, any> {
    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    
    const recentErrors = this.errors.filter(
      error => error.timestamp > oneDayAgo
    );
    
    return {
      totalErrors: this.errors.length,
      recentErrors24h: recentErrors.length,
      errorCounts: this.errorCounts,
      errorsByCategory: Object.fromEntries(
        Object.entries(this.errorCountsByCategory).map(([key, value]) => [key, value])
      ),
      errorsBySeverity: Object.fromEntries(
        Object.entries(this.errorCountsBySeverity).map(([key, value]) => [key, value])
      ),
      recentCriticalErrors: recentErrors
        .filter(error => error.severity === ErrorSeverity.CRITICAL)
        .map(error => this.errorInfoToObject(error))
    };
  }

  private errorInfoToObject(errorInfo: ErrorInfo): Record<string, any> {
    return {
      errorType: errorInfo.error.constructor.name,
      errorMessage: errorInfo.error.message,
      category: errorInfo.category,
      severity: errorInfo.severity,
      context: errorInfo.context,
      userMessage: errorInfo.userMessage,
      timestamp: errorInfo.timestamp.toISOString(),
      stack: errorInfo.stack
    };
  }
}

// 重试策略
export class RetryPolicy {
  private maxAttempts: number;
  private baseDelay: number;
  private maxDelay: number;
  private exponentialBase: number;
  private jitter: boolean;

  constructor(options: {
    maxAttempts?: number;
    baseDelay?: number;
    maxDelay?: number;
    exponentialBase?: number;
    jitter?: boolean;
  } = {}) {
    this.maxAttempts = options.maxAttempts || 3;
    this.baseDelay = options.baseDelay || 1000;
    this.maxDelay = options.maxDelay || 60000;
    this.exponentialBase = options.exponentialBase || 2;
    this.jitter = options.jitter !== false;
  }

  async execute<T>(
    fn: () => Promise<T>,
    context?: Record<string, any>
  ): Promise<T> {
    let lastError: Error;
    
    for (let attempt = 0; attempt < this.maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === this.maxAttempts - 1) {
          break;
        }
        
        const delay = this.calculateDelay(attempt);
        console.warn(`Attempt ${attempt + 1} failed. Retrying in ${delay}ms:`, error);
        
        await this.sleep(delay);
      }
    }
    
    throw lastError!;
  }

  private calculateDelay(attempt: number): number {
    let delay = this.baseDelay * Math.pow(this.exponentialBase, attempt);
    delay = Math.min(delay, this.maxDelay);
    
    if (this.jitter) {
      delay *= (0.5 + Math.random() * 0.5);
    }
    
    return delay;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// 降级处理器
export class FallbackHandler {
  private fallbacks: Record<string, (...args: any[]) => any> = {};

  register(serviceName: string, fallbackFunc: (...args: any[]) => any): void {
    this.fallbacks[serviceName] = fallbackFunc;
    console.info(`Registered fallback for ${serviceName}`);
  }

  getFallback(serviceName: string): ((...args: any[]) => any) | undefined {
    return this.fallbacks[serviceName];
  }

  async executeFallback(serviceName: string, ...args: any[]): Promise<any> {
    const fallback = this.getFallback(serviceName);
    if (fallback) {
      console.info(`Executing fallback for ${serviceName}`);
      return await fallback(...args);
    } else {
      throw new Error(`No fallback registered for ${serviceName}`);
    }
  }
}

// Axios错误类型定义
interface AxiosError extends Error {
  config?: any;
  code?: string;
  request?: any;
  response?: {
    data?: any;
    status?: number;
    headers?: any;
  };
  isAxiosError?: boolean;
}

// 错误分类函数
export function classifyError(error: Error | AxiosError): [ErrorCategory, ErrorSeverity] {
  const errorType = error.constructor.name;
  const errorMessage = error.message.toLowerCase();
  
  // 网络错误
  if (
    errorMessage.includes('network') ||
    errorMessage.includes('connection') ||
    errorMessage.includes('timeout') ||
    errorMessage.includes('fetch') ||
    errorType === 'NetworkError' ||
    errorType === 'TypeError' && errorMessage.includes('failed to fetch')
  ) {
    return [ErrorCategory.NETWORK, ErrorSeverity.HIGH];
  }
  
  // Axios网络错误
  if ((error as AxiosError).isAxiosError && !(error as AxiosError).response) {
    return [ErrorCategory.NETWORK, ErrorSeverity.HIGH];
  }
  
  // 认证错误
  if (
    errorMessage.includes('unauthorized') ||
    errorMessage.includes('authentication') ||
    errorMessage.includes('login') ||
    errorMessage.includes('credential') ||
    (error as AxiosError).response?.status === 401
  ) {
    return [ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM];
  }
  
  // 授权错误
  if (
    errorMessage.includes('forbidden') ||
    errorMessage.includes('permission') ||
    errorMessage.includes('access denied') ||
    (error as AxiosError).response?.status === 403
  ) {
    return [ErrorCategory.AUTHORIZATION, ErrorSeverity.MEDIUM];
  }
  
  // 验证错误
  if (
    errorMessage.includes('validation') ||
    errorMessage.includes('invalid') ||
    errorMessage.includes('required') ||
    errorMessage.includes('format') ||
    (error as AxiosError).response?.status === 400
  ) {
    return [ErrorCategory.VALIDATION, ErrorSeverity.LOW];
  }
  
  // 外部服务错误
  if (
    errorMessage.includes('external') ||
    errorMessage.includes('third party') ||
    errorMessage.includes('api') ||
    errorMessage.includes('service')
  ) {
    return [ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.HIGH];
  }
  
  // 服务器错误
  const axiosError = error as AxiosError;
  if (axiosError.response && typeof axiosError.response.status === 'number' && axiosError.response.status >= 500) {
    return [ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.HIGH];
  }
  
  // 超时错误
  if (
    errorMessage.includes('timeout') ||
    errorType === 'TimeoutError' ||
    (error as AxiosError).code === 'ECONNABORTED'
  ) {
    return [ErrorCategory.TIMEOUT, ErrorSeverity.HIGH];
  }
  
  // 限流错误
  if (
    errorMessage.includes('rate limit') ||
    errorMessage.includes('too many requests') ||
    errorMessage.includes('quota') ||
    (error as AxiosError).response?.status === 429
  ) {
    return [ErrorCategory.RATE_LIMIT, ErrorSeverity.MEDIUM];
  }
  
  // 默认为内部错误
  return [ErrorCategory.INTERNAL, ErrorSeverity.MEDIUM];
}

// 获取用户友好的错误消息
export function getUserFriendlyMessage(errorInfo: ErrorInfo): string {
  if (errorInfo.userMessage) {
    return errorInfo.userMessage;
  }
  
  const categoryMessages: Record<ErrorCategory, string> = {
    [ErrorCategory.NETWORK]: '网络连接出现问题，请检查您的网络连接后重试',
    [ErrorCategory.AUTHENTICATION]: '身份验证失败，请重新登录',
    [ErrorCategory.AUTHORIZATION]: '您没有权限执行此操作',
    [ErrorCategory.VALIDATION]: '输入数据格式不正确，请检查后重试',
    [ErrorCategory.EXTERNAL_SERVICE]: '外部服务暂时不可用，请稍后重试',
    [ErrorCategory.INTERNAL]: '系统内部错误，请联系管理员',
    [ErrorCategory.TIMEOUT]: '请求超时，请稍后重试',
    [ErrorCategory.RATE_LIMIT]: '请求过于频繁，请稍后再试'
  };
  
  return categoryMessages[errorInfo.category] || '未知错误，请稍后重试';
}

// 统一错误处理函数
export function handleError(
  error: Error | AxiosError,
  context?: Record<string, any>,
  userMessage?: string
): ErrorInfo {
  const [category, severity] = classifyError(error);
  
  const errorInfo: ErrorInfo = {
    error,
    category,
    severity,
    context,
    userMessage,
    timestamp: new Date(),
    stack: error.stack
  };
  
  // 记录错误
  errorMonitor.recordError(errorInfo);
  
  return errorInfo;
}

// 错误处理装饰器
export function withErrorHandling(options: {
  fallbackService?: string;
  retryPolicy?: RetryPolicy;
  context?: Record<string, any>;
  userMessage?: string;
} = {}) {
  return function<T extends (...args: any[]) => Promise<any>>(
    target: any,
    propertyName: string,
    descriptor: TypedPropertyDescriptor<T>
  ) {
    const method = descriptor.value!;
    
    descriptor.value = async function(this: any, ...args: any[]) {
      try {
        // 应用重试策略
        if (options.retryPolicy) {
          return await options.retryPolicy.execute(
            () => method.apply(this, args),
            { ...options.context, method: propertyName }
          );
        } else {
          return await method.apply(this, args);
        }
      } catch (error) {
        const errorInfo = handleError(
          error as Error,
          {
            ...options.context,
            method: propertyName,
            args: JSON.stringify(args).substring(0, 200) // 限制长度
          },
          options.userMessage
        );
        
        // 尝试降级处理
        if (options.fallbackService) {
          try {
            return await fallbackHandler.executeFallback(
              options.fallbackService,
              ...args
            );
          } catch (fallbackError) {
            console.error(`Fallback failed for ${options.fallbackService}:`, fallbackError);
          }
        }
        
        // 重新抛出原始错误
        throw error;
      }
    } as T;
    
    return descriptor;
  };
}

// 全局实例
export const errorMonitor = new ErrorMonitor();
export const fallbackHandler = new FallbackHandler();

// 默认重试策略
export const defaultRetryPolicy = new RetryPolicy({
  maxAttempts: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  exponentialBase: 2,
  jitter: true
});

// 错误边界组件的辅助函数
export function createErrorBoundaryFallback(
  error: Error,
  resetErrorBoundary: () => void
): React.ReactElement {
  const errorInfo = handleError(error);
  const userMessage = getUserFriendlyMessage(errorInfo);
  
  return React.createElement('div', {
    className: "error-boundary-fallback p-6 bg-red-50 border border-red-200 rounded-lg"
  }, [
    React.createElement('h2', {
      key: 'title',
      className: "text-xl font-semibold text-red-800 mb-2"
    }, '出现错误'),
    React.createElement('p', {
      key: 'message',
      className: "text-red-600 mb-4"
    }, userMessage),
    React.createElement('button', {
      key: 'retry',
      onClick: resetErrorBoundary,
      className: "px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
    }, '重试'),
    ...(process.env.NODE_ENV === 'development' ? [
      React.createElement('details', {
        key: 'details',
        className: "mt-4"
      }, [
        React.createElement('summary', {
          key: 'summary',
          className: "cursor-pointer text-red-500"
        }, '错误详情'),
        React.createElement('pre', {
          key: 'stack',
          className: "mt-2 p-2 bg-red-100 text-xs overflow-auto"
        }, error.stack || 'No stack trace available')
      ])
    ] : [])
  ]);
}

// 导出默认配置
export const ERROR_CONFIG = {
  // 自动重试的错误类型
  RETRYABLE_ERRORS: [
    ErrorCategory.NETWORK,
    ErrorCategory.TIMEOUT,
    ErrorCategory.EXTERNAL_SERVICE
  ],
  
  // 需要用户重新认证的错误
  AUTH_ERRORS: [
    ErrorCategory.AUTHENTICATION
  ],
  
  // 需要降级处理的错误
  FALLBACK_ERRORS: [
    ErrorCategory.EXTERNAL_SERVICE,
    ErrorCategory.NETWORK
  ]
};