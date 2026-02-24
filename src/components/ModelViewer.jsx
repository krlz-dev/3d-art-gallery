import { useRef, useEffect, useState, useCallback } from 'react'

export default function ModelViewer({ model, isOpen, onClose }) {
  const canvasRef = useRef(null)
  const engineRef = useRef(null)
  const sceneRef = useRef(null)
  const cameraRef = useRef(null)
  const groundRef = useRef(null)
  const [autoRotate, setAutoRotate] = useState(true)
  const [wireframeOn, setWireframeOn] = useState(false)
  const [darkBg, setDarkBg] = useState(true)
  const [stats, setStats] = useState('')
  const [animations, setAnimations] = useState([])
  const [activeAnim, setActiveAnim] = useState('')

  // Reset state when opening
  useEffect(() => {
    if (isOpen) {
      setAutoRotate(true)
      setWireframeOn(false)
      setDarkBg(true)
      setStats('')
      setAnimations([])
      setActiveAnim('')
    }
  }, [isOpen])

  // Initialize Babylon.js engine when modal is open
  useEffect(() => {
    if (!isOpen || !model) return

    let engine = null
    let scene = null
    let disposed = false

    // Small delay to ensure canvas is rendered in DOM
    const timer = setTimeout(async () => {
      if (disposed) return

      const canvas = canvasRef.current
      if (!canvas) return

      const BABYLON = await import('@babylonjs/core')
      await import('@babylonjs/loaders/glTF')

      if (disposed) return

      engine = new BABYLON.Engine(canvas, true, { adaptToDeviceRatio: true })
      engineRef.current = engine

      scene = new BABYLON.Scene(engine)
      sceneRef.current = scene
      scene.clearColor = new BABYLON.Color4(0.118, 0.145, 0.271, 1)

      // Camera
      const camera = new BABYLON.ArcRotateCamera(
        'cam', -Math.PI / 4, Math.PI / 3, 8,
        new BABYLON.Vector3(0, 2, 0), scene
      )
      camera.attachControl(canvas, true)
      camera.lowerRadiusLimit = 2
      camera.upperRadiusLimit = 25
      camera.wheelDeltaPercentage = 0.01
      camera.panningSensibility = 200
      cameraRef.current = camera

      // Lights — bright enough for dark-colored models
      const hemi = new BABYLON.HemisphericLight('h', new BABYLON.Vector3(0, 1, 0), scene)
      hemi.intensity = 1.0
      hemi.groundColor = new BABYLON.Color3(0.35, 0.38, 0.45)

      const dir = new BABYLON.DirectionalLight('d', new BABYLON.Vector3(-1, -2, 1), scene)
      dir.intensity = 1.4
      dir.diffuse = new BABYLON.Color3(0.95, 0.93, 1.0)

      // Fill light from opposite side
      const fill = new BABYLON.DirectionalLight('fill', new BABYLON.Vector3(1, -1, -1), scene)
      fill.intensity = 0.6
      fill.diffuse = new BABYLON.Color3(0.8, 0.85, 1.0)

      const shadow = new BABYLON.ShadowGenerator(1024, dir)
      shadow.useBlurExponentialShadowMap = true

      // Ground (positioned later after model loads)
      const ground = BABYLON.MeshBuilder.CreateGround('gnd', { width: 25, height: 25 }, scene)
      ground.position.y = -10
      const gMat = new BABYLON.StandardMaterial('gMat', scene)
      gMat.diffuseColor = new BABYLON.Color3(0.1, 0.11, 0.18)
      gMat.specularColor = new BABYLON.Color3(0.03, 0.03, 0.05)
      ground.material = gMat
      ground.receiveShadows = true
      groundRef.current = ground

      // Load model
      BABYLON.SceneLoader.ImportMesh('', '', model.model, scene, (meshes) => {
        let verts = 0
        let faces = 0
        meshes.forEach((mesh) => {
          if (mesh.geometry) {
            verts += mesh.getTotalVertices()
            faces += mesh.getTotalIndices() / 3
          }
          mesh.receiveShadows = true
          shadow.addShadowCaster(mesh)
        })
        setStats(`Meshes ${meshes.length}  Verts ${verts}  Faces ${Math.round(faces)}`)

        // Auto-frame camera to model bounds
        const bounds = meshes.reduce((acc, m) => {
          if (!m.getBoundingInfo) return acc
          const b = m.getBoundingInfo().boundingBox
          const min = b.minimumWorld
          const max = b.maximumWorld
          return {
            min: new BABYLON.Vector3(
              Math.min(acc.min.x, min.x), Math.min(acc.min.y, min.y), Math.min(acc.min.z, min.z)
            ),
            max: new BABYLON.Vector3(
              Math.max(acc.max.x, max.x), Math.max(acc.max.y, max.y), Math.max(acc.max.z, max.z)
            ),
          }
        }, {
          min: new BABYLON.Vector3(Infinity, Infinity, Infinity),
          max: new BABYLON.Vector3(-Infinity, -Infinity, -Infinity),
        })

        const center = bounds.min.add(bounds.max).scale(0.5)
        const extent = bounds.max.subtract(bounds.min)
        const maxDim = Math.max(extent.x, extent.y, extent.z)

        // Position ground at model's feet
        ground.position.y = bounds.min.y - 0.02

        // Frame camera: target model center, distance based on size
        camera.target = new BABYLON.Vector3(center.x, center.y, center.z)
        camera.radius = maxDim * 2.0
        camera.beta = Math.PI / 2.8

        // Handle animations
        const groups = scene.animationGroups || []
        if (groups.length > 0) {
          // Stop all first
          groups.forEach(ag => ag.stop())

          const animNames = groups.map(ag => ag.name)
          setAnimations(animNames)

          // Pick a default: prefer Idle, then Walk, then first
          const preferredOrder = ['Idle_Neutral', 'Idle', 'Walk', 'Run']
          let defaultAnim = animNames[0]
          for (const pref of preferredOrder) {
            const found = animNames.find(n =>
              n.toLowerCase().includes(pref.toLowerCase())
            )
            if (found) { defaultAnim = found; break }
          }

          // Play the default
          const ag = groups.find(g => g.name === defaultAnim)
          if (ag) ag.start(true)
          setActiveAnim(defaultAnim)
        }
      })

      // Auto-rotate
      scene.registerBeforeRender(() => {
        if (cameraRef.current && cameraRef.current._autoRotate !== false) {
          cameraRef.current.alpha += 0.003
        }
      })

      engine.runRenderLoop(() => scene.render())

      // Resize handler
      const handleResize = () => engine.resize()
      window.addEventListener('resize', handleResize)
      engine._resizeHandler = handleResize
    }, 50)

    return () => {
      disposed = true
      clearTimeout(timer)
      if (engineRef.current) {
        if (engineRef.current._resizeHandler) {
          window.removeEventListener('resize', engineRef.current._resizeHandler)
        }
        engineRef.current.dispose()
        engineRef.current = null
        sceneRef.current = null
        cameraRef.current = null
        groundRef.current = null
      }
    }
  }, [isOpen, model])

  // Sync autoRotate state with camera ref
  useEffect(() => {
    if (cameraRef.current) {
      cameraRef.current._autoRotate = autoRotate
    }
  }, [autoRotate])

  const toggleWireframe = useCallback(() => {
    setWireframeOn((prev) => {
      const next = !prev
      if (sceneRef.current) {
        sceneRef.current.meshes.forEach((m) => {
          if (m.material) m.material.wireframe = next
        })
      }
      return next
    })
  }, [])

  const toggleAutoRotate = useCallback(() => {
    setAutoRotate((prev) => !prev)
  }, [])

  const resetCamera = useCallback(() => {
    const cam = cameraRef.current
    if (cam) {
      cam.alpha = -Math.PI / 4
      cam.beta = Math.PI / 3
      cam.radius = 8
      cam.target.x = 0
      cam.target.y = 2
      cam.target.z = 0
    }
  }, [])

  const toggleBackground = useCallback(async () => {
    setDarkBg((prev) => {
      const next = !prev
      const scene = sceneRef.current
      const ground = groundRef.current
      if (scene) {
        if (next) {
          scene.clearColor.r = 0.118
          scene.clearColor.g = 0.145
          scene.clearColor.b = 0.271
          if (ground?.material) {
            ground.material.diffuseColor.r = 0.1
            ground.material.diffuseColor.g = 0.11
            ground.material.diffuseColor.b = 0.18
          }
        } else {
          scene.clearColor.r = 0.82
          scene.clearColor.g = 0.85
          scene.clearColor.b = 0.9
          if (ground?.material) {
            ground.material.diffuseColor.r = 0.72
            ground.material.diffuseColor.g = 0.75
            ground.material.diffuseColor.b = 0.8
          }
        }
      }
      return next
    })
  }, [])

  const switchAnimation = useCallback((animName) => {
    const scene = sceneRef.current
    if (!scene) return
    const groups = scene.animationGroups || []
    groups.forEach(ag => ag.stop())
    const ag = groups.find(g => g.name === animName)
    if (ag) ag.start(true)
    setActiveAnim(animName)
  }, [])

  if (!isOpen || !model) return null

  return (
    <div className="modal-viewer-overlay" onClick={onClose}>
      <div className="modal-viewer-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-viewer-content">
          <div className="modal-header">
            <h5 className="modal-title">{model.name}</h5>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close"></button>
          </div>
          <div className="modal-body p-0">
            <canvas ref={canvasRef} id="viewerCanvas"></canvas>
          </div>
          <div className="viewer-toolbar">
            <button
              className={`btn-tool${wireframeOn ? ' active' : ''}`}
              onClick={toggleWireframe}
            >
              <i className="bi bi-grid-3x3"></i> Wireframe
            </button>
            <button
              className={`btn-tool${autoRotate ? ' active' : ''}`}
              onClick={toggleAutoRotate}
            >
              <i className="bi bi-arrow-repeat"></i> Auto-Rotate
            </button>
            <button className="btn-tool" onClick={resetCamera}>
              <i className="bi bi-arrows-angle-contract"></i> Reset View
            </button>
            <button className="btn-tool" onClick={toggleBackground}>
              <i className="bi bi-circle-half"></i> {darkBg ? 'Light' : 'Dark'} Mode
            </button>
            {animations.length > 1 && (
              <select
                className="btn-tool anim-select"
                value={activeAnim}
                onChange={(e) => switchAnimation(e.target.value)}
              >
                {animations.map((name) => (
                  <option key={name} value={name}>
                    {name.replace(/^.*\|/, '')}
                  </option>
                ))}
              </select>
            )}
          </div>
          <div className="viewer-info">
            <div><span>LMB</span> Rotate</div>
            <div><span>Scroll</span> Zoom</div>
            <div><span>RMB</span> Pan</div>
            {stats && <div>{stats.split('  ').map((s, i) => {
              const [label, ...rest] = s.split(' ')
              return <span key={i}>{i > 0 && ' \u00A0 '}<span>{label}</span> {rest.join(' ')}</span>
            })}</div>}
          </div>
        </div>
      </div>
    </div>
  )
}
