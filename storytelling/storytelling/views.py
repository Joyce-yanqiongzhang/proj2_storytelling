import sys
import os
sys.path.append('..')
#sys.path.append(os.path.dirname(__file__) + os.sep + '../')
from django.http import JsonResponse
from django.shortcuts import render
import base64
from django.conf import settings
import time
import json
from .generate_story_from_img import character_mapping, User_face
import generate_fairytale as gf
#from ..generate_fairytale import generate_story_from_characters

 
sys.path.insert(0, "./story/pytorch_src")

def story_page(request):
    context = {}
    request.session["num_of_usr"] = 0
    request.session["usr_imgs"] = []
    return render(request, 'index.html', context)

def sepa_storypage(request):
    context = {}
    request.session["num_of_usr"] = 0
    request.session["usr_imgs"] = []
    room_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_room.txt'
    is_new_session = False
    with open(room_path, 'r+') as f:
        for line in f.readlines():
            if "STORY" in line:
                is_new_session = True
    f.close()
    if is_new_session:
        with open(room_path, 'w') as f1:
            f1.seek(0)
            f1.truncate()
            print("cleared buffer room text")
        f1.close()
    return render(request, 'storyindex.html', context)

def take_photo_page(request):
    context = {}
    return render(request, 'take_phto.html', context)

def upload_img(request):
    img_data = request.POST.get('img_data')
    img_base64 = img_data.split(',')[1]
    print(img_data.split(',')[0])
    print(img_base64[:100])
    data = base64.b64decode(img_base64)
    
    num_of_usr = request.session.get('num_of_usr')
    num_of_usr += 1
    print("num of user:", str(num_of_usr))
    usr_imgs = request.session.get('usr_imgs')
    img_path_sub = str(time.time()) + "user" + str(num_of_usr) + ".png"
    img_path = settings.MEDIA_ROOT + img_path_sub
    usr_imgs.append(img_path)
    print("user img paths: ", usr_imgs)
    with open(img_path, 'wb') as f:
        f.write(data)
    f.close()

    request.session["num_of_usr"] = num_of_usr
    request.session["usr_imgs"] = usr_imgs
    redata = {"test":"ok"}
    redata["img_url"] = "../static/uploaded_imgs/" + img_path_sub
    redata["user_num"] = str(num_of_usr)
    room_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_room.txt'
    if os.path.exists(room_path):
        with open(room_path, 'a+') as f:
            if os.path.getsize(room_path)==0:
                f.write('USERS\n')
            f.write("../static/uploaded_imgs/" + img_path_sub + '\n')
    f.close()
    return JsonResponse(redata)

    
def map_character(request):
    print('invoking map character')
    img_paths = get_user_photos_abs()
    print('img paths:', img_paths)
    user_characters, user_face_set = character_mapping(img_paths)
    print(user_characters)
    print(user_face_set)
    request.session["usr_characters"] = user_characters
    num_of_usr = request.session.get("num_of_usr")
    redata = {}
    redata["user_num"] = num_of_usr
    for i, user in enumerate(user_face_set):
        print("user"+str(i+1)+" gender: ", user.gender)
        print("user"+str(i+1)+" age: " + str(user.age1)+"-"+str(user.age2) )
        print("user"+str(i+1)+" attributes: " + ",".join(user.attributes))
        print("user"+str(i+1)+" score: " + ",".join(list(map(str, user.score))))
        print("user"+str(i+1)+" character: " + user_characters[i])
        redata["user"+str(i+1)+"gender"] = user.gender
        redata["user"+str(i+1)+"age"] = str(user.age1)+"-"+str(user.age2)
        redata["user"+str(i+1)+"attributes"] = ",".join(user.attributes)
        redata["user"+str(i+1)+"score"] = ",".join(list(map(str, user.score)))
        redata["user"+str(i+1)+"character"] = user_characters[i]
    room_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_room.txt'
    with open(room_path, 'a+') as f:
        f.write('CHARACTERS\n')
        for cha in user_characters:
            f.write(cha+'\n')

    return JsonResponse(redata)
    

