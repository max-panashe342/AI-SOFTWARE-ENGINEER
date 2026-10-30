import { useEffect, useState, type FormEvent } from 'react'

import { authenticatedApiRequest } from '../lib/api'
import { useAuth } from './AuthProvider'
import './ProtectedWorkspace.css'

type Profile = {
  id: number
  email: string | null
  display_name: string | null
  created_at: string
  updated_at: string
}

export function ProtectedWorkspace({ onSignOut }: { onSignOut: () => void }) {
  const { user, signOut } = useAuth()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [displayName, setDisplayName] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    void authenticatedApiRequest<Profile>('/api/me')
      .then((data) => {
        if (!isMounted) return
        setProfile(data)
        setDisplayName(data.display_name ?? '')
      })
      .catch((requestError: unknown) => {
        if (isMounted) setError(requestError instanceof Error ? requestError.message : 'Unable to load your profile.')
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => { isMounted = false }
  }, [])

  async function handleSignOut() {
    const result = await signOut()
    if (!result.error) onSignOut()
  }

  async function handleProfileSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMessage(null)
    setError(null)
    setIsSaving(true)
    try {
      const data = await authenticatedApiRequest<Profile>('/api/me', {
        method: 'PATCH',
        body: JSON.stringify({ display_name: displayName }),
      })
      setProfile(data)
      setDisplayName(data.display_name ?? '')
      setMessage('Your profile was saved.')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Unable to save your profile.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <main className="workspace-page">
      <div className="workspace-header">
        <div>
          <p className="eyebrow"><span className="eyebrow-dot" /> Private workspace</p>
          <h1>Your work<br /><em>starts here.</em></h1>
        </div>
        <button className="workspace-signout" onClick={handleSignOut} type="button">Sign out ↗</button>
      </div>
      <section className="workspace-card">
        <span className="workspace-label">SIGNED IN AS</span>
        <strong>{profile?.email ?? user?.email}</strong>
        <p>Your authenticated workspace is ready. Your profile is stored securely for your account.</p>
        <a className="workspace-assessments-link" href="/assessments">Explore assessments ↗</a>
      </section>
      <section className="profile-card" aria-labelledby="profile-heading">
        <p className="workspace-label">YOUR PROFILE</p>
        <h2 id="profile-heading">Make it yours.</h2>
        {isLoading && <p className="profile-state" role="status">Loading your profile...</p>}
        {!isLoading && (
          <form onSubmit={handleProfileSave}>
            <label htmlFor="display-name">Display name</label>
            <input
              id="display-name"
              maxLength={120}
              required
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
            />
            {error && <p className="profile-message error" role="alert">{error}</p>}
            {message && <p className="profile-message success" role="status">{message}</p>}
            <button className="profile-save" disabled={isSaving || !profile} type="submit">
              {isSaving ? 'Saving...' : 'Save profile'}
            </button>
          </form>
        )}
      </section>
    </main>
  )
}
