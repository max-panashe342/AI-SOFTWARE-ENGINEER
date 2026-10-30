import { useEffect, useState } from 'react'

import { DepartmentDirectory } from './components/DepartmentDirectory'
import { AssessmentDirectory } from './components/AssessmentDirectory'
import { AssessmentAuthState, AssessmentIntroduction } from './components/AssessmentIntroduction'
import { AuthPage } from './auth/AuthPage'
import { ProtectedWorkspace } from './auth/ProtectedWorkspace'
import { useAuth } from './auth/AuthProvider'
import './App.css'

function navigateTo(path: string) {
  window.history.pushState({}, '', path)
  window.dispatchEvent(new PopStateEvent('popstate'))
}

function App() {
  const [path, setPath] = useState(window.location.pathname)
  const { user, isLoading } = useAuth()

  useEffect(() => {
    const handlePopState = () => setPath(window.location.pathname)
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const isDepartmentsPage = path === '/departments'
  const isAssessmentsPage = path === '/assessments'
  const isAssessmentDetailPage = path.startsWith('/assessments/') && path.length > '/assessments/'.length
  const assessmentSlug = isAssessmentDetailPage ? path.slice('/assessments/'.length) : ''
  const isAuthPage = path === '/auth'
  const isWorkspacePage = path === '/workspace'

  useEffect(() => {
    if (!isLoading && isWorkspacePage && !user) navigateTo('/auth')
  }, [isLoading, isWorkspacePage, user])

  function navigateToAuth() {
    navigateTo(user ? '/workspace' : '/auth')
  }

  function navigateToAssessments() {
    navigateTo('/assessments')
  }

  return (
    <div className="app-shell">
      <nav className="site-nav" aria-label="Main navigation">
        <a className="brand" href="/" onClick={(event) => { event.preventDefault(); navigateTo('/') }}>
          <span className="brand-mark">EW</span>
          <span>Engineering Workplace</span>
        </a>
        <div className="nav-links">
          <a href="/#experience">The experience</a>
          <a href="/departments" onClick={(event) => { event.preventDefault(); navigateTo('/departments') }}>Departments</a>
          <a href="/assessments" onClick={(event) => { event.preventDefault(); navigateToAssessments() }}>Assessments</a>
          <a href="/#about">About</a>
        </div>
        <a className="nav-action" href={user ? '/workspace' : '/auth'} onClick={(event) => { event.preventDefault(); navigateToAuth() }}>
          {user ? 'Workspace' : 'Get started'} <span aria-hidden="true">↗</span>
        </a>
      </nav>

      {isAuthPage ? <AuthPage onAuthenticated={() => navigateTo('/workspace')} /> : isWorkspacePage ? (
        isLoading ? <main className="route-loading" role="status">Checking your session...</main>
          : user ? <ProtectedWorkspace onSignOut={() => navigateTo('/auth')} /> : null
      ) : isAssessmentsPage || isAssessmentDetailPage ? (
        isLoading ? <main className="route-loading" role="status">Checking your session...</main>
          : user ? isAssessmentDetailPage
            ? <AssessmentIntroduction onBack={navigateToAssessments} slug={decodeURIComponent(assessmentSlug)} />
            : <AssessmentDirectory onSelect={(slug) => navigateTo(`/assessments/${encodeURIComponent(slug)}`)} />
            : <AssessmentAuthState onSignIn={() => navigateTo('/auth')} />
      ) : isDepartmentsPage ? <DepartmentDirectory /> : (
        <main>
          <section className="hero" id="experience">
            <div className="hero-copy">
              <p className="eyebrow"><span className="eyebrow-dot" /> Simulated internship platform</p>
              <h1>Build the work<br /><em>before</em> you get the job.</h1>
              <p className="hero-description">
                Engineering Workplace gives you a realistic space to learn, collaborate,
                and ship meaningful work across the teams that shape the future.
              </p>
              <a className="primary-button" href="/departments" onClick={(event) => { event.preventDefault(); navigateTo('/departments') }}>
                Explore Departments <span aria-hidden="true">→</span>
              </a>
            </div>
            <div className="hero-visual" aria-label="A visual representation of a collaborative engineering workspace">
              <div className="visual-orbit orbit-one" />
              <div className="visual-orbit orbit-two" />
              <div className="visual-card card-main">
                <span className="card-label">YOUR NEXT SPRINT</span>
                <div className="card-title">Ship something<br />that matters.</div>
                <div className="card-progress"><span /></div>
                <div className="card-footer"><span>03 / 05 tasks</span><span className="status-dot" /> In progress</div>
              </div>
              <div className="visual-card card-note">
                <span className="note-icon">✦</span>
                <span>Learn by<br /><strong>doing</strong></span>
              </div>
              <div className="visual-card card-badge">01 <span>REAL<br />PROJECTS</span></div>
              <div className="visual-cross cross-one">+</div>
              <div className="visual-cross cross-two">+</div>
            </div>
          </section>

          <section className="department-section">
            <div>
              <p className="section-kicker">Find your place</p>
              <h2>Work across<br /><span>what&apos;s next.</span></h2>
            </div>
            <div className="department-cta">
              <p>Discover the teams and real opportunities available in the workplace.</p>
              <a className="text-link" href="/departments" onClick={(event) => { event.preventDefault(); navigateTo('/departments') }}>
                View departments <span aria-hidden="true">↗</span>
              </a>
            </div>
          </section>
        </main>
      )}

      <footer id="about">
        <span>© 2026 Engineering Workplace</span>
        <span>Make your first move count.</span>
      </footer>
    </div>
  )
}

export default App
