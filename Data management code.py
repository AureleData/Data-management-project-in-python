
import pandas as pd
import numpy as np
from IPython.display import display
from datetime import datetime



# Define the path where the files are located
path = 'yourpath\\Python data management example\\'


# Read raw data files into DataFrames
amounts = pd.read_excel(path + 'raw data for services example.xlsx', sheet_name='NEW DATA alloc')
cubealloc = pd.read_excel(path + 'raw data for services example.xlsx', sheet_name='cube alloc')
ctralloc = pd.read_excel(path + 'raw data for services example.xlsx', sheet_name='country alloc', keep_default_na=False)

# Read the matrix schema from an Excel file into a DataFrame
matrix = pd.read_excel(path + 'raw data for services example.xlsx', sheet_name='Matrix schema')


# Transpose 'ctralloc' DataFrame using pd.melt
ctrallocpivot = pd.melt(ctralloc, id_vars=ctralloc.columns[:3], value_vars=ctralloc.columns[3:185], var_name='country', value_name='allocations')

# Replace 'NA' with "NA'" in the 'country' column
ctrallocpivot.loc[ctrallocpivot['country'] == 'NA', 'country'] = "NA'"

# Display the transposed DataFrame
ctrallocpivot

# Melt 'amounts' DataFrame to long format, it is basically a pivot
amountspivot = pd.melt(amounts, id_vars=amounts.columns[:4], value_vars=amounts.columns[4:75], var_name='date', value_name='amounts')
amountspivot['yearon'] = amountspivot['date'].str.extract(r'(\d{4})')
amountspivot['yearon'] = amountspivot['yearon'].astype(int)

# Display the melted 'amountspivot' DataFrame
amountspivot

# Merge 'amountspivot' and 'ctrallocpivot' DataFrames on specific columns
ctrallocationv1 = amountspivot.merge(ctrallocpivot, left_on=['yearon', 'rcode', 'label'], right_on=['year', 'rcode', 'label'])

# Drop the 'description' column from 'ctrallocationv1'
ctrallocationv1 = ctrallocationv1.drop('description', axis=1)

# Drop the 'yearon' column from 'ctrallocationv1'
ctrallocationv1 = ctrallocationv1.drop('yearon', axis=1)

# Calculate 'amountsalloc' by multiplying 'amounts' with 'allocations' and dividing by 100
ctrallocationv1['amountsalloc'] = ctrallocationv1['amounts'] * ctrallocationv1['allocations'] / 100

# Create 'ctrallocationv2' by dropping columns and filtering rows where 'amountsalloc' is not equal to 0
ctrallocationv2 = ctrallocationv1.drop(['amounts', 'allocations'], axis=1)
ctrallocationv2 = ctrallocationv2[ctrallocationv2['amountsalloc'] != 0]
print(ctrallocationv2)

# Select transfers from 'ctrallocationv2' based on specific conditions
transfers = ctrallocationv2.loc[(ctrallocationv2['CUBE'] == 'NSNFC_53730') | (ctrallocationv2['CUBE'] == 'NSNFC_53730_1')]

# Create 'PAYMENTS' and 'RECEIPTS' columns based on conditions
transfers['PAYMENTS'] = np.where(transfers['label'] == 'Payments', transfers['amountsalloc'], 0)
transfers['RECEIPTS'] = np.where(transfers['label'] == 'Receipts', transfers['amountsalloc'], 0)

# Replace 'NSNFC_53730_1' with 'NSNFC_53730' in the 'CUBE' column
transfers.loc[transfers['CUBE'] == 'NSNFC_53730_1', 'CUBE'] = 'NSNFC_53730'

# Display the 'transfers' DataFrame
transfers

# Create 'ctrallocationv3' by filtering out transfers
ctrallocationv3 = ctrallocationv2.loc[(ctrallocationv2['CUBE'] != 'NSNFC_53730') & (ctrallocationv2['CUBE'] != 'NSNFC_53730_1')]

# Display 'ctrallocationv3' DataFrame
ctrallocationv3

# Melt 'cubealloc' DataFrame to long format
cubeallocpivot = pd.melt(cubealloc, id_vars=cubealloc.columns[:4], value_vars=cubealloc.columns[4:58], var_name='sectors', value_name='allocations')

# Display 'cubeallocpivot' DataFrame
cubeallocpivot

# Create 'PAYMENTS' and 'RECEIPTS' columns in 'ctrallocationv3' based on conditions
ctrallocationv3['PAYMENTS'] = np.where(ctrallocationv3['label'] == 'Payments', ctrallocationv3['amountsalloc'], 0)
ctrallocationv3['RECEIPTS'] = np.where(ctrallocationv3['label'] == 'Receipts', ctrallocationv3['amountsalloc'], 0)

# Concatenate 'ctrallocationv3' and 'transfers' DataFrames, resetting index
ctrallocationv4 = pd.concat([ctrallocationv3, transfers], axis=0, ignore_index=True)

# Assign 'RECEIPTS' values to 'PAYMENTS_ROM' column and vice versa for 'NSNFC_53730' rows
ctrallocationv4.loc[ctrallocationv4['CUBE'] == 'NSNFC_53730', 'PAYMENTS_ROM'] = ctrallocationv4['RECEIPTS']
ctrallocationv4.loc[ctrallocationv4['CUBE'] == 'NSNFC_53730', 'RECEIPTS_ROM'] = ctrallocationv4['PAYMENTS']
ctrallocationv4.loc[ctrallocationv4['CUBE'] == 'NSNFC_53730', 'RECEIPTS'] = ''
ctrallocationv4.loc[ctrallocationv4['CUBE'] == 'NSNFC_53730', 'PAYMENTS'] = ''

# Melt 'cubealloc' DataFrame to long format
cubeallocpivot = pd.melt(cubealloc, id_vars=cubealloc.columns[:4], value_vars=cubealloc.columns[4:56], var_name='sectors', value_name='allocations')

# Display 'cubeallocpivot' DataFrame
cubeallocpivot
####

# Merge 'cubeallocpivot' and 'ctrallocationv4' DataFrames on specific columns
ctrallocationv5 = cubeallocpivot.merge(ctrallocationv4, left_on=['rcode', 'label', 'CUBE'], right_on=['rcode', 'label', 'CUBE'])

# Create a copy of 'ctrallocationv5' DataFrame
ctrallocationv6 = ctrallocationv5.copy()

# Convert 'RECEIPTS', 'PAYMENTS', 'PAYMENTS_ROM', 'RECEIPTS_ROM' columns to numeric, handling errors by coercing to NaN
print(ctrallocationv6['RECEIPTS'].dtype)
print(ctrallocationv6['PAYMENTS'].dtype)
ctrallocationv6['RECEIPTS'] = pd.to_numeric(ctrallocationv6['RECEIPTS'], errors='coerce')
ctrallocationv6['PAYMENTS'] = pd.to_numeric(ctrallocationv6['PAYMENTS'], errors='coerce')
ctrallocationv6['PAYMENTS_ROM'] = pd.to_numeric(ctrallocationv6['PAYMENTS_ROM'], errors='coerce')
ctrallocationv6['RECEIPTS_ROM'] = pd.to_numeric(ctrallocationv6['RECEIPTS_ROM'], errors='coerce')

# Multiply 'RECEIPTS', 'PAYMENTS', 'PAYMENTS_ROM', 'RECEIPTS_ROM' by 'allocations'
ctrallocationv6['RECEIPTS'] = ctrallocationv6['RECEIPTS'] * ctrallocationv6['allocations']
ctrallocationv6['PAYMENTS'] = ctrallocationv6['PAYMENTS'] * ctrallocationv6['allocations']
ctrallocationv6['RECEIPTS_ROM'] = ctrallocationv6['RECEIPTS_ROM'] * ctrallocationv6['allocations']
ctrallocationv6['PAYMENTS_ROM'] = ctrallocationv6['PAYMENTS_ROM'] * ctrallocationv6['allocations']

# Drop unnecessary columns from 'ctrallocationv6'
ctrallocationv6 = ctrallocationv6.drop(['amountsalloc', 'label', 'rcode', 'allocations', 'description'], axis=1)

# Create a copy of 'ctrallocationv6' DataFrame
ctrallocationv7 = ctrallocationv6.copy()

# Extract 'TYPINS' column by splitting values in 'CUBE' column
ctrallocationv7['TYPINS'] = ctrallocationv7['CUBE'].str.split('_').str[1]

# Rename columns for consistency
ctrallocationv7.rename(columns={'sectors': 'ENTITYID', 'country': 'RESCOU', 'CUBE': 'CUBEID'}, inplace=True)

# Extract month from 'date' column and store it in a new column 'm'
ctrallocationv7['m'] = ctrallocationv7['date'].str.split('-').str[1]

# Create 'DateInt' by combining 'year' and 'm' columns, formatting month as two digits
ctrallocationv7['DateInt'] = ctrallocationv7['year'].astype(str) + ctrallocationv7['m'].astype(str).str.zfill(2)

# Convert 'DateInt' to 'monthyear' format using pd.to_datetime
ctrallocationv7['monthyear'] = pd.to_datetime(ctrallocationv7['DateInt'], format='%Y%m')

# Create 'fullyear' by converting 'monthyear' to timestamp
ctrallocationv7['fullyear'] = ctrallocationv7['monthyear'].dt.to_period('m').dt.to_timestamp('m')

# Format 'fullyear' as 'OBS_DATE' in the format '%Y%m%d'
ctrallocationv7['OBS_DATE'] = ctrallocationv7['fullyear'].dt.strftime('%Y%m%d')

# Drop unnecessary columns from 'ctrallocationv7'
apportion3 = ctrallocationv7.drop(['fullyear', 'monthyear', 'm', 'year', 'date', 'DateInt'], axis=1)

# Display the 'apportion3' DataFrame
apportion3

# Select specific columns from 'matrix' DataFrame
matrix = matrix[['CUBEID', 'TABLEID', 'TYPINS', 'RESENT']]
matrix['TYPINS'] = matrix['TYPINS'].astype(str)

# Merge 'apportion3' and 'matrix' DataFrames on specific columns
servicescor1 = apportion3.merge(matrix, left_on=['CUBEID', 'TYPINS'], right_on=['CUBEID', 'TYPINS'], how='left')

# Create a copy of 'servicescor1' DataFrame
services5 = servicescor1.copy()

# Replace 'RESENT' values with 'RESCOU' for 'NSNFC_53730' rows
services5.loc[services5['CUBEID'] == 'NSNFC_53730', 'RESENT'] = services5['RESCOU']

# Set 'RECEIPTS' and 'PAYMENTS' values to NaN for 'NSNFC_53730' rows
services5['RECEIPTS'] = np.where(services5['CUBEID'] == 'NSNFC_53730', np.nan, services5['RECEIPTS'])
services5['PAYMENTS'] = np.where(services5['CUBEID'] == 'NSNFC_53730', np.nan, services5['PAYMENTS'])

# Add prefix 'BOP_' to 'ENTITYID' column and drop 'cons' column
services5['cons'] = 'BOP_'
services5['ENTITYID'] = services5['cons'] + services5['ENTITYID']
services5 = services5.drop('cons', axis=1)

# Add 'STATUS' column with value 'A'
services5['STATUS'] = 'A'



# these adjustments here under were made to cater for the case when these 2 entities now do not exist
# in our new data but did exist in the previous version, however, on the software on which we upload the
# data, they cannot be removed from the database so they have to be uploaded as 0's to not cause any issue
# thus this process



