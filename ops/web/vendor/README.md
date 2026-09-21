# vendor

Third-party code, committed on purpose. Nothing here is fetched at runtime and nothing
needs npm to be installed - the files are served from `ops/dashboard.py` like any other
asset.

| File | Package | Version | Origin |
|---|---|---|---|
| `preact.module.js` | preact | 10.29.8 | `dist/preact.module.js` from the published tarball |
| `hooks.module.js` | preact | 10.29.8 | `preact/hooks/dist/hooks.module.js` |
| `htm.module.js` | htm | 3.1.1 | `dist/htm.module.js` |

About 16 KB in total, minified as published.

## The two edits

1. `hooks.module.js` imports from `"preact"` as published, which only resolves under a
   bundler or an import map. Rewritten to `"./preact.module.js"` so the browser resolves
   it directly and no import map is needed.
2. The trailing `//# sourceMappingURL=` comment was removed from `preact.module.js` and
   `hooks.module.js`. The `.map` files are not shipped, so the comment only produces a
   404 in devtools.

Nothing else was changed. To re-verify, `npm pack preact@10.29.8 htm@3.1.1`, unpack, and
diff against these files - the only differences should be the two above.

## Why these

`htm` uses tagged template literals, so components are written in plain JavaScript with
no JSX and nothing to compile. `preact` gives DOM diffing, which is the point: the pages
re-fetch every 60 seconds, and without diffing each refresh destroys an open drawer, the
scroll position, an expanded row and anything half-typed in a filter box.

## Upgrading

Replace the file, redo edit 1 and 2, record the new version in the table above, and load
each page once - there is no build step and no lockfile to update.
