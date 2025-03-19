type LogLevel = 'error' | 'warn' | 'info' | 'debug';

interface LogMessage {
  level: LogLevel;
  message: string;
  data?: unknown;
  timestamp: string;
}

class Logger {
  private static instance: Logger | null = null;
  private isDevelopment = process.env.NODE_ENV === 'development';

  private constructor() {}

  public static getInstance(): Logger {
    if (Logger.instance === null) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  private formatMessage(level: LogLevel, message: string, data?: unknown): LogMessage {
    return {
      level,
      message,
      data,
      timestamp: new Date().toISOString()
    };
  }

  private log(level: LogLevel, message: string, data?: unknown): void {
    const logMessage = this.formatMessage(level, message, data);

    if (this.isDevelopment) {
      switch (level) {
        case 'error':
          console.error(logMessage);
          break;
        case 'warn':
          console.warn(logMessage);
          break;
        case 'info':
        case 'debug':
          // These are disabled in production
          break;
      }
    }

    // Here you could add additional logging handlers
    // e.g., sending logs to a service like Sentry
  }

  public error(message: string, data?: unknown): void {
    this.log('error', message, data);
  }

  public warn(message: string, data?: unknown): void {
    this.log('warn', message, data);
  }

  public info(message: string, data?: unknown): void {
    if (this.isDevelopment) {
      this.log('info', message, data);
    }
  }

  public debug(message: string, data?: unknown): void {
    if (this.isDevelopment) {
      this.log('debug', message, data);
    }
  }
}

export const logger = Logger.getInstance(); 