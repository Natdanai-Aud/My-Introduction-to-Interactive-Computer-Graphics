# AGENTS.md

Coursework repo for *Introduction to Interactive Computer Graphics*. Every `.html` file is a
standalone, self-contained demo — there is **no build system, no `package.json`, no test runner, no
linter, no CI, no `.gitignore`, and no Git LFS**. Do not introduce any of those.

## Layout

- `week1/` … `week12/` — one directory per lecture week; `ASSIGNMENT2-PAINT/`,
  `ASSIGNMENT3-Next-Gen-Rendering/`, `ASSIGNMENT4/` are the graded assignments.
- **Filenames repeat across directories on purpose** — they are starter-vs-completed pairs, not
  duplicates: `800_Transformation.html` exists in `week4/`, `week5/`, and `ASSIGNMENT2-PAINT/`;
  `shader_starter.html` in both `week11/` and `week12/`; `gpuMesh.html` in `week5/` and `week6/`.
  Never rename, move, or dedupe files across week directories.
- Single branch `main`. History is GitHub-web-UI commits (`Add files via upload`, `Delete <path>`) —
  there is no message convention to follow.

## Three rendering eras — match the file you are editing, never unify them

1. **Canvas 2D software rasterizer** — `week1/800_raster.html`, `week2/raster.html`,
   `week3/800_raster.html`, `week4/800_Transformation.html`, `week5/800_Transformation.html`,
   `ASSIGNMENT2-PAINT/800_Transformation.html`. No three.js at all: a 200×200 canvas CSS-scaled to
   500×500 with `image-rendering: pixelated`, manual `createImageData` pixel writes, and hand-rolled
   matrix math. Keep the 200×200 backing store — the pixelated upscale is the point.
2. **three.js r128, UMD globals** — `week2/gpu.html`, `week3/gpu_interaction.html`,
   `week5/`–`week12/`, `ASSIGNMENT4/`. Core is `three@0.128.0/build/three.min.js`; addons come from
   the **`examples/js/`** tree (`controls/OrbitControls.js`, `loaders/OBJLoader.js`,
   `loaders/GLTFLoader.js`, `loaders/EXRLoader.js`) and attach to the `THREE` global. Some files pull
   the core from `cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js` instead of jsdelivr —
   both pin r128, keep whichever the file already uses.
   - **`examples/js/` was removed in modern three.js.** Bumping the version 404s every loader.
   - r128-only API that is *correct here* and would break if "modernized":
     `renderer.outputEncoding = THREE.sRGBEncoding` (modern: `outputColorSpace` / `SRGBColorSpace`),
     `PlaneBufferGeometry` / `Float32BufferAttribute` (r125+ renamed these), `texture.encoding`.
3. **three.js 0.170, ES modules** — `ASSIGNMENT3-Next-Gen-Rendering/` only. Uses
   `<script type="importmap">` → `three@0.170.0/build/three.module.js` and `examples/jsm/`. Do not
   convert the r128 files to ESM or add a bundler; the UMD/importmap split is load-bearing.

## Running and verifying

Verification is opening the file in a browser. There is no test suite to run.

- **Relative asset paths loaded through a loader require a local HTTP server** — `file://` is
  CORS-blocked and yields a blank scene. Affected: `ASSIGNMENT4/Interactive-3D-Portfolio.html:73`
  (`Model/Room.glb`) and `ASSIGNMENT3-Next-Gen-Rendering/index.html:358` (`toyota_ae86.glb`).
  Serve from the repo root and open the path:
  ```
  python -m http.server 8000     # then http://localhost:8000/ASSIGNMENT4/Interactive-3D-Portfolio.html
  ```
  A blank canvas from `file://` is expected behavior, **not** a bug to fix.
- **`standalone.html` is the deliberate counter-pattern**: the same demo with the GLB base64-embedded
  and fed to `loader.parse()` instead of `loader.load()`, so it opens from `file://`. When a
  deliverable must be double-clickable, follow that pattern rather than adding a server requirement.
- Most other demos fetch assets from **hardcoded external URLs** — `sibsansuk.github.io` (the
  instructor's CDN), `natdanai-aud.github.io`, `threejs.org/examples/textures`, `bwiggs.com`. These
  are not broken local references: do not repoint them at in-repo files, and expect them to fail
  offline.

## Blender → three.js export pipeline

`week5/ArrayExporter.py`, `week6/ArrayExporter.py`, `week7/export_vert_uv_color.py`,
`week10/export_vert_uv_color.py`, `week10/export_vert_uv_color_normal.py` are **not** CLI scripts.
They are pasted into Blender's **Scripting → Text Editor**, read `bpy.context.active_object`, and
write a Text datablock named **`ExportedJS`** that you then copy-paste into the HTML. There is no
codegen step and no headless way to run them.

- The newer scripts emit a leading marker `/* Auto-exported from Blender */`, then `const vertices`,
  `const uvs`, `const colors`, `const normals`, `const indices`. `ArrayExporter.py` (`week5`/`week6`)
  predates the marker and emits a bare `const vertices = [...]` only.
- **Axis conversion is baked in**: Blender Z-up → three.js Y-up as `(x, z, -y)`. `ArrayExporter.py`
  (`week5`/`week6`) predates this too, and emits raw `(x, y, z)` at 4 decimals — that difference is
  intentional, not a bug.
- **UVs are not flipped.** If a texture renders upside down, the intended fix is `v_ = 1.0 - v_`
  (documented in the script's own comment), not an image flip.
- `export_vert_uv_color_normal.py` de-duplicates by `v.index` and emits an `indices` array; the older
  scripts emit one vertex per face-corner with no indices. Match what the consuming file expects.
- A UV layer is required — the exporter raises `RuntimeError` without one.
- **Only the array directly after the `/* Auto-exported from Blender */` marker is live.** Re-exports
  leave earlier arrays commented out with `// const vertices = [` rather than deleted — in
  `week7/UV_Materials.html` ~2.4 MB of dead commented exports sit above the live one, which is most of
  why that file is 4.6 MB. Don't reformat or reflow those single multi-megabyte lines; the files are
  generated output and the line count is meaningless.

## Conventions

- Comments, and Blender `print()`/error strings, are written in **Thai** — match that when editing
  existing files. Thai terms worth keeping verbatim: `ExportedJS`, `ชนิด Mesh`,
  `/* Auto-exported from Blender */`.
- Most three.js files are near-identical copies of the instructor's `shader_starter.html` / `800_*`
  template. Keeping them structurally alike is intentional — 2-space indent inside the single
  `<script>`, `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`, a `resize` listener that
  updates `camera.aspect` and calls `renderer.setSize`, and a `requestAnimationFrame` loop feeding
  `uniforms.uTime.value = time * 0.001`.

## File hazards

- `week1/raster_graphics.html` and `week3/cpu.html` are committed **0 bytes**. They are not truncated
  by your edits.
- `week9/industrial_microscope_1k.fbx` is a **directory** containing the FBX plus a `textures/`
  subfolder.
- `week9/pbr.blend1` is a Blender autosave backup that got committed; `week9/pbr.blend` was deleted
  (commit `84a5562`) but `week9/pbr.glb` remains.
- ~15 MB of binaries are committed raw (`week9/ushaka_sea_world_aquarium_1k.exr` 5.8 MB,
  `week9/microscope.glb` 5.4 MB, the `.fbx` tree ~3.3 MB). Never run a formatter or codemod across
  the repo — operate only on the specific file you were asked to change.
