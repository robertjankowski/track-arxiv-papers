# Track arXiv papers

Simple tool which allows you to keep up with new publications. Feel free to add config file using pull request (PR). The github actions will every day send you a list of new publications (preprints) from your field from arxiv.org.


Example config:

```yaml
email_to: "your@email.com"
topics:
- 'list'
- 'of'
- 'topics'
- 'which'
- 'interest'
- 'you'
category: 'arxiv category' # see: https://arxiv.org/category_taxonomy
subject: 'The topic of the email'
last_n_days: 3 # get papers from the last X days
max_results: 20 # limit number of papers
```

Issues:

- if you don't see any new mail, make sure that `papers.from.arxiv@wp.pl` address in on your whitelist
