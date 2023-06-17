import re
import json
import nltk
import pandas as pd
from textblob import TextBlob
from nltk.corpus import stopwords
from django.http import HttpResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')


print("Starting data loading")
csv_path = 'static/temp_new_final.csv'
df_reviews = pd.read_csv(csv_path)
print("Data loading done")

def calc_polarity(review):
    review = preprocess_text(review)
    return TextBlob(review).sentiment.polarity

def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    words = nltk.word_tokenize(text)
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)


@csrf_exempt
def top_restaurants(request, postal_code, category, price):
    restaurants = []
    results = df_reviews.loc[(df_reviews['postal_code'] == float(postal_code)) & df_reviews['categories'].str.contains(category) & (df_reviews['price'] == int(price))]

    if results.empty:
        results = df_reviews.loc[df_reviews['categories'].str.contains(category) & ((df_reviews['postal_code'] == float(int(postal_code)-3)) | (df_reviews['postal_code'] == float(int(postal_code)+3))) & (df_reviews['price'] == int(price))]

    polarities = results.groupby('name')['textBlob_polarities'].mean().values

    unique_names = results.drop_duplicates(subset='name').sort_values(by = 'name')
    unique_names['updated_polarities'] = polarities

    sorted_results = unique_names.sort_values(by = 'updated_polarities', ascending=False)
    sorted_results = sorted_results.drop(columns = ['text', 'textBlob_polarities','categories'],axis = 1)
    sorted_results = sorted_results.drop_duplicates(subset=['name'])

    for _, record in sorted_results.head(3).iterrows():
        location = f"{record['address']}, {record['city']}, {record['postal_code']}"
        hours = str(record['hours'])
        restaurants.append({
            "business_id": record['business_id'],
            "name": record['name'],
            "location": location,
            "hours": hours,
            "stars": record['stars'],
            "price": record['price']
        })
    return HttpResponse(json.dumps({"restaurants": restaurants}))



@csrf_exempt
def get_reviews(request, business_id):
    reviews = []
    polarity = 0
    cnt = 0
    results = df_reviews.loc[df_reviews['business_id'] == business_id]
    for _, record in results.iterrows():
        polarity += record['textBlob_polarities']
        cnt += 1
        reviews.append({ 
            "review": record['text'],
            "polarity": "%.4f" % record['textBlob_polarities'],
            "cleanness": "%.4f" % record['Sentiment (Cleanliness)'],
            "service": "%.4f" % record['Sentiment (Service)'],
            "food": "%.4f" % record['Sentiment (Food)'],
            "price": "%.4f" % record['Sentiment (Price)']
        })
    return HttpResponse(json.dumps({
        "name": results.iloc[0]['name'],
        "polarity_score": "%.4f" % (polarity / cnt),
        "reviews": reviews
    }))


@csrf_exempt
def get_postal_codes(request):
    results = df_reviews['postal_code']
    cleanedList = [int(x) for x in list(set(results)) if str(x) != 'nan']
    return HttpResponse(json.dumps(cleanedList))


@csrf_exempt
def get_restaurants(request):
    restaurants = []
    check = []
    results = df_reviews[["name", "business_id"]]
    for _, record in results.iterrows():
        if record['business_id'] not in check:
            restaurants.append({
                "restaurant": record['name'],
                "business_id": record['business_id']
            })
            check.append(record['business_id'])
    return HttpResponse(json.dumps(restaurants))


def get_aspect_name(aspect):
    if aspect == "cleanness":
        return "Sentiment (Cleanliness)"
    elif aspect == "service":
        return "Sentiment (Service)"
    elif aspect == "food":
        return "Sentiment (Food)"
    else:
        return "Sentiment (Price)"


@csrf_exempt
def get_aspect(request, aspect, business_id):
    reviews = []
    polarity = 0
    cnt = 0
    results = df_reviews.loc[df_reviews['business_id'] == business_id]
    for _, record in results.iterrows():
        if record[get_aspect_name(aspect)] > 0:
            reviews.append({
                "review": record['text'],
                "polarity": "%.4f" % record['textBlob_polarities'],
                "cleanness": "%.4f" % record['Sentiment (Cleanliness)'],
                "service": "%.4f" % record['Sentiment (Service)'],
                "food": "%.4f" % record['Sentiment (Food)'],
                "price": "%.4f" % record['Sentiment (Price)']
            })
        polarity += record['textBlob_polarities']
        cnt += 1
    return HttpResponse(json.dumps({
        "name": results.iloc[0]['name'],
        "polarity_score": "%.4f" % (polarity / cnt),
        "reviews": reviews
    }))
