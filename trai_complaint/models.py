from django.db import models
from django.conf import settings
from datetime import date
from random import randint
from django.db.models import Count
from django.template.defaultfilters import slugify

# Create your models here.

def get_file_path(instance, filename):
	ext = filename.split('.')[-1]
	name = filename.split('.')[0]
	filename = "attachment_%s.%s" % (name,ext)
	folder_day = date.today()
	folderPath = (os.path.join(settings.BASE_DIR,'media'+os.sep+'attachments'+os.sep+str(folder_day)))
	return os.path.join(folderPath,filename)

class RandomManager(models.Manager):
    def random(self):
        count = self.aggregate(ids=Count('id'))['ids']
        random_index = randint(0, count - 1)
        return self.all()[random_index]

class Status(models.Model):
	display_name = models.CharField(max_length=200)
	code = models.CharField(max_length=10, unique=True)
	def __str__(self):
		return self.display_name

class TSP(models.Model):
	display_name = models.CharField(max_length=200)
	code = models.CharField(max_length=50, unique=True)

	objects = RandomManager()

	def __str__(self):
		return self.display_name
	def get_logo(self):
		return "/static/images/logos/tsp/%s.png"%(self.code)

class TSPService(models.Model):
	display_name = models.CharField(max_length=200)
	code = models.CharField(max_length=50, unique=True)
	def __str__(self):
		return self.display_name
	def get_logo(self):
		return "/static/images/logos/tsp/service_%s.png"%(self.code)

class Category(models.Model):
	display_name = models.CharField(max_length=200)
	code = models.CharField(max_length=50, unique=True)
	parent_category = models.ForeignKey('self', null=True, blank=True)
	def __str__(self):
		return self.display_name
	def get_logo(self):
		return "/static/images/logos/category/%s.png"%(self.code)

class Complaint(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	summary = models.CharField(max_length=200)
	description = models.CharField(max_length=400)
	attachment = models.FileField(upload_to=get_file_path,blank=True,null=True)
	created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
	updated_at = models.DateTimeField(blank=True, null=True, auto_now=True)
	status = models.ForeignKey(Status, blank=True, null=True)
	location = models.CharField(max_length=200)
	circle = models.CharField(max_length=200)
	tsp = models.ForeignKey(TSP)
	slug = models.SlugField(null=True,blank=True)
	customer_id = models.CharField(max_length=200,null=True,blank=True)

	def __str__(self):
		return self.summary+"_"+self.status.display_name
	def get_class(self):
		cat_class = " ".join([x.category.code.replace(" ","_") for x in self.complaintwithcategory_set.all()])
		service_class = " ".join([x.service.code.replace(" ","_") for x in self.complaintwithservice_set.all()])
		return self.tsp.code + " " + cat_class + " " + service_class
	def save(self, *args, **kwargs):
		if not self.status:
			opened_status = Status.objects.get(code="O")
			self.status = opened_status
		summary = self.summary
		if not self.slug:
			short_summary = summary[:50]
			if not short_summary.strip():
				short_summary = None
			slug = slugify(short_summary)
			if not slug and not slug.strip():
				slug = None
			self.slug = slug
		super(Complaint, self).save(*args, **kwargs)

class ComplaintWithService(models.Model):
	complaint = models.ForeignKey(Complaint)
	service = models.ForeignKey(TSPService)

class ComplaintWithCategory(models.Model):
	complaint = models.ForeignKey(Complaint)
	category = models.ForeignKey(Category)
		
