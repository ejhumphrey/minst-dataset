import os

# Couple notes
# - These should be migrated to a config
# - The files should be package resources
DATA_DIR = os.path.join(os.path.dirname(__file__), os.pardir, "data")
CANONICAL_FILES_PATH = os.path.join(DATA_DIR, "canonical_files.json")
