"""Exact offline research API. No broker/live trading or Terminal dependency."""
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from . import _native

__version__ = _native.__version__
SCHEMA_VERSION = '1.0'
MAX_DOCUMENT_BYTES = 32 * 1024 * 1024
_ERROR_NAMES = ['none','invalid_range','overflow','underflow','malformed','off_unit','invalid_enum','missing_metadata','inconsistent_metadata','duplicate','capacity','unsupported','crossed_quote','identity_mismatch','not_found','resource_exhausted','priority_violation','inconsistent_state','sequence_gap','sequence_duplicate','sequence_regression','sequence_exhausted','session_boundary','ordering_error','recovery_required']

class EngineError(ValueError):
    def __init__(self, code, field, index=None):
        self.code = str(code)
        self.field = field
        self.index = None if index is None else int(index)
        self.code_name = _ERROR_NAMES[int(code)] if self.code.isdecimal() and int(code) < len(_ERROR_NAMES) else self.code
        self.accepted = None
        self.failed_input_index = None
        super().__init__(f'{self.code_name}: {field}' + ('' if self.index is None else f'[{self.index}]'))

class SchemaError(EngineError):
    def __init__(self, field):
        super().__init__('schema', field)

def _checked(result):
    if not result['ok']:
        e = result['error']
        raise EngineError(e['code'], e['field'], e['index'])
    return result['value']

def _plain(value):
    return value.to_dict() if isinstance(value, ResearchDocument) else value

