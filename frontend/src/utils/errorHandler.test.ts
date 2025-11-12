/**
 * 前端错误处理机制测试
 * 测试错误分类、重试机制、降级策略和监控功能
 */

import {
  ErrorSeverity,
  ErrorCategory,
  ErrorMonitor,
  RetryPolicy,
  FallbackHandler,
  classifyError,
  handleError,
  getUserFriendlyMessage,
  errorMonitor,
  fallbackHandler,
  defaultRetryPolicy
} from './errorHandler';

// 模拟AxiosError
class MockAxiosError extends Error {
  response?: { status?: number; data?: any };
  request?: any;
  config?: any;
  isAxiosError = true;

  constructor(message: string, status?: number) {
    super(message);
    if (status) {
      this.response = { status };
    }
  }
}

// 测试错误分类
function testErrorClassification(): void {
  console.log('=== 测试错误分类 ===');

  const testCases = [
    { error: new MockAxiosError('Network Error'), expected: ErrorCategory.NETWORK },
    { error: new MockAxiosError('Unauthorized', 401), expected: ErrorCategory.AUTHENTICATION },
    { error: new MockAxiosError('Forbidden', 403), expected: ErrorCategory.AUTHORIZATION },
    { error: new MockAxiosError('Bad Request', 400), expected: ErrorCategory.VALIDATION },
    { error: new MockAxiosError('Internal Server Error', 500), expected: ErrorCategory.EXTERNAL_SERVICE },
    { error: new MockAxiosError('Too Many Requests', 429), expected: ErrorCategory.RATE_LIMIT },
    { error: new Error('Internal error'), expected: ErrorCategory.INTERNAL },
  ];

  testCases.forEach(({ error, expected }) => {
    const [category, severity] = classifyError(error);
    console.log(`错误: ${error.message} - 分类: ${category}, 严重程度: ${severity}`);
    if (category !== expected) {
      console.error(`分类错误: 期望 ${expected}, 实际 ${category}`);
    }
  });
}

// 测试错误监控
function testErrorMonitoring(): void {
  console.log('\n=== 测试错误监控 ===');

  const monitor = new ErrorMonitor();

  // 创建测试错误
  const testErrors = [
    new Error('测试错误1'),
    new MockAxiosError('测试网络错误'),
    new MockAxiosError('测试验证错误', 400),
  ];

  testErrors.forEach(error => {
    const errorInfo = handleError(error, { test: true }, '测试用户消息');
    monitor.recordError(errorInfo);
    console.log(`记录错误: ${error.constructor.name}`);
  });

  // 获取错误摘要
  const summary = monitor.getErrorSummary();
  console.log('错误摘要:', JSON.stringify(summary, null, 2));

  if (summary.totalErrors < 3) {
    console.error('错误数量不正确');
  }
}

// 测试重试策略
async function testRetryPolicy(): Promise<void> {
  console.log('\n=== 测试重试策略 ===');

  const retryPolicy = new RetryPolicy({
    maxAttempts: 3,
    baseDelay: 100,
    maxDelay: 1000
  });

  let attemptCount = 0;

  const sometimesFailingFunction = async (): Promise<string> => {
    attemptCount++;
    if (attemptCount < 3) {
      throw new Error(`第${attemptCount}次失败`);
    }
    return '成功';
  };

  try {
    const result = await retryPolicy.execute(sometimesFailingFunction);
    console.log(`重试成功: ${result}`);
    if (result !== '成功') {
      console.error('重试策略未正常工作');
    }
    if (attemptCount !== 3) {
      console.error(`重试次数不正确: ${attemptCount}`);
    }
  } catch (error) {
    console.error(`重试失败: ${error}`);
  }
}

// 测试降级处理器
async function testFallbackHandler(): Promise<void> {
  console.log('\n=== 测试降级处理器 ===');

  const handler = new FallbackHandler();

  // 注册降级函数
  const testFallback = (...args: any[]): any => {
    return { data: '降级数据', fallback: true, args };
  };

  handler.register('test_service', testFallback);

  // 测试降级执行
  try {
    const result = await handler.executeFallback('test_service', 'arg1', 'arg2');
    console.log('降级执行结果:', result);
    if (!result.fallback) {
      console.error('降级函数未正常执行');
    }
  } catch (error) {
    console.error(`降级执行失败: ${error}`);
  }
}

