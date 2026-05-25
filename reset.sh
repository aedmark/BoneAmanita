
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name "MagicMock" -exec rm -rf {} +
rm -rf ./tests/memories
rm -rf ./logs
rm -rf ./memories
rm -rf ./saves
rm -f ./lore/lenses.json
rm -f ./lore/akashic*
rm -f ./legacy.json
rm -rf ./output
rm -rf ./tests/tests_isolated_legacy_void.json
rm -rf ./tests_isolated_legacy_void.json
rm -rf ./tests/logs
rm -rf ./tests/saves
rm -rf ./tests/tests