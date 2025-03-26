from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator
from .tasks import scrape_categories, scrape_subcategories, scrape_businesses
from .models import Category, Subcategory, Business
import pandas as pd
import json
from django.conf import settings
import os

ITEMS_PER_PAGE = settings.ITEMS_PER_PAGE

def categories_dashboard(request):
    page = request.GET.get('page', 1)
    categories = Category.objects.all().order_by('name')
    paginator = Paginator(categories, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(page)
    context = {
        'categories': page_obj,
        'total_categories': categories.count(),
    }
    return render(request, 'scraper/categories.html', context)

def subcategories_dashboard(request):
    page = request.GET.get('page', 1)
    subcategories = Subcategory.objects.all().order_by('category__name', 'name')
    paginator = Paginator(subcategories, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(page)
    context = {
        'subcategories': page_obj,
        'total_subcategories': subcategories.count(),
    }
    return render(request, 'scraper/subcategories.html', context)

def businesses_dashboard(request):
    page = request.GET.get('page', 1)
    businesses = Business.objects.all().order_by('subcategory__category__name', 'subcategory__name', 'name')
    paginator = Paginator(businesses, ITEMS_PER_PAGE)
    page_obj = paginator.get_page(page)
    context = {
        'businesses': page_obj,
        'total_businesses': businesses.count(),
    }
    return render(request, 'scraper/businesses.html', context)

def trigger_scrape_categories(request):
    scrape_categories.delay()
    return redirect('categories_dashboard')

def trigger_scrape_subcategories(request, category_id):
    scrape_subcategories.delay(category_id)
    return redirect('subcategories_dashboard')

def trigger_scrape_businesses(request, subcategory_id):
    scrape_businesses.delay(subcategory_id)
    return redirect('businesses_dashboard')

def load_sample_data(request):
    sample_data = [
        {
            "Business Name": "Top Machinery and Factory Zone Broker",
            "Subcategory": "Commercial Broker",
            "Category": "Agents in Ethiopia",
            "Details": "{'Mobile': '+251 967 825 702', 'Mobile 2': '+251 980 157 401'}"
        },
        {
            "Business Name": "Eserve Consultancy",
            "Subcategory": "Commercial Broker",
            "Category": "Agents in Ethiopia",
            "Details": "{'Phone': '+251 11 5540691', 'Mobile': '+251 912 779813'}"
        },
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
    return redirect('businesses_dashboard')

def export_categories_csv(request):
    categories = Category.objects.all()
    data = [{'Name': c.name, 'URL': c.href} for c in categories]
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categories.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def export_subcategories_csv(request):
    subcategories = Subcategory.objects.all()
    data = [{'Name': s.name, 'Category': s.category.name, 'URL': s.href} for s in subcategories]
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="subcategories.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def export_businesses_csv(request):
    businesses = Business.objects.all()
    data = [{
        'Name': b.name,
        'Subcategory': b.subcategory.name,
        'Category': b.subcategory.category.name,
        'Details': json.dumps(b.details)
    } for b in businesses]
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="businesses.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response

def export_categories_excel(request):
    categories = Category.objects.all()
    data = [{'Name': c.name, 'URL': c.href} for c in categories]
    df = pd.DataFrame(data)
    file_path = os.path.join(settings.MEDIA_ROOT, 'categories.xlsx')
    df.to_excel(file_path, index=False)
    with open(file_path, 'rb') as excel_file:
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="categories.xlsx"'
    return response

def export_subcategories_excel(request):
    subcategories = Subcategory.objects.all()
    data = [{'Name': s.name, 'Category': s.category.name, 'URL': s.href} for s in subcategories]
    df = pd.DataFrame(data)
    file_path = os.path.join(settings.MEDIA_ROOT, 'subcategories.xlsx')
    df.to_excel(file_path, index=False)
    with open(file_path, 'rb') as excel_file:
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="subcategories.xlsx"'
    return response

def export_businesses_excel(request):
    businesses = Business.objects.all()
    data = [{
        'Name': b.name,
        'Subcategory': b.subcategory.name,
        'Category': b.subcategory.category.name,
        'Details': json.dumps(b.details)
    } for b in businesses]
    df = pd.DataFrame(data)
    file_path = os.path.join(settings.MEDIA_ROOT, 'businesses.xlsx')
    df.to_excel(file_path, index=False)
    with open(file_path, 'rb') as excel_file:
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="businesses.xlsx"'
    return response

def analysis(request):
    context = {
        'total_categories': Category.objects.count(),
        'total_subcategories': Subcategory.objects.count(),
        'total_businesses': Business.objects.count(),
    }
    return render(request, 'scraper/analysis.html', context)