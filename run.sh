#!/bin/bash

 ls configs/*.yaml | xargs -L 1 python3 ./track_arxiv_papers.py

