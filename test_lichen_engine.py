from lichen.engine import LichenEngine

engine = LichenEngine()
print(engine.process_input("/inventory"))
print("="*40)
print(engine.process_input("I walk bravely into the darkness."))
print("="*40)
print(engine.process_input("/look"))
