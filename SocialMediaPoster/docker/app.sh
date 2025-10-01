#!/bin/bash
set -e

poetry run celery -A src.tasks worker -n socialmediaposter-worker -Q socialmediaposter
