import engine
print(f"Engine file: {engine.__file__}")
print(f"Attributes in engine: {dir(engine)}")
try:
    from engine import final_result
    print("Successfully imported final_result")
except ImportError as e:
    print(f"ImportError: {e}")
