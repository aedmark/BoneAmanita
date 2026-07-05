
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name "MagicMock" -exec rm -rf {} +
rm -rf ./tests/.pytest_cache
rm -rf .pytest_cache
rm -rf ./logs
rm -rf ./memories
rm -rf ./tests/memories
rm -rf ./saves
rm -f ./lore/lenses.json
rm -f ./lore/akashic_discovered_words.json
rm -f ./legacy.json
rm -f ./fractal_adventure.json
rm -rf ./output
rm -rf ./test_telemetry_logs
rm -rf ./tests_isolated_legacy*.json
rm -rf ./test_output_full.log
rm -rf ./test_memories.log
rm -rf ./test_strata.json
rm -rf ./test_saves.log
rm -rf ./test_telemetry.log
rm -rf ./dummy.jsonl