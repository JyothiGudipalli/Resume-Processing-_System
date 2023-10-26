import spacy
import json
from spacy.tokens import DocBin
import itertools
import sys
from pymongo import MongoClient

filename = "train"
if len(sys.argv) > 1:
    filename = sys.argv[1]

training_data_json_file = f"data/{filename}.json"
training_data_json = []
empty_tds = []
training_data = []

# split train data in 10:2 ratio

client = MongoClient("mongodb://localhost:27017")

db = client["resumeparser"]

collection = db["tds"]
training_data_json = list(collection.find({}).limit(600))
#training_data_json = list(collection.find({}).skip(600))

# with open(training_data_json_file, "r", encoding="utf-8") as op:
#     training_data_json = json.load(op)

training_data_len = len(training_data_json)


# if training_data_len < 100:
#     print(
#         f"⚠ Insufficient Data. Please prepare atleast 100 records. provided {training_data_len} records only"
#     )
#     exit(0)

for td in training_data_json:
    text = td["text"]
    entities = td["entities"]
    # entities = [[tdv["start"], tdv["end"], tdv["labels"][0]] for tdv in td["label"]]

    # text = td["data"]["text"]
    # entities = [[tdv["value"]["start"],tdv["value"]["end"],tdv["value"]["text"]] for tdv in td["annotations"][0]["result"]]

    if len(entities) == 0:  # means no entities marked
        empty_tds.append(text)
        continue

    # remove duplicates from list of entities

    entities.sort()
    unique_entities = [ent for ent, _ in itertools.groupby(entities)]
    training_data.append((text, unique_entities))

# print(training_data)

nlp = spacy.blank("en")  # blank > no NER, Tagger, TEXTCAT
db = DocBin()
skipped = 0
total = 0

for text, entities in training_data:
    doc = nlp.make_doc(text)  # text = one resume text
    valid_ents = []
    # invalid entity = leading spaces, trailing space, boundary overlap
    try:
        for start, end, label in entities:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            total += 1
            if (
                span is None
                or span.text.startswith(" ")
                or span.text.endswith(" ")
                or span.text != span.text.strip()
            ):
                ent_text = text[start:end]
                print(f"⚠  Skipping Entity : {text[0:30]}... {ent_text}")
                skipped += 1

            else:
                valid_ents.append(span)

        # map ents to valid_ents
        doc.ents = valid_ents
        db.add(doc)
    except Exception as ex:
        print("⚠ ", ex)
        skipped += 1

db.to_disk(f"data/{filename}.spacy")

print("✨ Results:")
print(f"Total Training Data : {training_data_len}")
print(f"Empty TDs : {len(empty_tds)}")
print(f"Failed to Convert : {skipped} / {total} = {skipped/total*100} %")


# 100 records

# 80 records = train
# 20 records = evaluation


# python -m spacy train config_lg.cfg --paths.train ./train/ --paths.dev ./dev/
# python -m spacy train config_lg.cfg --output ./output --paths.train ./data/resume_td.spacy --paths.dev ./data/raju.spacy

# python -m spacy debug data  --paths.train ./train --paths.dev ./dev
# python -m spacy debug data --paths.train ./data/resume_td.spacy --paths.dev ./data/raju.spacy
# python -m spacy debug data config.cfg  --paths.train ./data/dhanaveera.spacy --paths.dev ./data/dhanaveera2.spacy

# python -m spacy debug data config.cfg  --paths.train ./data/train.spacy --paths.dev ./data/dev.spacy