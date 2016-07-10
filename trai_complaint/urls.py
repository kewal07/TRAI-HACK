from django.conf.urls import url, include
from trai_complaint import views

urlpatterns = [
    url(r'^$',views.IndexView.as_view(),name="index"),
    url(r'^dashboard/', views.DashboardView.as_view(),name="dashboard"),
    url(r'^add-complaint/', views.AddComplaintView.as_view(),name="add-complaint"),
    url(r'^create-complaint/', views.CreateComplaintView.as_view(),name="create-complaint"),
    url(r'^cust_details/', views.AjaxQueriesView.as_view(),name="cust_details"),
    url(r'^signup/', views.SignUpFormView.as_view(),name="signup"),
    url(r'^signin/', views.SignInFormView.as_view(),name="signin"),
    url(r'^logout$',views.logout_view,name="logout"),
]
