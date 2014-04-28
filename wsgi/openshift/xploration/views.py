'''
Homepage, Simulator and REST views
'''
import json
from django.http import HttpResponse, StreamingHttpResponse
#import random
from django.shortcuts import render_to_response
from django.http import Http404
import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

'''
import verity tables for mission's checking
'''
from data.tables_Bodies import destinations
from data.tables_Missions import mission_type
from data.tables_BusVsMission import bus_vs_mission_type
from data.tables_BusVsDist import bus_vs_dist
from data.tables_BusVsBus import bus_vs_bus
#from data.missions import missions
#from data.missions_details import missions_details


'''
import models and json serializers
'''
from models import Missions, Targets, Details, Planets
from serializers import TargetsSerializer, MissionsSerializer, DetailsSerializer, PlanetsSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def targets_list(request):
    '''
    List all possible Targets
    '''
    if request.method == 'GET':
        targets = Targets.objects.all()
        serializer = TargetsSerializer(targets, many=True)
        return JSONResponse(serializer.data)
    else:
        mex = {'response': '404', 'code': 1, 'message': 'NO POST, PUT or DELETE for this endpoint'}
        return JSONResponse(mex)

@csrf_exempt
def target_detail(request, t_id):
    '''
    Reply with only one among Targets
    '''
    try:
        target = Targets.objects.get(id=t_id)
    except Targets.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = TargetsSerializer(target)
        return JSONResponse(serializer.data)
    else:
        mex = {'response': '404', 'code': 1, 'message': 'NO POST, PUT or DELETE for this endpoint'}
        return JSONResponse(mex)

@csrf_exempt
def missions_list(request):
    '''
    List all possible Missions
    '''
    if request.method == 'GET':
        mix = Missions.objects.all()
        serializer = MissionsSerializer(mix, many=True)
        return JSONResponse(serializer.data)
    else:
        mex = {'response': '404', 'code': 1, 'message': 'NO POST, PUT or DELETE for this endpoint'}
        return JSONResponse(mex)

@csrf_exempt
def single_mission(request, m_id):
    '''
    Get single mission by mission id
    '''
    if request.method == 'GET':
        one_mission = Missions.objects.all().filter(id=m_id)[0]
        name_mission = one_mission.name
        all_target = Missions.objects.all().filter(name=name_mission)
        mission_targets = []
        for t in all_target:
            mission_targets.append(t.target.id)
        obj = {'target': mission_targets, 'era': one_mission.era, 'name': one_mission.name,
               'codename': one_mission.codename, 'hashed': one_mission.hashed, 'image_url': one_mission.image_url,
               'launch_date': one_mission.launch_date  }
        serializer = json.dumps(obj)
        return StreamingHttpResponse(serializer, content_type="application/json")
    else:
        mex = {'response': '404', 'code': 1, 'message': 'NO POST, PUT or DELETE for this endpoint'}
        return JSONResponse(mex)


@csrf_exempt
def mission_detail(request, m_id):
    '''
    Reply with all the data referred to one Missions.
    Search by mission id
    '''
    try:
        mix_details = Details.objects.all().filter(mission=m_id)
    except Targets.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = DetailsSerializer(mix_details)
        return JSONResponse(serializer.data)
    else:
        mex = {'response': '404', 'code': 1, 'message': 'NO POST, PUT or DELETE for this endpoint'}
        return JSONResponse(mex)

@csrf_exempt
def missions_by_target(request, t_id):
    '''
    Reply with all the data referred to one Targets.
    Search by target id
    '''
    try:
        target_missions = Missions.objects.all().filter(target=t_id)
        #mix_details = Details.objects.all().filter(mission=m_id)
    except Targets.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = MissionsSerializer(target_missions)
        return JSONResponse(serializer.data)
    else:
        mex = {'response': '404', 'code': 1, 'message': 'NO POST, PUT or DELETE for this endpoint'}
        return JSONResponse(mex)


def home(request):
    js = {'status': 'Coming Soon...', 'response': 200, 'code': 0}
    js = json.dumps(js)
    
    params = {}
    params['keywords'] = 'explore space planets star journey satellites exploration solar system simulation play'
    params['status'] = js
    return render_to_response('home/home.html', params)

def test(request):
    from data.ESA_output_COMPLETE import missions
    from data.ESA_MISSIONS_COMPLETE import ESA_missions

    from unicodedata import normalize

    def slug(text, encoding=None,
               permitted_chars='abcdefghijklmnopqrstuvwxyz0123456789_'):
        if isinstance(text, str):
            text = text.decode(encoding or 'ascii')
        clean_text = text.strip().replace(' ', '_').lower()
        while '__' in clean_text:
            clean_text = clean_text.replace('__', '_')
        ascii_text = normalize('NFKD', clean_text).encode('ascii', 'ignore')
        strict_text = map(lambda x: x if x in permitted_chars else '', ascii_text)
        return ''.join(strict_text)
 

    for m in ESA_missions:
        try:
            new = Missions.objects.all().filter(name=m['name'])[0]
            count = 0
            pass
        except:
            launch_str = str(m["launches"])
            dates = m["launches"]
            print m["short_description"]
            count=0
            for i,e in enumerate(dates):
                if e.find('(failed)'):
                    dates[i] = e.replace('(failed)', '')
            if all(int(i) <= 2000 for i in dates):
                era = 1
            if all(int(i) > 2015 and int(i) < 2020 for i in dates):
                era = 3
            if all(int(i) > 2000 and int(i) <= 2017 for i in dates):
                era = 2
            if all(int(i) > 2020 for i in dates):
                era = 0

            destination = Targets.objects.all().get(name=m["target"])
            new_mission = Missions(image_url=m["mission_image"],
            launch_dates=launch_str,
            name= m["name"][0],
            codename= m['name'][0],
            hashed= slug(m['name'][0]),
            target=destination,
            era=era 
            )
            new_mission.save()
            count += 1

            new = Missions.objects.all().filter(name=m['name'])[0]
            

            #create details
            new_goal= Details(mission=new, detail_type=1, header="Goal",
                body=m["short_description"])
            new_goal.save()
            
            header = m['name'][0]+' Website'
            new_link = Details(mission=new, detail_type=4, header=header , body=m["link"])
            new_link.save()

    return StreamingHttpResponse(json.dumps({'status': 'finished', 'count': count}), content_type="application/json")

