SHELL := /bin/bash

REPO_ROOT := $(abspath ..)
BUILD_DIR := $(REPO_ROOT)/tmp/pdfs/ear_paper
OUTPUT_DIR := $(REPO_ROOT)/output/pdf
OUTPUT_PDF := $(OUTPUT_DIR)/Evidence_Induced_Answer_Reversals_Praveena_Satti.pdf

export TEXMFVAR := $(REPO_ROOT)/tmp/texmf-var

.PHONY: all figure pdf

all: pdf

figure:
	MPLCONFIGDIR=$(REPO_ROOT)/tmp/matplotlib python $(REPO_ROOT)/paper/build_figures.py

pdf: figure
	mkdir -p $(BUILD_DIR) $(OUTPUT_DIR)
	cd $(REPO_ROOT) && pdflatex -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) paper/main.tex
	cd $(BUILD_DIR) && BIBINPUTS=$(REPO_ROOT):$(REPO_ROOT)/paper: bibtex main
	cd $(REPO_ROOT) && pdflatex -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) paper/main.tex
	cd $(REPO_ROOT) && pdflatex -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) paper/main.tex
	cp $(BUILD_DIR)/main.pdf $(OUTPUT_PDF)
	@echo "Built $(OUTPUT_PDF)"
