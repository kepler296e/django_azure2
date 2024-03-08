from django.shortcuts import render
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os

language_key = os.environ.get('LANGUAGE_KEY', '')
language_endpoint = os.environ.get('LANGUAGE_ENDPOINT', '')


def authenticate_client():
    ta_credential = AzureKeyCredential(language_key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=language_endpoint,
        credential=ta_credential)
    return text_analytics_client


def analyze_sentiment(text):
    client = authenticate_client()
    document_scores = []
    sentence_scores = []
    error = ""

    try:
        result = client.analyze_sentiment([text], show_opinion_mining=False)
        doc_result = [doc for doc in result if not doc.is_error]

        for doc in doc_result:
            # Document
            document_scores.append({
                'sentiment': doc.sentiment,
                'confidence': int(max(doc.confidence_scores.positive, doc.confidence_scores.neutral, doc.confidence_scores.negative) * 100)
            })
            for sentence in doc.sentences:
                # Sentence
                sentence_scores.append({
                    'text': sentence.text,
                    'sentiment': sentence.sentiment,
                    'confidence': int(max(sentence.confidence_scores.positive, sentence.confidence_scores.neutral, sentence.confidence_scores.negative) * 100)
                })
    except Exception as e:
        error = str(e)

    return document_scores, sentence_scores, error


def index(request):
    document_scores = []
    sentence_scores = []
    error = ""

    context = {}
    if request.method == 'POST':
        text = request.POST.get('text', '')
        document_scores, sentence_scores, error = analyze_sentiment(text)
    else:
        # Load default results
        document_scores = [{'sentiment': 'mixed', 'confidence': 50}]
        sentence_scores = [{'text': 'I loved the movie! ', 'sentiment': 'positive', 'confidence': 99},
                           {'text': 'but the soundtrack was really annoying.', 'sentiment': 'negative', 'confidence': 99}]

    context = {'document_scores': document_scores,
               'sentence_scores': sentence_scores, 'error': error}

    return render(request, 'index.html', context)
