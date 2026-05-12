# list is basically array 
list1 = ["a", "b", "c", "d", "e"]
# list = 0 1 2 3 4 5. ... n-1


# print(len(list1))  # length of list


# f string 
# a ="hello"
# b = "world"

# print(f' THIS IS {a.upper()} {b.capitalize()} \n {a+b}')  # this is string interpolation)


# for items in list1:
#     # print(items)
#     print(f'this is index {list1.index(items)} -> value {items}')  # this is string interpolation

# print(list1.append("f"))  # this will add f to the end of list1
# print(list1)  # this will print the updated list1 with f added to the end


# print(list1.extend(["f", "g", "h"]))  # this will add f, g, h to the end of list1
# print(list1)  # this will print the updated list1 with f, g, h

# db_link="postgresql://postgres:password@db:5432/mydb"


# s='akhileshmishra@livingdevops.com'

# print(s.split("@"))  # this will split the string at @ and print the first part (akhileshmishra)

d = {"name": "akhilesh", "age": 30, "city": "delhi"}

for key, value in d.items():
    print(f'{key} -> {value}')  # this will print the key and value of the dictionary in the format key -> value