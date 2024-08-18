import streamlit as st
import requests
import pandas as pd
from datetime import datetime 
import json 
import openpyxl


# try:
#     with open('request_counter.json', 'r') as file:
#         request_json = json.load(file)
#     request_count = request_json['request_count']
#     current_month = datetime.today().month
#     if current_month > request_json['month']:
#         request_json['month'] = current_month
#         request_count = 0
# except:
#     request_count = 0

request_count = st.secrets['num_requests']


URL = "https://zillow-com1.p.rapidapi.com/property"
headers = {
    'x-rapidapi-key': st.secrets['rapid_api_key'],
    'x-rapidapi-host': st.secrets['rapid_api_host']
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
                    'street_address': str(response.json()['streetAddress']),
                    'city': str(response.json()['city']),
                    'county': str(response.json()['county']),
                    'zipcode': str(response.json()['zipcode']),
                    'latitude': str(response.json()['latitude']),
                    'longitude': str(response.json()['longitude']),
                    'livingAreaUnits': str(response.json()['livingArea']),
                    'living_area_units': str(response.json()['livingAreaUnits']),
                    'num_bathrooms': str(response.json()['bathrooms']),
                    'num_bedrooms': str(response.json()['bedrooms']),
                    'hoa_fee': str(response.json()['monthlyHoaFee']),
                    'annual_ho_insurance': str(response.json()['annualHomeownersInsurance']),
                    'price': str(response.json()['price']),
                    'zestimate': str(response.json()['zestimate']),
                    'year_built': str(response.json()['yearBuilt']),
                    'home_type': str(response.json()['homeType']),
                    'has_attached_property': str(response.json()['resoFacts']['hasAttachedProperty']),
                    'pool_features': str(response.json()['resoFacts']['poolFeatures']),
                    'flooring': str(response.json()['resoFacts']['flooring']),
                    'foundation_details': str(response.json()['resoFacts']['foundationDetails']),
                    'has_garage': str(response.json()['resoFacts']['hasGarage']),
                    'pets_allowed': str(response.json()['resoFacts']['hasPetsAllowed']),
                    'exterior_features': str(response.json()['resoFacts']['exteriorFeatures']),
                    'fireplace_status': str(response.json()['resoFacts']['hasFireplace']),
                    'construction_materials': str(response.json()['resoFacts']['constructionMaterials']),
                    'appliances': str(response.json()['resoFacts']['appliances']),
                    'attic': str(response.json()['resoFacts']['attic']),
                    'can_raise_horses': str(response.json()['resoFacts']['canRaiseHorses']),
                    'sewer': str(response.json()['resoFacts']['sewer']),
                    'parking_features': str(response.json()['resoFacts']['parkingFeatures']),
                    'heating': str(response.json()['resoFacts']['heating']),
                    'other_facts': str(response.json()['resoFacts']['otherFacts'])
                } 
                properties.append(property)
            else:
                errors.append({'address': address, 'error code': status_code})

        # request_json['request_count'] = request_count
        # with open('request_counter.json', 'w') as file:
        #     json.dump(request_json, file, indent=4)
        st.secrets['num_requests'] = request_count

        property_tab, error_tab = st.tabs(['Data', 'Errors'])

        with property_tab:
            if len(properties) > 0:
                properties_df = pd.DataFrame(properties)
                st.write(properties)
                st.dataframe(properties_df)

        with error_tab:
            if len(errors) > 0:
                errors_df = pd.DataFrame(errors)
                st.dataframe(errors_df)
        

        
        