## Install Instructions
conda create -n legal-nlp python=3.11

pip install -r requirements.txt

pip install transformers==4.39.3

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