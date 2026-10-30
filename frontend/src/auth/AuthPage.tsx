import { useState, type FormEvent } from 'react'

import { useAuth } from './AuthProvider'
import './AuthPage.css'

type AuthMode = 'sign-in' | 'sign-up'

export function AuthPage({ onAuthenticated }: { onAuthenticated: () => void }) {
  const { signIn, signUp, error: configError, clearError } = useAuth()
  const [mode, setMode] = useState<AuthMode>('sign-in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMessage(null)
    setFormError(null)
    clearError()
    setIsSubmitting(true)

    const result = mode === 'sign-in'
      ? await signIn(email, password)
      : await signUp(email, password)

    setIsSubmitting(false)
    if (result.error) {
      setFormError(result.error)
      return
    }
    if (mode === 'sign-up' && result.needsConfirmation) {
      setMessage('Account created. Check your email to confirm your account before signing in.')
      setPassword('')
      return
    }
    onAuthenticated()
  }

  function switchMode(nextMode: AuthMode) {
    setMode(nextMode)
    setMessage(null)
    setFormError(null)
    clearError()
  }

  return (
    <main className="auth-page">
      <section className="auth-panel" aria-labelledby="auth-heading">
        <p className="eyebrow"><span className="eyebrow-dot" /> Engineering Workplace</p>
        <h1 id="auth-heading">{mode === 'sign-in' ? 'Welcome back.' : 'Start building.'}</h1>
        <p className="auth-intro">
          {mode === 'sign-in'
            ? 'Sign in to continue your engineering workplace experience.'
            : 'Create your account and take your first step into the workplace.'}
        </p>

        <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
          <button className={mode === 'sign-in' ? 'active' : ''} onClick={() => switchMode('sign-in')} role="tab" type="button">Sign in</button>
          <button className={mode === 'sign-up' ? 'active' : ''} onClick={() => switchMode('sign-up')} role="tab" type="button">Create account</button>
        </div>

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email address</label>
          <input id="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete={mode === 'sign-in' ? 'current-password' : 'new-password'} minLength={6} required value={password} onChange={(event) => setPassword(event.target.value)} />
          {(formError || configError) && <p className="auth-message error" role="alert">{formError ?? configError}</p>}
          {message && <p className="auth-message success" role="status">{message}</p>}
          <button className="auth-submit" disabled={isSubmitting} type="submit">
            {isSubmitting ? 'Working...' : mode === 'sign-in' ? 'Sign in' : 'Create account'}
            {!isSubmitting && <span aria-hidden="true">→</span>}
          </button>
        </form>
      </section>
    </main>
  )
}