def generate_story(request):
    character_set = get_user_characters()
    # os.system("ls")
    # os.system("cd storytelling")
    # os.system("ls")
    # os.system("cd ..")
    # os.system("python story/pytorch_src/generate_fairytale.py")
    gf.generate_story_from_characters(character_set)
    story_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_story.txt'
    storyline, story = get_story(story_path)
    redata = {}
    redata['storyline'] = storyline
    redata['story'] = story
    redata['characters'] = ', '.join(character_set)

    title_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_title.txt'
    with open(title_path, 'r') as f:
        line = f.readline()
        splited_line = line.split()
    f.close()
    environment = splited_line[2]
    redata['environment'] = environment
    print('Environment: ', environment)
    print('CharacterSet: ', character_set)
    print('Storyline: ', storyline)
    print('Story: ', story)
    room_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_room.txt'
    with open(room_path, 'a+') as f:
        f.write("STORY\n")
    return JsonResponse(redata)

def get_user_photos_abs():
    room_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_room.txt'
    static_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/'
    user_photos = []
    with open(room_path, 'r+') as f:
        usersend = False
        for line in f.readlines():
            if 'CHARACTERS' in line:
                usersend = True
            if not usersend:
                if not 'USERS' in line:
                    line = line.replace('\n', '')
                    line = line.replace('../static/', '')
                    line = static_path + line
                    user_photos.append(line.replace('\n', ''))
            else:
                break
    f.close()
    return user_photos

def get_user_characters():
    room_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_room.txt'
    characters = []
    with open(room_path, 'r+') as f:
        character_start = False
        character_end = False
        for line in f.readlines():
            if character_start and not character_end and not 'STORY' in line:
                characters.append(line.replace('\n', ''))
            if 'CHARACTERS' in line:
                character_start = True
            if 'STORY' in line:
                character_end = True
    f.close()
    return characters

def get_story(story_path):
    #redata = {}
    storyline = ''
    story = ''
    with open(story_path, 'r') as f:
        for i, line in enumerate(f.readlines()):
            if not i==0:
                words = line.split()
                story_flag = False
                for w in words:
                    if w=='<EOL>':
                        story_flag = True
                    if not story_flag:
                        storyline = storyline + w + ' ' 
                    elif not w=='<EOL>' and not w=='</s>':
                        story = story + w + ' '
                story = story + '<br>***** END OF THIS PART *****<br>'
                storyline += '<br>'
        story = story + '***** END OF THE STORY *****<br>'
    #redata['storyline'] = storyline
    #redata['story'] = story
    #print('storyline: ', storyline)
    #print('story: ', story)
    return storyline, story


def update_content(request):
    room_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_room.txt'
    num_of_usr = 0
    user_photos = []
    characters = []
    is_mapped = '0'
    is_story = '0'
    storyline = ''
    story = ''
    with open(room_path, 'r+') as f:
        usersend = False
        character_start = False
        character_end = False
        for line in f.readlines():
            if character_start and not character_end and not 'STORY' in line:
                characters.append(line.replace('\n', ''))
            if 'CHARACTERS' in line:
                is_mapped = '1'
                usersend = True
                character_start = True
            if 'STORY' in line:
                is_story = '1'
                character_end = True
            if not usersend and not 'USERS' in line:
                num_of_usr += 1
                user_photos.append(line.replace('\n', ''))
    f.close()
    redata = {}
    redata['user_num'] = str(num_of_usr)
    redata['is_mapped'] = is_mapped
    redata['is_story'] = is_story
    redata['user_photos'] = ','.join(user_photos)
    redata['characters'] = ','.join(characters)
    if is_story=='1':
        story_path = '/home/serena/Desktop/proj2_storytelling/story/storytelling/statics/text/buffer_story.txt'
        storyline, story = get_story(story_path)
    redata['storyline'] = storyline
    redata['story'] = story

    return JsonResponse(redata)

            
            



