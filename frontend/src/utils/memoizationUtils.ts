/**/**

 * Simplified Memoization Utilities for Performance Optimization * Memoization Utilities for Performance Optimization

 * Focuses on practical, TypeScript-compliant memoization patterns * Provides comprehensive memoization patterns using useMemo, useCallback, and custom solutions

 */ */



import React from 'react';import React from 'react';



/**/**

 * Deep comparison utility for dependencies * Deep comparison for React dependencies

 */ */

function deepEqual(a: unknown, b: unknown): boolean {function deepEqual(a: unknown, b: unknown): boolean {

  if (a === b) return true;  if (a === b) return true;

    

  if (a == null || b == null) return a === b;  if (a == null || b == null) return a === b;

    

  if (typeof a !== typeof b) return false;  if (typeof a !== typeof b) return false;

    

  if (typeof a !== 'object') return a === b;  if (typeof a !== 'object') return a === b;

    

  if (Array.isArray(a) !== Array.isArray(b)) return false;  if (Array.isArray(a) !== Array.isArray(b)) return false;

    

  const keysA = Object.keys(a as Record<string, unknown>);  const keysA = Object.keys(a as Record<string, unknown>);

  const keysB = Object.keys(b as Record<string, unknown>);  const keysB = Object.keys(b as Record<string, unknown>);

    

  if (keysA.length !== keysB.length) return false;  if (keysA.length !== keysB.length) return false;

    

  for (const key of keysA) {  for (const key of keysA) {

    if (!keysB.includes(key)) return false;    if (!keysB.includes(key)) return false;

    if (!deepEqual((a as Record<string, unknown>)[key], (b as Record<string, unknown>)[key])) return false;    if (!deepEqual((a as Record<string, unknown>)[key], (b as Record<string, unknown>)[key])) return false;

  }  }

    

  return true;  return true;

}}



/**/**

 * Custom deep memo hook that compares dependencies deeply * Custom deep memo hook that compares dependencies deeply

 */ */

export function useDeepMemo<T>(export function useDeepMemo<T>(

  factory: () => T,  factory: () => T,

  deps: React.DependencyList  deps: React.DependencyList

): T {): T {

  const ref = React.useRef<{  const ref = React.useRef<{

    deps: React.DependencyList;    deps: React.DependencyList;

    value: T;    value: T;

  } | undefined>(undefined);  } | undefined>(undefined);



  if (!ref.current || !deepEqual(ref.current.deps, deps)) {  if (!ref.current || !deepEqual(ref.current.deps, deps)) {

    ref.current = {    ref.current = {

      deps,      deps,

      value: factory()      value: factory()

    };    };

  }  }



  return ref.current.value;  return ref.current.value;

}}



/**/**

 * Memoization with cache size limit * Custom deep callback hook that compares dependencies deeply

 */ */

export function useMemoWithLimit<T>(export function useDeepCallback<T extends (...args: never[]) => unknown>(

  factory: () => T,  callback: T,

  deps: React.DependencyList,  deps: React.DependencyList

  limit: number = 10): T {

): T {  return useDeepMemo(() => callback, deps);

  const cache = React.useRef<Array<{}

    deps: React.DependencyList;

    value: T;/**

  }>>([]); * Memoization with cache size limit

 */

  // Check if current deps exist in cacheexport function useMemoWithLimit<T>(

  const cached = cache.current.find(item => deepEqual(item.deps, deps));  factory: () => T,

    deps: React.DependencyList,

  if (cached) {  limit: number = 10

    return cached.value;): T {

  }  const cache = React.useRef<Array<{

    deps: React.DependencyList;

  // Compute new value    value: T;

  const value = factory();  }>>([]);

  

  // Add to cache  // Check if current deps exist in cache

  cache.current.unshift({ deps, value });  const cached = cache.current.find(item => deepEqual(item.deps, deps));

    

  // Limit cache size  if (cached) {

  if (cache.current.length > limit) {    return cached.value;

    cache.current = cache.current.slice(0, limit);  }

  }

  // Compute new value

  return value;  const value = factory();

}  

  // Add to cache

/**  cache.current.unshift({ deps, value });

 * Debounced value hook  

 */  // Limit cache size

