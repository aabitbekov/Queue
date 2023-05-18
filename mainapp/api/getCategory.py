def getMainCategory(category='B, C1'):
    index = 0
    all_categories = ['A1', 'B1', 'A', 'B', 'C1', 'C', 'D1', 'D', 'BE', 'C1E', 'CE', 'D1E', 'DE']

    categories_list = [category.replace(' ', '') for category in category.split(',')]

    for category in categories_list:
        if index < all_categories.index(category):
            index = all_categories.index(category)

    return all_categories[index]
