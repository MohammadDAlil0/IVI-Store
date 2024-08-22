# import re
# from transformers import TFBertModel, BertTokenizer
# import tensorflow as tf

# # Load pre-trained BERT model and tokenizer
# model_name = 'bert-base-uncased'
# tokenizer = BertTokenizer.from_pretrained(model_name)
# model = TFBertModel.from_pretrained(model_name)


# # Function to extract BERT embeddings
# def extract_bert_features(text):
#     inputs = tokenizer(text, return_tensors='tf', padding=True, truncation=True, max_length=32)
#     outputs = model(**inputs)
#     embeddings = outputs.last_hidden_state[:, 0, :]  # CLS token embeddings
#     return embeddings.numpy().flatten()  # Flatten the array to save in CSV

# async def embeding_text(text: str):
#     features = extract_bert_features(text)
#     return features
