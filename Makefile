# RStudio Build pane (northwoods_faa.Rproj → BuildType: Makefile)
.PHONY: all dashboard

all: dashboard

dashboard:
	cd dashboard && quarto render
