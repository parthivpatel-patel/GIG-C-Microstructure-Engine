# Ten-minute honest demonstration

Use the isolated Sprint 3 branch, a private port and an offline fixture environment. Do not activate providers or create real paper orders during the interview. Missing external data is a useful boundary demonstration.

| Time | Demonstration | Explain |
|---|---|---|
| 0–1 min | Command Center and Securities Universe; search AAPL then NVDA. | Identity, data availability and entitlement are separate. Do not claim complete US listing coverage. |
| 1–2 min | Stock Intelligence, selected facts/filings or honest unavailable state. | Backend exact periods/ratios, source references, missingness and unavailable original receipt time. |
| 2–3 min | Options calculation S=K100,T1,σ.2,r=q0. | Raw independent reference7.965567455405804, UI≈7.966, full-precision disclosure; European assumptions. |
| 3–4 min | Company → Open Level1 research. | Selected symbol is preserved; no connection is opened. No input means no invented points or depth. |
| 4–5 min | Order Flow → advanced research → explicitly authored fixture. | Choose symbol/model/time. Show depth versus event versus quote requirements, rotate camera and inspect exact sample. |
| 5–6 min | 2D fallback and authored result export. | Reproducible selected parameters/source/results/SHA; provider observations excluded. |
| 6–7 min | Native historical replay: step/restart; native simulator: TWAP/VWAP/POV. | Determinism, provenance, authored liquidity/volume profiles, exact costs and limits. |
| 7–8 min | Research/validation and declared GARCH surface. | Mathematical response, filtering versus fitting, out-of-sample requirements; no alpha claim. |
| 8–9 min | Fake sandbox: arm example, durable AAPL intent, explicit fake fill, kill. | Commit-before-send, idempotency, risk reservations and reconciliation; no actual Alpaca account/order. |
| 9–10 min | Operations and test evidence. | Eight unchanged identities, compiler/sanitizer/reference tests and negative controls. External ARM64/provider/Codespaces/physical-device qualification still requires current evidence. |

Before presenting, run the applicable offline tests and confirm your actual checkout. Never show a credential/contact file. If time is short, demonstrate one coherent input→native/model→API→browser path and one meaningful negative case rather than claiming every model is economically validated.

## Optional Sprint4 extension (offline explanation)

Show the historical panel's explicit feed/time/adjustment controls and default-disabled state. Explain how authorized accepted bars would produce trailing research and a separate bar-derived dome while depth models remain unavailable. Use `terminal/tests/run_sprint4_browser.py` only in its isolated authored fixture environment to demonstrate populated paths;label screenshots AUTHORED_FIXTURE_NOT_PROVIDER. Show source revision/parameter binding and exact-byte export verification.

Then show the disabled paper-provider panel beside the authored sandbox. Explain persist-before-send,unknown acknowledgment,no blind create retry,exact FILL-ledger reconciliation and the difference between a kill gate and proof that outstanding orders were canceled. Never enable permissions or create a provider order as an interview demonstration under this sprint's authorization.
