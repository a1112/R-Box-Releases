#!/usr/bin/env python3
"""Validate the local release provenance index; never access the network or publish."""
import argparse
import json
from pathlib import Path
import re

SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?")

def validate(data):
    """Reject inconsistent release identities, versions, links and source mappings."""
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported schema_version')
    cat = data.get('catalog_release', {})
    if cat != {'tag':'catalog','release_url':'https://github.com/a1112/R-Box-Releases/releases/tag/catalog','versioned_application':False}:
        raise ValueError('catalog is a signed index, not an application version')
    identities, tags, count = set(), set(), 0
    if not isinstance(data.get('applications'), list) or not data['applications']:
        raise ValueError('Application history is required')
    for app in data['applications']:
        identity = app.get('identity', '')
        if not re.fullmatch(r'r-[a-z0-9-]+', identity) or identity in identities:
            raise ValueError('Invalid or duplicate application identity')
        identities.add(identity)
        repo, status = app.get('source_repository'), app.get('source_mapping')
        if status == 'unresolved':
            if repo is not None or not app.get('exception'):
                raise ValueError('Unresolved mapping must remain explicit and unassigned')
        elif status != 'verified' or not isinstance(repo, str) or not re.fullmatch(r'a1112/[A-Za-z0-9_.-]+',repo):
            raise ValueError('Invalid verified source repository')
        if identity == 'r-labelimg' and (repo is not None or status != 'unresolved'):
            raise ValueError('r-labelimg source identity is unresolved; reconcile evidence before changing this policy')
        if not app.get('releases'):
            raise ValueError('An identity must retain its release history')
        for release in app['releases']:
            version = release.get('version', '')
            match = SEMVER.fullmatch(version) if isinstance(version, str) else None
            if not match or (match[4] and any(p.isdigit() and len(p)>1 and p.startswith('0') for p in match[4].split('.'))):
                raise ValueError('Invalid SemVer')
            tag = f'{identity}-v{version}'
            if release.get('tag') != tag or tag in tags:
                raise ValueError('Duplicate tag or application/version mismatch')
            tags.add(tag)
            if release.get('release_url') != f'https://github.com/a1112/R-Box-Releases/releases/tag/{tag}':
                raise ValueError('Release URL does not bind the exact tag')
            if type(release.get('prerelease')) is not bool or release['prerelease'] != bool(match[4]):
                raise ValueError('Prerelease channel mismatch')
            commits = release.get('source_commits')
            if not isinstance(commits,list) or not commits or any(not isinstance(s,str) or not re.fullmatch(r'[a-f0-9]{40}',s) for s in commits):
                raise ValueError('Exact source commit evidence is required')
            assets = release.get('artifact_names')
            if not isinstance(assets,list) or not assets or len(assets)!=len(set(assets)) or any(not isinstance(a,str) or not (a.startswith(f'{identity}-{version}-') or (identity=='r-box' and a in {'manager-releases.json','manager-releases.json.sig'})) or '/' in a or '\\' in a for a in assets):
                raise ValueError('Artifact does not bind its application version')
            count += 1
    return {'applications':len(identities),'application_releases':count,'catalog_releases':1,'unresolved_sources':[a['identity'] for a in data['applications'] if a['source_mapping']=='unresolved']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['check','show'])
    args=parser.parse_args()
    try:
        data=json.loads((Path(__file__).resolve().parent/'release-history.json').read_text(encoding='utf-8'))
        result=validate(data)
        print(json.dumps(data if args.command=='show' else result,indent=2))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(1, f'error: {exc}\n')

if __name__=='__main__':
    main()
