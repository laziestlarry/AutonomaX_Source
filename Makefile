.PHONY: dev api dashboard fmt

dev:
	uvicorn apps.chatbot.main:APP --reload --port 8080 & \
	streamlit run apps/dashboard/app.py --server.port 8501

api:
	uvicorn apps.chatbot.main:APP --reload --port 8080

dashboard:
	streamlit run apps/dashboard/app.py --server.port 8501

.PHONY: preflight
preflight:
	python ops/preflight.py
