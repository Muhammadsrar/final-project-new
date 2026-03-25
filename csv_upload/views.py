import csv
from django.shortcuts import render
from .forms import CSVUploadForm

def upload_csv(request):
    data = []

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # Check file type
            if not file.name.endswith('.csv'):
                return render(request, 'csv_upload/csv_upload.html', {
                    'form': form,
                    'error': 'Please upload a CSV file'
                })

            # Read CSV file
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)

            for row in reader:
                data.append(row)

    else:
        form = CSVUploadForm()

    return render(request,'csv_upload/csv_upload.html', {
        'form': form,
        'data': data
    })