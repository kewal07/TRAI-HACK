from django.shortcuts import render
from django.views import generic
from django.contrib.auth.views import logout
from django.http import HttpResponseRedirect, HttpResponse
from trai_complaint.models import Category, TSP, TSPService, Complaint, ComplaintWithCategory, ComplaintWithService, Status
from random import randint
import os, sys, linecache
import simplejson as json
from wit import Wit

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

	def post(self,request,*args,**kwargs):
		try:
			success = {}
			userMsg = request.POST.get('message')
			actions = {
			    'getBalance': getBalance,
				'gettransactions':gettransactions,
			}
			client = Wit(access_token='TDBAKQ4EH4VKWJ4WXU3XD5RCICMUBHUH', actions=actions)
			print(userMsg)
			resp = client.converse('my-user-session-42', userMsg, {})
			print(resp)
			if 'msg' in resp:
				success['msg'] = resp.get('msg')
			elif 'action' in resp:
				if resp['action'] == 'gettransactions':
					success['msg'] = gettransactions()
				else:
					success['msg'] = getBalance()
			else:
				success['msg'] = "Finding resolution for your query"
			return HttpResponse(json.dumps(success), content_type='application/json')
		except Exception as e:
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

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
			if request.path == "/predict/":
				custId = request.POST.get("custId")
				random_index = randint(0, len(circles) - 1)
				response_dic = {}
				response_dic['circle'] = circles[random_index]
				response_dic['tsp'] = TSP.objects.random().code
				return HttpResponse(json.dumps(response_dic), content_type='application/json')
			if request.path == "/cmp_ana/":
				response_dic = {}
				categories = Category.objects.filter(parent_category__isnull=True)
				t1 = request.POST.get("tsp1").strip()
				t2 = request.POST.get("tsp2").strip()
				c1 = request.POST.get("circle1").strip()
				c2 = request.POST.get("circle2").strip()
				s1 = request.POST.get("service1").strip()
				s2 = request.POST.get("service2").strip()
				data1 = []
				data2 = []
				for cat in categories:
					cmps = [x.complaint for x in ComplaintWithCategory.objects.filter(category=cat)]
					addCnt1 = True
					addCnt2 = True
					d1 = 0
					d2 = 0
					for cmp in cmps:
						ser = [x.service.code for x in cmp.complaintwithservice_set.all()]
						if t1 and cmp.tsp.code != t1:
							addCnt1 = False
						if t2 and cmp.tsp.code != t2:
							addCnt2 = False
						if c1 and cmp.circle != c1:
							addCnt1 = False
						if c2 and cmp.circle != c2:
							addCnt2 = False
						if s1 and s1 not in ser:
							addCnt1 = False
						if s2 and s2 not in ser:
							addCnt2 = False
						if addCnt2:
							d2 += 1
						if addCnt1:
							d1 += 1
					data1.append(d1)
					data2.append(d2)
				response_dic['data1'] = data1
				response_dic['data2'] = data2
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

class OpinionPoll(generic.ListView):
	template_name = 'trai_complaint/opinion.html'
	def get_queryset(self):
		data = {}
		return data

class DoItYourself(generic.ListView):
	template_name = 'trai_complaint/do-it-yourself.html'
	def get_queryset(self):
		data = {}
		return data

import xlwt
normal_style = xlwt.easyxf(
	"""
	font:name Verdana
	"""
)

border_style = xlwt.easyxf(
	"""
	font:name Verdana;
	border: top thin, right thin, bottom thin, left thin;
	align: vert centre, horiz left;
	"""
)

def excel_view(request):

	complaints = Complaint.objects.all()
	response = HttpResponse(content_type='application/ms-excel')
	fname = "Complaints.xls"
	response['Content-Disposition'] = 'attachment; filename=%s' % fname
	wb = xlwt.Workbook()
	ws1 = wb.add_sheet('Raw Data', cell_overwrite_ok=True)
	ws1.write(0,0,"SR",normal_style)
	ws1.write(0,1,"Circle",normal_style)
	ws1.write(0,2,"Product",normal_style)
	ws1.write(0,3,"TSP",normal_style)
	ws1.write(0,4,"Summary",normal_style)
	ws1.write(0,5,"Created At",normal_style)
	ws1.write(0,6,"Updated At",normal_style)
	ws1.write(0,7,"Status",normal_style)
	ws1.write(0,8,"Category",normal_style)
	i = 1
	for complaint in complaints:
		ws1.write(i,0,complaint.id,normal_style)
		ws1.write(i,1,complaint.circle,normal_style)
		service = ",".join([x.service.display_name for x in complaint.complaintwithservice_set.all()])
		ws1.write(i,2,service,normal_style)
		ws1.write(i,3,complaint.tsp.display_name,normal_style)
		ws1.write(i,4,complaint.summary,normal_style)
		ws1.write(i,5,str(complaint.created_at),normal_style)
		ws1.write(i,6,str(complaint.updated_at),normal_style)
		ws1.write(i,7,complaint.status.display_name,normal_style)
		cats = ",".join([x.category.display_name for x in complaint.complaintwithcategory_set.all()])
		ws1.write(i,8,cats,normal_style)
		i+=1
	wb.save(response)
	return response

def getBalance(request, response):
	return "20"

def gettransactions():
	return 'Subscribed to caller tune'
	
