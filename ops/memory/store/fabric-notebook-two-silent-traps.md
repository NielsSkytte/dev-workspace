---
id: fabric-notebook-two-silent-traps
ts: 2026-08-20T16:10:00Z
type: semantic
scope: global
tags: [fabric, notebook, ipython, dax, rest-api, debugging]
source: session:8374f87e-2a3d-4166-8017-4515139d44c8
status: distilled
description: "Two failures that look like anything but their cause: IPython silently rebinds a helper named _i to a string between cells, and executeQueries omits a column from the row JSON when its value is BLANK"
---

Hand-written from the session. Both shipped in one change and both were found only because the same
change added logging.

## `_i` is IPython's, not yours

IPython owns `_i`, `_ii`, `_iii` and `_i<n>` as **input history**, and rebinds `_i` to the previous
cell's **source string** after every cell executes. A function defined as `def _i(v)` is a function
for the rest of its own cell and a `str` by the next one:

```
TypeError: 'str' object is not callable
```

raised several cells from the definition, in code that has not changed. Also reserved: `_`, `__`,
`___` (outputs), `_ih`, `_oh`, `_dh`, `In`, `Out`. This bites in Fabric notebooks specifically
because the cell boundary is where the rebinding happens, so a single-cell test never reproduces it.

Grep a notebook for these before shipping:
`(?<![A-Za-z0-9_])_(i|ii|iii|ih|oh|dh)(?![A-Za-z0-9_])`

## `executeQueries` drops BLANK columns from the row object

The Power BI `executeQueries` JSON response **omits a column entirely** when its value is BLANK -
it does not return `null`. `COUNTROWS` of an empty table is BLANK, so:

```
EVALUATE ROW("T","Date","R",COUNTROWS('Date'))       -> {"[T]": "Date"}          <- no [R]
EVALUATE ROW("T","Customer","R",COUNTROWS('Customer')) -> {"[T]":"Customer","[R]":238343}
```

`x["[R]"]` therefore raises `KeyError` the moment one table in the sweep is empty. Always `.get`.

In this case one empty dimension killed a whole cost ranking on every run for weeks, and the only
symptom was a `cost ranking unavailable` line printed into a notebook snapshot nobody reads.

## The lesson that outlasts both

The guard that was supposed to prevent this - a `try/except` inside the logging function so
telemetry could never break the job - **did not cover the expressions that built its arguments**.
Those were evaluated in the caller. Wrap the whole call site, not the callee.

And a diagnostic that only prints is a diagnostic that does not exist. Both bugs became findable
the moment the failure path wrote a row (`Status='CostRankingFailed'`, `ErrorCode='KeyError'`)
instead of a line to stdout.
