# 3D Art Gallery

A quiet little gallery where code becomes art.

Write a Python script, let Blender shape it, and watch it come alive in the browser — all from a few lines of code.

**[Visit the Gallery](https://krlz-dev.github.io/3d-art-gallery/)**

![Vite](https://img.shields.io/badge/Vite-6-646CFF?logo=vite&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Babylon.js](https://img.shields.io/badge/Babylon.js-7-BB464B?logo=data:image/svg+xml;base64,&logoColor=white)
![Blender](https://img.shields.io/badge/Blender-5.0-E87D0D?logo=blender&logoColor=white)

---

### How it works

```
Python script → Blender (headless) → .glb model + thumbnail → Web gallery
```

1. **Code it** — define geometry, materials, and lighting in Python
2. **Generate it** — Blender runs headlessly, exports GLB + renders a thumbnail
3. **View it** — React + Babylon.js serves an interactive 3D gallery

### Quick start

```bash
npm install
npm run dev
```

### Add a new model

```bash
npm run new-model
```

This scaffolds a generator from the template. Write your geometry, then:

```bash
blender -b --python generators/generate_<name>.py
```

Register it in `src/data/models.js` and you're done.

### Gallery features

- Orbit, zoom, and pan around each model
- Wireframe mode
- Auto-rotation
- Light / dark backgrounds
- Mesh, vertex, and face counts

### Built with

| Layer | Tech |
|-------|------|
| Generation | Python + Blender |
| Frontend | React 19 + Vite 6 |
| 3D Viewer | Babylon.js 7 |
| Styling | Bootstrap 5 |
| Deploy | GitHub Pages via Actions |

---

*Code it. Render it. View it.*