def _exact_tree(value, depth=0):
    if depth > 48:
        raise SchemaError('json.depth')
    if type(value) is str:
        try:
            value.encode('utf-8')
        except UnicodeError as error:
            raise SchemaError('json.utf8') from error
        return
    if value is None or type(value) is bool:
        return
    if type(value) is list:
        for item in value:
            _exact_tree(item, depth+1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise SchemaError('json.key_type')
            _exact_tree(key, depth+1)
            _exact_tree(item, depth+1)
        return
    raise SchemaError('json.numbers_must_be_exact_decimal_strings')

def _json(value):
    value = _plain(value)
    _exact_tree(value)
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
    if len(encoded.encode('utf-8')) > MAX_DOCUMENT_BYTES:
        raise SchemaError('json.byte_limit')
    return encoded

class ResearchDocument(Mapping):
    """Immutable owned canonical JSON; every retrieved nested value is an independent copy."""
    __slots__ = ('_json',)
    def __init__(self, value):
        object.__setattr__(self, '_json', _json(value))
    def __setattr__(self, name, value):
        raise AttributeError('ResearchDocument is immutable')
    def __getitem__(self, key):
        return self.to_dict()[key]
    def __iter__(self):
        return iter(self.to_dict())
    def __len__(self):
        return len(self.to_dict())
    def to_dict(self):
        return json.loads(self._json)
    def dumps(self):
        return self._json
    @property
    def sha256(self):
        return hashlib.sha256(self._json.encode('utf-8')).hexdigest()

@lru_cache(maxsize=1)
def _catalog():
    from .manifest_schema import MANIFEST_SCHEMA
    catalog = _native.schema_catalog()
    catalog['gig.run_manifest'] = deepcopy(MANIFEST_SCHEMA)
    catalog['gig.run_manifest']['properties']['data']['properties']['instrument_rules']['items'] = catalog['instrument_rules']
    def strict_patterns(value):
        if type(value) is dict:
            pattern = value.get('pattern')
            if type(pattern) is str and pattern.endswith('$'):
                value['pattern'] = pattern + r'(?![\s\S])'
            for child in value.values(): strict_patterns(child)
        elif type(value) is list:
            for child in value: strict_patterns(child)
    strict_patterns(catalog)  # ECMA/Python $ may otherwise accept a final newline.
    return catalog

def schema_catalog():
    return deepcopy(_catalog())

@lru_cache(maxsize=32)
def _validator(name):
    from jsonschema import Draft202012Validator, validators, ValidationError
    def minimum(validator, bound, instance, schema):
        if type(instance) is str and len(instance) <= 40 and re.fullmatch(r'-?[0-9]+', instance) and int(instance) < int(bound):
            yield ValidationError('integer below exact native minimum')
    def maximum(validator, bound, instance, schema):
        if type(instance) is str and len(instance) <= 40 and re.fullmatch(r'-?[0-9]+', instance) and int(instance) > int(bound):
            yield ValidationError('integer above exact native maximum')
    ExactValidator = validators.extend(Draft202012Validator, {'x-integer-minimum':minimum,'x-integer-maximum':maximum})
    schema = _catalog().get(name)
    if schema is None:
        raise SchemaError('wire.schema')
    Draft202012Validator.check_schema(schema)
    return ExactValidator(schema)

def validate_document(document):
    doc = _plain(document)
    _exact_tree(doc)
    if type(doc) is not dict or set(doc) != {'schema','version','data'}:
        raise SchemaError('wire.envelope')
    if type(doc['schema']) is not str or type(doc['version']) is not str:
        raise SchemaError('wire.envelope_types')
    if doc['version'] != SCHEMA_VERSION:
        raise SchemaError('wire.unsupported_version')
    errors = iter(_validator(doc['schema']).iter_errors(doc))
    error = next(errors, None)
    if error is not None:
        raise SchemaError('wire.' + '.'.join(map(str, error.absolute_path)))
    if doc['schema'] == 'gig.run_manifest':
        data = doc['data']
        for field, key in [('inputs','identity'),('parents','run_id'),('outputs','identity')]:
            identifiers = [x[key] for x in data[field]]
            if len(set(identifiers)) != len(identifiers):
                raise SchemaError('manifest.duplicate_'+field)
        if any(name not in _catalog() or not name.startswith('gig.') for name in data['schema_versions']):
            raise SchemaError('manifest.unknown_schema')
        for value in data['seeds'] + [data['coverage']['records']]:
            if not 0 <= int(value) <= (1 << 64)-1:
                raise SchemaError('manifest.uint64_range')
        for field in ['start_ns','end_ns']:
            time = data['coverage'][field]
            if time['reason'] == '0' and not -(1 << 63) <= int(time['value']) < (1 << 63):
                raise SchemaError('manifest.timestamp_range')
        start, end = data['coverage']['start_ns'], data['coverage']['end_ns']
        if start['reason'] == end['reason'] == '0' and int(start['value']) > int(end['value']):
            raise SchemaError('manifest.coverage_order')
        for rules in data['instrument_rules']:
            _checked(_native.validate_rules(rules))
        if doc['data']['complete'] and doc['data']['errors']:
            raise SchemaError('manifest.complete_with_errors')
    return ResearchDocument(doc)

def dumps(document):
    return validate_document(document).dumps()

def loads(encoded):
    if type(encoded) is bytes:
        try:
            encoded = encoded.decode('utf-8')
        except UnicodeError as error:
            raise SchemaError('json.utf8') from error
    if type(encoded) is not str:
        raise SchemaError('json.type')
    try:
        if len(encoded.encode('utf-8')) > MAX_DOCUMENT_BYTES:
            raise SchemaError('json.byte_limit')
    except UnicodeError as error:
        raise SchemaError('json.utf8') from error
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise SchemaError('json.duplicate_key')
            result[key] = value
        return result
    def constant(value):
        raise SchemaError('json.nonfinite')
    try:
        value = json.loads(encoded, object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, RecursionError) as error:
        if isinstance(error, EngineError):
            raise
        raise SchemaError('json.malformed') from error
    return validate_document(value)

def event(document, rules, *, inspect_incomplete=False):
    if type(inspect_incomplete) is not bool:
        raise SchemaError('event.inspect_boolean')
    doc = validate_document(document)
    return ResearchDocument(_checked(_native.event_roundtrip(doc.to_dict(), rules, inspect_incomplete)))

def event_canonical(document, rules):
    return _checked(_native.event_canonical(validate_document(document).to_dict(), rules))

def as_fraction(metric):
    value = metric['value']
    return None if value is None else Fraction(int(value['numerator']), int(value['denominator']))

def exact_fraction(numerator, denominator='1'):
    result = _checked(_native.fraction_roundtrip({'numerator':numerator,'denominator':denominator}))
    return Fraction(int(result['numerator']), int(result['denominator']))

class Replay:
    """One mutable native owner; calls keep the GIL. Snapshots/results are independent values."""
    def __init__(self, rules, config, *, limits=None, resource_budget_bytes='134217728'):
        if limits is None:
            limits = {'max_orders':'100000','max_levels':'10000','max_snapshot_depth':'4096'}
        self._owner = _checked(_native.new_replay(rules, config, limits, resource_budget_bytes))
    def apply(self, document):
        _checked(self._owner.apply(validate_document(document).to_dict()))
    def run(self, documents):
        accepted = 0
        for index, doc in enumerate(documents):
            try:
                self.apply(doc)
            except EngineError as error:
                error.accepted = accepted
                error.failed_input_index = index
                raise
            accepted += 1
        return accepted
    def reset(self, document, restart_plan):
        _checked(self._owner.reset(validate_document(document).to_dict(), restart_plan))
    def recover(self, document):
        _checked(self._owner.recover(validate_document(document).to_dict()))
    def snapshot(self, depth='1'):
        return ResearchDocument(_checked(self._owner.snapshot(depth)))
    def metrics(self, depth='1'):
        return ResearchDocument(_checked(self._owner.metrics(depth)))
    def canonical(self):
        return _checked(self._owner.canonical())
    def status(self):
        return deepcopy(_checked(self._owner.status()))

def book_analytics(snapshot, depth='1'):
    return ResearchDocument(_checked(_native.book_analytics(validate_document(snapshot).to_dict(), depth)))

def flow_analytics(quotes, trades, config, as_of):
    return ResearchDocument(_checked(_native.flow_analytics(quotes, trades, config, as_of)))

class Simulation:
    """Offline synthetic matching. Internal exchange truth differs from delayed client reports."""
    def __init__(self, config, *, resource_budget_bytes='134217728'):
        self._owner = _checked(_native.new_simulation(config, resource_budget_bytes))
    def submit(self, decision_time, order):
        _checked(self._owner.submit(decision_time, order))
    def cancel(self, decision_time, order_id):
        _checked(self._owner.cancel(decision_time, order_id))
    def advance(self, simulation_time):
        _checked(self._owner.advance(simulation_time))
    def snapshot(self):
        return ResearchDocument(_checked(self._owner.snapshot()))
    def queue_position(self, order_id):
        return deepcopy(_checked(self._owner.queue(order_id)))
    def canonical(self):
        return _checked(self._owner.canonical())

def twap(config):
    return ResearchDocument(_checked(_native.twap(config)))

def vwap(config, weights, profile_artifact, profile_available_at, *, oracle=False):
    if type(oracle) is not bool:
        raise SchemaError('execution.oracle_boolean')
    return ResearchDocument(_checked(_native.vwap(config, weights, profile_artifact, profile_available_at, '1' if oracle else '0')))

def pov(config, observations, numerator, denominator):
    return ResearchDocument(_checked(_native.pov(config, observations, numerator, denominator)))

@dataclass(frozen=True)
class ExecutionResult:
    plan: ResearchDocument
    simulation: ResearchDocument

def simulate_plan(plan, config, initial_liquidity, finish):
    result = _checked(_native.simulate_plan(validate_document(plan).to_dict(), config, initial_liquidity, finish))
    return ExecutionResult(ResearchDocument(result['plan']), ResearchDocument(result['simulation']))

def transaction_costs(config, fills):
    return ResearchDocument(_checked(_native.transaction_costs(config, fills)))

def run_manifest(data):
    return validate_document({'schema':'gig.run_manifest','version':SCHEMA_VERSION,'data':deepcopy(data)})

def _validate_export_references(manifest, documents):
    """Shared consistency checks, after input-byte integrity has been established."""
    inputs = manifest['data']['inputs']
    input_by_name = {a['identity']: a for a in inputs}
    input_names = set(input_by_name)
    def check_digest(identity, digest, kind):
        # An artifact identity names exactly the retained bytes, not an implicit transformation.
        # Unknown hashes remain unknown; known contradictory hashes are never silently replaced.
        if digest['reason'] == '0' and digest['value'] != input_by_name[identity]['sha256']:
            raise SchemaError('export.' + kind + '_digest_mismatch')
    source_runs = {manifest['data']['run_id']} | {p['run_id'] for p in manifest['data']['parents']}
    input_hashes = {a['sha256'] for a in inputs}
    if any(p['manifest_sha256'] not in input_hashes for p in manifest['data']['parents']):
        raise SchemaError('export.parent_manifest_not_retained')
    for document in documents:
        doc = _plain(document); data = doc['data'];refs = []
        if doc['schema'] == 'gig.event':
            provenance = data['metadata']['provenance']
            dataset = provenance['dataset']['value']
            if dataset is not None and dataset['identity'] not in input_names:
                raise SchemaError('export.dataset_artifact_not_retained')
            if dataset is not None:
                check_digest(dataset['identity'], dataset['sha256'], 'dataset')
            if provenance['generator_seed']['reason'] == '0' and provenance['generator_seed']['value'] not in manifest['data']['seeds']:
                raise SchemaError('export.generator_seed_not_declared')
            for parent in provenance['parents']:
                if parent['identity'] not in input_names:
                    raise SchemaError('export.parent_artifact_not_retained')
                check_digest(parent['identity'], parent['sha256'], 'parent')
        elif doc['schema'] == 'gig.book_snapshot':
            refs.append(data['run_id'])
        elif doc['schema'] == 'gig.simulation_output':
            refs.append(data['state']['config']['run_id'])
            if data['state']['config']['seed'] not in manifest['data']['seeds']:
                raise SchemaError('export.simulation_seed_not_declared')
        elif doc['schema'] == 'gig.execution_schedule':
            refs.append(data['config']['run_id'])
            if data['algorithm'] == '1':
                profile = data['profile']
                if profile['reason'] != '0' or profile['value'] not in input_names:
                    raise SchemaError('export.profile_artifact_not_retained')
            if data['algorithm'] == '2' and any(v['source_artifact'] not in input_names for v in data['volumes']):
                raise SchemaError('export.volume_artifact_not_retained')
            if data['oracle'] and manifest['data']['parameters'].get('oracle_benchmark') is not True:
                raise SchemaError('export.oracle_label_required')
        elif doc['schema'] == 'gig.metric_result':
            result = data['result']
            if data['kind'] == 'book': refs.append(result['source']['run_id'])
            elif data['kind'] == 'flow': refs += [p['run_id'] for p in result['parents']]
            elif data['kind'] == 'cost':
                refs += [result['config']['run_id'],result['config']['simulation_run_id']]
                benchmarks = [result['config']['arrival'],result['config']['terminal']] + [p['decision_benchmark'] for p in result['parents']]
                if any(b['source_artifact'] not in input_names for b in benchmarks):
                    raise SchemaError('export.benchmark_artifact_not_retained')
        if any(r not in source_runs for r in refs):
            raise SchemaError('export.unresolved_parent_run')
        if manifest['data']['schema_versions'].get(doc['schema']) != SCHEMA_VERSION:
            raise SchemaError('export.schema_version_not_declared')


def export_run(directory, manifest, artifacts, *, input_artifacts):
    """Local no-overwrite export. Incomplete marker persists until all checksummed files finalize."""
    if type(artifacts) is not dict or type(input_artifacts) is not dict:
        raise SchemaError('export.mapping_type')
    manifest = validate_document(manifest)
    if manifest['schema'] != 'gig.run_manifest' or not manifest['data']['complete']:
        raise SchemaError('manifest.complete_required')
    encoded = {}
    for name, document in sorted(artifacts.items()):
        if type(name) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\.json',name) or name in {'manifest.json','manifest.incomplete.json'}:
            raise SchemaError('export.artifact_name')
        encoded[name] = dumps(document).encode('utf-8')
    inputs = manifest['data']['inputs']
    if set(input_artifacts) != {a['identity'] for a in inputs}:
        raise SchemaError('export.input_artifact_set')
    input_bytes = {}
    for artifact in inputs:
        supplied = input_artifacts[artifact['identity']]
        data = supplied if type(supplied) is bytes else (supplied.encode('utf-8') if type(supplied) is str else dumps(supplied).encode('utf-8'))
        if len(data) > MAX_DOCUMENT_BYTES or hashlib.sha256(data).hexdigest() != artifact['sha256']:
            raise SchemaError('export.input_hash_or_size')
        input_bytes[artifact['identity']] = data
    if sum(map(len, input_bytes.values())) + sum(map(len, encoded.values())) > 128*1024*1024:
        raise SchemaError('export.run_byte_limit')
    _validate_export_references(manifest, artifacts.values())
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    incomplete = directory/'manifest.incomplete.json'
    pending = manifest.to_dict()
    pending['data']['complete'] = False
    incomplete.write_text(_json(pending), encoding='utf-8')
    try:
        (directory/'inputs').mkdir()
        retained_inputs = []
        for index, artifact in enumerate(inputs):
            name = f'inputs/input-{index:04d}.bin'
            with (directory/name).open('xb') as stream:
                stream.write(input_bytes[artifact['identity']]);stream.flush();os.fsync(stream.fileno())
            retained = deepcopy(artifact);retained['local_file'] = name;retained_inputs.append(retained)
        outputs = []
        for name, data in encoded.items():
            with (directory/name).open('xb') as stream:
                stream.write(data);stream.flush();os.fsync(stream.fileno())
            outputs.append({'identity':name,'sha256':hashlib.sha256(data).hexdigest(),'schema':_plain(artifacts[name])['schema'],'version':SCHEMA_VERSION})
        final = manifest.to_dict()
        final['data']['outputs'] = outputs
        final['data']['inputs'] = retained_inputs
        validated = run_manifest(final['data'])
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', dir=directory, prefix='.manifest-', delete=False, encoding='utf-8') as stream:
                temporary = Path(stream.name)
                stream.write(validated.dumps());stream.flush();os.fsync(stream.fileno())
            os.link(temporary, directory/'manifest.json')
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        incomplete.unlink()
        return validated
    except Exception as error:
        failed = pending
        failed['data']['errors'].append({'code':'export_failure','field':type(error).__name__,'index':None})
        try:
            incomplete.write_text(_json(failed), encoding='utf-8')
        except OSError:
            pass  # Original error propagates; existing incomplete marker remains authoritative.
        raise


def _read_export_file(path):
    with path.open('rb') as stream:
        data = stream.read(MAX_DOCUMENT_BYTES+1)
    if len(data) > MAX_DOCUMENT_BYTES:
        raise SchemaError('export.file_byte_limit')
    return data

def verify_export(directory):
    """Read-only local integrity verification; hashes are not proof of source authenticity."""
    directory = Path(directory)
    if (directory/'manifest.incomplete.json').exists():
        raise SchemaError('export.incomplete')
    if (directory/'manifest.json').is_symlink():
        raise SchemaError('export.manifest_path')
    manifest = loads(_read_export_file(directory/'manifest.json'))
    if manifest['schema'] != 'gig.run_manifest' or not manifest['data']['complete']:
        raise SchemaError('export.incomplete_manifest')
    verified_bytes = 0
    for artifact in manifest['data']['inputs']:
        name = artifact['local_file']
        if name is None:
            raise SchemaError('export.input_not_retained')
        path = directory/name
        if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
            raise SchemaError('export.input_path')
        encoded = _read_export_file(path);verified_bytes += len(encoded)
        if verified_bytes > 128*1024*1024 or hashlib.sha256(encoded).hexdigest() != artifact['sha256']:
            raise SchemaError('export.input_integrity')
    def documents():
        nonlocal verified_bytes
        for artifact in manifest['data']['outputs']:
            name = artifact['identity']
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\.json', name):
                raise SchemaError('export.artifact_name')
            path = directory/name
            if path.is_symlink() or not path.resolve().is_relative_to(directory.resolve()):
                raise SchemaError('export.path')
            encoded = _read_export_file(path);verified_bytes += len(encoded)
            if verified_bytes > 128*1024*1024:
                raise SchemaError('export.run_byte_limit')
            if hashlib.sha256(encoded).hexdigest() != artifact['sha256']:
                raise SchemaError('export.output_integrity')
            doc = loads(encoded)
            if doc['schema'] != artifact['schema'] or doc['version'] != artifact['version']:
                raise SchemaError('export.output_schema')
            yield doc
    _validate_export_references(manifest, documents())
    return manifest

def native_build_info():
    return {'compiler':_native.__compiler__,'python':_native.__python__,'pybind11':_native.__pybind11__,'package_version':__version__,'schema_version':SCHEMA_VERSION,'build_type':_native.__build_type__,'config_flags':_native.__config_flags__,'binding_flags':_native.__target_flags__,'core_flags':_native.__core_flags__}
