/**
 * Ultra-optimized API service with request deduplication,
 * prefetching, and intelligent caching.
 */
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

// In-flight request tracker for deduplication
const inFlightRequests = new Map<string, Promise<any>>();

// Prefetch cache
const prefetchCache = new Map<string, {
  data: any;
  timestamp: number;
  ttl: number;
}>();

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add cache busting for mutations
    if (config.method !== 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      };
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    // Log performance metrics from server
    const processTime = response.headers['x-process-time'];
    if (processTime && parseFloat(processTime) > 1) {
      console.warn(`Slow API call: ${response.config.url} took ${processTime}s`);
    }

    return response;
  },
  (error) => {
    // Handle 401 unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

/**
 * Generate cache key from request config
 */
function generateCacheKey(config: AxiosRequestConfig): string {
  const { method = 'get', url = '', params, data } = config;
  const paramsStr = params ? JSON.stringify(params) : '';
  const dataStr = data ? JSON.stringify(data) : '';
  return `${method}:${url}:${paramsStr}:${dataStr}`;
}

/**
 * Deduplicated GET request - prevents multiple identical requests
 */
export async function deduplicatedGet<T = any>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const fullConfig = { ...config, method: 'get', url };
  const cacheKey = generateCacheKey(fullConfig);

  // Check if request is already in flight
  if (inFlightRequests.has(cacheKey)) {
    return inFlightRequests.get(cacheKey)!;
  }

  // Check prefetch cache
  const cached = prefetchCache.get(cacheKey);
  if (cached && Date.now() - cached.timestamp < cached.ttl) {
    return Promise.resolve(cached.data);
  }

  // Make new request
  const requestPromise = api.get<T>(url, config).then((response) => {
    inFlightRequests.delete(cacheKey);
    return response.data;
  }).catch((error) => {
    inFlightRequests.delete(cacheKey);
    throw error;
  });

  inFlightRequests.set(cacheKey, requestPromise);

  return requestPromise;
}

/**
 * Prefetch data for faster future access
 */
export async function prefetch(
  url: string,
  config?: AxiosRequestConfig,
  ttl: number = 5 * 60 * 1000  // 5 minutes default
): Promise<void> {
  const fullConfig = { ...config, method: 'get', url };
  const cacheKey = generateCacheKey(fullConfig);

  try {
    const data = await deduplicatedGet(url, config);
    prefetchCache.set(cacheKey, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  } catch (error) {
    // Prefetch failures are not critical
    console.debug('Prefetch failed:', url, error);
  }
}

/**
 * Prefetch next page of paginated data
 */
export function prefetchNextPage(
  baseUrl: string,
  currentPage: number,
  perPage: number = 20
): void {
  const nextPage = currentPage + 1;
  prefetch(`${baseUrl}?page=${nextPage}&per_page=${perPage}`);
}

/**
 * Prefetch related resources
 */
export function prefetchRelated(resourceType: string, id: number): void {
  switch (resourceType) {
    case 'manuscript':
      // Prefetch reviews, files, and related manuscripts
      prefetch(`/api/v1/manuscripts/${id}/reviews`);
      prefetch(`/api/v1/manuscripts/${id}/files`);
      break;
    case 'user':
      // Prefetch user manuscripts and reviews
      prefetch(`/api/v1/users/${id}/manuscripts`);
      prefetch(`/api/v1/users/${id}/reviews`);
      break;
  }
}

/**
 * Clear prefetch cache
 */
export function clearPrefetchCache(): void {
  prefetchCache.clear();
}

/**
 * Clear cache for specific pattern
 */
export function clearCachePattern(pattern: RegExp): void {
  for (const [key] of prefetchCache.entries()) {
    if (pattern.test(key)) {
      prefetchCache.delete(key);
    }
  }
}

/**
 * Batch requests - combine multiple requests into one
 */
export async function batchGet<T = any>(
  urls: string[]
): Promise<T[]> {
  return Promise.all(
    urls.map((url) => deduplicatedGet<T>(url))
  );
}

/**
 * Optimized API methods
 */
export const optimizedApi = {
  // GET with deduplication
  get: deduplicatedGet,

  // POST (no deduplication)
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    api.post<T>(url, data, config).then((res) => res.data),

  // PUT (no deduplication)
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    api.put<T>(url, data, config).then((res) => res.data),

  // DELETE (no deduplication)
  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    api.delete<T>(url, config).then((res) => res.data),

  // PATCH (no deduplication)
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    api.patch<T>(url, data, config).then((res) => res.data),

  // Utilities
  prefetch,
  prefetchNextPage,
  prefetchRelated,
  clearPrefetchCache,
  clearCachePattern,
  batchGet,
};

export default optimizedApi;
