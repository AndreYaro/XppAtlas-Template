ProjectPrefix: "XXX"
LabelFile:     "XXXLabel"
LabelLanguages: "en-us"
AutoTranslate: false
UserVISA:      "YOUR_VISA"

code_path:    "Tasks/{TaskName}/code"
docs_path:    "Tasks/{TaskName}/docs"
samples_path: "Tasks/{TaskName}/samples"

reference_paths:
  - path: "MCP_MODEL_SOURCE"
    description: "Primary model source via D365 MCP (`resolve_object`, `get_chunk`, `get_file`). Do not use local Source folders."

ignore_patterns:
  - "*.dll"
  - "*.pdb"
  - "bin/"
  - "obj/"
  - ".git/"

model_indexes:
  description: >
    Pre-built structural indexes of all X++ models.
    Read these at session start instead of scanning raw XML source files.
  bootstrap: "python tools/bootstrap_context.py [path]"
  ensure_current: "python tools/ensure_index.py [--model `ModelName`] [--quiet]"
  cross_model:     ".claude/index/_all_summary.json"
  per_model_summary: ".claude/index/`ModelName`_summary.json"
  per_model_full:    ".claude/index/`ModelName`.json"
  rebuild: "python tools/index_all.py [--incremental]"
  search:  "python tools/search_index.py `query` [--type class] [--stats]"
