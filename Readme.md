conda create -n legal-nlp python=3.11

pip install -r requirements.txt

python -m spacy download en_core_web_sm

git lfs install

cd src/legal_nlp

mkdir models

cd models

git clone https://huggingface.co/opennyaiorg/en_legal_ner_trf

open en_legal_ner_trf/meta.json and: 
 - find+replace single quotes with double quotes
 - on line 152 after "partial_f1": 90.34146341463416 remove the comma

cd into src/legal_nlp

insert your api keys into src\legal_nlp\frontend\config.py

python start_both.py

![NER Example](https://gitlab.com/SmartR_AI/gpt/demo-projects/legal-nlp/-/raw/main/images/NER_Example.png)