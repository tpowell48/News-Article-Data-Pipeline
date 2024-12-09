import boto3
from collections import Counter
import re
from datetime import datetime

STOPWORDS = {
    "a", "an", "and", "the", "is", "it", "to", "of", "in", "for", "on", 
    "with", "as", "this", "by", "at", "from", "that", "or", "be", "are", 
    "was", "were", "but", "not", "which", "you", "we", "they", "he", 
    "she", "his", "her", "their", "our", "my", "your", "its", "so"
}

def clean_and_tokenize(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return words

def remove_stopwords(words):
    return [word for word in words if word not in STOPWORDS]

def find_most_common_keywords(text, n=10):
    words = clean_and_tokenize(text)
    filtered_words = remove_stopwords(words)
    word_counts = Counter(filtered_words)
    return word_counts.most_common(n)

def lambda_handler(event, context):
    bucket_name = "team11headlines"
    s3_client = boto3.client("s3")
    
    # Combine all text from S3 files
    all_text = ""
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="results/")
    if "Contents" in response:
        for obj in response["Contents"]:
            file_key = obj["Key"]
            print(f"Processing file: {file_key}")
            file_content = s3_client.get_object(Bucket=bucket_name, Key=file_key)["Body"].read().decode("utf-8")
            all_text += file_content + "\n"

    # Process text and find keywords
    if not all_text.strip():
        print("No text to process.")
        return {
            "statusCode": 400,
            "body": "No text found in bucket files to process."
        }

    print("Processing text to extract keywords...")
    common_keywords = find_most_common_keywords(all_text, n=10)

    # Save keywords to a file in S3
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_name = f"keywords/keyword_analysis_{timestamp}.txt"
    temp_file_path = f"/tmp/{output_file_name.split('/')[-1]}"
    with open(temp_file_path, "w") as file:
        file.write("\n".join([f"{word}: {count}" for word, count in common_keywords]))

    s3_client.upload_file(temp_file_path, bucket_name, output_file_name)
    print(f"Keywords file uploaded to S3: s3://{bucket_name}/{output_file_name}")

    return {
        "statusCode": 200,
        "body": f"Keyword analysis completed. Results saved to s3://{bucket_name}/{output_file_name}"
    }
