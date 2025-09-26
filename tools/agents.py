from __future__ import annotations
from typing import Dict, Any, List, Tuple
import os, re

KEYWORDS = {
    'shopify': ['shopify','order','product','graphql'],
    'gcp': ['gcloud','cloud run','scheduler','bigquery','ga4','gcs','pubsub'],
    'ml': ['model','train','embedding','llm','prompt','feature','inference'],
    'growth': ['campaign','referral','kpi','lifecycle','pricing','subscription'],
    'branding': ['logo','brand','palette','guideline'],
    'video': ['.mp4','.mov','.mkv','voiceover','script','thumbnail'],
}

def suggest_tags_for_path(path: str, kind: str) -> List[str]:
    tags = set([kind])
    lower = path.lower()
    for tag, needles in KEYWORDS.items():
        for n in needles:
            if n in lower:
                tags.add(tag)
                break
    # language tags
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.py','.ipynb']: tags.add('python')
    if ext in ['.js','.ts','.tsx','.jsx']: tags.add('js')
    if ext in ['.md','.txt']: tags.add('doc')
    if ext in ['.csv','.parquet','.json','.ndjson']: tags.add('data')
    return sorted(tags)

def suggest_tasks_for_item(item: Dict[str, Any]) -> List[Dict[str, str]]:
    kind = item.get('kind','other')
    path = item.get('path','')
    tasks: List[Dict[str,str]] = []
    if kind == 'code':
        tasks.append({'role':'dev','desc': 'lint + unit check', 'path': path})
        tasks.append({'role':'dev','desc': 'readme + usage stub', 'path': path})
        if 'shopify' in path.lower(): tasks.append({'role':'dev','desc':'wire shopify backfill to BQ','path': path})
        if 'gcp' in path.lower() or 'infra' in path.lower(): tasks.append({'role':'dev','desc':'review gcloud scripts','path': path})
    elif kind == 'doc':
        tasks.append({'role':'research','desc': 'summarize + tag', 'path': path})
        tasks.append({'role':'analysis','desc': 'extract action items', 'path': path})
    elif kind == 'media':
        tasks.append({'role':'growth','desc': 'prepare post schedule', 'path': path})
        tasks.append({'role':'growth','desc': 'generate variants (thumbs/captions)', 'path': path})
    elif kind == 'data':
        tasks.append({'role':'analysis','desc': 'schema + sample rows', 'path': path})
        tasks.append({'role':'dev','desc': 'load to BQ table', 'path': path})
    elif kind == 'link':
        tasks.append({'role':'pm','desc': 'triage external link', 'path': path})
    else:
        tasks.append({'role':'pm','desc': 'triage + route', 'path': path})
    return tasks

def propose_from_inventory(items: List[Dict[str, Any]], limit: int = 200) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    tag_suggestions: List[Dict[str, Any]] = []
    task_suggestions: List[Dict[str, str]] = []
    for it in items[:limit]:
        tags = suggest_tags_for_path(it.get('path',''), it.get('kind','other'))
        tag_suggestions.append({'path': it.get('path',''), 'tags': tags})
        task_suggestions.extend(suggest_tasks_for_item(it))
    return tag_suggestions, task_suggestions

