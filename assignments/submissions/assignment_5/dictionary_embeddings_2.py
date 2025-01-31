import numpy as np
import csv
import matplotlib.pyplot as plt
from pathlib import Path
from gensim.models import KeyedVectors
from sklearn.manifold import TSNE
from docx import Document
from docx.shared import Inches
import io

# Paths setup
local_data_path = Path(__file__).resolve().parent.parent.parent.parent / "local_data"
glove_file_path = local_data_path / "glove.6B.100d.txt"
evaluated_word_list_path = "assignments/submissions/assignment_5/word_list_for_evaluation.csv"
word_doc_path = "assignments/submissions/assignment_5/word_embeddings_results.docx"

# Load GloVe embeddings
print("Loading GloVe model...")
embeddings = KeyedVectors.load_word2vec_format(
    glove_file_path.as_posix(), binary=False, no_header=True)

# Load and filter evaluated word list
included_words = []
with open(evaluated_word_list_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['eval'] == '1' and row['word'] in embeddings:
            included_words.append(row['word'])

# Extract word vectors for the included words
word_vectors = np.array([embeddings[word] for word in included_words])

# Reduce dimensionality using t-SNE
tsne = TSNE(n_components=2, perplexity=5, random_state=24601, max_iter=10000)
reduced_vectors = tsne.fit_transform(word_vectors)

# Create the plot
plt.figure(figsize=(12, 8))

for i, word in enumerate(included_words):
    plt.scatter(reduced_vectors[i, 0], reduced_vectors[i, 1],c='blue', s=30)
    plt.annotate(
        word,
        xy=(reduced_vectors[i, 0], reduced_vectors[i, 1]),
        xytext=(5, 2),
        textcoords='offset points',
    )

# Save plot to bytes buffer
img_buffer = io.BytesIO()
plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
img_buffer.seek(0)

# Create a new Word document
doc = Document()

# Add the plot to the document
doc.add_picture(img_buffer, width=Inches(7.0))

# Save the Word document
doc.save(word_doc_path)
print(f"Plot saved to Word document: {word_doc_path}")