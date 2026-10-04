#!/usr/bin/env python3
"""Read-only credential preflight. Never print API bodies or credentials."""
import json
import os
import urllib.error
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def main():
    token = os.environ.get('ANACONDA_API_TOKEN', '').strip()
    owner = os.environ.get('ANACONDA_OWNER', 'hallamlab').lower()
    if not token:
        raise SystemExit('Missing ANACONDA_API_TOKEN in the release environment or repository secrets.')
    opener = urllib.request.build_opener(NoRedirect)

    def get(path):
        request = urllib.request.Request(
            'https://api.anaconda.org' + path,
            headers={'Authorization': 'token ' + token, 'Accept': 'application/json'},
        )
        try:
            with opener.open(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise SystemExit(f'Anaconda GET {path}: HTTP {error.code}; check token validity and permissions.') from None
        except (urllib.error.URLError, ValueError):
            raise SystemExit(f'Anaconda GET {path}: connection failure or invalid API response.') from None

    user = get('/user')
    print('PASS: Anaconda.org accepted the credential.', flush=True)
    auth = get('/authentication')
    scopes = auth.get('scopes') or []
    if isinstance(scopes, str):
        scopes = scopes.split()
    if not set(scopes).intersection({'all', 'api', 'api:write'}):
        raise SystemExit('Token does not report an API write scope; create a token with api scope.')
    print('PASS: Token reports API write permission.', flush=True)
    if user.get('login', '').lower() != owner:
        orgs = get('/user/orgs')
        if not isinstance(orgs, list) or not any(
            isinstance(org, dict) and org.get('login', '').lower() == owner for org in orgs
        ):
            raise SystemExit('Authenticated account does not report membership in the configured organization.')
    print('PASS: Token owner or account membership matches the configured Anaconda organization.')
    print('No packages uploaded or changed. Package-specific write access is not proven by this read-only check.')


if __name__ == '__main__':
    main()
