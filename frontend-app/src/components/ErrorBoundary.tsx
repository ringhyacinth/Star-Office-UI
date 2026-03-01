import { Component, type ErrorInfo, type ReactNode } from 'react'

type ErrorBoundaryProps = {
  children: ReactNode
}

type ErrorBoundaryState = {
  hasError: boolean
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  public state: ErrorBoundaryState = {
    hasError: false,
  }

  public static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Unhandled render error:', error, errorInfo)
  }

  private handleRetry = (): void => {
    this.setState({ hasError: false })
  }

  public render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="card">
          <h2>页面遇到异常</h2>
          <p className="read-the-docs">已拦截运行时错误，避免整页白屏。</p>
          <button type="button" onClick={this.handleRetry}>
            重试渲染
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
