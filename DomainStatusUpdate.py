import pandas as pd
import numpy as np
import re

## the file names below need to be updated to work properly
checked_domains_file = 'CheckedCompanies_20191206.csv'
# first run the DomainFrequencyGenerator.py file with appropriate files before using this file
emails_file = 'DistinctEmails_20191125.csv'

emails = pd.read_csv(emails_file)
checked = pd.read_csv(checked_domains_file)
emails['Status'] = ''
emails = emails[pd.notnull(emails['Domain'])]

emails.reset_index(inplace=True)
emails = emails.iloc[:, 1:]
emails_array = emails.to_numpy()
for i in range(emails_array.shape[0]):
    emails_array[i][0] = '@{}'.format(emails_array[i][0])

after_underscore = checked_domains_file.find('_')+1
before_ext = checked_domains_file.find('.csv')
checked_file_date = checked_domains_file[after_underscore:before_ext]
checked_domains = pd.read_csv(checked_domains_file)
cols = ['Date', 'Company Name(s)', 'Email Domain',
        'Industry Segment', 'Respective Sub-Industry Segment']
checked_domains = checked_domains[cols]
# Splitting company name(s) attribute and email domains
for i in range(checked_domains.shape[0]):
    co_names = str(checked_domains.iloc[i][1]).lower().split(';')
    e_domains = str(checked_domains.iloc[i][2]).lower().split(',')
    checked_domains.iloc[i][1] = co_names
    checked_domains.iloc[i][2] = e_domains
checked_domains['Date'] = pd.to_datetime(
    checked_domains['Date'], errors='coerce').dt.date
checked_domains.sort_values('Date', ascending=False, inplace=True)
checked_domains.reset_index(drop=True, inplace=True)
checked_domains.dropna(subset=['Date'], inplace=True)
checked_array = checked_domains.to_numpy()
for i in range(checked_array.shape[0]):
    checked_array[i][0] = checked_array[i][0].strftime('%Y%m%d')

    domain_list = checked_array[i][2]
    for d in range(len(domain_list)):
        domain_list[d] = domain_list[d].strip()
    checked_array[i][2] = domain_list

    company_list = checked_array[i][1]
    for c in range(len(company_list)):
        #company_list[c] = company_list[c].translate(None, string.punctuation)
        company_list[c] = re.sub(r"[(,.;@#?!&$)]+\ *", " ", company_list[c])
        company_list[c] = ' '.join(company_list[c].split())
        #company_list[c] = cleanco(company_list[c].strip()).clean_name()
    checked_array[i][1] = company_list

cel = []

for i in range(checked_array.shape[0]):
    for j in range(len(checked_array[i][2])):
        cel.append(checked_array[i][2][j])

cel = set(cel)

for i in range(emails_array.shape[0]):
    if emails_array[i][0] in cel:
        emails_array[i][2] = 'Checked'
    else:
        emails_array[i][2] = ''

filled_array = pd.DataFrame(data=emails_array)

filled_array.to_csv('DomainStatusUpdated_{}.csv'.format(checked_file_date))
