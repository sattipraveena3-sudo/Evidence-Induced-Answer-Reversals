from __future__ import annotations
import argparse, json, math, random, re, urllib.request
from pathlib import Path
from collections import Counter

URL = 'http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json'


def tok(s: str):
    return re.findall(r"[a-z0-9]+", s.lower())


def lexical_rank(question: str, paragraphs: list[tuple[str,list[str]]]):
    q = Counter(tok(question))
    scored=[]
    for idx,(title,sents) in enumerate(paragraphs):
        text = title + ' ' + ' '.join(sents)
        d = Counter(tok(text))
        overlap = sum(min(q[t], d[t]) for t in q)
        title_overlap = sum(1 for t in set(tok(title)) if t in q)
        score = 3*title_overlap + overlap + 0.001*(len(paragraphs)-idx)
        scored.append((score, idx, text))
    scored.sort(key=lambda x:(-x[0], x[1]))
    return [x[2] for x in scored]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output', default='data/primary.jsonl')
    ap.add_argument('--limit', type=int, default=100)
    ap.add_argument('--seed', type=int, default=7)
    args=ap.parse_args()

    print('Downloading official HotpotQA distractor dev set...')
    with urllib.request.urlopen(URL, timeout=180) as r:
        data=json.loads(r.read().decode('utf-8'))

    rng=random.Random(args.seed)
    rng.shuffle(data)
    data=data[:args.limit]
    out=Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w',encoding='utf-8') as w:
        for ex in data:
            passages=lexical_rank(ex['question'], ex['context'])
            rec={
                'id': ex['_id'],
                'question': ex['question'],
                'answers': [ex['answer']],
                'passages': passages,
                'source': 'HotpotQA dev distractor',
                'ranking': 'deterministic lexical-overlap baseline'
            }
            w.write(json.dumps(rec, ensure_ascii=False)+'\n')
    print(f'Wrote {len(data)} questions to {out}')

if __name__=='__main__':
    main()
