"""Owner-invoked private Codespaces profile for ticket #384778, not a default gate.

No network, file writes, credential values or global environment mutation here.
Codespaces metadata cannot prove private forwarding; the operator attests that
separate boundary. This profile cannot enable any broker execution or disk capture.
"""
from .auth import credentials, presence
from terminal.server.config import launch_settings

PERMISSION_REFERENCE = 'Alpaca Support #384778; owner-reported confirmation 2026-11-02'


def private_environment(environment, *, confirm_private=False):
    if confirm_private is not True:
        raise ValueError('private_single_user_confirmation_required')
    if environment.get('CODESPACES') != 'true':
        raise ValueError('owner_private_codespace_required')
    _, origins, expected = launch_settings(environment)
    if not expected or origins != expected:
        raise ValueError('single_exact_codespaces_origin_required')
    result = dict(environment)
    for name in ('ENABLED', 'PROTOCOL_REVIEWED', 'PRIVATE_DISPLAY_APPROVED',
                 'CLOUD_PROCESSING_APPROVED', 'NO_COST_CONFIRMED'):
        result['GIG_ALPACA_' + name] = '1'
    result['GIG_ALPACA_PERMISSION_REFERENCE'] = PERMISSION_REFERENCE
    for name in ('ENABLED', 'CLOUD_APPROVED', 'PRIVATE_DISPLAY_APPROVED',
                 'PROTOCOL_REVIEWED', 'NO_COST_CONFIRMED', 'IEX_APPROVED'):
        result['GIG_ALPACA_HISTORY_' + name] = '1'
    result.update(
        GIG_TERMINAL_ALLOWED_ORIGINS=expected,
        GIG_ALPACA_HISTORY_PERMISSION_REFERENCE=PERMISSION_REFERENCE,
        GIG_ALPACA_IEX_STREAM_ENABLED='1',
        GIG_ALPACA_LIVE_ENABLED='0',
        GIG_PAPER_EXECUTION_ENABLED='0',
        GIG_ALPACA_HISTORY_SIP_APPROVED='0',
        GIG_ALPACA_HISTORY_EXPORT_APPROVED='0',
        GIG_ALPACA_OPTIONS_ENABLED='0',
        GIG_ALPACA_STORE_ENABLED='0',
        GIG_HISTORY_STORE_ENABLED='0',
        GIG_ALPACA_ASSET_REFERENCE_ENABLED='0',
    )
    # Validate aliases/shape without returning the credential values in a report.
    credentials(result)
    return result


def readiness(environment):
    from .live import secure_msgpack
    try:
        profile = private_environment(environment, confirm_private=True)
        secure_msgpack()
        ready, reason = True, None
    except (ValueError, ImportError) as error:
        profile = None
        allowed = ('private_single_user_confirmation_required',
                   'owner_private_codespace_required',
                   'single_exact_codespaces_origin_required',
                   'alpaca_server_credentials_required',
                   'alpaca_invalid_server_credentials',
                   'alpaca_conflicting_credential_aliases',
                   'alpaca_incomplete_alpaca_credential_pair',
                   'alpaca_incomplete_apca_credential_pair',
                   'msgpack_security_patch_required')
        reason = str(error) if str(error) in allowed else 'private_runtime_or_origin_configuration_invalid'
        ready = False
    return {
        'schema': 'gig.private.iex.readiness.v1', 'ready': ready, 'reason': reason,
        'credentials': presence(environment),
        'profile': 'EXPLICIT_OWNER_INVOKED_READ_ONLY_IEX',
        'execution_enabled': False, 'disk_capture_enabled': False,
        'permission_reference': PERMISSION_REFERENCE,
        'expected_origin': profile['GIG_TERMINAL_ALLOWED_ORIGINS'] if profile else None,
        'private_port_verified': False,
        'required_operator_assertion': 'Port8787 PRIVATE; authenticated owner only; personal noncommercial use',
        'provider_verified': False, 'network_requests': 0,
        'scope': 'Configuration/protocol readiness only;native,assets,private authentication and providers qualify separately',
    }
