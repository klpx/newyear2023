import json

EXAMPLES_FILE = './data/tuning.prompts.csv'
EXAMPLES_PREPARED = './data/train.jsonl'
START = "Дополни это поздравление с новым годом неожиданным прикольным добрым и позитивным образом: "
DELIMITER = "\nДополнение:"
STOP = "\n###\n"


# read examples from csv file (semicolon separated)
# and prepare them for fine-tuning
def prepare_examples():
    with open(EXAMPLES_FILE, 'r') as f:
        with open(EXAMPLES_PREPARED, 'w') as g:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                prompt, completion = line.split("\t")
                g.write(json.dumps({'prompt': START + prompt + DELIMITER, 'completion': ' ' + completion + STOP}))
                g.write("\n")


def main():
    prepare_examples()


if __name__ == "__main__":
    main()