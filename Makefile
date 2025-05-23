# ROS2 네비게이션 프로젝트 Makefile

.PHONY: all run launch rviz clean

# 환경 변수	demo, dongcheon, jiphyeon, gwanggaeto 
ENV_METASEJONG_SCENARIO ?= demo

METASEJONG_PROJECT_PATH ?= ../metacom2025-metasejong

all: run

link-scenario-data-folder:
	@echo "link metasejong scenario-data folder from ${METASEJONG_PROJECT_PATH}/scenario-data"
	@if [ -d "scenario-data" ]; then \
		echo "Removing scenario-data directory"; \
		rm -rf scenario-data; \
	fi
	ln -s ${METASEJONG_PROJECT_PATH}/scenario-data scenario-data

run:
	@echo "환경변수 설정 및 dockup compose up 실행"
	ENV_METASEJONG_SCENARIO=$(ENV_METASEJONG_SCENARIO) METASEJONG_PROJECT_PATH=$(METASEJONG_PROJECT_PATH) docker compose up
