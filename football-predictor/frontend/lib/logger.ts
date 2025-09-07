// Logger utility for frontend
// Production-ready logging with minimal overhead

interface LogEntry {
  timestamp: string
  level: 'info' | 'warn' | 'error'
  component: string
  message: string
  data?: any
  sessionId?: string
}

class Logger {
  private logBuffer: LogEntry[] = []
  private maxBufferSize = 1000
  private flushInterval = 5000 // 5 seconds
  private sessionId: string

  constructor() {
    // Generate unique session ID for this frontend instance
    this.sessionId = `frontend-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    // Production mode - minimal logging
  }

  private formatLog(level: string, component: string, message: string, data?: any): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level: level as LogEntry['level'],
      component,
      message,
      data,
      sessionId: this.sessionId
    }
  }

  private addToBuffer(entry: LogEntry) {
    this.logBuffer.push(entry)
    
    // Keep buffer size manageable
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxBufferSize)
    }
  }

  private async clearLogs() {
    // Production mode - no log clearing
    return
  }

  private async flushLogs() {
    // Production mode - no log flushing
    return
  }

  private log(level: string, component: string, message: string, data?: any) {
    // Production mode - only log errors and warnings
    if (level === 'error' || level === 'warn') {
      const emoji = this.getEmoji(level)
      const consoleMessage = `${emoji} [${component}] ${message}`
      
      if (level === 'error') {
        console.error(consoleMessage, data || '')
      } else {
        console.warn(consoleMessage, data || '')
      }
    }
  }

  private getEmoji(level: string): string {
    switch (level) {
      case 'error': return '❌'
      case 'warn': return '⚠️'
      default: return '✅'
    }
  }

  info(component: string, message: string, data?: any) {
    this.log('info', component, message, data)
  }

  warn(component: string, message: string, data?: any) {
    this.log('warn', component, message, data)
  }

  error(component: string, message: string, data?: any) {
    this.log('error', component, message, data)
  }


  // Force flush logs immediately
  async flush() {
    await this.flushLogs()
  }

  // Clear logs manually
  async clear() {
    await this.clearLogs()
  }

  // Get current session ID
  getSessionId() {
    return this.sessionId
  }
}

// Create singleton instance
export const logger = new Logger()

// Export convenience functions
export const logInfo = (component: string, message: string, data?: any) => logger.info(component, message, data)
export const logWarn = (component: string, message: string, data?: any) => logger.warn(component, message, data)
export const logError = (component: string, message: string, data?: any) => logger.error(component, message, data)