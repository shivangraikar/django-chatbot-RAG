from django.shortcuts import render
from django.http import JsonResponse
from .forms import PDFUploadForm
from .utils import extract_text_from_pdf, generate_embeddings, query_embeddings, index_embeddings, generate_response_from_llm, generate_response_based_on_pdf
import json

def index(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            extracted_text = extract_text_from_pdf(pdf_file)
            embeddings = generate_embeddings(extracted_text)
            index_embeddings(embeddings)
            # Store the PDF upload status in session
            request.session['pdf_uploaded'] = True
            return JsonResponse({'status': 'success', 'message': 'PDF processed and embeddings indexed.'})
    else:
        form = PDFUploadForm()
    return render(request, 'chatbot/index.html', {'form': form})

def chat(request):
    if request.method == 'POST':
        user_message = json.loads(request.body).get('user_message', '').strip()
        if not user_message:
            return JsonResponse({'response': 'No message provided.'})

        # Check if a PDF was uploaded
        pdf_uploaded = request.session.get('pdf_uploaded', False)
        print(f"PDF Uploaded: {pdf_uploaded}")  # Debug print

        if pdf_uploaded:
            # Generate response based on the PDF content or general response
            response = generate_response_based_on_pdf(user_message)
        else:
            # Provide a general response if no PDF is uploaded
            response = generate_response_from_llm(user_message)

        return JsonResponse({'response': str(response)})

    return render(request, 'chatbot/index.html')


def process_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            extracted_text = extract_text_from_pdf(pdf_file)
            embeddings = generate_embeddings(extracted_text)
            index_embeddings(embeddings)
            request.session['pdf_uploaded'] = True  # Update session status
            return JsonResponse({'status': 'success', 'message': 'PDF processed and embeddings indexed.'})
    
    form = PDFUploadForm()
    return render(request, 'chatbot/index.html', {'form': form})