def clean(request):

    from data.physics import physics

    for p in physics:
        discover = p['data']
        rings = p['rings']
        light = p['light']
        mass = p['mass']
        diameter = p['diameter']
        density = p['density']
        gravity = p['gravity']
        l_day = p['l_day']
        l_year = p['l_year']
        ecc = p['eccentricity']
        dist = p['distance']
        per = p['perihelion']
        aph = p['aphelion']
        tilt = p['tilt']
        active = p['active']
        atm = p['atmosphere']
        newPla = Planets(discover=discover, rings=rings, light=light, mass=mass, diameter=diameter, density=density, gravity=gravity, l_day=l_day, l_year=l_year, eccent=ecc, distance=dist, perihelion=per, aphelion=aph, inclination=tilt, active=active, atmosphere=atm)
        newPla.save()  

    return StreamingHttpResponse(json.dumps({'status': 'done'}), content_type="application/json")


def homeTEST(request):
    js = {'status': 'Coming Soon...', 'response': 200, 'code': 0}
    js = json.dumps(js)
    
    params = {}
    params['keywords'] = 'explore space planets star journey satellites exploration solar system simulation play'
    params['status'] = js
    return render_to_response('home/homeTEST.html', params)

def simulation(request):

    ''' 
    GET example: 
    /simulation/?
        destination=mars
        &mission=prop_chem
        &opt_sensor=true
        &radio_sensor=false
        &spectrometer=true
        &probe=true
        &amplifierfier=false
    '''

    if 'destination' not in request.GET: # raise 404 if not destination in the URL
        raise Http404

    results = {}


    usr_planet = request.GET['destination']


    # cycles destinations in table_Bodies.py
    for p in destinations:
        if p['slug'] == usr_planet:
            usr_planet = p
    

    if 'mission' not in request.GET: # raise 404 if not mission in the URL
        raise Http404

    usr_mission_slug = request.GET['mission']
    #print  usr_planet['name'], usr_mission['name']

    # check compatibility planet/mission  
    if usr_planet[usr_mission_slug] != True :
        results = {'code': 1, 'Error': 'Error in mission type ' + usr_mission_slug }
        return StreamingHttpResponse(json.dumps(results), content_type="application/json")
        

    # take components from URL and dump into a list
    components = [k for k,v in request.GET.iteritems() if v == 'true']
    

    #components = ['opt_sensor', 'radio_sensor', 'spectrometer', 'probe', 'amplifier']
    #comp_samples = random.sample(components, random.randint(1, len(components)))

    # check components/mission compatibility - mission_type
    for e in components:
        #print e
        for k in mission_type:
            #print k
            if k['slug'] == usr_mission_slug:
                if k[e] != True: 
                    results = { 'code': 1, 'Error': 'Error in component ' + e }
                    return StreamingHttpResponse(json.dumps(results), content_type="application/json") 

    
    # get BUS components from URL
    busAll = {}
    for k,v in request.GET.iteritems():
        if v == 'bustrue':
            busAll[k] = True

    # check if systems and subsystems are compatible with type of mission - bus_vs_mission_type
    if len(busAll) != 0:
      for e in bus_vs_mission_type:
        if e['slug'] == usr_mission_slug:
            for k,v in busAll.iteritems():
                if e[k] != v:
                    results = {'code': 1, 'Error': 'Error in BUS in system ' + k }
                    return StreamingHttpResponse(json.dumps(results), content_type="application/json")

    

    usr_distance = usr_planet['distance']

    # check if destination's distance is compatible - bus_vs_dist
    if len(busAll) != 0:
        for e in bus_vs_dist:
            j = e['range_min']
            # return StreamingHttpResponse(json.dumps(j), content_type="application/json")
            if isinstance(j, str):
              if j < int(usr_distance):
                for k,v in busAll.iteritems():
                    if e[k] != v:
                        results = { 'code':1, 'Error': 'Error in BUS vs distance ' + k }
                        return StreamingHttpResponse(json.dumps(results), content_type="application/json")


    
    # check if the payload is compatible - bus_vs_bus
    if len(busAll) != 0:
      for e in bus_vs_bus:
        if e['slug'] == usr_mission_slug:
            for k,v in busAll.iteritems():
                if e[k] != v:
                    results = { 'code':1, 'Error': 'Error in BUS in payload check ' + k }
                    return StreamingHttpResponse(json.dumps(results), content_type="application/json")

    results = { 'code':0, 'status':'OK', 'message': 'Mission is way to go!' }
    return StreamingHttpResponse(json.dumps(results), content_type="application/json") 

        



