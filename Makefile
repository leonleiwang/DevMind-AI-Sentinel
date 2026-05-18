.PHONY: backend frontend build dev docker-up docker-down clean

backend:
	cd backend && uvicorn main:app --reload

frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

dev:
	docker-compose up --build

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down

clean:
	rm -rf frontend/dist frontend/node_modules backend/__pycache__ backend/app/**/__pycache__
