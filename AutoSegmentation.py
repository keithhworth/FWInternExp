import pandas as pd
import datetime as dt
import numpy as np
from tqdm import tqdm
import re
import os.path
import json
## above lines import necessary libraries

# a class is created
class AutoSegment(object):

    # a method is declared
    def __init__(self, acf, cdf, ac_df=None, ca=None, before_updates=None, updated_ac_df=None):
        self.acf = acf
        self.cdf = cdf
        self.ac_df = ac_df
        self.ca = ca
        self.before_updates = before_updates
        self.updated_ac_df = updated_ac_df
        with open('DictDomainSegments.json', 'r') as dsf, open('DictCoNameSegments.json','r') as cnsf:
            self.ds = json.load(dsf)
            self.cns = json.load(cnsf)
        self.cols = ['Contact ID', 'Email', 'Company Name', 'Industry', 'Carrier Industry Segment',
                        'Intermediary Industry Segment', 'Shipper Industry Segment', 'Create Date']
        after_underscore = self.cdf.find('_')+1
        before_ext = self.cdf.find('.csv')
        self.checked_file_date = self.cdf[after_underscore:before_ext]
    # all_contacts_file = 'all-contacts_20191212.csv'
    # checked_domains_file = 'CheckedCompanies_20191212.csv'

    def read_all_contacts(self):
        self.ac_df = pd.read_csv(self.acf)
        self.ac_df = self.ac_df[self.cols]
        self.ac_df['Create Date'] = pd.to_datetime(
            self.ac_df['Create Date'], errors='coerce').dt.date
        self.ac_df.sort_values('Create Date', ascending=False, inplace=True)
        self.ac_df.reset_index(drop=True, inplace=True)
        
        self.ca = self.ac_df.to_numpy()
        print('\n---\nReading all-contacts file...\n---')
        for i in tqdm(range(self.ca.shape[0])):
            str_date = self.ca[i][7].strftime('%Y%m%d')
            self.ca[i][7] = str_date
            email = str(self.ca[i][1]).lower().strip()
            where_at = email.find('@')
            domain = email[where_at:]
            self.ca[i][1] = domain

            co_name = str(self.ca[i][2]).lower().strip()
            co_name = re.sub(r"[(,.;@#?!&$-)]+\ *", " ", co_name)
            co_name = ' '.join(co_name.split())
            self.ca[i][2] = co_name
        
        before = self.ac_df['Industry'].isnull().sum()
        self.before_updates = before

    def use_email_dict(self):
        email_count = 0
        print('\n---\nUsing domain dictionary...\n---')
        # contacts_array = [Contact ID, Domain, Company Name, Industry, Carrier Industry, Intermediary Industry, Shipper Industry, Create Date]
        for i in tqdm(range(self.ca.shape[0])):
            if pd.isnull(self.ca[i][3]) and not pd.isnull(self.ca[i][1]) and pd.isnull(self.ca[i][2]):
                domain = self.ca[i][1]
                if domain in self.ds:
                    email_count += 1
                    # info = [Company name, Industry, Sub-industry, checked_contact_date, checked_file_date]
                    info = self.ds.get(domain)
                    if info[1] == 'Carrier':
                        self.ca[i][2], self.ca[i][3], self.ca[i][4] = info[0], info[1], info[2]
                    elif info[1] == 'Intermediary':
                        self.ca[i][2], self.ca[i][3], self.ca[i][5] = info[0], info[1], info[2]
                    elif info[1] == 'Shipper/Retailer/Manufacturer/BCO':
                        # more if-statements to change segmentation info to include commas
                        # this is because commas
                        if info[2] == 'Food Beverages & Tobacco':
                            self.ca[i][2], self.ca[i][3], self.ca[i][6] = info[0], info[1], 'Food, Beverages & Tobacco'
                        elif info[2] == 'Hotels Restaurants & Leisure':
                            self.ca[i][2], self.ca[i][3], self.ca[i][6] = info[0], info[1], 'Hotels, Restaurants & Leisure'
                        else:
                            self.ca[i][2], self.ca[i][3], self.ca[i][6] = info[0], info[1], info[2]
                    else:
                        self.ca[i][2], self.ca[i][3] = info[0], info[1]
            elif not pd.isnull(self.ca[i][2]) and pd.isnull(self.ca[i][3]) and not pd.isnull(self.ca[i][1]):
                domain = self.ca[i][1]
                if domain in self.ds:
                    email_count += 1
                    if self.ds.get(domain)[0] in self.ca[i][2]:
                        # info = [Company name, Industry, Sub-industry, checked_contact_date, checked_file_date]
                        info = self.ds.get(domain)
                        if info[1] == 'Carrier':
                            self.ca[i][3], self.ca[i][4] = info[1], info[2]
                        elif info[1] == 'Intermediary':
                            self.ca[i][3], self.ca[i][5] = info[1], info[2]
                        elif info[1] == 'Shipper/Retailer/Manufacturer/BCO':
                            self.ca[i][3], self.ca[i][6] = info[1], info[2]
                        else:
                            self.ca[i][3] = info[0], info[1]
        print('\n---------------------\nEmail Changes: {}\n---------------------'.format(email_count))


#    def check_domain_segmentation(self):
#        d_segmented_contacts = pd.DataFrame(data=self.ca)
#        d_segmented_contacts.columns = cols
#        d_after = d_segmented_contacts['Industry'].isnull().sum()
#        self.ds_check = before_updates-d_after
#        return self.ds_check

    def use_coname_dict(self):
        coname_count = 0
        print('\nUsing coname dictionary...')
        for i in tqdm(range(self.ca.shape[0])):
            # not pd.isnull(contacts_array[i][3]):
            if not pd.isnull(self.ca[i][2]) and pd.isnull(self.ca[i][3]):
                coname = self.ca[i][2]
                if coname in self.cns:
                    coname_count += 1
                    # info = [Industry, Sub-industry, checked_file_date]
                    info = self.cns.get(coname)
                    if info[0] == 'Carrier':
                        self.ca[i][3], self.ca[i][4] = info[0], info[1]
                    elif info[0] == 'Intermediary':
                        self.ca[i][3], self.ca[i][5] = info[0], info[1]
                    elif info[0] == 'Shipper/Retailer/Manufacturer/BCO':
                        if info[1] == 'Food Beverages & Tobacco':
                            self.ca[i][3], self.ca[i][6] = info[0], 'Food, Beverages & Tobacco'
                        elif info[1] == 'Hotels Restaurants & Leisure':
                            self.ca[i][3], self.ca[i][6] = info[0], 'Hotels, Restaurants & Leisure'
                        else:
                            self.ca[i][3], self.ca[i][6] = info[0], info[1]
                    else:
                        self.ca[i][3] = info[0]
        print('\n---------------------\nCoName Changes: {}\n---------------------'.format(coname_count))
    
    def export_ca(self):
        self.updated_ac_df = pd.DataFrame(data=self.ca)
        self.updated_ac_df.columns = self.cols
        self.updated_ac_df.to_csv(
            'AutoSegmentedContacts_{}.csv'.format(self.checked_file_date))


#    def check_coname_segmentation(self):
#        segmented_contacts = pd.DataFrame(data=self.ca)
#        segmented_contacts.columns = cols
#        cn_after = segmented_contacts['Industry'].isnull().sum()
#        self.cns_check = before_updates-cn_after
#        return self.cns_check
        #print('Updated contacts after using DictCoNameSegments: {}'.format(cns_check-ds_check))

    #print('Total change: {}'.format(self.before-after))
