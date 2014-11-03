import logging
import json
from rider.models import Rider, Affinity_Group_Mapping
from affinity.models import Group
from rider.serializer import riderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rider.rider_id_tools import create_uuid, decrypt_uuid
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseNotAllowed
from django.utils import simplejson


logger = logging.getLogger(__name__)

def list_group_view(request, r_id):
	#Check that the rider exists
	rider_exists_test = Rider.objects.filter(id=r_id)
	if not rider_exists_test:
		response = HttpResponse("ERROR: Rider does not exist")
		response.status_code = 400
		return response

	#response object placeholder
	json_data = []
	
	#get the list of groups the rider is associated with
	rider_data = Group.objects.filter(rider__id=r_id)
	#check that they're in a group
	if rider_data:
		#iterate over groups they're in
		#get the group ID and group name to return to the client
		for group in rider_data:
                	#affinity_group = group.code
			affinity_group = group.id
			group_data = Group.objects.get(id=affinity_group)
			#json_data.append({'name':group_data.name,'id':affinity_group})
			json_data.append({'name':group_data.name,'code':group_data.code})
	#return the group data as a JSON response and set the response type appropriately
	#return HttpResponse('callback('+json.dumps(json_data)+');', content_type="application/json")
	if 'callback' in request.REQUEST:
		return_string = '%s(%s);' % (request.REQUEST['callback'], json.dumps(json_data))
		return HttpResponse(return_string, content_type="application/json")
	return HttpResponse(json.dumps(json_data), content_type="application/json")

def create_group_view(request):
	#make sure the request is a POST request and that form data has been provided
	if request.method == "POST" and request.POST:
		#Extract the necessary info from the request
		post_data = request.POST
		group_name = post_data['name']
		rider_id = post_data['rider_id']
		aff_code = post_data['aff_code']
		
		#Check if group code is already in use
		#if group test doesn't come back empty, return a bad request error
		group_test = Group.objects.filter(code=aff_code)
		if group_test:
			response = HttpResponse("ERROR: Group code in use")
			response.status_code = 400;
			return response

		#Create a new group with the requested name and affinity code
		group = Group(name=group_name, code=aff_code)
		group.save()

		#Get the PK of the new group and create a mapping to a rider
		group_id = Group.objects.get(code=aff_code).id
		agm = Affinity_Group_Mapping(rider=rider_id, affinity_group=group_id)
		agm.save()
	
		#return a success code
		response = HttpResponse("Success")
		response.status_code = 200
		return response
	#return an error - tells client that only POST is allowed
	response = HttpResponseNotAllowed(['POST'])
	response.write("ERROR: Only POST requests allowed")
	return response

def join_group_view(request, aff_id, r_id):
	#Check if the group exists
	group_exists_test = Group.objects.filter(code=aff_id)
	if not group_exists_test:
		response = HttpResponse("ERROR: Group does not exist")
		response.status_code = 400
		return response

	#Check if the rider is already in the group
	rider_in_group_test = Group.objects.filter(rider__id=r_id).filter(code=aff_id)
	#if group_test isn't empty, return an error code
	if rider_in_group_test:
		response = HttpResponse("ERROR: already in group")
		response.status_code = 400
		return response

	#Get the numerical ID that matches the group's affinity code
	#Then create a mapping from the rider to the group
	group_id=Group.objects.get(code=aff_id).id
	agm = Affinity_Group_Mapping(rider_id=r_id,affinity_group_id=group_id)
	agm.save()

	#return a success response
	response = HttpResponse("Success")
	response.status_code = 200
	return response

def leave_group_view(request, aff_id, r_id):
	#Check that the group exists
	group_exists_test = Group.objects.filter(code=aff_id)
	if not group_exists_test:
		response = HttpResponse("ERROR: Group does not exist")
		response.status_code = 400
		return response

	#Check that the rider is in the group
	rider_in_group_test = Group.objects.filter(rider__id=r_id).filter(code=aff_id)
	if not rider_in_group_test:
		response = HttpResponse("ERROR: Not in group")
		response.status_code = 400
		return response

	#Get the numerical ID that matches the group's affinity code
	#Then find the mapping entry in the Affinity Group Mapping table and delete it
	group_id=Group.objects.get(code=aff_id).id
	agm = Affinity_Group_Mapping.objects.filter(rider_id=r_id).filter(affinity_group_id=group_id)
	agm.delete()
	
	#return a success response
	response = HttpResponse("Success")
	response.status_code = 200
	return response

class RiderAPI(APIView):

    def post(self, request, format=None):
        try:
            logger.debug('trying')
            data = request.DATA
            serializer = riderSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                rider_uuid = create_uuid(serializer.object.pk)

                return Response(
                    {settings.JSON_KEYS['RIDER_ID']: rider_uuid},
                    status=status.HTTP_201_CREATED
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as ex:
            return Response(
                {settings.JSON_KEYS['BAD_REQ']: ex.message},
                status=status.HTTP_400_BAD_REQUEST
            )


class RiderPushUpdateAPI(APIView):

    def post(self, request, format=None):
        data = request.DATA
        id = decrypt_uuid(data[settings.JSON_KEYS['RIDER_ID']])
        try:
            rider = Rider.objects.get(id=id)
            rider.push_id = data.get(settings.JSON_KEYS['RIDER_PUSH_ID'], '')
            rider.save()

            return Response(
                {settings.JSON_KEYS['RIDER_ID']:
                    data[settings.JSON_KEYS['RIDER_ID']]},
                status=status.HTTP_201_CREATED
            )

        except Exception as ex:
            return Response(
                {settings.JSON_KEYS['BAD_REQ']: ex.message},
                status=status.HTTP_400_BAD_REQUEST
            )
