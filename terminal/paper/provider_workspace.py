"""Explicit future qualification boundary. Nothing starts or reads keys on import.

No HTTP transport is constructed until a proof-authorized start action passes all
independent gates,an expiring session and exact reviewed risk configuration.
"""
import asyncio,hashlib,time
from pathlib import Path
from .contracts import PaperError,ExecutionGate,RiskLimits,canonical
from .alpaca import PaperAuthorization,AlpacaPaperBroker,validate_plan,exact_money
from .engine import PaperEngine
from .store import IntentStore
from terminal.alpaca_wire import FixtureWire,HTTPWire

FLAGS=('PROVIDER_ENABLED','CLOUD_APPROVED','PRIVATE_DISPLAY_APPROVED','PROTOCOL_REVIEWED','AUDIT_RETENTION_APPROVED','EXCLUSIVE_ACCOUNT_REVIEWED','RECONCILIATION_REVIEWED','NO_COST_CONFIRMED')
RISK=('max_order_cents','max_position_cents','max_gross_cents','max_daily_loss_cents','max_open_orders','max_snapshot_age_ms','max_price_distance_bps','max_concentration_bps')

class PaperProviderWorkspace:
    def __init__(self,directory,*,environment=None,credential_headers=None,reference=None,transport=None,authorization=None,limits=None,clock=None,monotonic=time.monotonic,sleep=asyncio.sleep):
        self.directory=Path(directory);self.environment=environment or {};self.credential_headers=credential_headers;self.reference=reference;self.transport=transport;self.clock=clock or(lambda:time.time_ns()//10**6);self.monotonic,self.sleep=monotonic,sleep
        self.engine=None;self.lock=asyncio.Lock();self.config_error=None
        if authorization is not None:
            self.authorization,self.limits=authorization,limits or RiskLimits();return
        e=self.environment
        try:
            values={k:int(e['GIG_PAPER_'+k.upper()])for k in RISK if type(e.get('GIG_PAPER_'+k.upper()))is str and e['GIG_PAPER_'+k.upper()].isascii() and e['GIG_PAPER_'+k.upper()].isdecimal()}
            if len(values)!=len(RISK):raise PaperError('paper_explicit_owner_risk_limits_required')
            self.limits=RiskLimits(**values)
        except (ValueError,KeyError):self.limits=RiskLimits();self.config_error='paper_explicit_owner_risk_limits_required'
        expires=e.get('GIG_PAPER_SESSION_EXPIRES_MS','0')
        self.authorization=PaperAuthorization(ExecutionGate.configured(e),*(e.get('GIG_PAPER_'+k)=='1' for k in FLAGS),e.get('GIG_PAPER_ACCOUNT_ID',''),e.get('GIG_PAPER_SESSION_START',''),int(expires)if type(expires)is str and expires.isascii() and expires.isdecimal() and len(expires)<=16 else 0,e.get('GIG_PAPER_RISK_SHA256',''))
    def readiness(self):
        reason=self.config_error
        try:
            if reason:raise PaperError(reason)
            self.authorization.require(self.clock())
            if hashlib.sha256(canonical(self.limits.view())).hexdigest()!=self.authorization.risk_sha256:raise PaperError('paper_reviewed_risk_binding_mismatch')
            if self.transport is None and self.credential_headers is None:raise PaperError('paper_server_credential_boundary_not_configured')
        except PaperError as e:reason=e.code
        return {'schema':'gig.paper.provider.readiness.v1','ready_for_explicit_qualification':reason is None,'provider_qualified':False,'active':self.engine is not None,'network_transport_active':self.engine is not None and type(self.engine.broker.transport)is HTTPWire,'reason':reason,'required_policy_flags':['GIG_PAPER_'+k for k in FLAGS]+['GIG_PAPER_EXECUTION_ENABLED','GIG_PAPER_OWNER_REVIEWED','GIG_PAPER_RISK_LIMITS_REVIEWED'],'risk_values_explicit':self.config_error is None,'fixture_transport':type(self.transport)is FixtureWire,'account_binding_present':bool(self.authorization.account_id),'account_identity_disclosed':False,'source':'AUTHORED_PROTOCOL_FIXTURE' if type(self.transport)is FixtureWire else 'UNAVAILABLE_UNTIL_QUALIFIED','limitations':['No startup account/credential/provider request.','General market-data permission never authorizes execution.','Stable REST double-read is not exchange-atomic;reviewed exclusive-account policy required.','Cloud/display,audit retention,session,risk,account/source/order qualification remain separate.']}
    def status(self):return {'readiness':self.readiness(),'session':self.engine.view() if self.engine else None}
    async def action(self,value):
        if type(value)is not dict or type(value.get('action'))is not str:raise PaperError('paper_provider_action_fields')
        if self.lock.locked():raise PaperError('paper_provider_busy')
        async with self.lock:
            action=value['action']
            # Local admission closes even if provider permission subsequently expires.
            if action=='kill' and set(value)=={'action'} and self.engine:self.engine.kill();return self.status()
            if action=='start_qualified_session' and set(value)=={'action','confirm_paper_only'} and value['confirm_paper_only'] is True:
                readiness=self.readiness()
                if not readiness['ready_for_explicit_qualification']:raise PaperError(readiness['reason'])
                if self.engine is None:
                    store=IntentStore(self.directory,profile=self.authorization.profile())
                    transport=self.transport or HTTPWire(lambda:self.authorization.require(self.clock()),self.credential_headers,validate_plan)
                    broker=AlpacaPaperBroker(store,transport,authorization=self.authorization,clock=self.clock,monotonic=self.monotonic,sleep=self.sleep,reference=self.reference)
                    self.engine=PaperEngine(store,broker,gate=self.authorization.execution,limits=self.limits,clock=self.clock);self.engine.kill()
                await self.engine.refresh()
            elif self.engine is None:raise PaperError('paper_qualified_session_not_started')
            elif action=='reconcile' and set(value)=={'action'}:await self.engine.refresh()
            elif action=='arm_reviewed_limits' and set(value)=={'action','confirm_reviewed_limits'}:await self.engine.arm_demo(value['confirm_reviewed_limits'])
            elif action=='submit' and set(value)=={'action','request_id','intent'}:
                await self.engine.submit(value['request_id'],value['intent']);await self.engine.refresh()
            elif action=='cancel' and set(value)=={'action','request_id'}:
                await self.engine.cancel(value['request_id']);await self.engine.refresh()
            elif action=='kill_and_cancel' and set(value)=={'action'}:await self.engine.kill_and_cancel()
            else:raise PaperError('paper_provider_action_fields')
            return self.status()
