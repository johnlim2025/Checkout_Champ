import pandas as pd

# Columns we need to read
columns_to_read = ['code', 'product_name', 'generic_name', 'brands', 'stores']

# Process in chunks
chunk_size = 500000
output_file = 'whole_foods_products.csv'

# Initialize the output file with headers
pd.DataFrame(columns=['barcode', 'product_name', 'generic_name', 'brands']).to_csv(output_file, index=False)

# Process the file in chunks
processed_rows = 0
whole_foods_count = 0

for chunk in pd.read_csv('main/barcodes/en.openfoodfacts.org.products.csv', 
                         sep='\t',
                         usecols=columns_to_read,
                         chunksize=chunk_size,
                         dtype={'code': str, 'product_name': str, 'stores': str},
                         na_values=[''],
                         keep_default_na=False):
    
    processed_rows += len(chunk)
    
    # Filter for Whole Foods products
    # Convert NaN to empty string to avoid errors with str.contains
    chunk['stores'] = chunk['stores'].fillna('')
    whole_foods_products = chunk[chunk['stores'].str.contains('whole foods', case=False)]
    
    whole_foods_count += len(whole_foods_products)
    
    # Select and rename columns
    if not whole_foods_products.empty:
        result = whole_foods_products[['code', 'product_name', 'generic_name', 'brands']]
        #result = result.drop_duplicates(subset=['barcode'])
        result = result.dropna(subset=['product_name'])
        
        # Append to the output file
        result.to_csv(output_file, mode='a', header=False, index=False)
    
    print(f"Processed {processed_rows} rows, found {whole_foods_count} Whole Foods products so far")

print(f"Done! Found a total of {whole_foods_count} Whole Foods products")
print(f"Results saved to {output_file}")