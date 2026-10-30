import { useEffect, useState } from 'react'

import './DepartmentDirectory.css'

export type Department = {
  id: number
  name: string
  slug: string
  description: string
  status: string
  created_at: string
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function DepartmentCard({ department }: { department: Department }) {
  return (
    <article className="department-card">
      <div className="department-card-top">
        <span className="department-status">{department.status}</span>
        <span className="department-card-number">/{String(department.id).padStart(2, '0')}</span>
      </div>
      <h2>{department.name}</h2>
      <p>{department.description}</p>
      <span className="department-slug">{department.slug}</span>
    </article>
  )
}

export function DepartmentDirectory() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function loadDepartments() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/departments`, {
          signal: controller.signal,
        })
        if (!response.ok) {
          throw new Error(`The department service returned ${response.status}.`)
        }
        const data: Department[] = await response.json()
        setDepartments(data)
      } catch (requestError) {
        if (requestError instanceof DOMException && requestError.name === 'AbortError') return
        setError(requestError instanceof Error ? requestError.message : 'Unable to load departments.')
      } finally {
        if (!controller.signal.aborted) setIsLoading(false)
      }
    }

    void loadDepartments()
    return () => controller.abort()
  }, [])

  return (
    <main className="directory-page">
      <div className="directory-heading">
        <div>
          <p className="eyebrow"><span className="eyebrow-dot" /> Your opportunities</p>
          <h1>Explore<br /><em>departments.</em></h1>
        </div>
        <p className="directory-intro">
          Find a team where you can contribute, learn from experienced people,
          and make meaningful progress.
        </p>
      </div>

      {isLoading && <div className="directory-state" role="status">Loading departments...</div>}
      {error && (
        <div className="directory-state directory-error" role="alert">
          <strong>We couldn&apos;t load the departments.</strong>
          <span>{error} Check that the backend is running and try again.</span>
        </div>
      )}
      {!isLoading && !error && departments.length === 0 && (
        <div className="directory-state">No departments are available yet.</div>
      )}
      {!isLoading && !error && departments.length > 0 && (
        <div className="department-grid">
          {departments.map((department) => <DepartmentCard department={department} key={department.id} />)}
        </div>
      )}
    </main>
  )
}
