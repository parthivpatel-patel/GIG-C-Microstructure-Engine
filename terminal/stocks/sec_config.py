"""SEC-only startup configuration. No shell sourcing or disclosure of contact values."""
import json,os,re,stat,tempfile
from pathlib import Path

KEYS=('GIG_SEC_ENABLED','GIG_SEC_POLICY_REVIEWED','GIG_SEC_USER_AGENT')
TRUE=frozenset(('1','true','yes','on'));FALSE=frozenset(('0','false','no','off',''))
ROOT=Path(__file__).resolve().parents[2]

def enabled(value):
    return value is True or (type(value) is str and value.strip().lower() in TRUE)

def user_agent_valid(value):
    if type(value) is not str or not re.fullmatch(r'[ -~]{8,160}',value):return False
    found=re.search(r'[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}(?![A-Za-z0-9.-])',value)
    return bool(found and re.search('[A-Za-z]{2}',value[:found.start()]))

def readiness(environment):
    flags={k:enabled(environment.get(k)) for k in KEYS[:2]}
    valid=user_agent_valid(environment.get(KEYS[2]));missing=[k for k,v in flags.items() if not v]
    if not valid:missing.append(KEYS[2])
    reason='sec_disabled_pending_fair_access_review' if not all(flags.values()) else 'sec_identifying_user_agent_required' if not valid else None
    invalid=[k for k in KEYS[:2] if k in environment and not (type(environment[k]) is bool or type(environment[k]) is str and environment[k].strip().lower() in TRUE|FALSE)]
    return {'ready':reason is None,'reason':reason,'missing_configuration':missing,'enabled':flags[KEYS[0]],'policy_reviewed':flags[KEYS[1]],'user_agent_present':bool(environment.get(KEYS[2])),'user_agent_valid':valid,'invalid_boolean_variables':invalid}

def _private(path,directory=False):
    s=path.lstat()
    if path.is_symlink() or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)&0o077 or (not stat.S_ISDIR(s.st_mode) if directory else not stat.S_ISREG(s.st_mode) or s.st_nlink!=1):raise ValueError('sec_private_configuration_permissions')

def resolve(environment,root=ROOT):
    # Explicit environment always wins,including empty/false values. No provider aliases.
    if all(k in environment for k in KEYS):return environment,{'source':'environment','error':None}
    directory=Path(root)/'.gig-sec';path=directory/'config.json'
    if not directory.exists() and not directory.is_symlink():return environment,{'source':'environment','error':None}
    try:
        _private(directory,True)
        if not path.exists() and not path.is_symlink():return environment,{'source':'environment','error':None}
        _private(path)
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
        try:
            if os.fstat(fd).st_size>4096:raise ValueError('sec_configuration_budget')
            raw=os.read(fd,4097)
        finally:os.close(fd)
        if len(raw)>4096:raise ValueError('sec_configuration_budget')
        def pairs(rows):
            out={}
            for k,v in rows:
                if k in out:raise ValueError('sec_configuration_duplicate_key')
                out[k]=v
            return out
        values=json.loads(raw,object_pairs_hook=pairs)
        if type(values) is not dict or set(values)!=set(KEYS) or any(type(v) not in (str,bool) for v in values.values()) or type(values[KEYS[2]]) is not str:raise ValueError('sec_configuration_fields')
        result=dict(environment)
        for k,v in values.items():result.setdefault(k,v)
        return result,{'source':'private_file_with_environment_precedence','error':None}
    except (OSError,ValueError,UnicodeError,RecursionError):
        # Configuration faults disable SEC alone;native and other providers can start.
        result=dict(environment);result[KEYS[0]]='0'
        return result,{'source':'private_file_rejected','error':'sec_private_configuration_invalid;run_SEC_configuration_check'}

def save(contact,*,policy_reviewed,root=ROOT):
    if policy_reviewed is not True or type(contact) is not str or contact!=contact.strip() or any(c.isspace() for c in contact):raise ValueError('sec_explicit_policy_and_contact_required')
    agent='GIG ATLAS '+contact
    if not user_agent_valid(agent) or not re.fullmatch(r'[A-Za-z0-9.!#$%&\'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',contact):raise ValueError('sec_owner_contact_invalid')
    directory=Path(root)/'.gig-sec';directory.mkdir(mode=0o700,exist_ok=True);_private(directory,True)
    path=directory/'config.json'
    if path.exists() or path.is_symlink():_private(path)
    fd,name=tempfile.mkstemp(prefix='.config-',dir=directory)
    try:
        with os.fdopen(fd,'w') as f:json.dump({KEYS[0]:'true',KEYS[1]:'true',KEYS[2]:agent},f);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
        directory_fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
        try:os.fsync(directory_fd)
        finally:os.close(directory_fd)
    finally:
        if Path(name).exists():Path(name).unlink()
    return {'status':'PRIVATE_SEC_CONFIGURATION_SAVED','restart_required':True,'contact_disclosed':False}
