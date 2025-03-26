from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scrape-categories/', views.trigger_scrape_categories, name='scrape_categories'),
    path('scrape-subcategories/<int:category_id>/', views.trigger_scrape_subcategories, name='scrape_subcategories'),
    path('scrape-businesses/<int:subcategory_id>/', views.trigger_scrape_businesses, name='scrape_businesses'),
    path('load-sample-data/', views.load_sample_data, name='load_sample_data'),
    path('export-csv/', views.export_csv, name='export_csv'),
    path('export-excel/', views.export_excel, name='export_excel'),
    path('analysis/', views.analysis, name='analysis'),
]