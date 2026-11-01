"""Bounded fake-only HTTP facade. Opening the terminal never opens a broker store."""
import asyncio
from .contracts import PaperError, RiskLimits, nonce
from .engine import PaperEngine
from .fake import FakeBroker
from .store import IntentStore


class PaperWorkspace:
    def __init__(self, directory, *, clock=None):
        self.directory, self.clock = directory, clock
        self.engine = None
        self.lock = asyncio.Lock()

    def status(self):
        if self.engine is None:
            return {'schema':'gig.paper.sandbox.v1','mode':'DISABLED','classification':'UNAVAILABLE',
                    'external_execution_enabled':False,'account':None,'orders':[],
                    'kill_switch':True,'requires_reconciliation':True,
                    'risk_limits':RiskLimits().view(),'audit':None,
                    'limitations':['No broker access or account authentication.',
                                   'Open the explicit authored fake sandbox to test offline infrastructure.']}
        return self.engine.view()

    async def action(self, value):
        if type(value) is not dict or type(value.get('action')) is not str:
            raise PaperError('paper_action_fields')
        if self.lock.locked():
            raise PaperError('paper_workspace_busy')
        async with self.lock:
            action = value['action']
            if action == 'open_fake' and set(value) == {'action'}:
                if self.engine is None:
                    store = IntentStore(self.directory)
                    engine = PaperEngine(store, clock=self.clock)
                    engine.broker = FakeBroker(store, engine.clock)
                    # Restarts require a fresh explicit fake-risk acknowledgment.
                    engine.kill()
                    self.engine = engine
                await self.engine.refresh()
            elif self.engine is None:
                raise PaperError('paper_fake_sandbox_not_open')
            elif action == 'reconcile' and set(value) == {'action'}:
                await self.engine.refresh()
            elif action == 'arm_fake' and set(value) == {'action','acknowledge_example_limits'}:
                await self.engine.arm_demo(value['acknowledge_example_limits'])
            elif action == 'kill' and set(value) == {'action'}:
                self.engine.kill()
            elif action == 'kill_and_cancel' and set(value) == {'action'}:
                await self.engine.kill_and_cancel()
            elif action == 'submit' and set(value) == {'action','request_id','intent'}:
                await self.engine.submit(value['request_id'],value['intent'])
                await self.engine.refresh()
            elif action == 'cancel' and set(value) == {'action','request_id'}:
                await self.engine.cancel(value['request_id'])
                await self.engine.refresh()
            elif action in ('fill','expire','reject') and set(value) == ({'action','request_id','quantity','price'} if action == 'fill' else {'action','request_id'}):
                key=nonce(value['request_id']);record=self.engine.store.read()['orders'].get(key)
                if record is None:
                    raise PaperError('paper_unknown_intent')
                # Explicit AUTHORED fake event,not a provider fill or market assumption.
                self.engine.broker.event(record['client_id'],action,value.get('quantity'),value.get('price'))
                await self.engine.refresh()
            else:
                raise PaperError('paper_action_fields')
            return self.status()
