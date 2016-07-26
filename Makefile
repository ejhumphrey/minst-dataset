PYTHON=python
DATA_DIR=~/data
SEGMENTS_DIR=$(DATA_DIR)/segments
SEGMENTS_DATA_DIR=$(SEGMENTS_DIR)/audio_files

UIOWA_DIR=$(DATA_DIR)/uiowa
PHIL_DIR=$(DATA_DIR)/philharmonia
RWC_DIR=$(DATA_DIR)/RWC\ Instruments

UIOWA_INDEX=uiowa_index.csv
PHIL_INDEX=philharmonia_index.csv
RWC_INDEX=rwc_index.csv

UIOWA_NOTES=uiowa_notes.csv
PHIL_NOTES=phil_notes.csv
RWC_NOTES=rwc_notes.csv

.PHONY: clean

# You have to download manually.
all: clean deps test build

deps:
	pip install -r requirements.txt


clean:
	rm -rf $(UIOWA_INDEX) $(PHIL_INDEX) $(RWC_INDEX) $(UIOWA_NOTES) $(PHIL_NOTES) $(RWC_NOTES)

# Run the download scripts. TODO: Zips?
download_uiowa:
	$(PYTHON) scripts/download.py ./data/uiowa.json $(UIOWA_DIR)

download_phil:
	$(PYTHON) scripts/download.py ./data/philharmonia.json $(PHIL_DIR)

download: download_uiowa download_phil

$(UIOWA_INDEX):
	$(PYTHON) scripts/collect_data.py uiowa $(UIOWA_DIR) $(UIOWA_INDEX)
$(PHIL_INDEX):
	$(PYTHON) scripts/collect_data.py philharmonia $(PHIL_DIR) $(PHIL_INDEX)
$(RWC_INDEX): 
	$(PYTHON) scripts/collect_data.py rwc $(RWC_DIR) $(RWC_INDEX)

$(UIOWA_NOTES): $(UIOWA_INDEX)
	$(PYTHON) scripts/segment_audio.py $(UIOWA_INDEX) $(UIOWA_NOTES) $(SEGMENTS_DATA_DIR)

# PHIL doesn't have segments. This just creates a notes file. Which,
#  lets be real we might as well just copy.
$(PHIL_NOTES): $(PHIL_INDEX)
	cp $(PHIL_INDEX) $(PHIL_NOTES)

$(RWC_NOTES): $(RWC_INDEX)
	$(PYTHON) scripts/segment_audio.py $(RWC_INDEX) $(RWC_NOTES) $(SEGMENTS_DATA_DIR)


uiowa: $(UIOWA_INDEX) $(UIOWA_NOTES)
philharmonia: $(PHIL_INDEX) $(PHIL_NOTES)
rwc: $(RWC_INDEX) $(RWC_NOTES)
build: uiowa philharmonia rwc


test:
