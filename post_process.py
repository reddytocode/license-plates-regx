def return_dict(list):
    dict = {}
    for plate in list:
        if(plate in dict):
            dict[plate] = dict[plate] + 1
        else:
            dict[plate] = 1
    return dict

def isNumber(character):
    return True if(character<='9' and character>='0') else False
def isLetter(character):
    return True if((character<='z' and character>='a') or (character<='Z' and character>='A')) else False

def lookForIntersection(plate):
    listIntersections = []
    for i in range(len(plate)-1):
        if(isNumber(plate[i]) and isLetter(plate[i+1])):
            listIntersections.append(i)
    return listIntersections
    
letter_to_number = {'z':'2', 's':'5', 'g':'6', 'i':'1','l':'1', 'a':'4', 't':'7', 'b':'8', 'o':'0'}
number_to_letter = {'2':'z', '5':'s', '6':'g', '1':'i', '4':'a', '7':'t', '8':'b', '0':'o'}

def change_letter_to_number(c):
    return letter_to_number[c] if (c in letter_to_number) else c

def change_number_to_letter(c):
    return number_to_letter[c] if (c in number_to_letter) else c
    
def replace(plate, flag, debug=False):
    if (debug):
        print(len(plate))
    auxL = flag
    auxR = flag+1
    aux_numerical = ""
    aux_letter = ""
    while(auxL>-1):
        if(isNumber(plate[auxL])):
            aux_numerical += plate[auxL]
        elif(isNumber(change_letter_to_number(plate[auxL]))):
            aux_numerical += change_letter_to_number(plate[auxL])
        auxL -= 1
    aux_numerical = aux_numerical[::-1]
    
    while(auxR<len(plate)):
        if(isLetter(plate[auxR])): 
            aux_letter += plate[auxR]
        elif(isLetter(change_number_to_letter(plate[auxR]))):
            aux_letter += change_number_to_letter(plate[auxR])
        auxR += 1
        
    #print(aux_numerical, " and ", aux_letter)
    res = aux_numerical+aux_letter
    return res

def count_number_and_letters(plate, flag, debug=False):
    #plate = replace(plate, flag)
    if (debug):
        print(len(plate))
    auxL = flag
    auxR = flag+1
    numbers = 0
    letters = 0
    while(auxL>-1):
        if (isNumber(plate[auxL])):
            numbers += 1
        if (debug):
            print(auxL, " ", plate[auxL])
        auxL -= 1
    if debug:
        print()
    while(auxR<len(plate)):
        if (debug):
            print(auxR, " ", plate[auxR])
        if(isLetter(plate[auxR])):
            letters += 1
        auxR += 1
    return numbers, letters

def filter2(word, flag):
    word = replace(word, flag)
    flag = lookForIntersection(word)[0]
    auxL = flag
    auxR = flag + 1
    number = ""
    numbers = 0
    letter = ""
    letters = 0
    while(auxL>-1):
        if(isNumber(word[auxL]) and numbers < 4):
            number += word[auxL]
            numbers += 1
        auxL -= 1
    number = number[::-1]
    while(auxR<len(word)):
        if(isLetter(word[auxR]) and letters < 3):
            letter += word[auxR]
            letters += 1
        auxR += 1
    
    return number+letter if(numbers==4 and letters==3) else ""

def filter(test, debug=False):
    answers = []
    for plate in test:
        aux = lookForIntersection(plate)
        if (len(aux) >0):
            
            #numbers, letters = count_number_and_letters(plate, aux[0], False)
            #if(numbers == 4 and letters == 3):
            #    #print(plate)
            #    answers.append(plate)
            #else:
            value = filter2(plate, aux[0])
            if(len(value)>0):
                answers.append(value)
            if(debug):
                print("bo cumple")
    return answers

def choose_the_best(car_id, debug = False):
    try:
        wordsFreqDict = return_dict(filter(car_id))
        listofTuples = reversed(sorted(wordsFreqDict.items() ,  key=lambda x: x[1]))
        # Iterate over the sorted sequence
        cont_in_list = 0
        for elem in listofTuples :
            if(cont_in_list==0):
                if (debug):
                    print(type(elem[0]) , " ::" , elem[1] )
                return elem[0]
            else:
                break
            cont_in_list += 1
    except:
        print("error")
        return "placa no visible"


#####if  is an old plate
def filter3_old(word, flag):
    #word = replace(word, flag)
    flag = lookForIntersection(word)[0]
    auxL = flag
    auxR = flag + 1
    number = ""
    numbers = 0
    letter = ""
    letters = 0
    while(auxL>-1):
        if(isNumber(word[auxL]) and numbers < 3):
            number += word[auxL]
            numbers += 1
        auxL -= 1
    number = number[::-1]
    while(auxR<len(word)):
        if(isLetter(word[auxR]) and letters < 3):
            letter += word[auxR]
            letters += 1
        auxR += 1
    
    return number+letter if(numbers==3 and letters==3) else ""

def find_old_plate(tres):
    posible_answers = []
    for old_plate in list(return_dict(tres).keys()):
        intersections = lookForIntersection(old_plate)
        for intersection in intersections:
            #send value to the post processing part only if intersetcion is greater than 2
            if(intersection >= 2):
                filtered_old_plate = filter3_old(old_plate, intersection)
                if (len(filtered_old_plate)>0):
                    posible_answers.append(filtered_old_plate)
                #print(intersection, old_plate, sep= '; ')
    old_plate_poss=return_dict(posible_answers)
    ans = sorted(old_plate_poss)
    return ans[-1]
    