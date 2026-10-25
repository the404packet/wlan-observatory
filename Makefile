.PHONY: manifests pipeline test serve clean-manifests

manifests:
	python -m src.pipeline.manifest --raw data/raw --out data/manifests

pipeline: manifests
	@echo "Stage 0 only. Stages 1+ will extend this target."

test:
	pytest -q

serve:
	flask --app src.web.app run --debug

clean-manifests:
	rm -f data/manifests/*.manifest.json