#!/bin/bash

./start_app.sh -d
docker compose exec web python3 game.py
