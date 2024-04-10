#!/bin/bash

mkdir -p postgres_data
docker compose up $1
