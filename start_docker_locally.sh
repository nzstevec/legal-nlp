#!/bin/bash

docker run -d -p 8501:8501 -e "HUGGING_FACE_HUB_TOKEN=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" stevechapman/legal_nlp:1.11

docker run -d -p 8501:8501 stevechapman/legal_nlp:1.5

docker run -p 8501:8501 -e "HUGGING_FACE_HUB_TOKEN=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" stevechapman/legal_nlp:1.11