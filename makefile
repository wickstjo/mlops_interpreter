test:
	clear && python3 test.py

run:
	clear && python3 run.py

push:
	@echo "Commit message?"; \
	read msg; \
	git add -A; \
	git commit -m "$$msg"; \
	git push origin main