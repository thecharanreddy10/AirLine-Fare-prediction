"""
URL configuration for fair_price_prediction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainapp import views as mainviews
from adminapp import views as adminviews
from userapp import views as userviews
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mainviews.home, name="home"),
    path('user-login', mainviews.user_login, name="user_login"),
    path('user-register', mainviews.user_register, name="user_register"),
    path('admin-login', mainviews.admin_login, name="admin_login"),
    path('otp', mainviews.otp, name='otp'),
    path('new-otp', mainviews.resendOtp, name='resendOtp'),
    path('about', mainviews.about, name='about'),


    #admin
    path('admin-dashboard', adminviews.admin_dashboard, name='admin_dashboard'),
    path('pending-users', adminviews.pending_users, name='pending_users'),
    path('all-users', adminviews.all_users, name='all_users'),
    path('upload-dataset', adminviews.upload_dataset, name='upload_dataset'),
    path('datasets-list', adminviews.view_datasets_list, name='view_datasets_list'),
    path('delete-dataset/<int:id>/', adminviews.delete_dataset, name='delete_dataset'),
    path('dataset-result/<int:id>/', adminviews.view_dataset_result, name='view_dataset_result'),
    path('train-and-test', adminviews.train_and_test, name='train_and_test'),
    path('train-and-test-result', adminviews.train_and_test_result, name='train_and_test_result'),
    path('user-feedbacks', adminviews.admin_feedbacks, name='admin_feedbacks'),
    path('delete-feedback-item/<int:id>/', adminviews.deleteFeed, name="deleteFeed"),
    path('sentiment-analysis', adminviews.sentiment_analysis, name='sentiment_analysis'),
    path('delete-sent-feed/<int:id>/', adminviews.deleteSentFeed, name='deleteSentFeed'),
    path('delete-all-feeds', adminviews.deleteAllFeeds, name='deleteAllFeeds'),
    path('delete-all-sent-feeds', adminviews.deleteAllsentFeeds, name='deleteAllsentFeeds'),
    path('feedback-graphs', adminviews.feedbacks_graph, name='feedbacks_graph'),
    path('accept-user/<int:id>/', adminviews.accept_user, name='accept_user'),
    path('reject-user/<int:id>/', adminviews.reject_user, name="reject_user"),
    path('change-status/<int:id>/', adminviews.change_status, name='change_status'),
    path('delete-user/<int:id>/', adminviews.delete_user, name='delete_user'),
    path('delete-all-users', adminviews.deleteAll_users, name="deleteAll_users"),
    path('comparision-graph', adminviews.comparison_graph, name='comparison_graph'),
    path('adminlogout',adminviews.adminlogout, name='adminlogout'),

    #models
    path('densenet-model', adminviews.run_densenet, name='run_densenet'),
    path('densenet-model-result', adminviews.run_densenet_result, name='run_densenet_result'),

    path('mobilenet-model', adminviews.run_mobilenet, name='run_mobilenet'),
    path('mobilenet-model-result', adminviews.run_mobilenet_result, name='run_mobilenet_result'),

    path('xception-model', adminviews.run_xception, name='run_xception'),
    path('xception-model-result', adminviews.run_xception_result, name='run_xception_result'),

    path('random-forest', adminviews.run_random_forest, name="run_random_forest"),
    path('random-forest-result', adminviews.run_random_forest_result, name="run_random_forest_result"),


    path('data-visualization', adminviews.data_visualization, name='data_visualization'),

    #user
    path('user-dashboard', userviews.user_dashboard, name='user_dashboard'),
    path('route-list', userviews.route_list, name='route_list'),
    path('detection-dashboard', userviews.detection_dashboard, name='detection_dashboard'),
    path('detection-result', userviews.detection_result, name="detection_result"),
    path('user-logout', userviews.user_logout, name='user_logout'),
    path('user-profile', userviews.user_profile, name='user_profile'),
    path('user-feedback', userviews.user_feedback, name='user_feedback'),
    path('about-models', userviews.about_models, name='about_models'),
    path('user-about',  userviews.user_about, name='user_about'),
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
