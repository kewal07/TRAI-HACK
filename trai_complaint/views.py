from django.shortcuts import render
from django.views import generic
from django.contrib.auth.views import logout
from django.http import HttpResponseRedirect, HttpResponse
from trai_complaint.models import Category, TSP, TSPService, Complaint, ComplaintWithCategory, ComplaintWithService, Status
from random import randint
import os, sys, linecache
import simplejson as json

# Create your views here.

circles = ['Andhra Pradesh', 'Assam', 'Bihar & Jharkhand', 'Chennai', 'Delhi', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu & Kashmir', 'Karnataka', 'Kerala', 'Kolkata', 'Madhya Pradesh & Chhattisgarh', 'Maharashtra', 'Mumbai', 'North East', 'Orissa', 'Punjab', 'Rajasthan', 'Tamilnadu', 'UP-East', 'UP-West & Uttarakhand', 'West Bengal']

class SignUpFormView(generic.ListView):
	template_name = 'trai_complaint/signup.html'
	def get_queryset(self):
		return {}

class SignInFormView(generic.ListView):
	template_name = 'trai_complaint/signin.html'
	def get_queryset(self):
		return {}

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

class IndexView(generic.ListView):
	template_name = 'trai_complaint/index.html'
	context_object_name = 'data'
	def get_queryset(self):
		data = {}
		data["complaints"] = Complaint.objects.all()
		data['categories'] = Category.objects.all()
		data['tsps'] = TSP.objects.all()
		data['services'] = TSPService.objects.all()
		return data

class DashboardView(generic.ListView):
	template_name = 'trai_complaint/dashboard.html'
	context_object_name = 'data'
	def get_queryset(self):
		data = {}
		data["complaints"] = Complaint.objects.all()
		op_status = Status.objects.filter(code__in=['O','RO'])
		data['openc'] = Complaint.objects.filter(status__in=op_status)
		data['categories'] = Category.objects.all()
		data['tsps'] = TSP.objects.all()
		data['services'] = TSPService.objects.all()
		data['circles'] = circles
		return data

class ComplaintDetailView(generic.DetailView):
	template_name = 'trai_complaint/complaint-detail.html'
	model = Complaint

class AddComplaintView(generic.ListView):
	template_name = 'trai_complaint/add-complaint.html'
	context_object_name = 'data'
	def get_queryset(self):
		data = {}
		if self.request.GET.get("id"):
			comp_id = self.request.GET.get("id")
			comp = Complaint.objects.get(id=int(comp_id))
			if comp:
				data["summary"] = comp.summary
				data["description"] = comp.description
				data["scat"] = ",".join([x.category.display_name for x in comp.complaintwithcategory_set.all()])+","
				data["sserv"] = ",".join([x.service.display_name for x in comp.complaintwithservice_set.all()])+","
		data['categories'] = Category.objects.all()
		data['tsps'] = TSP.objects.all()
		data['services'] = TSPService.objects.all()
		data['circles'] = circles
		return data

class CreateComplaintView(generic.ListView):
	template_name = 'trai_complaint/index.html'
	def post(self,request,*args,**kwargs):
		try:
			print(request.path,request.POST)
			post_data = request.POST
			custId = post_data.get('phoneNoOrUserId')
			tsp_code = post_data.get('tsp')
			circle = post_data.get('circle')
			summary = post_data.get('summary')
			description = post_data.get('description')
			selectedCats = post_data.get('selectedCategories').split(",")
			services = post_data.get('selectedServices').split(",")
			errors = {}
			if not list(filter(bool, selectedCats)):
				errors['categories'] = "Please Select a category"
			if not list(filter(bool, services)):
				errors['services'] = "Please Select a service"
			if not summary.strip():
				errors['summary'] = "Please provide a Summary"
			if not custId.strip():
				errors['phoneNoOrUserId'] = "Please provide the Phone No / User id"
			if not description.strip():
				errors['description'] = "Please provide description"
			if not errors:
				tsp = TSP.objects.get(code=tsp_code)
				complaint = Complaint(user=request.user, summary=summary, description=description, tsp=tsp, circle=circle, customer_id=custId)
				complaint.save()
				for cat in selectedCats:
					if cat.strip():
						category = Category.objects.filter(display_name=cat)[0]
						compWithCat = ComplaintWithCategory.objects.get_or_create(category=category, complaint=complaint)
				for serv in services:
					if serv.strip():
						service = TSPService.objects.filter(display_name=serv)[0]
						compWithServ = ComplaintWithService.objects.get_or_create(service=service, complaint=complaint)
			return HttpResponse(json.dumps(errors), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

class AjaxQueriesView(generic.ListView):
	template_name = 'trai_complaint/index.html'
	def post(self,request,*args,**kwargs):
		try:
			print(request.path,request.POST)
			if request.path == "/cust_details/":
				custId = request.POST.get("custId")
				random_index = randint(0, len(circles) - 1)
				response_dic = {}
				response_dic['circle'] = circles[random_index]
				response_dic['tsp'] = TSP.objects.random().code
				return HttpResponse(json.dumps(response_dic), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))


class ComparativeView(generic.ListView):
	template_name = 'trai_complaint/comparative-analytics.html'
	context_object_name = 'data'
	def get_queryset(self):
		data = {}
		data["complaints"] = Complaint.objects.all()
		data['categories'] = Category.objects.filter(parent_category__isnull=True)
		data['tsps'] = TSP.objects.all()
		data['services'] = TSPService.objects.all()
		data['circles'] = circles
		return data

class PredictiveView(generic.ListView):
	template_name = 'trai_complaint/predective-analytics.html'
	context_object_name = 'data'
	def get_queryset(self):
		data = {}
		data["complaints"] = Complaint.objects.all()
		data['categories'] = Category.objects.all()
		data['tsps'] = TSP.objects.all()
		data['services'] = TSPService.objects.all()
		return data

class ExportView(generic.ListView):
	template_name = 'trai_complaint/download.html'
	context_object_name = 'data'
	def get_queryset(self):
		data = {}
		data["complaints"] = Complaint.objects.all()
		data['categories'] = Category.objects.all()
		data['tsps'] = TSP.objects.all()
		data['services'] = TSPService.objects.all()
		data['circles'] = circles
		return data