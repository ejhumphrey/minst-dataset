PYTHON=python
DATA_DIR=~/data

UIOWA_DIR=$(DATA_DIR)/uiowa
PHIL_DIR=$(DATA_DIR)/philharmonia
RWC_DIR=$(DATA_DIR)/RWC\ Instruments

UIOWA_INDEX=uiowa_index.csv
PHIL_INDEX=philharmonia_index.csv
RWC_INDEX=rwc_index.csv

.PHONY: clean

# You have to download manually.
all: clean deps test build

deps:
	pip install -r requirements.txt


clean:
	rm -rf $(UIOWA_INDEX) $(PHIL_INDEX) $(RWC_INDEX)


# Run the download scripts. Re
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



uiowa: $(UIOWA_INDEX)
philharmonia: $(PHIL_INDEX)
rwc: $(RWC_INDEX)
build: uiowa philharmonia rwc


test:
