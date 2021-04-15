import os, re
import string
import pandas as pd
import requests
from datetime import datetime, date
from tqdm import tqdm
import openpyxl as pxl
from openpyxl.utils.dataframe import dataframe_to_rows
from shutil import copy, rmtree
from openpyxl.worksheet.datavalidation import DataValidation
import urllib.parse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

NOTDuser = os.getenv('NOTDuser')
NOTDpassword = os.getenv('NOTDpassword')
today = date.today().strftime("%d/%m/%Y")
working_dir = os.getcwd()
folder = 'New URLs between ' +  input('New URLs between>') + '/'
metadata_folder = folder+'metadata/'

#SET UP
while not os.path.isfile('Harvesting Summary.csv'):
    new_sites = input(f'Unable to locate Harvesting Summary.csv file. Please add Harvesting summary to folder {working_dir}')

if not os.path.isdir(folder):
    os.mkdir(folder)

if not os.path.isdir(metadata_folder):
    os.mkdir(metadata_folder)

os.replace('Harvesting Summary.csv', f'{metadata_folder}Harvesting Summary.csv')

def UKGWA_URL(url):
    social = {'twitter.com': 'twitter',
              'flickr.com': 'flickr',
              'youtube.com': 'video'}

    domain = re.search('.*:\/\/(?:www.)?([^\/]+)', url).group(1)

    if domain in social:
        channel = url[:-1].split('/')[-1] + url[-1]     ### takes last character off before splitting in case it is a slash '/'. Appends after split
        return f'https://webarchive.nationalarchives.gov.uk/{social[domain]}/{channel}'
    else:
        return f'https://webarchive.nationalarchives.gov.uk/*/{url}'


def first_capture(archive_url):
    if '/*/' in archive_url:
        url = archive_url.split('/*/')[1]
        query = f'http://tnaqanotd.mirrorweb.com/published-cdx?url={urllib.parse.quote(url)}&fields=timestamp&limit=1'
        #query = f'https://webarchive.nationalarchives.gov.uk/largefiles-cdx?url={urllib.parse.quote(url)}&fields=timestamp&limit=1'
        r = requests.get(query, allow_redirects=False, auth=(NOTDuser, NOTDpassword))
        if r.status_code == 200:
            date = r.text[:6]
            date = datetime.strptime(date, '%Y%m')
            date_string = date.strftime('%B %Y')
            return date_string
    else:
        try:
            r = requests.get(archive_url+'?sort=date_oldest', timeout=30)
            soup = BeautifulSoup(r.text, 'html.parser')
            if '/twitter/' in archive_url:
                tag = soup.find('li')
                tag = tag.find(attrs={'class': 'mwtwtime'})
                tag = tag.find('span')
                date = tag.text.replace(' ', '').replace('\n', '')
            if '/video/' in archive_url:
                tag = soup.find('li')
                tag = tag.find(attrs={'class': 'video-date-s'})
                date = tag.text
            if '/flickr/' in archive_url:
                tag = soup.find(attrs={'class': 'col-sm-6 col-md-4'})
                tag = tag.find(attrs={'class': 'date'})
                date = tag.text.replace(' ', '').replace('\n', '')

            date = datetime.strptime(date, '%d/%m/%Y')
            date_string = date.strftime('%B %Y')
            return date_string
        except:
            pass
    return False

####Load and clean Harvesting Summary
full_list = pd.read_excel(f'Full List.xlsx') ###IGNORE IF ALREADY IN LIST?
new_sites = pd.read_csv(f'{metadata_folder}Harvesting Summary.csv')
new_sites['Additional Information'] = ''
new_sites.rename(columns={'textbox20': 'URL', 'textbox22': 'Site Name', 'textbox26': 'Archivist Notes', 'Dept_acronym': 'Department'}, inplace=True)
new_sites['Archive URL'] = new_sites['URL'].apply(UKGWA_URL)
new_sites = new_sites[~new_sites['Archive URL'].isin(full_list['Archive URL'])]

#####BACK UPS
copy('not_active.csv', f'{metadata_folder}not_active prev.csv')
copy('Full List.xlsx', f'{metadata_folder}Full List prev.xlsx')

