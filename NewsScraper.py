import boto3
import os
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests

def lambda_handler(event, context):
    url = "https://news.google.com/"

    response = requests.get(url) #GET request to URL
    results = []

    #Check if request is successful
    if response.status_code == 200:
        soup = bs(response.content, "html.parser") #Parse HTML content

        headlines = soup.find_all('a', class_ = 'gPFEn')

        for headline in headlines:
            results.append(headline.text.strip())
        
        print("Fetched headlines:")
        print(results)

    else:
        return {
            "statusCode": 500,
            "body": f"Failed to fetch the page. Status code: {response.status_code}"
        }
    
    # Define the S3 bucket and file name
    s3_bucket = "team11headlines"
    file_name = f"results/result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Save the result to a file in /tmp (Lambda's temporary storage)
    temp_file_path = f"/tmp/{file_name.split('/')[-1]}"
    with open(temp_file_path, "w") as file:
        file.write("\n".join(results))
    
    # Upload the file to S3
    s3_client = boto3.client("s3")
    print(f"Uploading file to bucket: {s3_bucket}, path: {file_name}")
    try:
        s3_client.upload_file(temp_file_path, s3_bucket, file_name)
        print("Upload successful")
    except Exception as e:
        print(f"Upload failed: {e}")
    
    # Return the S3 file path
    return {
        "statusCode": 200,
        "body": f"File uploaded to S3: {s3_bucket}/{file_name}"
    }
