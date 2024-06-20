# # Dois dicionários com algumas chaves e valores
# dict1 = {
#     'b': 2,
#     'a': 1,
#     'c': 3 
# }

# dict2 = {
#     'a': 1,
#     'c': 3
# }

# # itera sobre os valores, por ordem, sem olhar pra Keys, e sizes diferentes ignora os últimos
# # for v1, v2 in zip(dict1.values(), dict2.values()):
# #     print(v1, v2)

# # Alternativamente, para garantir que as chaves são iguais:
# for key in dict1.keys():
#     if key in dict2:
#         print(dict1[key], dict2[key])


list1 = [1, 2, 3]
list2 = [1, 2, 3]
print (list1 != list2) 
