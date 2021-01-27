from numpy.core.fromnumeric import argmax
from . import predict

img_paths = ['/home/serena/Desktop/proj2_storytelling/storytelling/statics/uploaded_imgs/1609853089.6942558user1.png',
                '/home/serena/Desktop/proj2_storytelling/storytelling/statics/uploaded_imgs/1609853095.5605984user2.png',
                '/home/serena/Desktop/proj2_storytelling/storytelling/statics/uploaded_imgs/1609853100.6583555user3.png']
# get attributes of the users' faces
class User_face:
    def __init__(self, user_number, gender, age1, age2, attributes):
        self.user_number = user_number
        self.gender = gender
        self.age1 = age1
        self.age2 = age2
        self.attributes = attributes
        self.score = []

class Character:
    def __init__(self, index, name, gender, gender_weight, age1, age2, age_weight, attributes, attribute_weight):
        self.index = index
        self.name = name
        self.gender = gender
        self.gender_weight = gender_weight
        self.age1 = age1
        self.age2 = age2
        self.age_weight = age_weight
        self.attributes = attributes
        self.attribute_weight = attribute_weight


prince = Character(0, 'prince', 'Male', 50, 5, 25, 25, ['Attractive', 'Young', 'Oval_Face'], 15)
princess = Character(1, 'princess', 'Female', 50, 5, 25, 25, ['Attractive', 'Young', 'Oval_Face'], 15)
wizard = Character(2, 'wizard', 'Male', 10, 30, 80, 50, ['Chubby', 'Eeyeglasses', 'Bags_Under_Eyes', 'Mustache', 'Heavy_Makeup', 'Goatee'], 25)
rabbit = Character(3, 'Rabbit', 'Female', 10, 0, 10, 50, ['Chubby', 'Young', 'Pale_Skin', 'Wearing_Lipstick'], 30)
character_set = [prince, princess, wizard, rabbit]

def calculate_score(user_face):
    def calculate_single(user_face, character):
        single_score = 0
        if user_face.gender == character.gender:
            single_score += character.gender_weight
        if user_face.age1 in range(character.age1, character.age2+1) or user_face.age2 in range(character.age1, character.age2+1):
            single_score += character.age_weight
        for attr in user_face.attributes:
            if attr in character.attributes:
                single_score += character.attribute_weight
        return single_score
    user_score = []
    for cha in character_set:
        user_score.append(calculate_single(user_face, cha))
    return user_score



def character_mapping(img_paths):
    user_face_set = []
    for i, img_path in enumerate(img_paths):
        gender, age1, age2, attributes = predict.get_attributes(img_path)
        user_face_set.append(User_face(i+1, gender, int(age1), int(age2), attributes))
    user_scores = []
    for user in user_face_set:
        user_score = calculate_score(user)
        user.score = user_score
        print("user " + str(user.user_number) + " got the scores for prince, princess, wizard, rabbit :", user_score)
        user_scores.append(user_score)
    print(user_scores)
    user_characters = []
    for user_score in user_scores:
        selected_index = user_score.index(max(user_score))
        selected = character_set[selected_index]
        user_score_co = user_score.copy()
        while selected.name in user_characters:  
            user_score_co[selected_index] = -1
            selected_index = user_score_co.index(max(user_score_co))
            selected = character_set[selected_index]
        user_characters.append(selected.name)
    print(user_characters)
    return user_characters, user_face_set

