import { useEffect, useState } from 'react'

import { authenticatedApiRequest } from '../lib/api'
import type { AssessmentSummary } from '../lib/assessments'
import './AssessmentDirectory.css'

export function AssessmentDirectory({ onSelect }: { onSelect: (slug: string) => void }) {
  const [assessments, setAssessments] = useState<AssessmentSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true
    void authenticatedApiRequest<AssessmentSummary[]>('/api/assessments')
      .then((data) => {
        if (isMounted) setAssessments(data)
      })
      .catch((requestError: unknown) => {
        if (isMounted) setError(requestError instanceof Error ? requestError.message : 'Unable to load assessments.')
      })
      .finally(() => {
        if (isMounted) setIsLoading(false)
      })
    return () => { isMounted = false }
  }, [])

  return (
    <main className="assessment-page">
      <div className="assessment-heading">
        <div>
          <p className="eyebrow"><span className="eyebrow-dot" /> Recruitment pathway</p>
          <h1>Show your<br /><em>craft.</em></h1>
        </div>
        <p className="assessment-intro">
          Assessments are practical opportunities to demonstrate how you think,
          build, and communicate as an engineer.
        </p>
      </div>
      {isLoading && <div className="assessment-state" role="status">Loading assessments...</div>}
      {error && (
        <div className="assessment-state assessment-error" role="alert">
          <strong>We couldn&apos;t load the assessments.</strong>
          <span>{error}</span>
        </div>
      )}
      {!isLoading && !error && assessments.length === 0 && (
        <div className="assessment-state">No published assessments are available yet.</div>
      )}
      {!isLoading && !error && assessments.length > 0 && (
        <div className="assessment-grid">
          {assessments.map((assessment) => (
            <article className="assessment-card" key={assessment.id}>
              <div className="assessment-card-top">
                <span className="assessment-label">{assessment.department_name}</span>
                <span className="assessment-version">v{assessment.version}</span>
              </div>
              <h2>{assessment.name}</h2>
              <p>{assessment.description}</p>
              <button className="assessment-link" onClick={() => onSelect(assessment.slug)} type="button">
                Read assessment brief <span aria-hidden="true">↗</span>
              </button>
            </article>
          ))}
        </div>
      )}
    </main>
  )
}
