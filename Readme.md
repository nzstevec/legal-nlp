conda create -n legal-nlp python=3.11

pip install -r requirements.txt

#pip install https://huggingface.co/opennyaiorg/en_legal_ner_trf/resolve/main/en_legal_ner_trf-any-py3-none-any.whl

git lfs install
git clone https://huggingface.co/opennyaiorg/en_legal_ner_trf

pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.2.0/en_core_web_sm-3.2.0-py3-none-any.whl

python -m spacy download en_core_web_sm

open en_legal_ner_trf and: 
 - find+replace single quotes with double quotes
 - on line 152 after "partial_f1": 90.34146341463416 remove the comma