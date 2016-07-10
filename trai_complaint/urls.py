from django.conf.urls import url, include
from trai_complaint import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^$',views.IndexView.as_view(),name="index"),
    url(r'^dashboard/', views.DashboardView.as_view(),name="dashboard"),
    url(r'^comparative/', views.ComparativeView.as_view(),name="comparative"),
    url(r'^predective/', views.PredictiveView.as_view(),name="predective"),
    url(r'^download/', views.ComparativeView.as_view(),name="download"),
    url(r'^add-complaint/', login_required(views.AddComplaintView.as_view()),name="add-complaint"),
    url(r'^create-complaint/', login_required(views.CreateComplaintView.as_view()),name="create-complaint"),
    url(r'^complaint/(?P<pk>\d+)/(?P<slug>[\w\-]+)$', (views.ComplaintDetailView.as_view()),name="complaint-detail"),
    url(r'^cust_details/', views.AjaxQueriesView.as_view(),name="cust_details"),
    url(r'^signup/', views.SignUpFormView.as_view(),name="signup"),
    url(r'^signin/', views.SignInFormView.as_view(),name="signin"),
    url(r'^logout$',views.logout_view,name="logout"),
]
