import streamlit as st
import requests
import pandas as pd
from datetime import datetime 
import json 
import openpyxl
from app_secrets import rapid_api_key, rapid_api_host


try:
    with open('request_counter.json', 'r') as file:
        request_json = json.load(file)
    request_count = request_json['request_count']
    current_month = datetime.today().month
    if current_month > request_json['month']:
        request_json['month'] = current_month
        request_count = 0
except:
    request_count = 0


URL = "https://zillow-com1.p.rapidapi.com/property"
headers = {
    'x-rapidapi-key': rapid_api_key,
    'x-rapidapi-host': rapid_api_host
}



st.write(f'This month {request_count} addresses have been scraped')
bill = 0 if request_count <= 100 else (request_count - 100) * 0.04
st.write(f'Total Rapid-API bill: ${bill:,.2f}')

address_file = st.file_uploader('Upload a CSV or .xlsx file with addresses to collect data on')
if address_file is not None:
    file_type = address_file.name.split('.')[-1]
    if file_type == 'csv':
        address_df = pd.read_csv(address_file)
    elif file_type == 'xlsx':
        wb = openpyxl.load_workbook(address_file)
        sheet_selector = st.selectbox('Select Sheet :', wb.sheetnames)
        address_df = pd.read_excel(address_file, sheet_selector)
    else:
        st.error('File Must be either .csv or .xlsx', icon=':material/thumb_down')

    st.dataframe(address_df)

    address_column = st.selectbox('Select the Address Column', address_df.columns)

    scrape_btn = st.button('Submit')

    if address_column and scrape_btn:
        addresses = list(set(address_df[address_column].tolist()))
        properties = []
        for address in addresses:
            querystring = {'address': address}

            response = requests.get(URL, headers=headers, params=querystring)
            request_count += 1
            status_code = response.status_code
            
            errors = []
            if status_code == 200:
                property = {
                    'street_address': response.json()['streetAddress'],
                    'city': response.json()['city'],
                    'county': response.json()['county'],
                    'zipcode': response.json()['zipcode'],
                    'latitude': response.json()['latitude'],
                    'longitude': response.json()['longitude'],
                    'livingAreaUnits': response.json()['livingArea'],
                    'living_area_units': response.json()['livingAreaUnits'],
                    'num_bathrooms': response.json()['bathrooms'],
                    'num_bedrooms': response.json()['bedrooms'],
                    'hoa_fee': response.json()['monthlyHoaFee'],
                    'annual_ho_insurance': response.json()['annualHomeownersInsurance'],
                    'price': response.json()['price'],
                    'zestimate': response.json()['zestimate'],
                    'year_built': response.json()['yearBuilt'],
                    'home_type': response.json()['homeType'],
                    'has_attached_property': response.json()['resoFacts']['hasAttachedProperty'],
                    'pool_features': response.json()['resoFacts']['poolFeatures'],
                    'flooring': response.json()['resoFacts']['flooring'],
                    'foundation_details': response.json()['resoFacts']['foundationDetails'],
                    'has_garage': response.json()['resoFacts']['hasGarage'],
                    'pets_allowed': response.json()['resoFacts']['hasPetsAllowed'],
                    'exterior_features': response.json()['resoFacts']['exteriorFeatures'],
                    'fireplace_status': response.json()['resoFacts']['hasFireplace'],
                    'construction_materials': response.json()['resoFacts']['constructionMaterials'],
                    'appliances': response.json()['resoFacts']['appliances'],
                    'attic': response.json()['resoFacts']['attic'],
                    'can_raise_horses': response.json()['resoFacts']['canRaiseHorses'],
                    'sewer': response.json()['resoFacts']['sewer'],
                    'parking_features': response.json()['resoFacts']['parkingFeatures'],
                    'heating': response.json()['resoFacts']['heating'],
                    'other_facts': response.json()['resoFacts']['otherFacts']
                } 
                properties.append(property)
            else:
                errors.append({'address': address, 'error code': status_code})

        request_json['request_count'] = request_count
        st.write(request_json)
        with open('request_counter.json', 'w') as file:
            json.dump(request_json, file, indent=4)

        property_tab, error_tab = st.tabs(['Data', 'Errors'])

        with property_tab:
            if len(properties) > 0:
                properties_df = pd.DataFrame(properties)
                st.dataframe(properties_df)

        with error_tab:
            if len(errors) > 0:
                errors_df = pd.DataFrame(errors)
                st.dataframe(errors_df)
        

        
        