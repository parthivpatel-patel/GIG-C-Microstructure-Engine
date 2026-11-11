# Live worker command ownership and safe failure diagnostics

No provider connection or account access was made. This is offline engineering evidence,not live IEX qualification.

A deterministic concurrent `start(NVDA)` / `start(MSFT)` fixture reproduced two simultaneous replacement workers after both callers awaited cancellation of the old worker. The original regression failed (`peak=2`,expected1);the receipt is retained in `build/remaining-engineering/live-concurrent-failing-before.log`. Public start/close commands now serialize through one owner lock. Internal cleanup avoids recursive lock acquisition. Retired socket owners are rejected before frame decoding or semantic mutation. Existing generation,subscription,source-accounting and entitlement controls remain intact.

Provider error diagnostics now retain the exact bounded MessagePack integer code and actual protocol phase. Categories distinguish authentication,subscription,runtime,connection and local protocol rejection **by observed phase**,without guessing unknown provider-code meanings. Raw provider message text is not echoed. The frontend validates the bounded diagnostic shape and displays phase/code beside transport status. Existing replies without the optional field remain valid.

Executed:35 focused live/reconnect/checkpoint tests;124 selected no-launch regressions with socket bind/connect and app-factory guards;154 frontend tests;TypeScript and production build. Zero final failures/errors/skips. The no-launch cohort grows from121 to124 because3 new live regressions were added;it is not the full API/browser cohort. The frontend grows from153 to154. Build retains the known optional-Three.js chunk-size warning;warnings were not suppressed.

The source/profile receipts are bound in the continuation evidence manifest. No authorization gate,trading setting,credential,private-origin policy or UI composition was changed. Actual owner-private transport/provider qualification remains pending and must not be inferred from fake transports. Full current native checks and all eight frozen identities are separately recorded in `NATIVE_HOT_RECOVERY_EVIDENCE.json`.
