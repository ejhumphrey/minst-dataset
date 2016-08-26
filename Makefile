PYTHON=python
DATA_DIR=~/data/minst
SEGMENTS_DATA_DIR=$(DATA_DIR)/note_files

UIOWA_DIR=$(DATA_DIR)/uiowa
PHIL_DIR=$(DATA_DIR)/philharmonia
RWC_DIR=$(DATA_DIR)/RWC\ Instruments
GOODSOUNDS_DIR=$(DATA_DIR)/good-sounds

UIOWA_INDEX=$(DATA_DIR)/uiowa_index.csv
PHIL_INDEX=$(DATA_DIR)/philharmonia_index.csv
RWC_INDEX=$(DATA_DIR)/rwc_index.csv
GOODSOUNDS_INDEX=$(DATA_DIR)/goodsounds_index.csv

UIOWA_NOTES=$(DATA_DIR)/uiowa_notes.csv
PHIL_NOTES=$(DATA_DIR)/phil_notes.csv
RWC_NOTES=$(DATA_DIR)/rwc_notes.csv
GOODSOUNDS_NOTES=$(DATA_DIR)/goodsounds_notes.csv

MASTER_INDEX=$(DATA_DIR)/master_index.csv
RWC_TRAIN_INDEX=$(DATA_DIR)/rwc_train_index.csv
PHIL_TRAIN_INDEX=$(DATA_DIR)/phil_train_index.csv
UIOWA_TRAIN_INDEX=$(DATA_DIR)/uiowa_train_index.csv

TRAIN_TEST_SPLIT=.2

.PHONY: clean test

# You have to download manually.
all: clean deps test build

deps:
	pip install -r requirements.txt


clean:
	rm -rf $(UIOWA_INDEX) $(PHIL_INDEX) $(RWC_INDEX) $(UIOWA_NOTES) $(PHIL_NOTES) $(RWC_NOTES) $(GOODSOUNDS_INDEX) $(GOODSOUNDS_NOTES)

# Run the download scripts. TODO: Zips?
download_uiowa:
	$(PYTHON) scripts/download.py ./data/uiowa.json $(UIOWA_DIR)

download_phil:
	$(PYTHON) scripts/download.py ./data/philharmonia.json $(PHIL_DIR)

download: download_uiowa download_phil

$(UIOWA_INDEX):
	$(PYTHON) scripts/collect_data.py uiowa $(UIOWA_DIR) $(UIOWA_INDEX) --strict_taxonomy
$(PHIL_INDEX):
	$(PYTHON) scripts/collect_data.py philharmonia $(PHIL_DIR) $(PHIL_INDEX) --strict_taxonomy
$(RWC_INDEX):
	$(PYTHON) scripts/collect_data.py rwc $(RWC_DIR) $(RWC_INDEX) --strict_taxonomy
$(GOODSOUNDS_INDEX):
	$(PYTHON) scripts/collect_data.py goodsounds $(GOODSOUNDS_DIR) $(GOODSOUNDS_INDEX) --strict_taxonomy


$(UIOWA_NOTES): $(UIOWA_INDEX)
	$(PYTHON) scripts/split_audio_to_clips.py $(UIOWA_INDEX) $(UIOWA_NOTES) $(SEGMENTS_DATA_DIR)

# pass_thru because phil already has notes
$(PHIL_NOTES): $(PHIL_INDEX)
	$(PYTHON) scripts/split_audio_to_clips.py $(PHIL_INDEX) $(PHIL_NOTES) --pass_thru

$(RWC_NOTES): $(RWC_INDEX)
	$(PYTHON) scripts/split_audio_to_clips.py $(RWC_INDEX) $(RWC_NOTES) $(SEGMENTS_DATA_DIR)

# pass_thru because good-sounds already has notes
$(GOODSOUNDS_NOTES): $(GOODSOUNDS_INDEX)
	$(PYTHON) scripts/split_audio_to_clips.py $(GOODSOUNDS_INDEX) $(GOODSOUNDS_NOTES) --pass_thru


# Build the master index from the note indeces
$(MASTER_INDEX): $(UIOWA_NOTES) $(PHIL_NOTES) $(RWC_NOTES)
	$(PYTHON) scripts/manage_dataset.py join $(UIOWA_NOTES) $(PHIL_NOTES) $(RWC_NOTES) --output=$(MASTER_INDEX)

$(RWC_TRAIN_INDEX): $(MASTER_INDEX)
	echo $(PYTHON) scripts/manage_dataset.py split $(MASTER_INDEX) rwc $(TRAIN_TEST_SPLIT) $(RWC_TRAIN_INDEX)
# $(PHIL_TRAIN_INDEX): $(MASTER_INDEX)
# 	echo $(PYTHON) scripts/manage_dataset.py split $(MASTER_INDEX) philharmonia $(TRAIN_TEST_SPLIT) $(PHIL_TRAIN_INDEX)
$(UIOWA_TRAIN_INDEX): $(MASTER_INDEX)
	echo $(PYTHON) scripts/manage_dataset.py split $(MASTER_INDEX) uiowa $(TRAIN_TEST_SPLIT) $(UIOWA_TRAIN_INDEX)


uiowa: $(UIOWA_INDEX) $(UIOWA_NOTES)
philharmonia: $(PHIL_INDEX) $(PHIL_NOTES)
rwc: $(RWC_INDEX) $(RWC_NOTES)
goodsounds: $(GOODSOUNDS_INDEX) $(GOODSOUNDS_NOTES)
dataset: $(MASTER_INDEX) $(RWC_TRAIN_INDEX) $(UIOWA_TRAIN_INDEX) #$(PHIL_TRAIN_INDEX)
# build: uiowa philharmonia rwc goodsounds
build: uiowa rwc

test:
	./run_tests.sh
