import re
import textwrap

input_file = "assignments/materials/week_4/article_preprint.txt" 

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

#Read input file and ensure the text is read correctly
text = read_file(input_file) 
print("The text is: ")
print("="*30)
print(textwrap.fill(text, width=80))

# Function to extract citations with names and dates
def extract_name_date_citations(text):
    # Regex for citations in three formats: "Name et al., Date", "Name & Name, Date", or "Name, Date"
    pattern = r"\b(?:(?:[A-Z][a-zA-Z]+ et al\., \d{4})|(?:[A-Z][a-zA-Z]+ & [A-Z][a-zA-Z]+, \d{4})|(?:[A-Z][a-zA-Z]+, \d{4}))\b"
    matches = re.findall(pattern, text)
    return [match.strip() for match in matches]

# Function to extract citations with dates only
def extract_date_only_citations(text):
    # Regex for citations in three formats: "Name et al. (Date)", "Name & Name (Date)", or "Name (Date)"
    pattern = r"\b(?:[A-Z][a-zA-Z]+ et al\. \(\d{4}\)|[A-Z][a-zA-Z]+ & [A-Z][a-zA-Z]+ \(\d{4}\)|[A-Z][a-zA-Z]+ \(\d{4}\))"
    matches = re.findall(pattern, text)
    return [match.strip() for match in matches]

import matplotlib.pyplot as plt
# Creat bar chart
def create_bar_chart(citation_counts, output_path):
    sort_citation_counts = citation_counts.most_common(10)
    citations, counts = zip(*sort_citation_counts)

    plt.figure(figsize=(10, 5))
    plt.bar(citations, counts)
    plt.xlabel('Frequency')
    plt.ylabel('Citations')
    plt.title('Frequency of the Most Commonly Cited Papers')
    plt.xticks(rotation=45, ha='right')

    # Save the bar chart
    plt.tight_layout()
    plt.savefig(output_path)

# Create reference report
def save_reference_report(name_date_citations, date_only_citations, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write("Names-and-dates references:\n")
        file.write("==================================================\n")
        file.write("\n".join(sorted(set(name_date_citations))))
        file.write("\n\nDate-only references:\n")
        file.write("==================================================\n")
        file.write("\n".join(sorted(set(date_only_citations))))

from collections import Counter
output_image = "assignments/submissions/assignment_4/common_citations.jpg"
output_report = "assignments/submissions/assignment_4/references_report.txt"

# File save
name_date_citations = extract_name_date_citations(text)
date_only_citations = extract_date_only_citations(text)
citation_counts = Counter(name_date_citations)
create_bar_chart(citation_counts, output_image)
save_reference_report(name_date_citations, date_only_citations, output_report)
print("Citation analysis complete. Files saved:")
print(f"- Bar chart: {output_image}")
print(f"- References report: {output_report}")
