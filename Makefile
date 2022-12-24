
fine-tune:
	openai api fine_tunes.create -t ./data/train.jsonl -m davinci
