import { useState } from 'react'
import models from '../data/models'
import ModelViewer from '../components/ModelViewer'

export default function Home() {
  const [selectedModel, setSelectedModel] = useState(null)

  return (
    <>
      {/* Hero */}
      <section className="hero">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-7">
              <div className="hero-label">Collection</div>
              <h1>Procedural <span>3D</span> Art<br />Gallery</h1>
              <p>
                Low-poly game assets generated programmatically with Blender Python
                scripts. Each piece is crafted via code, rendered headlessly, and
                viewable in real-time 3D.
              </p>
              <div className="hero-stats">
                <div>
                  <div className="hero-stat-num">{models.length}</div>
                  <div className="hero-stat-label">Models</div>
                </div>
                <div>
                  <div className="hero-stat-num">Blender 5.0</div>
                  <div className="hero-stat-label">Engine</div>
                </div>
                <div>
                  <div className="hero-stat-num">GLB</div>
                  <div className="hero-stat-label">Format</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Gallery */}
      <section className="gallery-section" id="gallery">
        <div className="container">
          <div className="section-label">Gallery</div>
          <h2 className="section-title">Explore the Collection</h2>
          <p className="section-subtitle mb-4">Click any piece to view it in interactive 3D</p>

          <div className="row g-4">
            {models.map((m) => (
              <div className="col-sm-6 col-md-4 col-lg-3" key={m.id}>
                <div className="gallery-card" onClick={() => setSelectedModel(m)}>
                  <img src={m.thumb} alt={m.name} className="card-thumb" loading="lazy" />
                  <div className="card-overlay">
                    <button className="btn-view">
                      <i className="bi bi-box"></i> View in 3D
                    </button>
                  </div>
                  <div className="card-info">
                    <h5>{m.name}</h5>
                    <p>{m.description}</p>
                  </div>
                  <div className="card-tags">
                    {m.tags.map((t) => (
                      <span className="card-tag" key={t}>{t}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3D Viewer Modal */}
      <ModelViewer
        model={selectedModel}
        isOpen={!!selectedModel}
        onClose={() => setSelectedModel(null)}
      />
    </>
  )
}
