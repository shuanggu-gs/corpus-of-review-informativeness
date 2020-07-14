from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
from nltk import tokenize
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import json
from wordcloud import WordCloud, STOPWORDS
import altair as alt
import pandas as pd

full_corpus_path = './data/corpus.json'
annotated_corpus_path = './data/subset_corpus_annotated.json'

def categpry_graph(filename):
    counter = {}
    with open(full_corpus_path, 'r') as f:
        data = json.load(f)
    for entry in data:
        counter[entry['category']] = counter.get(entry['category'], 0) + 1

    sorted_category = sorted(counter.keys(), key=lambda x: counter[x], reverse=True)
    nums = [counter[cate] for cate in sorted_category]

    plt.rcdefaults()
    fig, ax = plt.subplots()
    y_pos = np.arange(len(sorted_category))

    ax.barh(y_pos, nums, align='center', color=(43/255, 42/255, 42/255))
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_category)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Counts')
    ax.set_title('Number Of Reviews In Each Category')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)
    fig.set_size_inches(18.5, 10.5)
    fig.savefig(filename, dpi=100)


def show_wordcloud(data, stopwords, level, title=None):
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stopwords,
        max_words=100,
        max_font_size=40,
        scale=3,
        random_state=1
    ).generate(str(data))

    fig = plt.figure(1, figsize=(12, 12))
    plt.axis('off')
    if title:
        fig.suptitle(title, fontsize=20)
        fig.subplots_adjust(top=2.3)
    plt.imshow(wordcloud)
    fig.set_size_inches(12.5, 8.5)
    fig.savefig('./imgs/' + level +'.png', dpi=100)


def get_graphs(level=None):
    with open(annotated_corpus_path, 'r') as fin:
        data = json.load(fin)
    stopwords = set(STOPWORDS)

    words_set = set()
    for review in data:
        if level and review['review_label'] == level:
            words = tokenize.sent_tokenize(review['consumer_review'])
            words_set.update(words)
    show_wordcloud(words_set, stopwords, level)


def get_reviews(annotated=False, category=None, search_word='', search_company='', rating=None, level=None, only_text=False):
    '''

    :param annotated: boolean, if True, use annotated data, else use whole corpus
    :param category: str
    :param search_word: str
    :param rating: str
    :param level: str
    :param only_text: boolean, if boolean, only return text, else return all information

    :return: list, list of reviews
    '''

    reviews_dict = defaultdict(list)

    if annotated:
        with open(annotated_corpus_path, 'r') as f:
            data = json.load(f)
    else:
        with open(full_corpus_path, 'r') as f:
            data = json.load(f)

    reviews_dict["index"] = []
    reviews_dict["Category"] = []
    reviews_dict["Company"] = []
    reviews_dict["Rating"] = []
    reviews_dict["Review"] = []
    if annotated:
        reviews_dict["Label"] = []

    count = 1
    for entry in data:
        if category and entry['category'] != category:
            continue
        if search_word and search_word.lower() not in entry['consumer_review'].lower():
            continue
        if search_company and search_company.lower() not in entry['company'].lower():
            continue
        if rating and str(entry['rating']) != rating:
            continue
        if level and entry['review_label'] != level:
            continue

        if only_text:
            reviews_dict["index"].append(str(count))
            reviews_dict["Review"].append(entry['consumer_review'])
        else:
            reviews_dict["index"].append(str(count))
            reviews_dict["Category"].append(entry['category'])
            reviews_dict["Company"].append(entry['company'])
            reviews_dict["Rating"].append(entry['rating'])
            reviews_dict["Review"].append(entry['consumer_review'])
            if annotated:
                reviews_dict["Label"].append(entry['review_label'])

        count += 1
    return reviews_dict

class MyWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # 200: all is well, prepared to receive information
        self.send_response(200)
        # the format that we are gonna to receive info

        query = parse.urlsplit(self.path).query
        query_dict = parse.parse_qs(query)

        if 'frontend.css' in self.path:
            self.send_header('Content-type', 'text/css; charset=utf-8')
            self.end_headers()
            f = open("frontend.css", encoding='utf-8')
            html = f.read()
            f.close()
            self.wfile.write(html.encode('utf-8'))
        if 'frontend.js' in self.path:
            self.send_header('Content-type', 'text/javascript; charset=utf-8')
            self.end_headers()
            f = open("frontend.js", encoding='utf-8')
            html = f.read()
            f.close()
            self.wfile.write(html.encode('utf-8'))
        if self.path == '/':
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            f = open("frontend.html", encoding='utf-8')
            html = f.read()
            f.close()
            self.wfile.write(html.encode('utf-8'))


        if self.path.endswith(".png"):
            self.send_header('Content-type', 'image/png')
            self.end_headers()
            with open("."+self.path, "rb") as f:
                self.wfile.write(f.read())

        if 'text' in query_dict['type']:
            # analysis query dictionary
            annotated = True if query_dict.get('annotated', ['False'])[0] == 'True' else False
            level = None
            category = None
            search_word = None
            rating = None
            search_company = None

            if 'level' in query_dict:
                level = query_dict['level'][0]
                if level == 'None':
                    level = None
            if 'category' in query_dict:
                category = query_dict['category'][0]
                if category == 'None':
                    category = None
            if 'search_word' in query_dict:
                search_word = query_dict.get('search_word', [''])[0]
            if 'search_company' in query_dict:
                search_company = query_dict.get('search_company', [''])[0]
            if 'rating' in query_dict:
                rating = query_dict['rating'][0]
                if rating == 'None':
                    rating = None
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            data = get_reviews(annotated=annotated,
                               category=category,
                               search_word=search_word,
                               search_company=search_company,
                               rating=rating,
                               level=level,
                               only_text=False)
            self.wfile.write(json.dumps(data).encode('utf-8'))

        if 'graph' in query_dict['type']:
            pass

        return


if __name__ == '__main__':
    http_port = 9998
    server = HTTPServer(('localhost', http_port),  MyWebServer)
    server.serve_forever()