# Replace '53280' with '53270' for 'TYPINS' column
services65 = services5.loc[services5['TYPINS'] == '53280']
services65['TYPINS'] = '53270'
services65.loc[services65['CUBEID'] == 'NSNFC_53280', 'CUBEID'] = 'NSNFC_53270'

# Assign 0 values to specific columns for 'NSNFC_53270' rows
services65['PAYMENTS_ROM'] = 0
services65['RECEIPTS_ROM'] = 0
services65['PAYMENTS'] = 0
services65['RECEIPTS'] = 0
services65['RESCOU'] = 'FR'

# Select specific columns from 'services5' DataFrame for 'TYPINS' equal to '53100'
services9 = services5.loc[services5['TYPINS'] == '53100']

# Assign 0 values to specific columns for '53100' rows
services9['PAYMENTS'] = 0
services9['RECEIPTS'] = 0
services9['PAYMENTS_ROM'] = 0
services9['RECEIPTS_ROM'] = 0
services9['RESCOU'] = 'FR'
services9['ENTITYID'] = 'BOP_A'






# Define a list of cube values and corresponding cube IDs
cube_values = ['53300', '53050', '53240', '53470']
cube_ids = ['NSNFC_53300', 'NSNFC_53050', 'NSNFC_53240', 'NSNFC_53470']

# Create modified DataFrames for each cube value and cube ID combination
modified_dataframes = []
for cube_value, cube_id in zip(cube_values, cube_ids):
    modified_df = services9.copy()
    modified_df['TYPINS'] = cube_value
    modified_df['CUBEID'] = cube_id
    modified_dataframes.append(modified_df)

# Concatenate the modified DataFrames into a single DataFrame
combined_works = pd.concat(modified_dataframes, ignore_index=True)

# Create another set of modified DataFrames for a specific cube (TYPINS='53100')
services10 = services5.loc[services5['TYPINS'] == '53100']
services10['PAYMENTS'] = 0
services10['RECEIPTS'] = 0
services10['PAYMENTS_ROM'] = 0
services10['RECEIPTS_ROM'] = 0
services10['RESCOU'] = 'FR'
services10['ENTITYID'] = 'BOP_C20'

# Define a list of cube values and corresponding cube IDs for the second set
cube_values1 = ['53040', '53080', '53110', '53160', '53300', '53380', '53470']
cube_ids1 = ['NSNFC_53040', 'NSNFC_53080', 'NSNFC_53110', 'NSNFC_53160', 'NSNFC_53300', 'NSNFC_53380', 'NSNFC_53470']

# Create modified DataFrames for the second set of cube values and cube IDs
modified_dataframes = []
for cube_value, cube_id in zip(cube_values1, cube_ids1):
    modified_df = services10.copy()
    modified_df['TYPINS'] = cube_value
    modified_df['CUBEID'] = cube_id
    modified_dataframes.append(modified_df)

# Concatenate the second set of modified DataFrames into a single DataFrame
combined_works2 = pd.concat(modified_dataframes, ignore_index=True)

# here is the end of the process, which basically includes all the cubes for which BOP_C20 and BOP_A had
# data, and now are ready to be inputted as 0's



# Concatenate all relevant DataFrames into a single DataFrame
services_combined = pd.concat([services5, services65, services9, services10, combined_works, combined_works2], ignore_index=True)

# Define aggregation functions for specific columns
agg_funcs = {
    'PAYMENTS': 'sum',
    'RECEIPTS': 'sum',
    'PAYMENTS_ROM': 'sum',
    'RECEIPTS_ROM': 'sum',
    # Add any other columns you want to keep intact here
}




# Fill NaN values in specific columns with default values
services_combined['PAYMENTS'] = services_combined['PAYMENTS'].fillna(0)
services_combined['RECEIPTS'] = services_combined['RECEIPTS'].fillna(0)
services_combined['PAYMENTS_ROM'] = services_combined['PAYMENTS_ROM'].fillna(0)
services_combined['RECEIPTS_ROM'] = services_combined['RECEIPTS_ROM'].fillna(0)
services_combined['RESCOU'] = services_combined['RESCOU'].fillna('')
services_combined['RESENT'] = services_combined['RESENT'].fillna('')
services_combined['STATUS'] = services_combined['STATUS'].fillna('')
services_combined['TYPINS'] = services_combined['TYPINS'].fillna('')
services_combined['TABLEID'] = services_combined['TABLEID'].fillna('')
services_combined['ENTITYID'] = services_combined['ENTITYID'].fillna('')

# Get unique values of 'CUBEID'
uni_codes = services_combined['CUBEID'].unique()

# Reorder and group the DataFrame using aggregation functions
services_combined = services_combined[['OBS_DATE', 'CUBEID', 'RESCOU', 'ENTITYID', 'PAYMENTS', 'TABLEID', 'TYPINS', 'RESENT', 'RECEIPTS', 'PAYMENTS_ROM', 'RECEIPTS_ROM', 'STATUS']]
services_combined = services_combined.groupby(by=['OBS_DATE', 'CUBEID', 'RESCOU', 'ENTITYID', 'TABLEID', 'TYPINS', 'RESENT', 'STATUS']).agg(agg_funcs).reset_index()

# Display the final DataFrame
services_combined

# Filter rows where 'ENTITYID' is 'BOP_A'
rows_with_BOP_A = services_combined[services_combined['ENTITYID'] == 'BOP_A']
rows_with_BOP_A

# Create a copy of the DataFrame
services8 = services_combined.copy()

# Replace "NA'" with 'NA' in column 'RESCOU' because otherwise country code of Nambia is considered NA
services8.loc[services8['RESCOU'] == "NA'", 'RESCOU'] = 'NA'

# Same as above but for 'RESENT' column which is equivalent to 'RESCOU'
# This problem can be solved using a different import method at the beginning which recognize NA as an entry and not a missing value
services8.loc[services8['RESENT'] == "NA'", 'RESENT'] = 'NA'

# Filter rows based on specific conditions
services8 = services8.loc[((services8['PAYMENTS'] != 0) | (services8['RECEIPTS'] != 0) | (services8['PAYMENTS_ROM'] != 0) | (services8['RECEIPTS_ROM'] != 0)) | ((services8['ENTITYID'] == 'BOP_A') | (services8['ENTITYID'] == 'BOP_C20'))]

# Set specific values for 'PAYMENTS', 'RECEIPTS', 'PAYMENTS_ROM', and 'RECEIPTS_ROM'
services8['PAYMENTS'] = services8['PAYMENTS'].round(5)
services8['RECEIPTS'] = services8['RECEIPTS'].round(5)
services8['PAYMENTS_ROM'] = services8['PAYMENTS_ROM'].round(5)
services8['RECEIPTS_ROM'] = services8['RECEIPTS_ROM'].round(5)

# Update values for specific rows and columns based on conditions
services8.loc[services8['TYPINS'] == '53730', 'RESCOU'] = ''
services8.loc[services8['TYPINS'] == '53730', 'PAYMENTS'] = ''
services8.loc[services8['TYPINS'] == '53730', 'RECEIPTS'] = ''
services8.loc[services8['TYPINS'] != '53730', 'PAYMENTS_ROM'] = ''
services8.loc[services8['TYPINS'] != '53730', 'RECEIPTS_ROM'] = ''

# Exclude rows where specific columns have certain values
services8 = services8[~((services8['PAYMENTS_ROM'] == 0) & (services8['RECEIPTS_ROM'] == 0) & (services8['PAYMENTS'] == '') & (services8['RECEIPTS'] == ''))]

for year in range(2018, 2024):
    year_str = str(year)
    year_df = services8[services8['OBS_DATE'].str.contains(year_str)]
    year_df.to_csv(path + f'services_{year_str}.csv', sep=';', index=False)
    

