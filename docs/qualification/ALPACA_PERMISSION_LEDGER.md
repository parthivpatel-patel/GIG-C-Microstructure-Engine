# Alpaca private research permission ledger

Recorded November 2, 2026 (America/New_York). Evidence source: the owner's statement in this task that Alpaca Support ticket **#384778** confirmed the following scope. This sprint did not contact support, independently retrieve the correspondence or authenticate an Alpaca account.

| Scope | Recorded permission/boundary |
|---|---|
| Environment | Private single-user GitHub Codespace controlled exclusively by the account owner |
| Use | Personal, noncommercial research |
| Display | Owner only, authenticated private browser UI |
| Real-time equities | Basic IEX; partial venue coverage, no complete-market/NBBO claim |
| Historical IEX | Subject to applicable account/API/plan limits; availability must be qualified |
| Historical SIP | Basic 15-minute restriction; deliberately not enabled by this narrow profile |
| Storage | Personal research/backtesting/local storage reported permitted; this launcher still leaves capture/export off |
| Cost | No paid subscription required for this stated usage; no plan upgrades or purchases authorized |
| Exclusions | Redistribution, third-party display, public dashboards, commercial/business-entity services |
| Trading | No order/account mutations authorized; independent execution gates stay disabled |

The process-only `private_iex` profile refers to this ticket and confirmation date. It neither stores new permission files nor changes the default server gates. The owner must explicitly invoke it in the described Codespace and confirm the private single-user condition. Credentials establish authentication, not usage rights or independently verified plan scope.

New `GIG_ALPACA_IEX_STREAM_ENABLED` is solely a read-only data gate. When present, its exact value `'1'` is required; false/invalid values override the legacy read-only `GIG_ALPACA_LIVE_ENABLED` alias. Legacy fallback remains only when the new key is absent, preserving older consumers. The new launcher never sets the legacy flag to one. Neither data flag authorizes orders.

Live/historical access, retention, exports, options, SIP, and paper execution remain distinct. This sprint does not grant unrestricted exchange-data rights. Pending provider results must remain pending until real owner-run evidence is available.