export function useDebouncedValue<T>(  if (cache.current.length > limit) {

  value: T,    cache.current = cache.current.slice(0, limit);

  delay: number = 300  }

): T {

  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);  return value;

}

  React.useEffect(() => {

    const handler = setTimeout(() => {/**

      setDebouncedValue(value); * Debounced memo hook

    }, delay); */

export function useDebouncedMemo<T>(

    return () => clearTimeout(handler);  factory: () => T,

  }, [value, delay]);  deps: React.DependencyList,

  delay: number = 300

  return debouncedValue;): T {

}  const [debouncedValue, setDebouncedValue] = React.useState<T>(() => factory());



/**  React.useEffect(() => {

 * Async memo hook for expensive async computations    const handler = setTimeout(() => {

 */      setDebouncedValue(factory());

export function useAsyncMemo<T>(    }, delay);

  initialValue: T,

  deps: React.DependencyList    return () => clearTimeout(handler);

): {  }, [...deps, delay, factory]);

  value: T;

  loading: boolean;  return debouncedValue;

  error: Error | null;}

  execute: (asyncFactory: () => Promise<T>) => void;

} {/**

  const [state, setState] = React.useState<{ * Async memo hook for expensive async computations

    value: T; */

    loading: boolean;export function useAsyncMemo<T>(

    error: Error | null;  asyncFactory: () => Promise<T>,

  }>({  deps: React.DependencyList,

    value: initialValue,  initialValue: T

    loading: false,): {

    error: null  value: T;

  });  loading: boolean;

  error: Error | null;

  const execute = React.useCallback((asyncFactory: () => Promise<T>) => {} {

    let cancelled = false;  const [state, setState] = React.useState<{

    value: T;

    setState(prev => ({ ...prev, loading: true, error: null }));    loading: boolean;

    error: Error | null;

    asyncFactory()  }>({

      .then(value => {    value: initialValue,

        if (!cancelled) {    loading: false,

          setState({ value, loading: false, error: null });    error: null

        }  });

      })

      .catch(error => {  const memoizedAsyncFactory = React.useCallback(asyncFactory, deps);

        if (!cancelled) {

          setState(prev => ({ ...prev, loading: false, error }));  React.useEffect(() => {

        }    let cancelled = false;

      });

    setState(prev => ({ ...prev, loading: true, error: null }));

    return () => {

      cancelled = true;    memoizedAsyncFactory()

    };      .then(value => {

  }, deps);        if (!cancelled) {

          setState({ value, loading: false, error: null });

  return { ...state, execute };        }

}      })

      .catch(error => {

/**        if (!cancelled) {

 * Memoized selector hook for complex state selections          setState(prev => ({ ...prev, loading: false, error }));

 */        }

export function useMemoizedSelector<TState, TResult>(      });

  selector: (state: TState) => TResult,

  state: TState,    return () => {

  equalityFn: (a: TResult, b: TResult) => boolean = Object.is      cancelled = true;

): TResult {    };

  const ref = React.useRef<{  }, [memoizedAsyncFactory]);

    state: TState;

    result: TResult;  return state;

  } | undefined>(undefined);}



  if (!ref.current || !Object.is(ref.current.state, state)) {/**

    const newResult = selector(state); * Memoized selector hook for complex state selections

     */

    if (!ref.current || !equalityFn(ref.current.result, newResult)) {export function useMemoizedSelector<TState, TResult>(

      ref.current = {  selector: (state: TState) => TResult,

        state,  state: TState,

        result: newResult  equalityFn: (a: TResult, b: TResult) => boolean = Object.is

      };): TResult {

    }  const ref = React.useRef<{

  }    state: TState;

    result: TResult;

  return ref.current.result;  } | undefined>(undefined);

}

  if (!ref.current || !Object.is(ref.current.state, state)) {

/**    const newResult = selector(state);

 * Memoized component factory    

 */    if (!ref.current || !equalityFn(ref.current.result, newResult)) {

export function createMemoizedComponent<TProps>(      ref.current = {

  Component: React.ComponentType<TProps>,        state,

  propsAreEqual?: (prevProps: TProps, nextProps: TProps) => boolean        result: newResult

): React.MemoExoticComponent<React.ComponentType<TProps>> {      };

  return React.memo(Component, propsAreEqual);    }

}  }



/**  return ref.current.result;

 * Performance monitoring for memoized values}

 */

export class MemoizationProfiler {/**

  private static instances = new Map<string, { * Performance-optimized computation hook

    computations: number; */

