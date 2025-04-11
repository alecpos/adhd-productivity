import { logger } from './logger';

export async function handlePromise<T>(
  promise: Promise<T>,
  errorMessage = 'Operation failed'
): Promise<T> {
  try {
    return await promise;
  } catch (error) {
    logger.error(errorMessage, error);
    throw error;
  }
}

export function ignorePromise(promise: Promise<unknown>): void {
  promise.catch((error) => {
    logger.error('Ignored promise rejected', error);
  });
}

export async function retryPromise<T>(
  fn: () => Promise<T>,
  retries = 3,
  delay = 1000,
  onError?: (error: unknown, attempt: number) => void
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      if (onError) {
        onError(error, attempt);
      }
      if (attempt < retries) {
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  timeoutError = new Error('Operation timed out')
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => reject(timeoutError), timeoutMs);
  });

  return Promise.race([promise, timeout]);
}
