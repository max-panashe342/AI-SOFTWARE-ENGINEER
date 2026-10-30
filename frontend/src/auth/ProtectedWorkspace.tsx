import { useAuth } from './AuthProvider'
import './ProtectedWorkspace.css'

export function ProtectedWorkspace({ onSignOut }: { onSignOut: () => void }) {
  const { user, signOut } = useAuth()

  async function handleSignOut() {
    const result = await signOut()
    if (!result.error) onSignOut()
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
        <strong>{user?.email}</strong>
        <p>Your authenticated workspace is ready. This area is protected by your Supabase session.</p>
      </section>
    </main>
  )
}