    cacheHits: number;export function useComputedValue<T, TDeps extends readonly unknown[]>(

    cacheMisses: number;  computation: (...deps: TDeps) => T,

    totalTime: number;  dependencies: TDeps,

  }>();  options: {

    lazy?: boolean;

  static track(id: string): {    cache?: boolean;

    start: () => void;    cacheSize?: number;

    end: () => void;  } = {}

  } {): T {

    if (!this.instances.has(id)) {  const { lazy = false, cache = true, cacheSize = 1 } = options;

      this.instances.set(id, {  

        computations: 0,  const cacheRef = React.useRef<Array<{

        cacheHits: 0,    deps: TDeps;

        cacheMisses: 0,    value: T;

        totalTime: 0  }>>([]);

      });

    }  return React.useMemo(() => {

    if (cache) {

    const stats = this.instances.get(id)!;      // Check cache first

    let startTime = 0;      const cached = cacheRef.current.find(item => 

            item.deps.length === dependencies.length &&

    return {        item.deps.every((dep, index) => Object.is(dep, dependencies[index]))

      start: () => {      );

        startTime = performance.now();

        stats.computations++;      if (cached) {

        stats.cacheMisses++;        return cached.value;

      },      }

      end: () => {    }

        const endTime = performance.now();

        stats.totalTime += endTime - startTime;    // Compute value

      }    const value = lazy ? 

    };      (() => computation(...dependencies)) as T :

  }      computation(...dependencies);



  static getStats(id?: string) {    if (cache) {

    if (id) {      // Update cache

      return this.instances.get(id) || null;      cacheRef.current.unshift({ deps: dependencies, value });

    }      if (cacheRef.current.length > cacheSize) {

            cacheRef.current = cacheRef.current.slice(0, cacheSize);

    return Object.fromEntries(this.instances.entries());      }

  }    }



  static clearStats(id?: string) {    return value;

    if (id) {  }, dependencies);

      this.instances.delete(id);}

    } else {

      this.instances.clear();/**

    } * Memoized event handlers factory

  } */

}export function useEventHandlers<T extends Record<string, (...args: any[]) => any>>(

  handlers: T,

/**  deps: React.DependencyList

 * Memoization utilities for common patterns): T {

 */  return React.useMemo(() => {

export const memoUtils = {    const memoizedHandlers = {} as T;

  /**    

   * Memoize expensive array operations    for (const [key, handler] of Object.entries(handlers)) {

   */      memoizedHandlers[key as keyof T] = React.useCallback(

  memoizeArrayOperation: <T, R>(        handler,

    operation: (arr: T[]) => R,        deps

    equalityCheck: (a: T[], b: T[]) => boolean = (a, b) =>       ) as T[keyof T];

      a.length === b.length && a.every((item, index) => Object.is(item, b[index]))    }

  ) => {    

    let lastInput: T[] | undefined;    return memoizedHandlers;

    let lastResult: R;  }, deps);

}

    return (input: T[]): R => {

      if (!lastInput || !equalityCheck(lastInput, input)) {/**

        lastInput = input; * Memoized component factory

        lastResult = operation(input); */

      }export function createMemoizedComponent<TProps>(

      return lastResult;  Component: React.ComponentType<TProps>,

    };  propsAreEqual?: (prevProps: TProps, nextProps: TProps) => boolean

  },): React.MemoExoticComponent<React.ComponentType<TProps>> {

  return React.memo(Component, propsAreEqual);

  /**}

   * Memoize object transformations

   *//**

  memoizeObjectTransform: <T extends Record<string, unknown>, R>( * Performance monitoring for memoized values

    transform: (obj: T) => R, */

    keyComparison: (a: T, b: T) => boolean = (a, b) => export class MemoizationProfiler {

      JSON.stringify(a) === JSON.stringify(b)  private static instances = new Map<string, {

  ) => {    computations: number;

    let lastInput: T | undefined;    cacheHits: number;

    let lastResult: R;    cacheMisses: number;

    totalTime: number;

    return (input: T): R => {  }>();

      if (!lastInput || !keyComparison(lastInput, input)) {

        lastInput = input;  static createProfiledMemo<T>(

        lastResult = transform(input);    id: string,

      }    factory: () => T,

      return lastResult;    deps: React.DependencyList

    };  ): T {

  },    if (!this.instances.has(id)) {

      this.instances.set(id, {

  /**        computations: 0,

   * Create memoized selector with custom equality        cacheHits: 0,

   */        cacheMisses: 0,

  createSelector: <TState, TResult>(        totalTime: 0

    selector: (state: TState) => TResult,      });

    equalityFn: (a: TResult, b: TResult) => boolean = Object.is    }

  ) => {

    let lastState: TState;    const stats = this.instances.get(id)!;

    let lastResult: TResult;    

    let hasResult = false;    return React.useMemo(() => {

      const startTime = performance.now();

    return (state: TState): TResult => {      stats.computations++;

      if (!hasResult || !Object.is(lastState, state)) {      stats.cacheMisses++;

        const newResult = selector(state);      

        if (!hasResult || !equalityFn(lastResult, newResult)) {      const result = factory();

          lastResult = newResult;      

        }      const endTime = performance.now();

        lastState = state;      stats.totalTime += endTime - startTime;

        hasResult = true;      

      }      return result;

      return lastResult;    }, deps);

    };  }

  },

  static getStats(id?: string) {

  /**    if (id) {

   * Simple function memoization      return this.instances.get(id) || null;

   */    }

  memoize: <TArgs extends unknown[], TReturn>(    

    fn: (...args: TArgs) => TReturn,    return Object.fromEntries(this.instances.entries());

    getKey?: (...args: TArgs) => string  }

  ): ((...args: TArgs) => TReturn) => {

    const cache = new Map<string, TReturn>();  static clearStats(id?: string) {

        if (id) {

    return (...args: TArgs): TReturn => {      this.instances.delete(id);

      const key = getKey ? getKey(...args) : JSON.stringify(args);    } else {

            this.instances.clear();

      if (cache.has(key)) {    }

        return cache.get(key)!;  }

      }}

      

      const result = fn(...args);/**

      cache.set(key, result); * Memoization utilities for common patterns

      return result; */

    };export const memoUtils = {

  }  /**

};   * Memoize expensive array operations

   */

/**  memoizeArrayOperation: <T, R>(

 * React Hook for expensive computations with automatic dependency tracking    operation: (arr: T[]) => R,

 */    equalityCheck: (a: T[], b: T[]) => boolean = (a, b) => 

export function useExpensiveComputation<T>(      a.length === b.length && a.every((item, index) => Object.is(item, b[index]))

  computation: () => T,  ) => {

  dependencies: React.DependencyList    let lastInput: T[] | undefined;

): T {    let lastResult: R;

  return React.useMemo(() => {

    const tracker = MemoizationProfiler.track('useExpensiveComputation');    return (input: T[]): R => {

    tracker.start();      if (!lastInput || !equalityCheck(lastInput, input)) {

    const result = computation();        lastInput = input;

    tracker.end();        lastResult = operation(input);

    return result;      }

  }, dependencies);      return lastResult;

}    };

  },

