// Logger utility for frontend debugging
// Writes logs to both console and files for deployment debugging

interface LogEntry {
  timestamp: string
  level: 'info' | 'warn' | 'error' | 'debug'
  component: string
  message: string
  data?: any
}

class Logger {
  private logBuffer: LogEntry[] = []
  private maxBufferSize = 1000
  private flushInterval = 5000 // 5 seconds

  constructor() {
    // Flush logs periodically
    setInterval(() => {
      this.flushLogs()
    }, this.flushInterval)

    // Flush logs before page unload
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.flushLogs()
      })
    }
  }

  private formatLog(level: string, component: string, message: string, data?: any): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level: level as LogEntry['level'],
      component,
      message,
      data
    }
  }

  private addToBuffer(entry: LogEntry) {
    this.logBuffer.push(entry)
    
    // Keep buffer size manageable
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxBufferSize)
    }
  }

  private async flushLogs() {
    if (this.logBuffer.length === 0) return

    const logsToFlush = [...this.logBuffer]
    this.logBuffer = []

    try {
      // Send logs to backend endpoint
      const response = await fetch('/api/logs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ logs: logsToFlush })
      })

      if (!response.ok) {
        console.warn('Failed to send logs to backend:', response.status)
      }
    } catch (error) {
      console.warn('Error sending logs to backend:', error)
    }
  }

  private log(level: string, component: string, message: string, data?: any) {
    const entry = this.formatLog(level, component, message, data)
    
    // Add to buffer for file logging
    this.addToBuffer(entry)
    
    // Also log to console with emoji
    const emoji = this.getEmoji(level)
    const consoleMessage = `${emoji} [${component}] ${message}`
    
    switch (level) {
      case 'error':
        console.error(consoleMessage, data || '')
        break
      case 'warn':
        console.warn(consoleMessage, data || '')
        break
      case 'debug':
        console.debug(consoleMessage, data || '')
        break
      default:
        console.log(consoleMessage, data || '')
    }
  }

  private getEmoji(level: string): string {
    switch (level) {
      case 'error': return '❌'
      case 'warn': return '⚠️'
      case 'debug': return '🔍'
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

  debug(component: string, message: string, data?: any) {
    this.log('debug', component, message, data)
  }

  // Force flush logs immediately
  async flush() {
    await this.flushLogs()
  }
}

// Create singleton instance
export const logger = new Logger()

// Export convenience functions
export const logInfo = (component: string, message: string, data?: any) => logger.info(component, message, data)
export const logWarn = (component: string, message: string, data?: any) => logger.warn(component, message, data)
export const logError = (component: string, message: string, data?: any) => logger.error(component, message, data)
export const logDebug = (component: string, message: string, data?: any) => logger.debug(component, message, data)