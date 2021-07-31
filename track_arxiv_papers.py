import os
import sys
import urllib.request, urllib.parse, urllib.error
import feedparser
from datetime import date, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml

from cryptography.fernet import Fernet

BASE_URL = 'http://export.arxiv.org/api/query?'


def get_password():
    f = Fernet(os.environ['MAIL_KEY'])
    token = b'gAAAAABg-uPmxFifJKrHL8lCJirkAZai_sAoCp_zs8HC4sfiTMrArfy83JBiqjBZ-4zrP8tRU8OTIkwilAT5UkZQSNuPyA2R6ABaJ2oG0D94WWmDVjOpXfA='
    password = f.decrypt(token)
    return password.decode("utf-8")


def get_papers(topic, title, category, max_results=10, last_n_days=7):
    yesterday = date.today() - timedelta(1)
    dby = yesterday - timedelta(last_n_days)
    start_date = dby.strftime("%Y%m%d") + "2000"
    end_date = yesterday.strftime("%Y%m%d") + "2000"
    search_query = f'all:{topic}+AND+all:{category}+AND+submittedDate:[{start_date}+TO+{end_date}]'

    query = f'search_query={search_query}&start=0&max_results={max_results}'

    feedparser._FeedParserMixin.namespaces[
        'http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces[
        'http://arxiv.org/schemas/atom'] = 'arxiv'

    response = urllib.request.urlopen(BASE_URL + query).read()

    feed = feedparser.parse(response)
    body = "<h1>{}</h1>".format(f"New publications about: {title}")
    body += '<b>Feed last updated</b>: {}'.format(
        feed.feed.updated.split("T")[0])

    if not feed.entries:
        body += '<p>Nothing new today</p>'
        return body

    body += format_single_paper(feed.entries)
    return body


def format_single_paper(entries):
    body = "<ul>"
    for entry in entries:
        body += '<li>'
        all_categories = [t['term'] for t in entry.tags]
        pdf_link = ''
        for link in entry.links:
            if link.rel == 'alternate':
                pdf_link = 'no pdf link'
            elif link.title == 'pdf':
                pdf_link = link.href
        body += '<a href="{}"><h2>{}</h2></a>'.format(pdf_link, entry.title)

        try:
            body += '<b>Authors</b>:  <i>{}</i></br>'.format(', '.join(
                author.name for author in entry.authors))
        except AttributeError:
            pass

        try:
            comment = entry.arxiv_comment
        except AttributeError:
            comment = 'No comment found'
        body += f'<b>Comments</b>: {comment}</br>'

        updated = entry.updated.split("T")[0]
        body += f'<b>Updated</b>: {updated} </br>'
        published = entry.published.split("T")[0]
        body += f'<b>Published</b>: {published} </br>'
        body += f"<b>Primary Category</b>: {entry.tags[0]['term']}</br>"
        all_categories = [t['term'] for t in entry.tags]
        body += f'<b>All Categories</b>: {(", ").join(all_categories)}</br>'
        body += f'<p>{entry.summary}</p></br>'
        body += '</li>'
    body += '</ul>'
    return body


def send_mail(body, email_to):
    email_from = "papers.from.arxiv@wp.pl"
    password = get_password()
    msg = MIMEMultipart()
    msg['Subject'] = 'New papers from arXiv'
    msg['From'] = email_from
    msg['To'] = email_to
    msg.attach(MIMEText(body, 'html'))
    with smtplib.SMTP_SSL('smtp.wp.pl', 465) as server:
        server.login(email_from, password)
        server.sendmail(email_from, email_to, msg.as_string())


def format_topic(topic: str):
    return '+'.join(topic.lower().split())


def load_config(filename: str):
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.SafeLoader)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} config.yaml')
        exit(1)
    config = load_config(sys.argv[1])
    all_publications = []
    for topic in config['topics']:
        publications = get_papers(format_topic(topic), topic,
                                  config['category'], config['max_results'],
                                  config['last_n_days'])
        all_publications.append(publications)
    send_mail('<br>'.join(all_publications), config['email_to'])