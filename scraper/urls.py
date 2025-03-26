from django.urls import path
from . import views

urlpatterns = [
    path('', views.categories_dashboard, name='categories_dashboard'),
    path('subcategories/', views.subcategories_dashboard, name='subcategories_dashboard'),
    path('businesses/', views.businesses_dashboard, name='businesses_dashboard'),
    path('scrape-categories/', views.trigger_scrape_categories, name='scrape_categories'),
    path('scrape-subcategories/<int:category_id>/', views.trigger_scrape_subcategories, name='scrape_subcategories'),
    path('scrape-businesses/<int:subcategory_id>/', views.trigger_scrape_businesses, name='scrape_businesses'),
    path('load-sample-data/', views.load_sample_data, name='load_sample_data'),
    path('export-categories-csv/', views.export_categories_csv, name='export_categories_csv'),
    path('export-subcategories-csv/', views.export_subcategories_csv, name='export_subcategories_csv'),
    path('export-businesses-csv/', views.export_businesses_csv, name='export_businesses_csv'),
    path('export-categories-excel/', views.export_categories_excel, name='export_categories_excel'),
    path('export-subcategories-excel/', views.export_subcategories_excel, name='export_subcategories_excel'),
    path('export-businesses-excel/', views.export_businesses_excel, name='export_businesses_excel'),
    path('analysis/', views.analysis, name='analysis'),
]