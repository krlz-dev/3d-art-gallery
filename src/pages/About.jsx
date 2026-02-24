export default function About() {
  return (
    <>
      {/* Hero */}
      <section className="hero-about">
        <div className="container">
          <div className="hero-label">How it works</div>
          <h1>Code it. Render it.<br /><em>View it.</em></h1>
          <p>
            Every 3D model in this gallery was written as code. No mouse clicks, no
            manual sculpting. Just Python scripts, Blender's headless engine, and a
            browser.
          </p>
        </div>
      </section>

      {/* Stack */}
      <section className="content-section">
        <div className="container">
          <div className="section-label">Stack</div>
          <h2 className="section-title">Three tools. Zero GUI.</h2>
          <p className="section-subtitle">The entire pipeline runs from the terminal</p>

          <div className="row g-4">
            <div className="col-md-4">
              <div className="stack-card">
                <div className="stack-icon python"><i className="bi bi-filetype-py"></i></div>
                <h4>Python</h4>
                <p>
                  The brain. Python scripts define every vertex, material, and bone.
                  Parametric functions generate infinite variations from a single seed.
                  No GUI needed.
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="stack-card">
                <div className="stack-icon blender"><i className="bi bi-box"></i></div>
                <h4>Blender 5.0</h4>
                <p>
                  The muscle. Runs headlessly via <code>blender -b</code>. Executes
                  Python scripts, builds geometry, applies materials, renders
                  thumbnails, and exports to GLTF/GLB.
                </p>
              </div>
            </div>
            <div className="col-md-4">
              <div className="stack-card">
                <div className="stack-icon babylon"><i className="bi bi-globe"></i></div>
                <h4>Babylon.js</h4>
                <p>
                  The eyes. Loads GLB files in the browser with real-time lighting,
                  shadows, and orbit controls. Rotate, zoom, and inspect every polygon.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="content-section">
        <div className="container">
          <div className="section-label">Tutorial</div>
          <h2 className="section-title">Make a 3D tree in 3 steps</h2>
          <p className="section-subtitle">From an empty terminal to a spinning 3D model in your browser</p>

          <div className="row">
            <div className="col-lg-6">
              <div className="step">
                <div className="step-num">1</div>
                <div>
                  <h5>Write the generator</h5>
                  <p>
                    A Python script uses Blender's <code>bpy</code> API to build
                    geometry from primitives. Cones become branches, displaced
                    ico-spheres become snow caps, and materials are assigned per-part.
                  </p>
                </div>
              </div>

              <div className="step">
                <div className="step-num">2</div>
                <div>
                  <h5>Run it headlessly</h5>
                  <p>
                    One command. No window opens. Blender boots in background mode,
                    executes your script, exports a <code>.glb</code> file, renders a
                    thumbnail, and exits. Done in seconds.
                  </p>
                </div>
              </div>

              <div className="step">
                <div className="step-num">3</div>
                <div>
                  <h5>View it in the browser</h5>
                  <p>
                    Babylon.js loads the GLB with a few lines of JavaScript. Add an
                    orbit camera, a directional light, and shadow generator. Your model
                    is now interactive.
                  </p>
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="code-block">
                <div className="code-header">
                  <div className="code-dots"><i></i><i></i><i></i></div>
                  <span>terminal</span>
                </div>
                <div className="code-body">
                  <pre>{`# Generate the model + thumbnail\nblender -b --python generators/generate_tree.py\n\n# Output:\n# \u2713 Exported GLB to: models/tree.glb\n# \u2713 Rendered thumbnail to: thumbnails/tree.png\n\n# Or use the npm script\nnpm run generate:tree`}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Code: Python */}
      <section className="content-section">
        <div className="container">
          <div className="section-label">Python</div>
          <h2 className="section-title">Build geometry with code</h2>
          <p className="section-subtitle">Every shape is a function call. Every variation is a parameter.</p>

          <div className="row g-4">
            <div className="col-lg-6">
              <div className="code-block">
                <div className="code-header">
                  <div className="code-dots"><i></i><i></i><i></i></div>
                  <span>generate_tree.py &mdash; Primitives</span>
                </div>
                <div className="code-body">
                  <pre><span className="kw">import</span> bpy{'\n'}<span className="kw">import</span> bmesh, random, math{'\n'}{'\n'}<span className="cm"># A trunk is just a tapered cylinder</span>{'\n'}bpy.ops.mesh.<span className="fn">primitive_cone_add</span>({'\n'}{'    '}vertices=<span className="nu">7</span>,{'\n'}{'    '}radius1=<span className="nu">0.18</span>,   <span className="cm"># thick base</span>{'\n'}{'    '}radius2=<span className="nu">0.08</span>,   <span className="cm"># thin top</span>{'\n'}{'    '}depth=<span className="nu">3.5</span>,{'\n'}{'    '}location=(<span className="nu">0</span>, <span className="nu">0</span>, <span className="nu">1.75</span>),{'\n'}){'\n'}{'\n'}<span className="cm"># Branch layers = stacked cones</span>{'\n'}layers = [{'\n'}{'    '}(<span className="nu">1.2</span>, <span className="nu">1.8</span>, <span className="nu">1.6</span>),  <span className="cm"># z, radius, height</span>{'\n'}{'    '}(<span className="nu">2.0</span>, <span className="nu">1.5</span>, <span className="nu">1.5</span>),{'\n'}{'    '}(<span className="nu">2.7</span>, <span className="nu">1.2</span>, <span className="nu">1.4</span>),{'\n'}{'    '}(<span className="nu">3.3</span>, <span className="nu">0.95</span>, <span className="nu">1.2</span>),{'\n'}]{'\n'}<span className="kw">for</span> z, r, h <span className="kw">in</span> layers:{'\n'}{'    '}bpy.ops.mesh.<span className="fn">primitive_cone_add</span>({'\n'}{'        '}vertices=<span className="nu">8</span>, radius1=r,{'\n'}{'        '}radius2=<span className="nu">0</span>, depth=h,{'\n'}{'        '}location=(<span className="nu">0</span>, <span className="nu">0</span>, z + h/<span className="nu">2</span>),{'\n'}{'    '})</pre>
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="code-block">
                <div className="code-header">
                  <div className="code-dots"><i></i><i></i><i></i></div>
                  <span>generate_tree.py &mdash; Organic feel</span>
                </div>
                <div className="code-body">
                  <pre><span className="cm"># Displace vertices for organic shapes</span>{'\n'}bm = bmesh.<span className="fn">new</span>(){'\n'}bm.<span className="fn">from_mesh</span>(cone.data){'\n'}{'\n'}<span className="kw">for</span> v <span className="kw">in</span> bm.verts:{'\n'}{'    '}<span className="cm"># Push bottom ring outward randomly</span>{'\n'}{'    '}displacement = random.<span className="fn">uniform</span>(<span className="nu">-0.15</span>, <span className="nu">0.2</span>){'\n'}{'    '}angle = math.<span className="fn">atan2</span>(v.co.y, v.co.x){'\n'}{'    '}v.co.x += math.<span className="fn">cos</span>(angle) * displacement{'\n'}{'    '}v.co.y += math.<span className="fn">sin</span>(angle) * displacement{'\n'}{'\n'}bm.<span className="fn">to_mesh</span>(cone.data){'\n'}bm.<span className="fn">free</span>(){'\n'}{'\n'}<span className="cm"># Materials = flat colors, no textures</span>{'\n'}mat = bpy.data.materials.<span className="fn">new</span>(<span className="st">"LeavesDark"</span>){'\n'}mat.use_nodes = <span className="kw">True</span>{'\n'}bsdf = mat.node_tree.nodes[<span className="st">"Principled BSDF"</span>]{'\n'}bsdf.inputs[<span className="st">"Base Color"</span>].default_value = \{'\n'}{'    '}(<span className="nu">0.08</span>, <span className="nu">0.28</span>, <span className="nu">0.06</span>, <span className="nu">1.0</span>){'\n'}bsdf.inputs[<span className="st">"Roughness"</span>].default_value = <span className="nu">0.9</span></pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Code: Export */}
      <section className="content-section">
        <div className="container">
          <div className="section-label">Export</div>
          <h2 className="section-title">One line to GLB</h2>
          <p className="section-subtitle">GLTF Binary is the universal 3D format. Every engine reads it.</p>

          <div className="row g-4">
            <div className="col-lg-6">
              <div className="code-block">
                <div className="code-header">
                  <div className="code-dots"><i></i><i></i><i></i></div>
                  <span>generate_tree.py &mdash; Export</span>
                </div>
                <div className="code-body">
                  <pre><span className="cm"># Export entire scene as binary GLTF</span>{'\n'}bpy.ops.export_scene.<span className="fn">gltf</span>({'\n'}{'    '}filepath=<span className="st">"models/tree.glb"</span>,{'\n'}{'    '}export_format=<span className="st">'GLB'</span>,{'\n'}{'    '}export_materials=<span className="st">'EXPORT'</span>,{'\n'}{'    '}export_apply=<span className="kw">True</span>,{'\n'}{'    '}check_existing=<span className="kw">False</span>,{'\n'}){'\n'}{'\n'}<span className="cm"># Render a thumbnail too</span>{'\n'}scene = bpy.context.scene{'\n'}scene.render.engine = <span className="st">'BLENDER_EEVEE'</span>{'\n'}scene.render.resolution_x = <span className="nu">600</span>{'\n'}scene.render.resolution_y = <span className="nu">600</span>{'\n'}scene.render.film_transparent = <span className="kw">True</span>{'\n'}scene.render.filepath = <span className="st">"thumbnails/tree.png"</span>{'\n'}bpy.ops.render.<span className="fn">render</span>(write_still=<span className="kw">True</span>)</pre>
                </div>
              </div>
            </div>

            <div className="col-lg-6">
              <div className="code-block">
                <div className="code-header">
                  <div className="code-dots"><i></i><i></i><i></i></div>
                  <span>index.html &mdash; Babylon.js viewer</span>
                </div>
                <div className="code-body">
                  <pre><span className="cm">// Load GLB into the browser</span>{'\n'}BABYLON.SceneLoader.<span className="fn">ImportMesh</span>({'\n'}{'    '}<span className="st">""</span>, <span className="st">""</span>, <span className="st">"models/tree.glb"</span>, scene,{'\n'}{'    '}(meshes) =&gt; {'{'}{'\n'}{'        '}meshes.<span className="fn">forEach</span>((m) =&gt; {'{'}{'\n'}{'            '}m.receiveShadows = <span className="kw">true</span>;{'\n'}{'            '}shadow.<span className="fn">addShadowCaster</span>(m);{'\n'}{'        '}{'}'});{'\n'}{'    '}{'}'}{'\n'});{'\n'}{'\n'}<span className="cm">// Orbit camera with auto-rotation</span>{'\n'}<span className="kw">const</span> cam = <span className="kw">new</span> BABYLON.<span className="fn">ArcRotateCamera</span>({'\n'}{'    '}<span className="st">"cam"</span>, -Math.PI/<span className="nu">4</span>, Math.PI/<span className="nu">3</span>, <span className="nu">8</span>,{'\n'}{'    '}<span className="kw">new</span> BABYLON.<span className="fn">Vector3</span>(<span className="nu">0</span>, <span className="nu">2</span>, <span className="nu">0</span>), scene{'\n'});{'\n'}cam.<span className="fn">attachControl</span>(canvas, <span className="kw">true</span>);{'\n'}{'\n'}scene.<span className="fn">registerBeforeRender</span>(() =&gt; {'{'}{'\n'}{'    '}cam.alpha += <span className="nu">0.003</span>; <span className="cm">// spin</span>{'\n'}{'}'});</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* What's next */}
      <section className="content-section" style={{ background: '#fff' }}>
        <div className="container">
          <div className="section-label">Next</div>
          <h2 className="section-title">What you can generate</h2>
          <p className="section-subtitle">Same pattern, different scripts. The pipeline scales to anything.</p>

          <div className="row g-3 mt-2">
            {[
              { icon: 'bi-tree', label: 'Trees & Vegetation' },
              { icon: 'bi-gem', label: 'Rocks & Minerals' },
              { icon: 'bi-house', label: 'Shelters & Cabins' },
              { icon: 'bi-person', label: 'Characters' },
              { icon: 'bi-fire', label: 'Campfires & Props' },
              { icon: 'bi-snow', label: 'Terrain & Snow' },
              { icon: 'bi-tools', label: 'Weapons & Tools' },
              { icon: 'bi-box-seam', label: 'Crates & Storage' },
            ].map((item) => (
              <div className="col-6 col-md-3" key={item.label}>
                <div className="stack-card text-center py-3">
                  <i
                    className={`bi ${item.icon}`}
                    style={{ fontSize: '1.8rem', color: 'var(--coral)' }}
                  ></i>
                  <h4 className="mt-2 mb-0" style={{ fontSize: '0.9rem' }}>{item.label}</h4>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
