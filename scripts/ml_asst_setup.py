import os
from pathlib import Path
import nltk

def main():
    print("Getting NLTK Models")
    nltk_dir = Path.cwd()/"models"
    assert nltk_dir.exists()
    os.environ["NLTK_DATA"] = str(nltk_dir)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)

if __name__ == "__main__":
    main()