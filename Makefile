PYTHON = python
VENV_DIR = hotswap_env
PACKAGE_NAME = binswap

ifeq ($(OS),Windows_NT)
    ACTIVATE_VENV = $(VENV_DIR)\Scripts\activate
else
    ACTIVATE_VENV = source $(VENV_DIR)/bin/activate
endif

venv:
	$(PYTHON) -m venv $(VENV_DIR)

activate: venv

install: venv
	$(ACTIVATE_VENV) && $(PYTHON) -m pip install -r requirements.txt

run: activate
	$(PYTHON) -m $(PACKAGE_NAME)

clean:
	rm -rf $(VENV_DIR)

.PHONY: venv activate install run clean