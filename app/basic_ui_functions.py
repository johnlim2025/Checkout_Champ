# suppose CV model gives a prediction each time the user 
# puts and item into the cart

items_dict = {}

def update_dict(prediction, add):
    if prediction in items_dict:
        if add:
            items_dict[prediction] += 1
        else:
            items_dict[prediction] -= 1
            if items_dict[prediction] == 0:
                del items_dict[prediction]
    else:
        items_dict[prediction] = 1


def get_item_list():
    return list(items_dict.keys())

def get_item_count(item):
    return items_dict[item]

def get_pair(item):
    return (item, items_dict[item])

def get_all_pairs():
    return list(items_dict.items())

# simple xample 

update_dict("orange", 1)
update_dict("apple", 1)

print(get_item_list())
print(get_item_count("orange"))
print(get_pair("orange"))
print(get_all_pairs())




