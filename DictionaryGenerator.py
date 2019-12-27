import pandas as pd
import numpy as np
import re
import datetime as dt
import os.path
import json
from tqdm import tqdm

class DictGenerator(object):

    def __init__(self,cdf,cd_df=None):
        self.cdf = cdf
        self.cd_df = cd_df
        cols = ['Date', 'Company Name(s)', 'Email Domain',
                'Industry Segment', 'Respective Sub-Industry Segment']
        self.cols = cols
        after_underscore = self.cdf.find('_')+1
        before_ext = self.cdf.find('.csv')
        self.checked_file_date = self.cdf[after_underscore:before_ext]

    def create_dictionaries(self):
        
        self.cd_df = pd.read_csv(self.cdf)
        self.cd_df = self.cd_df[self.cols]
        # Splitting company name(s) attribute and email domains
        for i in tqdm(range(self.cd_df.shape[0])):
            co_names = str(self.cd_df.iloc[i][1]).lower().split(';')
            e_domains = str(self.cd_df.iloc[i][2]).lower().split(',')
            self.cd_df.iloc[i][1] = co_names
            self.cd_df.iloc[i][2] = e_domains

        self.cd_df['Date'] = pd.to_datetime(
            self.cd_df['Date'], errors='coerce').dt.date

        self.cd_df.sort_values('Date', ascending=False, inplace=True)
        self.cd_df.reset_index(drop=True, inplace=True)

        self.cd_df.dropna(subset=['Date'], inplace=True)

        checked_array = self.cd_df.to_numpy()

        for i in tqdm(range(checked_array.shape[0])):
            checked_array[i][0] = checked_array[i][0].strftime('%Y%m%d')

            domain_list = checked_array[i][2]
            for d in range(len(domain_list)):
                domain_list[d] = domain_list[d].strip()
            checked_array[i][2] = domain_list

            company_list = checked_array[i][1]
            for c in range(len(company_list)):
                #company_list[c] = company_list[c].translate(None, string.punctuation)
                company_list[c] = re.sub(r"[(,.;@#?!&$-)]+\ *", " ", company_list[c])
                company_list[c] = ' '.join(company_list[c].split())
                #company_list[c] = cleanco(company_list[c].strip()).clean_name()
            checked_array[i][1] = company_list

        d_segment_file = 'DictDomainSegments.json'
        d_duplicate_file = 'DictDomainDuplicates.json'

        if os.path.exists(d_segment_file) and os.path.exists(d_duplicate_file):
            print('\nDomain: Dictionary files already exist.')
            with open(d_segment_file, 'r+') as dsf, open(d_duplicate_file, 'r+') as ddf:
                ds = json.load(dsf)
                dd = json.load(ddf)
                for i in range(checked_array.shape[0]):
                    for j in range(len(checked_array[i][2])):
                        domain = checked_array[i][2][j]
                        if domain not in ds and domain not in dd:
                            ds[domain] = [checked_array[i][1][0], checked_array[i][3],
                                        checked_array[i][4], checked_array[i][0], self.checked_file_date]
                        elif domain in ds and domain not in dd:
                            if ds.get(domain)[4] < checked_array[i][0] <= self.checked_file_date:
                                temp = {domain: 2}
                                dd.update(temp)

                dsf.seek(0)
                json.dump(ds, dsf)
                dsf.truncate()
                ddf.seek(0)
                json.dump(dd, ddf)
                ddf.truncate()
        else:
            print('\nDomain: Dictionary files do not exist, they have been created.')
            with open(d_segment_file, 'w') as dsf, open(d_duplicate_file, 'w') as ddf:
                ds = dict()
                dd = dict()
                for i in range(checked_array.shape[0]):
                    for j in range(len(checked_array[i][2])):
                        domain = checked_array[i][2][j]
                        if domain not in ds:
                            ds[domain] = [checked_array[i][1][0], checked_array[i][3],
                                        checked_array[i][4], checked_array[i][0], self.checked_file_date]
                        else:
                            if domain not in dd:
                                temp = {domain: 2}
                                dd.update(temp)

                            else:
                                temp = {domain: dd.get(domain)+1}
                                dd.update(temp)
                json.dump(ds, dsf)
                json.dump(dd, ddf)

        cn_segment_file = 'DictCoNameSegments.json'
        cn_duplicate_file = 'DictCoNameDuplicates.json'

        if os.path.exists(cn_segment_file) and os.path.exists(cn_duplicate_file):
            print('CoName: Dictionary files already exist.')
            with open(cn_segment_file, 'r+') as cnf, open(cn_duplicate_file, 'r+') as cndf:
                cnd = json.load(cnf)
                cndd = json.load(cndf)
                for i in range(checked_array.shape[0]):
                    for j in range(len(checked_array[i][1])):
                        coname = checked_array[i][1][j]
                        coname = re.sub(r"[(,.;@#?!&$-)]+\ *", " ", coname)
                        coname = ' '.join(coname.split())
                        if coname not in cnd and coname not in cndd:
                            cnd[coname] = [checked_array[i][3],
                                        checked_array[i][4], self.checked_file_date]
                        elif coname in cnd and coname not in cndd:
                            if cnd.get(coname)[2] < checked_array[i][0] <= self.checked_file_date:
                                temp = {coname: 2}
                                cndd.update(temp)
                cnf.seek(0)
                json.dump(cnd, cnf)
                cnf.truncate()
                cndf.seek(0)
                json.dump(cndd, cndf)
                cndf.truncate()
        else:
            print('CoName: Dictionary files do not exist, they have been created.')
            with open(cn_segment_file, 'w') as cnf, open(cn_duplicate_file, 'w') as cndf:
                cnd = dict()
                cndd = dict()
                for i in range(checked_array.shape[0]):
                    for j in range(len(checked_array[i][1])):
                        coname = checked_array[i][1][j]
                        coname = re.sub(r"[(,.;@#?!&$-)]+\ *", " ", coname)
                        coname = ' '.join(coname.split())
                        if coname not in cnd:
                            cnd[coname] = [checked_array[i][3],
                                        checked_array[i][4], self.checked_file_date]
                        else:
                            if coname not in cndd:
                                temp = {coname: 2}
                                cndd.update(temp)

                            else:
                                temp = {coname: cndd.get(coname)+1}
                                cndd.update(temp)
                json.dump(cnd, cnf)
                json.dump(cndd, cndf)

        dd_keys = list(dd.keys())
        for i in range(len(dd_keys)):
            if dd_keys[i] in ds:
                del ds[dd_keys[i]]

        cndd_keys = list(cndd.keys())
        for i in range(len(cndd_keys)):
            if cndd_keys[i] in cnd:
                del cnd[cndd_keys[i]]

        with open(d_segment_file, 'w') as dsf, open(d_duplicate_file, 'w') as ddf, open(cn_segment_file, 'w') as cnf, open(cn_duplicate_file, 'w') as cndf:
            json.dump(ds, dsf)
            json.dump(dd, ddf)
            json.dump(cnd, cnf)
            json.dump(cndd, cndf)

        print('\nDictDomainSegments: {0}\nDictDomainDuplicates: {1}\nDictCoNameSegments: {2}\nDictCoNameDuplicates: {3}'.format(
            len(ds.keys()), len(dd.keys()), len(cnd.keys()), len(cndd.keys())))
