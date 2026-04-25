# Literature Entity Extraction Plan

The MVP now has an offline-first parser for reviewed LC-MS/MS method snippets:

```powershell
.\.venv\Scripts\python.exe scripts\extract_lcms_entities.py path\to\snippets.txt --source-name paper_batch_001
```

It extracts conservative entities into the canonical dataset schema:

- compound name
- column name, chemistry, and stationary-phase type
- mobile phase A/B
- simplified gradient start/end/duration
- temperature, flow, injection volume, pH
- ion mode, precursor/product m/z
- retention time

The `--use-openai` flag is reserved for future opt-in LLM extraction from abstracts or PDF-derived text. It is intentionally disabled in this MVP so that API keys are never printed or used implicitly. Recommended next step: add a reviewed JSON schema prompt that returns only canonical fields plus confidence and source spans.
