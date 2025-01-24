import spacy
nlp = spacy.load("en_core_web_sm")

# Download stopwords
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('stopwords')
list_of_stopwords = nltk.corpus.stopwords.words('english')

# Create Data Frame
import pandas as pd
input_folder = "local_data/aussie/About" 
def load_text_files(folder_path):
    data = []
    for file_name in sorted([f for f in pd.io.common.os.listdir(folder_path) if f.endswith(".txt")]):
        file_path = f"{folder_path}/{file_name}"
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        data.append({"name": file_name.split('.')[0], "filepath": file_path, "text": text})
    return pd.DataFrame(data)
text_dataframe = load_text_files(input_folder)

# Text Preprocessing 
import string

def preprocess_text(doc, remove_stopwords=False):
    token = []
    for sent in doc.sents:
        filtered_tokens = [
            token.lemma_.lower()  # Lowercasing
            for token in sent
            if not token.is_punct  # Exclude punctuation
            and not token.is_digit  # Exclude digits
            and not token.is_space  # Exclude spaces
            and not (remove_stopwords and token.is_stop)  # Exclude stopwords if specified
        ]
        token.extend(filtered_tokens)  
    return token
        
text_dataframe['preprocessed_ws'] = text_dataframe['text'].apply(lambda x: preprocess_text(nlp(x), remove_stopwords=False))
text_dataframe['preprocessed_wos'] = text_dataframe['text'].apply(lambda x: preprocess_text(nlp(x), remove_stopwords=True))

# Create word frequencies 
from collections import Counter
counter_ws = Counter([word for sent in text_dataframe['preprocessed_ws'] for word in sent])
counter_wos = Counter([word for sent in text_dataframe['preprocessed_wos'] for word in sent])

common100_ws = counter_ws.most_common(100)
common100_wos = counter_wos.most_common(100)

# Function to generate plot
import matplotlib.pyplot as plt
def plot_word_frequency(counter, title, filename):
    words, counts = zip(*counter)
    
    plt.figure(figsize=(15, 8))
    plt.plot(words, counts, marker='o')
    plt.xticks(rotation=90)
    plt.title(title)
    plt.xlabel('Words')
    plt.ylabel('Frequencies')
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(filename)

# Create images
common100_ws_image = "assignments/submissions/assignment_4/common100_ws.jpg"
common100_wos_image = "assignments/submissions/assignment_4/common100_wos.jpg"

plot_word_frequency(common100_ws, 'Word Frequencies', common100_ws_image)
plot_word_frequency(common100_wos, 'Word Frequencies', common100_wos_image)

print(f"Charts saved as {common100_ws_image} and {common100_wos_image}.")

# Innovativeness Dic
inno_dict = [
    "ad lib", "adroit", "adroitness", "bright idea", "clever", "cleverness",
    "conceive", "concoct", "concoction", "concoctive", "conjure up", "creative",
    "creativity", "develop", "developed", "dream", "dream up", "expert",
    "formulation", "freethinker", "genesis", "genius", "gifted", "hit upon",
    "imagination", "imaginative", "improvise", "ingenious", "ingenuity", "innovate",
    "innovated", "innovates", "innovating", "innovation", "innovations", "innovative",
    "innovativeness", "introduced", "introducing", "introduction", "introductions",
    "invent", "invented", "invention", "inventive", "inventiveness", "inventor",
    "launch", "launched", "launching", "master stroke", "mastermind", "metamorphose",
    "metamorphosis", "neoteric", "neoterism", "neoterize", "new capabilities",
    "new capability", "new compounds", "new content", "new core areas", "new course",
    "new directions", "new family", "new features", "new generation", "new generations",
    "new idea", "new ideas", "new line of business", "new medicine", "new medicines",
    "new molecular entities", "new pharmaceuticals", "new platform", "new process",
    "new processes", "new product", "new products", "new solutions", "new systems",
    "new technique", "new techniques", "new technologies", "new technology",
    "new therapies", "new thinking", "new tools", "new treatments", "new ways",
    "new wrinkle", "new-generation", "new-product", "next generation", "next-generation",
    "novation", "novel", "novelty", "patent", "patented", "patents", "process development",
    "product development", "product launch", "product launches", "proprietary",
    "prototype", "prototyping", "push the envelope", "R&D", "radical", "re-engineering",
    "reformulated", "refreshed", "reinvent", "re-invent", "reinvented", "reinventing",
    "reinvention", "reinvents", "released", "renewal", "renewing", "research", "reshape",
    "reshaped", "reshapes", "reshaping", "resourceful", "resourcefulness", "restyle",
    "restyling", "revolutionary", "revolutionize", "revolutionized", "roll out",
    "rolled out", "see things", "technologically advanced", "think up", "trademark",
    "transform", "transformation", "transformed", "transforming", "visualize"
]

word_freq = Counter([word for sent in text_dataframe['preprocessed_ws'] for word in sent])
filtered_innov_freq = {word: word_freq[word] for word in inno_dict if word in word_freq}
sorted_innov_freq = Counter(filtered_innov_freq).most_common(20)

innov_image = "assignments/submissions/assignment_4/innov_freqs.jpg"
plot_word_frequency(sorted_innov_freq, 'Word Frequencies', innov_image)
print(f"Innovativeness chart saved as {innov_image}.")

# Function to add innov_w and innov_perwd_ws columns
def calculate_innovativeness_metrics(tokens, inno_dict):
    total_words = len(tokens)
    innov_count = sum(1 for word in tokens if word in inno_dict)
    return innov_count, innov_count / total_words if total_words > 0 else 0

text_dataframe['innov_ws'], text_dataframe['innov_perwd_ws'] = zip(
    *text_dataframe['preprocessed_ws'].apply(lambda tokens: calculate_innovativeness_metrics(tokens, inno_dict))
)

# Save to CSV
innov_csv = "assignments/submissions/assignment_4/innov_aussie_data.csv"
text_dataframe.to_csv(innov_csv, index=False)
print(f"Dataset with Innovativeness metrics saved as {innov_csv}.")
