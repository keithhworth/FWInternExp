import pandas as pd
import tqdm

### update all-contacts filename in appropriate space
## file_name = '[file]_YYYYMMDD.csv'
file_name = 'all-contacts_20191118.csv'

df = pd.read_csv(file_name)

## the following lines extract the date from file_name
after_underscore = file_name.find('_')+1
before_ext = file_name.find('.csv')
file_date = file_name[after_underscore:before_ext]

# limits the all-contacts file to emails
df = df['Email']
email_array = df.to_numpy()
email_endings = []

for i in tqdm(range(len(email_array))):
    email = str(email_array[i]).lower().strip()
    where_at = email.find('@')
    ending = email[where_at+1:]
    email_endings.extend([ending])
unique_emails = list(dict.fromkeys(email_endings))
d = {'': ''}

for i in tqdm(range(len(unique_emails))):
    count = 0
    domain = unique_emails[i]
    for j in range(len(email_endings)):
        if email_endings[j] == domain:
            count += 1
    d[domain] = count
d.pop('')

s = pd.Series(d, name='Count')
s.index.name = 'Domain'
s.reset_index()
s = pd.DataFrame(s, index=None)
s.sort_values(by=['Count'], ascending=False, inplace=True)

s.to_csv('DistinctEmailsCount_{}.csv'.format(file_date))
