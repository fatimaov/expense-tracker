function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="text-center py-5" role="status" aria-live="polite">
      <div className="spinner-border text-primary" aria-hidden="true" />
      <p className="text-secondary mt-2 mb-0">{message}</p>
    </div>
  )
}

export default LoadingState
