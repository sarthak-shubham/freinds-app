import React, { Component } from 'react';

function ErrorIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-page" id="error-page">
          <div className="error-page-icon">
            <ErrorIcon />
          </div>
          <h1 className="error-page-title">Something went wrong</h1>
          <p className="error-page-message">
            An unexpected error occurred. Please try again or go back to the home page.
          </p>
          <button className="btn btn--primary" onClick={this.handleReset} id="error-go-home-btn">
            Go Home
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
