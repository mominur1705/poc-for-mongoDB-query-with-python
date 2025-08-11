# poc-for-mongoDB-query-with-python

A Python script that queries MongoDB collections to find companies that are not affiliated with a given organization number.

## Description

This script connects to a local MongoDB database and queries two collections:
- `bus network affiliation company` - Contains affiliation relationships between companies
- `bus network enlisted company` - Contains enlisted company details

Given an organization number from an enlisted company, the script returns all other enlisted companies that are **not** affiliated with it.

## Installation

Install the required dependency:

```bash
pip install pymongo
