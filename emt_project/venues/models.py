from __future__ import unicode_literals
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class City(models.Model):
	city_name = models.CharField(max_length=50)
	total_locality = models.IntegerField(default=0)
	total_venues = models.IntegerField(default=0)
	city_slug = models.SlugField(unique=True,default=None)
	def __unicode__(self):
		return self.city_name

	def __str__(self):
		return self.city_name

	def children(self):
		return Locality.objects.filter(city_name=self.id)

class Locality(models.Model):
	locality_name = models.CharField(max_length=50)
	city_name = models.ForeignKey(City)
	total_venues = models.IntegerField(default=0)
	locality_slug = models.SlugField(unique=True,default=None)
	def __unicode__(self):
		return self.locality_name

	def __str__(self):
		return self.locality_name

	def children(self):
		return Venues.objects.filter(venue_locality=self.id,venue_city=self.city_name)

	

class Venues(models.Model):
	venue_name = models.CharField(max_length=50)
	venue_city = models.ForeignKey(City)
	venue_locality = models.ForeignKey(Locality)
	content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,default=None)
	object_id = models.PositiveIntegerField(default=0)
	content_object = GenericForeignKey('content_type', 'object_id')
	def __unicode__(self):
		return self.venue_name

	def __str__(self):
		return self.venue_name

	def children(self):
		return Address.objects.filter(venue=self.id)

class Address(models.Model):
	venue = models.ForeignKey(Venues)
	address_line = models.CharField(max_length=150)
	zip_code = models.CharField(max_length=50)
	lon = models.CharField(max_length=50)
	let = models.CharField(max_length=50)

def create_slug(instance ,new_slug=None):
	slug = slugify(instance.locality_name)
	if new_slug is not None:
		slug = new_slug
	qs = Locality.objects.filter(locality_slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = slug+"-"+str(qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	return slug
def pre_save_venue_receiver(sender, instance, *args, **kwargs):
	city_qs = City.objects.filter(city_name=instance.venue_city).first()
	city_qs.total_venues = city_qs.total_venues + 1
	city_qs.save()
	loclity_qs = Locality.objects.filter(locality_name=instance.venue_locality).first()
	loclity_qs.total_venues = loclity_qs.total_venues + 1
	loclity_qs.save()

def pre_save_city_slug(sender, instance, *args, **kwargs):
	if not instance.city_slug:
		instance.city_slug = instance.city.lower()
def pre_save_locality_slug(sender, instance, *args, **kwargs):
	if not instance.locality_slug:
		instance.locality_slug = create_slug(instance)
pre_save.connect(pre_save_venue_receiver, sender=Venues)

pre_save.connect(pre_save_city_slug, sender=City)

pre_save.connect(pre_save_locality_slug, sender=Locality)