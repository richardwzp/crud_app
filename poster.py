import requests as requests


def create_inven():
    for id in range(1000, 1005):
        ans = {"cost": 20,
         "country_code_of_origin": "FR",
         "harmonized_system_code": "123456",
         "id": id,
         "province_code_of_origin": "CA",
         "sku": "huh123",
         "tracked": True,
         "required_shipping": False,
         "country_harmonized_system_codes":
             [{"harmonized_system_code": "123456",
               "country_code": "CA"}]}
        requests.post('http://127.0.0.1:5000/create', json=ans)
    ans = requests.get('http://127.0.0.1:5000/get', params={"ids": ",".join([str(i) for i in range(1000, 1005)])})
    for an in ans.json()['inventory_items']:
        print(an)

    #for id in range(1000, 1005):
    #    requests.delete('http://127.0.0.1:5000/delete', params={'id': id})


if __name__ == '__main__':
    create_inven()