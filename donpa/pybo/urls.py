from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list),
    path('aabata/', views.aabata_view, name='aabata'),
    path('process_data/', views.process_data, name='process_data'),  # "/process_input/" URL 패턴 추가
    path('process_data1/', views.process_data1, name='process_data1'),  # "/process_input/" URL 패턴 추가
    path('event/', views.events_view, name='event'),
    path('news/', views.news_view, name='news'),  # /news/ 경로에 news_view를 연결
    
    
    # 다른 URL 패턴들...
]