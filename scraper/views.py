from django.shortcuts import render, redirect
from django.http import HttpResponse
from .tasks import scrape_categories, scrape_subcategories, scrape_businesses
from .models import Category, Subcategory, Business
import pandas as pd
import json
from django.conf import settings
import os

def index(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    businesses = Business.objects.all()
    context = {
        'categories': categories,
        'subcategories': subcategories,
        'businesses': businesses,
        'category_count': categories.count(),
        'subcategory_count': subcategories.count(),
        'business_count': businesses.count(),
    }
    return render(request, 'scraper/index.html', context)

def trigger_scrape_categories(request):
    scrape_categories.delay()
    return redirect('index')

def trigger_scrape_subcategories(request, category_id):
    scrape_subcategories.delay(category_id)
    return redirect('index')

def trigger_scrape_businesses(request, subcategory_id):
    scrape_businesses.delay(subcategory_id)
    return redirect('index')

def load_sample_data(request):
    sample_data = [
        {"Business Name": "Top Machinery and Factory Zone Broker", "Subcategory": "Commercial Broker", "Category": "Agents in Ethiopia", "Details": "{'Mobile': '+251 967 825 702', 'Mobile 2': '+251 980 157 401', 'Location': '', 'Primary Category': 'Commercial Broker'}"},
        {"Business Name": "Eserve Consultancy for Business, Investment and Conveya...", "Subcategory": "Commercial Broker", "Category": "Agents in Ethiopia", "Details": "{'Phone': '+251 11 5540691', 'Fax': '+251 11 5540692', 'Mobile': '+251 912 779813', 'Mobile 2': '+251 911 513842', 'Mobile 3': '+251 913 242055', 'Sub City': 'Kirkos', 'Business Type': 'Private', 'Location': 'Africa Avenue, Mega Building, 1st floor, Office. 116, Addis Ababa, Ethiopia', 'Primary Category': 'Consultancy/ Business and Investment'}"},
        # Add more sample data here as needed
    ]
    
    for entry in sample_data:
        category, _ = Category.objects.get_or_create(name=entry["Category"])
        subcategory, _ = Subcategory.objects.get_or_create(category=category, name=entry["Subcategory"])
        details = json.loads(entry["Details"].replace("'", '"'))
        Business.objects.update_or_create(
            subcategory=subcategory,
            name=entry["Business Name"],
            defaults={'details': details}
        )
    return redirect('index')

def export_csv(request):
    businesses = Business.objects.all()
    data = [{
        'Business Name': b.name,
        'Subcategory': b.subcategory.name,
        'Category': b.subcategory.category.name,
        'Details': json.dumps(b.details)
    } for b in businesses]
    
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="business_data.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def export_excel(request):
    businesses = Business.objects.all()
    data = [{
        'Business Name': b.name,
        'Subcategory': b.subcategory.name,
        'Category': b.subcategory.category.name,
        'Details': json.dumps(b.details)
    } for b in businesses]
    
    df = pd.DataFrame(data)
    file_path = os.path.join(settings.MEDIA_ROOT, 'business_data.xlsx')
    df.to_excel(file_path, index=False)
    
    with open(file_path, 'rb') as excel_file:
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="business_data.xlsx"'
    return response

def analysis(request):
    businesses = Business.objects.all()
    context = {
        'business_count': businesses.count(),
        'subcategory_count': Subcategory.objects.count(),
        'category_count': Category.objects.count(),
    }
    return render(request, 'scraper/analysis.html', context)