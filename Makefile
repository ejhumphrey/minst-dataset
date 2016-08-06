PYTHON=python
DATA_DIR=~/data
SEGMENTS_DIR=$(DATA_DIR)/segments
SEGMENTS_DATA_DIR=$(SEGMENTS_DIR)/audio_files

UIOWA_DIR=$(DATA_DIR)/uiowa
PHIL_DIR=$(DATA_DIR)/philharmonia
RWC_DIR=$(DATA_DIR)/RWC\ Instruments
GOODSOUNDS_DIR=$(DATA_DIR)/good-sounds

UIOWA_INDEX=uiowa_index.csv
PHIL_INDEX=philharmonia_index.csv
RWC_INDEX=rwc_index.csv
GOODSOUNDS_INDEX=goodsounds_index.csv

UIOWA_NOTES=uiowa_notes.csv
PHIL_NOTES=phil_notes.csv
RWC_NOTES=rwc_notes.csv
GOODSOUNDS_NOTES=goodsounds_notes.csv

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
	$(PYTHON) scripts/segment_audio.py $(UIOWA_INDEX) $(UIOWA_NOTES) $(SEGMENTS_DATA_DIR)

# pass_thru because phil already has notes
$(PHIL_NOTES): $(PHIL_INDEX)
	$(PYTHON) scripts/segment_audio.py $(PHIL_INDEX) $(PHIL_NOTES) --pass_thru

$(RWC_NOTES): $(RWC_INDEX)
	$(PYTHON) scripts/segment_audio.py $(RWC_INDEX) $(RWC_NOTES) $(SEGMENTS_DATA_DIR)

# pass_thru because good-sounds already has notes
$(GOODSOUNDS_NOTES): $(GOODSOUNDS_INDEX)
	$(PYTHON) scripts/segment_audio.py $(GOODSOUNDS_INDEX) $(GOODSOUNDS_NOTES) --pass_thru


uiowa: $(UIOWA_INDEX) $(UIOWA_NOTES)
philharmonia: $(PHIL_INDEX) $(PHIL_NOTES)
rwc: $(RWC_INDEX) $(RWC_NOTES)
goodsounds: $(GOODSOUNDS_INDEX) $(GOODSOUNDS_NOTES)
build: uiowa philharmonia rwc

test:
	./run_tests.sh
