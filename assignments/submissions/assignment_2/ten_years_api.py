from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse
from pprint import pprint
import json
import datetime
import pandas as pd

def get_journal_issn(journal_title, my_email):
    try:
        endpoint = "/journals"
        query = f"query={urllib.parse.quote(journal_title)}"
        api_url = f"https://api.crossref.org{endpoint}?{query}"
        print(f"Querying URL for {journal_title} ISSN: {api_url}")

        api_response = requests.get(api_url, headers={"mailto": my_email}) 
        print(f"CrossRef server responded with status code: {api_response.status_code}")
        
        if api_response.status_code != 200:
            print(f"Failed to retrieve ISSN for {journal_title}. Status code: {api_response.status_code}")
            return None
        
        journal_json = api_response.json()
        issn_list = []
        
        for item in journal_json["message"]["items"]:
            if item["title"].lower() == journal_title.lower():
                issn_list.extend(item.get("ISSN", []))
                break
        
        if not issn_list:
            print(f"No ISSN found for {journal_title}. Check the journal title or CrossRef data.")
            return None
        
        return issn_list[0] if issn_list else None
    except Exception as e:
        print(f"Error getting ISSN for {journal_title}: {e}")
        return None

#Retrieve Publications from ISSN
def get_journal_articles(issn, from_date, until_date, rows_per_query, my_email):
    try:
        endpoint = f"/journals/{issn}/works"
        query = f"filter=from-pub-date:{from_date},until-pub-date:{until_date}&rows={rows_per_query}"
        api_url = f"https://api.crossref.org{endpoint}?{query}"
        print(f"Querying works for ISSN {issn}: {api_url}")
        
        api_response = requests.get(api_url, headers={"mailto": my_email})
        print(f"CrossRef server responded with status code: {api_response.status_code}")
        
        if api_response.status_code != 200:
            print(f"Failed to retrieve works for ISSN {issn}. Status code: {api_response.status_code}")
            return None
        
        works_json = api_response.json()
        if "message" not in works_json or "items" not in works_json["message"]:
            print(f"Unexpected API response structure for ISSN {issn}.")
            return None
        
        total_results = works_json["message"]["total-results"]
        print(f"Total works found for ISSN {issn}: {total_results}")
        
        return works_json
    except Exception as e:
        print(f"Error getting articles for ISSN {issn}: {e}")
        return None

def build_date(date_parts):
    if len(date_parts[0]) == 3:
        year, month, day = date_parts[0]
    else:
        year, month = date_parts[0]
        day = 1
    return datetime.datetime(year, month, day)

def parse_article(article):
    try:
        doi = article["DOI"]
        title = article["title"][0]
        n_refs = article["references-count"]
        n_authors = len(article.get("author", []))
        n_cites = article["is-referenced-by-count"]
        pub_date = build_date(article["published"]["date-parts"])
        url = article["URL"]
        journal_name = article.get("container-title", ["N/A"])[0] if article.get("container-title") else "N/A"
        raw_abstract = article.get("abstract", "N/A")
        if raw_abstract:
            try:
                soup = BeautifulSoup(raw_abstract, "html5lib")
                abstract = soup.get_text().strip()
                if not abstract:  # Handle case where BeautifulSoup parsing results in an empty string
                    abstract = "Abstract provided but could not be parsed"
            except Exception as e:
                print(f"Error parsing abstract for article '{title}': {e}")
                abstract = "Abstract provided but parsing failed"
        else:
            abstract = "No abstract provided"
    
        return {
            "doi": doi,
            "title": title,
            "n_refs": n_refs,
            "n_authors": n_authors,
            "n_cites": n_cites,
            "url": url,
            "journal_name": journal_name,
            "abstract": abstract,
            "pub_year": pub_date.year if pub_date else "N/A",
        }
    except Exception as e:
        print(f"Error parsing article: {e}")
        return None

def process_journals(journal_list, from_date, until_date, rows_per_query, my_email):
    paper_list = []
    for journal_title in journal_list:
        try:
            print(f"\nProcessing {journal_title}")
            issn = get_journal_issn(journal_title, my_email)
            if not issn:
                print(f"Could not retrieve ISSN for {journal_title}")
                continue
            articles_json = get_journal_articles(issn, from_date, until_date, rows_per_query, my_email)
            if not articles_json:
                print(f"No articles found for {journal_title}")
                continue

            for article in articles_json["message"]["items"]:
                parsed_article = parse_article(article)
                if parsed_article:
                    paper_list.append(parsed_article)
        except Exception as e:
            print(f"Error parsing article: {article.get('title', ['N/A'])[0]} - {e}")
            continue

    if not paper_list:
        print("No articles were successfully processed")
        return pd.DataFrame()
    
    try: 
        paper_df = pd.DataFrame(paper_list).sort_values("pub_year", ascending=True)
        if 'pub_year' in paper_df.columns and not paper_df['pub_year'].isna().all():
            # Convert pub_year to numeric, replacing non-numeric values with NaN
            paper_df['pub_year'] = pd.to_numeric(paper_df['pub_year'], errors='coerce')
            # Sort only if we have valid years
            paper_df = paper_df.sort_values('pub_year', ascending=True, na_position='last')
        else:
            print("Warning: Could not sort by publication year due to missing or invalid data")
        return paper_df
    
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        return pd.DataFrame()

#Information plug in
if __name__ == "__main__":
    my_email = "li454273@ucf.edu"
    journal_list = ["Journal of Management", "Personnel Psychology", "Organization Science"]
    from_date = "2015-01-01"
    until_date = "2025-01-11"
    rows_per_query = 100
    
    # Process journals
    results_df = process_journals(journal_list, from_date, until_date, rows_per_query, my_email)
    
    if not results_df.empty:
        #Save to CSV
        from pathlib import Path
        current_dir = Path(__file__).parent
        file = current_dir / "ten_years_api.csv"
        results_df.to_csv(file, encoding="utf-8-sig", index=False, header=True)
        print(f"Data saved to {file}")

#Calculations using the dataset
from scipy.stats import pearsonr, f_oneway
correlation, p_value = pearsonr(results_df["pub_year"], results_df["n_cites"])
anova_result = f_oneway(
    *(results_df[results_df["journal_name"] == journal]["n_cites"].values for journal in results_df["journal_name"].unique())
)

#Text results
results_text = f"""
Correlation between publication year and citation count:
Correlation coefficient: {correlation}
P-value: {p_value}

ANOVA results for mean differences in citation count by journal:
F-statistic: {anova_result.statistic}
P-value: {anova_result.pvalue}
"""

#Save the text file
output_dir = Path(__file__).parent
output_file = output_dir / "publication_stats.txt"
with open(output_file, "w") as f:
    f.write(results_text) 
print(f"Correlation and ANOVA results saved to {output_file}")
