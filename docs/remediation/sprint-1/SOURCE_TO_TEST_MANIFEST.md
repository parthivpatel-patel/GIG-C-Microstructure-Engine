# Source-to-test change inventory

Implementation `3f4c1984603c03f35d92d32a5aaaa5d0b874f0d3` against `10eaee30d598807a23e42a8b60abe3d5a5dc2514`; 26 paths below. The subsequent evidence
commit changes only this documentation directory. JSON contains bytes/SHA256 and test
mapping. No C++core/bindings, workflows, provider gate files orconfiguration changed.

| Changed path | Verification |
|---|---|
| docs/backend/QUANT_MODEL_VALIDATION.md | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| docs/remediation/sprint-1/CONCENTRATION_RESEARCH_CONTRACT.md | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| docs/remediation/sprint-1/MODEL_STATUS.md | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| docs/remediation/sprint-1/OPTIONS_GRID_CONTRACT.md | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| docs/remediation/sprint-1/RESEARCH_SESSION_ENVELOPE.md | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| scripts/qualify_remediation_envelope.py | evidence/envelope.json; evidence/journal-scaling.json |
| terminal/server/analysis.py | terminal/test_research_resources.py; terminal/stocks/test_overnight.py |
| terminal/server/app.py | terminal/test_concentration.py; terminal/test_research_resources.py; terminal/test_request_proof.py |
| terminal/server/concentration.py | terminal/test_concentration.py; terminal/tests/remediation-sprint1-validation.mjs |
| terminal/server/engine.py | terminal/test_concentration.py; terminal/server/test_server.py |
| terminal/server/market_events.py | terminal/test_research_resources.py; terminal/stocks/test_projection.py |
| terminal/stocks/options.py | terminal/stocks/test_remediation_options.py; terminal/tests/remediation-sprint1-validation.mjs |
| terminal/stocks/test_remediation_options.py | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| terminal/test_concentration.py | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| terminal/test_research_resources.py | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| terminal/tests/atlas5-validation.mjs | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| terminal/tests/remediation-sprint1-validation.mjs | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| terminal/tests/run_remediation_sprint1.py | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| terminal/web/src/App.tsx | terminal/tests/workspace-qualification.mjs |
| terminal/web/src/ConcentrationPanel.tsx | terminal/tests/remediation-sprint1-validation.mjs |
| terminal/web/src/PortfolioLab.tsx | terminal/tests/atlas5-validation.mjs |
| terminal/web/src/ResearchDiagnostics.tsx | terminal/tests/atlas5-validation.mjs |
| terminal/web/src/StockIntelligence.tsx | terminal/tests/remediation-sprint1-validation.mjs; terminal/tests/atlas-validation.mjs |
| terminal/web/src/VolatilitySurface.tsx | terminal/tests/remediation-sprint1-validation.mjs |
| terminal/web/src/format.test.ts | Dedicated regression runner, frontend build orsource/link review; see test evidence |
| terminal/web/src/format.ts | terminal/web/src/format.test.ts; terminal/tests/atlas5-validation.mjs |
