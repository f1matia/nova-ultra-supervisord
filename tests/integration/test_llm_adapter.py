import os
from backend.backend_addons.adapters.llm import LLMAdapter

def test_llm_adapter_generate_stream():
    # Works in mock mode without keys
    os.environ.setdefault("LLM_PROVIDER","mock")
    llm = LLMAdapter()
    txt = llm.generate("Hello NOVA!")
    assert isinstance(txt, str) and len(txt) > 0
    chunks = list(llm.stream("Hello NOVA!"))
    assert len(chunks) > 0
