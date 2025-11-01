import React, { useCallback as reactUseCallback, DependencyList } from 'react';

/**
 * 自定义useCallback hook，用于解决@radix-ui/react-compose-refs包中useCallback导入失败的问题
 * 
 * 这个hook与React的useCallback功能完全相同，用于记忆化回调函数，
 * 只有在依赖项发生变化时才会返回新的回调函数。
 * 
 * @param callback 需要记忆化的回调函数
 * @param deps 依赖项数组，当这些依赖项发生变化时会重新创建回调函数
 * @returns 记忆化的回调函数
 * 
 * @example
 * ```tsx
 * const memoizedCallback = useCallback(
 *   () => {
 *     doSomething(a, b);
 *   },
 *   [a, b],
 * );
 * ```
 */
export function useCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: DependencyList
): T {
  return reactUseCallback(callback, deps);
}

export default useCallback;