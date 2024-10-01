### New Install Instructions

clone from portal.scoti.au branch from github repo nzstevec/legal-nlp

docker build -t stevechapman/legal_nlp:1.15 .

create a huggingface.co account and generate an access token or get the one steve put in secretsmgr on aws

docker run -p 8501:8501 -e "HUGGING_FACE_HUB_TOKEN=somenewtoken" stevechapman/legal_nlp:1.15

docker login

docker push stevechapman/legal_nlp:1.15

The container registry is in hub.docker.com
The docker image url is configured in the portal solution

## Original Install Instructions
conda create -n legal-nlp python=3.11

pip install -r requirements.txt

pip install transformers==4.39.3

pip install tokenizers==0.19.1

git lfs install

cd src\legal_nlp\backend\nlp\models

git clone https://huggingface.co/opennyaiorg/en_legal_ner_trf

open en_legal_ner_trf/meta.json and: 
 - find+replace single quotes with double quotes
 - on line 152 after "partial_f1": 90.34146341463416 remove the comma

cd into src\legal_nlp\frontend\components\streamlit-agraph\streamlit_agraph\frontend

Refer to [Readme](https://gitlab.com/SmartR_AI/streamlit-components/knowledge-graph) on how to install.

cd into src/legal_nlp

insert your api keys into src\legal_nlp\frontend\config.py

python start_both.py

![NER Example](https://gitlab.com/SmartR_AI/gpt/demo-projects/legal-nlp/-/raw/main/images/NER_Example.png)