// 测试用户友好消息
function testUserFriendlyMessages(): void {
  console.log('\n=== 测试用户友好消息 ===');

  const testCases = [
    { error: new MockAxiosError('Network Error'), expected: '网络连接出现问题，请检查您的网络连接后重试' },
    { error: new MockAxiosError('Unauthorized', 401), expected: '身份验证失败，请重新登录' },
    { error: new MockAxiosError('Forbidden', 403), expected: '您没有权限执行此操作' },
    { error: new MockAxiosError('Bad Request', 400), expected: '输入数据格式不正确，请检查后重试' },
  ];

  testCases.forEach(({ error, expected }) => {
    const errorInfo = handleError(error);
    const userMessage = getUserFriendlyMessage(errorInfo);
    console.log(`错误: ${error.message} - 用户消息: ${userMessage}`);
    
    if (userMessage !== expected) {
      console.warn(`用户消息与期望不符: "${userMessage}" vs "${expected}"`);
    }
  });
}

// 测试全局错误监控
function testGlobalErrorMonitoring(): void {
  console.log('\n=== 测试全局错误监控 ===');

  // 清空之前的错误
  (errorMonitor as any).errors = [];
  (errorMonitor as any).errorCounts = {};

  // 创建一些错误
  const errors = [
    new Error('全局测试错误1'),
    new MockAxiosError('全局测试网络错误'),
    new Error('全局测试错误2'),
  ];

  errors.forEach(error => {
    handleError(error, { globalTest: true });
  });

  const summary = errorMonitor.getErrorSummary();
  console.log('全局错误摘要:', JSON.stringify(summary, null, 2));

  if (summary.totalErrors < 3) {
    console.error('全局错误数量不正确');
  }
}

// 测试默认重试策略
async function testDefaultRetryPolicy(): Promise<void> {
  console.log('\n=== 测试默认重试策略 ===');

  let callCount = 0;

  const testFunction = async (): Promise<string> => {
    callCount++;
    if (callCount < 2) {
      throw new Error('模拟网络错误');
    }
    return '默认重试成功';
  };

  try {
    const result = await defaultRetryPolicy.execute(testFunction);
    console.log(`默认重试结果: ${result}`);
    if (callCount !== 2) {
      console.error(`默认重试次数不正确: ${callCount}`);
    }
  } catch (error) {
    console.error(`默认重试失败: ${error}`);
  }
}

// 测试错误边界降级
function testErrorBoundaryFallback(): void {
  console.log('\n=== 测试错误边界降级 ===');

  const testError = new Error('测试边界错误');
  const resetFunction = () => console.log('重置错误边界');

  try {
    // 这里我们只测试函数调用，不测试React组件渲染
    const errorInfo = handleError(testError, { boundary: true });
    const userMessage = getUserFriendlyMessage(errorInfo);
    console.log(`错误边界处理: ${userMessage}`);
  } catch (error) {
    console.error(`错误边界测试失败: ${error}`);
  }
}

// 运行所有测试
export async function runAllErrorHandlingTests(): Promise<void> {
  console.log('开始前端错误处理机制测试...');

  try {
    testErrorClassification();
    testErrorMonitoring();
    await testRetryPolicy();
    testFallbackHandler();
    testUserFriendlyMessages();
    testGlobalErrorMonitoring();
    await testDefaultRetryPolicy();
    testErrorBoundaryFallback();

    console.log('\n✅ 所有前端错误处理测试完成!');

    // 显示最终错误统计
    const finalSummary = errorMonitor.getErrorSummary();
    console.log('\n最终错误统计:', JSON.stringify(finalSummary, null, 2));

  } catch (error) {
    console.error('\n❌ 前端错误处理测试失败:', error);
    throw error;
  }
}

// 如果直接运行此文件，执行测试
if (typeof window === 'undefined') {
  // Node.js环境
  runAllErrorHandlingTests().catch(console.error);
}

// 导出测试函数供其他模块使用
export {
  testErrorClassification,
  testErrorMonitoring,
  testRetryPolicy,
  testFallbackHandler,
  testUserFriendlyMessages,
  testGlobalErrorMonitoring,
  testDefaultRetryPolicy,
  testErrorBoundaryFallback
};