ProjectPrefix: "XXX"
LabelFile:     "XXXLabel"
LabelLanguages: "en-us"
UserVISA:      "YOUR_VISA"
TaskID:        "0000"
TaskName:      "TaskName"

code_path:    "./code"
docs_path:    "./docs"
samples_path: "./samples"

reference_paths:
  - path: "MCP_MODEL_SOURCE:_Model_Template"
    description: "Primary model source via D365 MCP (`resolve_object`, `get_chunk`, `get_file`). Do not use local Source folders."
  - path: "./refcode"
    description: "Task-specific reference code"

ignore_patterns:
  - "*.dll"
  - "*.pdb"
  - "bin/"
  - "obj/"
  - ".git/"
