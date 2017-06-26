import json
import os
import face_matcher
import shutil
from flask import Flask, request
app = Flask(__name__)



def get_customer_id():
    dir_list = os.listdir('database')
    if not dir_list:
        return '1'
    dir_list = [int(item) for item in dir_list]
    customer_id = str(int(max(dir_list)) + 1)
    return customer_id



@app.route("/")
def hello():
    return "Server is working!"

@app.route("/exit",methods=['POST'] )
def exit():
    if 'face' not in request.files:
        print "No face image received in exit() ['POST']"
        return 'No image file received!'

    if 'shoes' not in request.files:
        print "No shoes image received in exit() ['POST']"
        return 'No image file received!'

    image_file = request.files.get('face', '')
    with open('temp/temp_image.jpg','w') as file:
        image_file.save(file)

    shoes_file = request.files.get('shoes', '')
    with open('temp/shoes_temp_image.jpg','w') as file:
        shoes_file.save(file)
    faceMatcher = face_matcher.FaceMatcher()


    shoes_photo_path_list = []
    face_score_list = []
    for entry in os.listdir('database'):
        entry_path = 'database/' + entry + '/face.jpg'
        shoes_photo_path_list.append('database/' + entry + '/shoes.jpg')
        face_score_list.append(faceMatcher.compare_faces('temp/temp_image.jpg',entry_path))
    shoes_score_list = faceMatcher.compare_shoes('temp/shoes_temp_image.jpg', shoes_photo_path_list)

    w1 = 1
    w2 = 1
    min_r = 9999999999
    match = ''
    for i in range(0, len(shoes_score_list)):
        r = w1*face_score_list[i] + w2*shoes_score_list[i]
        
        if r < min_r:
            min_r = r
            match = os.listdir('database')[i]
        print '-----------'
        print 'Shoes:'
        print shoes_score_list[i]
        print 'Face:'
        print face_score_list[i]        
        print r
    print 'Min:'
    print min_r
    if min_r > 1.4:
        return json.dumps({'status': 'Client not found', 'found': False })
    with open('database/'+match+'/parameters.json') as f:
        parameters =  json.load(f)
    if 'debug' in request.values:
        if request.values.get('debug') == '1':
            print 'debug'
            return json.dumps({'status': 'Client found!', 'id': match, 'found': True, 'weight': parameters['weight'] })
    shutil.rmtree('database/'+match)
    return json.dumps({'status': 'Client found!', 'id': match, 'found': True, 'weight':parameters['weight'] })



@app.route("/enter",methods=['POST'] )
def enter():
    if 'face' not in request.files:
        print "No face image received in enter() ['POST']"
        return 'No image file received!'

    if 'shoes' not in request.files:
        print "No shoes image received in enter() ['POST']"
        return 'No image file received!'

    if 'weight' not in request.values:
        print "No weight value received in enter() ['POST']"
        return "No weight value received"

    image_file = request.files.get('face', '')
    customer_id = get_customer_id()
    os.makedirs('database/'+customer_id)
    with open('database/'+customer_id+'/face.jpg','w') as file:
        image_file.save(file)
    shoes_file = request.files.get('shoes', '')
    with open('database/'+customer_id+'/shoes.jpg','w') as file:
        shoes_file.save(file)
    customer_dict = {'weight':request.values.get('weight')}
    customer_dict['id'] = customer_id
    customer_dict['status'] = 'success'
    json_string = json.dumps(customer_dict)
    with open('database/'+customer_id+'/parameters.json','w') as file:
        file.write(json_string)
    return json_string



if __name__ == "__main__":
    app.run()
