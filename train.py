from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding

LABEL = "FORK"

TRAIN_DATA = [
    (
        "Fork RockShox Lyric RC DebonAir, OverDrive steerer, 15x110mm Maxle Stealth, 170mm travel",
        {"entities": [(5, 22, LABEL)]},
    ),
    ("Do they bite?", {"entities": []}),
    (
        "Front suspension RockShox Lyrik RCT3, DebonAir, Charger 2 damper, tapered steerer, Boost110, 160 mm travel",
        {"entities": [(17, 36, LABEL)]},
    ),
		("Fork: RockShox Revelation RC 120mm", 
		{"entities": [(6, 28, LABEL)]}),
    (
        "FORK FOX FACTORY 36 KASHIMA 15QR",
        {"entities": [(5, 27, LABEL)]},
    ),
    (
        "FORK FOX PERFORMANCE 36/170MM",
        {"entities": [(5, 23, LABEL)]},
    ),
]

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)

def main(model=None, new_model_name="fork", output_dir=None, n_iter=300):
    """Set up the pipeline and entity recognizer, and train the new entity."""
    random.seed(0)
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")
    # Add entity recognizer to model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe("ner")

    ner.add_label(LABEL)  # add new entity label to entity recognizer
    # Adding extraneous labels shouldn't mess anything up
    # ner.add_label("VEGETABLE")
    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.resume_training()
    move_names = list(ner.move_names)
    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        sizes = compounding(1.0, 4.0, 1.001)
        # batch up the examples using spaCy's minibatch
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            batches = minibatch(TRAIN_DATA, size=sizes)
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35, losses=losses)
            print("Losses", losses)

    # test the trained model
    test_text = "Frame	ALUXX SL grade aluminium, Maestro 200mm travel, ISCG 05 Fork DVO Onyx DC WC, 200mm travel, Boost Shock	DVO Jade Coil Handlebar	Truvativ Descendant DH alloy riser, 35mm Stem	Truvativ Descendant alloy, direct mount, 0 degree, 35mm Seatpost	Giant Contact SL Zero, 30.9mm Saddle	Giant Contact, Forward Pedals	N/A"
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name  # rename model
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        # Check the classes have loaded back consistently
        assert nlp2.get_pipe("ner").move_names == move_names
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)


if __name__ == "__main__":
    plac.call(main)