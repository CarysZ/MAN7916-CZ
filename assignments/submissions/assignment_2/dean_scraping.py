dean_blog_site = "https://pauljarley.wordpress.com/"

import re
from curl_cffi import requests

blog_post = requests.get(dean_blog_site, impersonate="chrome124")
blog_html = blog_post.text
blog_html = re.sub(r"\s+"," ", blog_html)
print("Blog responded with status code:", blog_post.status_code)
#statuscode=200(=success)

#Parse the HTML content
from bs4 import BeautifulSoup
blog_soup = BeautifulSoup(blog_html,"html5lib")

#Extract the title, date, and url
print("\nHere are the title, date, and url of the articles on the landing page of dean's blog:\n")
articles_data = []
articles = blog_soup.find_all("article")
for article in articles:
    title = article.find("h1", class_="entry-title")
    if title:
        print(title.text)
    else:
        print("No title found for this article.")
    date = article.find("time", class_="entry-date")
    if title:
        print("Date:", date.text.strip())
    else:
        print("No date found for this article.")
    url = article.find("a")
    if url:
        print("URL: ", url.get("href"))
    else:
        print("No URL found for this article.")
    articles_data.append({
        "Title": title.text,
        "Date": date.text.strip(),
        "URL": url.get("href")
    })
    
#Create dataframe
import pandas as pd
articles_df = pd.DataFrame(articles_data)
print(articles_df)

#Extract full text and comments
for index, row in articles_df.iterrows():
    url = row["URL"]
    try:
        # Fetch the article page
        article_response = requests.get(url)
        article_soup = BeautifulSoup(article_response.text, "html5lib")

        # Extract full text
        fulltext_section = article_soup.find("div", class_="entry-content")
        if fulltext_section:
            fulltext = fulltext_section.text.strip()
        else:
            fulltext = "No text found for this article."

        # Extract comments
        comments = article_soup.find_all("li", class_="comment")
        if comments:
            formatted_comments = []
            for idx, comment in enumerate(comments, start=1):
                author = comment.find("span", class_="fn")
                author_text = author.text.strip() if author else "Unknown commenter"

                text = comment.find("div", class_="comment-content")
                comment_content = text.text.strip() if text else "No comment text"

                formatted_comments.append(f"Commenter {idx}: {author_text}\n{comment_content}")

            # Join all comments into a single string
            formatted_comments = "\n".join(formatted_comments)
        else:
            formatted_comments = "No comments found."

        # Update the DataFrame
        articles_df.at[index, "FullText"] = fulltext
        articles_df.at[index, "Comments"] = formatted_comments

    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        articles_df.at[index, "FullText"] = "Error fetching content."
        articles_df.at[index, "Comments"] = "Error fetching comments."

#Save to a CSV
from pathlib import Path
current_dir = Path(__file__).parent
file = current_dir / "dean_scraping.csv"
articles_df.to_csv(file, encoding="utf-8-sig", index=False, header=True)
print(f"Data saved to {file}")