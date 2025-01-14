from geopy.distance import distance
import json
import requests
import urllib


#＜＜通勤交通費支給規定＞＞
# ・勤務地まで歩行距離２ｋｍ 以上で公共交通機関を利用して通勤する場合支給
# ・バス路線は、最寄駅までの距離が１．５ｋｍ 未満の利用不可
# ・最低料金の路線（以下「経済路線」という）を利用
# 　ただし、以下に該当すれば経済路線との差額（上限〇.〇千円）を上限に支給 ※実際は１万５千円
# 　　ア． 経済路線では乗換回数が増加する。
# 　　　　　（同一ホームにおける乗換えは、乗換え回数に参入しない）
# 　　イ． 経済路線では通勤所要時間（片道）が２０分以上増加
# 　　　　　（徒歩区間は 80m ／分、乗換え 5 分／回として算定）
# 　　ウ．経済路線では運転間隔が 15 分以上ひらく
# ・通勤交通費の上限は、１ヵ月あたり〇万円 ※実際は１ヶ月７万円
# ・公共の交通機関が無い場合は自転車通勤可。ただし10km 未満。※2km以上は自転車手当〇千円を支給 ※実際は4,200円

# 通勤交通費支給規定を満たしているかどうかを判定する関数
WORK_COORDS = (35.674551498111555, 139.81642056742788)
def is_commute_allowance(
        home_address, 
        transportation_type, 
        route_json=None, 
        economic_route_json=None, 
        is_bicycle_commute=False, 
        bus_route_json=None):

    # 自宅から会社までの距離を計算
    makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    s_quote = urllib.parse.quote(home_address)
    response = requests.get(makeUrl + s_quote)
    home_latitute = response.json()[0]["geometry"]["coordinates"][1]
    home_longitude = response.json()[0]["geometry"]["coordinates"][0]
    home_coords = (home_latitute, home_longitude)
    work_coords = WORK_COORDS
    
    distance_home_to_work_km = distance(home_coords, work_coords).km
    if distance_home_to_work_km < 2:
        return (False, '自宅から勤務地までの歩行距離が2km未満のため、公共交通機関を利用しての通勤不可。')
    
    # 通勤経路がバスの場合、最寄駅までの距離を計算
    if transportation_type == 'bus' and bus_route_json:
        # 文字列の場合、jsonに変換
        if isinstance(bus_route_json, str):
            bus_route_json = json.loads(bus_route_json)
        station = bus_route_json["Course"]["Route"]["Point"][-1]
        station_coords = (float(station["GeoPoint"]["lati_d"]), float(station["GeoPoint"]["longi_d"]))
        distance_home_to_station_km = distance(home_coords, station_coords).km
        if distance_home_to_station_km < 1.5:
            return (False, '自宅から最寄駅までの距離が1.5km未満のため、バス利用不可。')
    
    # 支給経路をかどうかを判定

    # ア． 経済路線では乗換回数が増加する。
    if route_json and economic_route_json:
        # 文字列の場合、jsonに変換
        if isinstance(route_json, str):
            route_json = json.loads(route_json)
        if isinstance(economic_route_json, str):
            economic_route_json = json.loads(economic_route_json)
        
        if route_json["Course"]["SerializeData"] == economic_route_json["SerializeData"]:
            return (True, '通勤交通費支給規定を満たしています。')
        selected_transfer_count = int(route_json["Course"]["Route"]["transferCount"])
        economic_transfer_count = int(economic_route_json["Route"]["transferCount"])
        if selected_transfer_count > economic_transfer_count:
            return (False, '選択した経路では経済路線と比べて乗り換え回数が増加するため、支給対象外')
        
        # イ． 経済路線では通勤所要時間（片道）が２０分以上増加
        selected_time = int(route_json["Course"]["Route"]["timeOnBoard"] + route_json["Course"]["Route"]["timeWalk"] + route_json["Course"]["Route"]["timeOther"]) 
        economic_time = int(economic_route_json["Route"]["timeOnBoard"] + economic_route_json["Route"]["timeWalk"] + economic_route_json["Route"]["timeOther"])
        if economic_time - selected_time < 20:
            return (False, '選択した経路では経済路線と比べて通勤所要時間の増加量が20分未満なため、支給対象外')
    
        # ウ．経済路線では運転間隔が 15 分以上ひらく

    # 通勤手段が自転車の場合、自転車通勤が可能かどうかを判定
    if is_bicycle_commute:
        if distance_home_to_work_km >= 10:
            return (False, '自宅から勤務地までの距離が10km以上です。')  

    return (True, '通勤交通費支給規定を満たしています。')    

# 自転車通勤手当を支給するかどうかを判定する関数

# ・公共の交通機関が無い場合は自転車通勤可。ただし10km 未満。※2km以上は自転車手当〇千円を支給 ※実際は4,200円

def is_bicycle_allowance(home_address):
    # 自宅から会社までの距離を計算
    makeUrl = "https://msearch.gsi.go.jp/address-search/AddressSearch?q="
    s_quote = urllib.parse.quote(home_address)
    response = requests.get(makeUrl + s_quote)
    home_latitute = response.json()[0]["geometry"]["coordinates"][1]
    home_longitude = response.json()[0]["geometry"]["coordinates"][0]
    home_coords = (home_latitute, home_longitude)
    work_coords = WORK_COORDS
    
    distance_home_to_work_km = distance(home_coords, work_coords).km
    if distance_home_to_work_km >= 10:
        return (False, '自宅から勤務地までの距離が10km以上です。', 0)  
    
    if distance_home_to_work_km < 2:
        return (True, '自宅から勤務地までの歩行距離が2km未満のため、自転車通勤手当は支給されません。', 0)
    
    return (True, '自転車通勤手当を支給します。', 4200)  

    