/**

 * React Hook for memoized callbacks with performance tracking  /**

 */   * Memoize object transformations

export function useTrackedCallback<T extends (...args: never[]) => unknown>(   */

  callback: T,  memoizeObjectTransform: <T extends Record<string, any>, R>(

  dependencies: React.DependencyList,    transform: (obj: T) => R,

  trackingId?: string    keyComparison: (a: T, b: T) => boolean = (a, b) => 

): T {      JSON.stringify(a) === JSON.stringify(b)

  return React.useCallback((...args: Parameters<T>) => {  ) => {

    if (trackingId) {    let lastInput: T | undefined;

      const tracker = MemoizationProfiler.track(trackingId);    let lastResult: R;

      tracker.start();

      const result = callback(...args);    return (input: T): R => {

      tracker.end();      if (!lastInput || !keyComparison(lastInput, input)) {

      return result;        lastInput = input;

    }        lastResult = transform(input);

    return callback(...args);      }

  }, dependencies) as T;      return lastResult;

}    };

  },

export default {

  useDeepMemo,  /**

  useMemoWithLimit,   * Create memoized selector with custom equality

  useDebouncedValue,   */

  useAsyncMemo,  createSelector: <TState, TResult>(

  useMemoizedSelector,    selector: (state: TState) => TResult,

  createMemoizedComponent,    equalityFn: (a: TResult, b: TResult) => boolean = Object.is

  MemoizationProfiler,  ) => {

  memoUtils,    let lastState: TState;

  useExpensiveComputation,    let lastResult: TResult;

  useTrackedCallback    let hasResult = false;

};
    return (state: TState): TResult => {
      if (!hasResult || !Object.is(lastState, state)) {
        const newResult = selector(state);
        if (!hasResult || !equalityFn(lastResult, newResult)) {
          lastResult = newResult;
        }
        lastState = state;
        hasResult = true;
      }
      return lastResult;
    };
  }
};

export default {
  useDeepMemo,
  useDeepCallback,
  useMemoWithLimit,
  useDebouncedMemo,
  useAsyncMemo,
  useMemoizedSelector,
  useComputedValue,
  useEventHandlers,
  createMemoizedComponent,
  MemoizationProfiler,
  memoUtils
};