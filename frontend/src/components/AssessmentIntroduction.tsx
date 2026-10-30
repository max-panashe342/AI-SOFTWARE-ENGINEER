import { useEffect, useState } from 'react'

import { authenticatedApiRequest } from '../lib/api'
import type { AssessmentDetail } from '../lib/assessments'
import './AssessmentDirectory.css'

export function AssessmentIntroduction({ slug, onBack }: { slug: string; onBack: () => void }) {
  const [assessment, setAssessment] = useState<AssessmentDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    void authenticatedApiRequest<AssessmentDetail>(`/api/assessments/${encodeURIComponent(slug)}`)
      .then((data) => {
        if (isMounted) setAssessment(data)
      })
      .catch((requestError: unknown) => {
        if (isMounted) setError(requestError instanceof Error ? requestError.message : 'Unable to load this assessment.')
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => { isMounted = false }
  }, [slug])

  if (isLoading) return <main className="assessment-page"><div className="assessment-state" role="status">Loading assessment brief...</div></main>
  if (error || !assessment) {
    return (
      <main className="assessment-page">
        <button className="back-link" onClick={onBack} type="button">← Back to assessments</button>
        <div className="assessment-state assessment-error" role="alert">
          <strong>We couldn&apos;t load this assessment.</strong>
          <span>{error ?? 'This assessment is not available.'}</span>
        </div>
      </main>
    )
  }

  return (
    <main className="assessment-page">
      <button className="back-link" onClick={onBack} type="button">← Back to assessments</button>
      <div className="assessment-detail-heading">
        <p className="eyebrow"><span className="eyebrow-dot" /> {assessment.department_name} · Version {assessment.version.version_number}</p>
        <h1>{assessment.name}</h1>
        <p className="assessment-detail-description">{assessment.description}</p>
      </div>
      <section className="assessment-brief">
        <div>
          <p className="section-kicker">What this measures</p>
          <p className="assessment-instructions">{assessment.version.instructions}</p>
        </div>
        {assessment.version.time_limit_minutes && (
          <div className="assessment-duration">
            <span className="assessment-label">CONFIGURED DURATION</span>
            <strong>{assessment.version.time_limit_minutes} minutes</strong>
          </div>
        )}
      </section>
      <section className="assessment-tasks" aria-labelledby="assessment-tasks-heading">
        <div className="assessment-tasks-heading">
          <p className="section-kicker">Competencies in view</p>
          <h2 id="assessment-tasks-heading">The work<br /><span>you&apos;ll explore.</span></h2>
        </div>
        <div className="assessment-question-list">
          {assessment.version.questions.map((question) => (
            <article className="assessment-question" key={question.id}>
              <span className="question-number">0{question.position}</span>
              <div>
                <span className="assessment-label">{question.competency.name}</span>
                <h3>{question.type.replace('_', ' ')}</h3>
                <p>{question.prompt}</p>
                {question.instructions && <small>{question.instructions}</small>}
              </div>
            </article>
          ))}
        </div>
      </section>
      <p className="assessment-note">This is an assessment brief. Starting and submitting an attempt will be available in a future milestone.</p>
    </main>
  )
}

export function AssessmentAuthState({ onSignIn }: { onSignIn: () => void }) {
  return (
    <main className="assessment-page">
      <div className="assessment-state assessment-auth-state">
        <strong>Sign in to view recruitment assessments.</strong>
        <span>Assessment briefs are available to authenticated candidates.</span>
        <button className="assessment-link" onClick={onSignIn} type="button">Go to sign in <span aria-hidden="true">↗</span></button>
      </div>
    </main>
  )
}
