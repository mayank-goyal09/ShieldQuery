import sys
import importlib

def find_module(target_name):
    # known entrypoints
    pkgs = ['langchain_core', 'langchain_community', 'langchain', 'langchain_text_splitters', 'langgraph']
    for p in pkgs:
        try:
            m = importlib.import_module(p)
            print(f"Checking in {p}")
        except:
            continue
            
print("Looking for create_retrieval_chain...")
try:
    from langchain.chains import create_retrieval_chain
    print("Found in langchain.chains")
except ImportError:
    print("Not in langchain.chains")