try:
    ####CHECK URLs
    frames = [new_sites] + [pd.read_csv(file) for file in os.listdir() if 'not_active' in file]
    to_check = pd.concat(frames, ignore_index=True)
    to_check.drop_duplicates(subset='URL', inplace=True)
    tqdm.pandas(desc='Checking URLs against Archive')       #Creates tqdm instance for progress bar
    to_check['From'] = to_check['Archive URL'].progress_apply(first_capture)
    to_check.to_csv(f'{metadata_folder}All checked.csv', index=False)

    #####CREATE NOT ACTIVE CSV
    not_active = to_check[to_check['From'] == False].drop(['From'], axis=1)
    not_active.to_csv('not_active.csv', index=False)

    ######CREATE ACTIVE URLs XLSX
    active_sites = to_check[to_check['From'] != False]
    active_sites['To'] = ['Ongoing'] * len(active_sites)
    active_sites = active_sites[['Archive URL', 'Site Name', 'From', 'To', 'Additional Information', 'Archivist Notes', 'Department']]  ####define columns
    for x in range(1, 7):
        active_sites[f'Category #{x}'] = ''
    active_sites['Added to Full List'] = [today] * len(active_sites)
    wb = pxl.Workbook()
    ws = wb.active

    for r in dataframe_to_rows(active_sites, index=False, header=True):
        ws.append(r)

    #### CREATE DATA VALIDATION FOR CATEGORIES
    cats = wb.create_sheet('cats')
    cats.sheet_state = 'hidden'
    categories = ['Business, industry, economics and finance', 'Central and regional government', 'Culture and leisure', 'Environment', 'Health, well-being and care', 'Home affairs, public order, justice and rights', 'Honours, awards and appointments', 'International affairs and defence', 'People, community and housing', 'Public inquiries, inquests and royal commissions', 'Transport, communication, science and technology', 'Work, education and skills']
    for i, x in enumerate(categories):
        cats.cell(row=i+1, column=1).value = x
    dv = DataValidation(type="list", formula1=f'cats!$A$1:$A${i+1}', allow_blank=True)

    ws.add_data_validation(dv)
    dv.add('H2:M1048576')
    wb.save(f'{folder}Verification.xlsx')

    input(f'''Verify Site names and add categories to sites in '{folder}Verification.xlsx'
When finished, close and save spreadsheet and hit enter here:>''')
    input('Re-hit enter to confirm:>')

    ###Create cataloguing sheet
    verified = pd.read_excel(f'{folder}Verification.xlsx')
    copy(f'{folder}Verification.xlsx', f'{metadata_folder}Verified New sites.xlsx')
    cataloguing = verified.drop(columns=['Added to Full List', 'Archivist Notes'])
    cataloguing.to_excel(f'{folder}Verification.xlsx')
    os.rename(f'{folder}Verification.xlsx', f'{folder}cataloguing.xlsx')
    verified['Date Range'] = verified['From'].str.cat(verified['To'], sep=' - ')
    to_full_list = verified[['Archive URL', 'Site Name', 'Date Range',
                              'Department', 'Category #1', 'Category #2',
                              'Category #3', 'Category #4', 'Category #5',
                              'Category #6', 'Additional Information',
                              'Archivist Notes', 'Added to Full List']]

    ###ADD NEW LIST TO FULL LIST
    while True:
        try:
            frames = [full_list] + [to_full_list]
            full_list = pd.concat(frames, ignore_index=True)
            full_list.drop_duplicates(subset='Archive URL', keep='last', inplace=True) ####superfluous
            to_full_list.to_csv(f'{metadata_folder}Newly Added to Full List.xlsx', quotechar='"')
            #SORT COLUMN
            full_list['sort'] = full_list['Site Name'].apply(lambda x: x.lower().replace('the ', '') if x[:3].lower() == 'the' else x.lower())
            full_list['sort'] = full_list['sort'].apply(lambda x: x.strip(string.punctuation))
            full_list = full_list.sort_values('sort')
            full_list = full_list.reset_index(drop=True)
            break
        except Exception as e:
            print(e)
            input('Make sure all files are closed, hit enter when they are:>')


    #####Wrtie new full list
    # wb = pxl.Workbook()
    # ws = wb.active
    # for r in dataframe_to_rows(full_list, index=False, header=True):            ###pd.to_excel?!?!?
    #     ws.append(r)
    #
    # wb.save(f'Full List.xlsx')
    full_list.to_excel('Full List.xlsx', index=False, header=True)

    while 'confirm' not in input('\n  Type "confirm" to save and push update. Hit enter to UNDO process.>').lower():
        if input(f'''\nWARNING: Edited Site Names and Categories will be lost 
WARNING: unless '{metadata_folder}Verified New sites.xlsx' is saved elsewhere.
        
        Type "confirm" to undo whole process.>''').lower() == 'confirm':
            raise Exception('Reverting to Prior State')

    os.system('git add "Full List.xlsx" not_active.csv')
    os.system(f'git commit -m "Updated for {folder[16:-1]}"')
    os.system('git push')

    if input('   Generate HTML?>[y/n]').lower() == 'y':
        os.system(f'python generateHTML.py {folder}A-Z list HTML')
        print(f'HTML located in {folder}A-Z list HTML.txt')

    print('PROCESS COMPLETE')

except Exception as e:
    print(e)
    copy(f'{metadata_folder}Full List prev.xlsx', 'Full List.xlsx')
    copy(f'{metadata_folder}Harvesting Summary.csv', 'Harvesting Summary.csv' )
    copy(f'{metadata_folder}not_active prev.csv', 'not_active.csv')
    rmtree(folder)