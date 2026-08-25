# HotpotQA data source

The target is the official HotpotQA distractor development set linked by the authors at `http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json`. HotpotQA is distributed under CC BY-SA 4.0.

On 2026-08-25 the authors' host returned HTTP 502, so the completed pilot used the preparation script's JSON mirror at Hugging Face revision `7e54db4656209750ff487f6fdf8e39a66dba136b`. The mirrored 7,405-row file had SHA-256 `e3da074df24e8369009918aa5cdbdd254dadcde4c63f7569d36afd6f2268caa8`.

The script shuffles with Python `random.Random(7)`, selects the first 100 rows, and applies deterministic lexical-overlap passage ranking. The resulting EAR JSONL sample has SHA-256 `915d6b5706981b0f76e13bd56e3b81f8e09d11be09fd44ad1aa405aadb99f424`. The full dataset and prepared sample are not committed; both are reproducible from `scripts/prepare_hotpotqa.py`.
