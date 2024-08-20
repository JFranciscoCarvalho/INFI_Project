import json

from order import LoadingOrder, TransformationOrder, UnloadingOrder

order_id_counter = 1

class JsonParser:
    
    @staticmethod
    def parse(data):
        global order_id_counter

        orders = []

        json_data = dict(json.loads(data))

        print(json_data)

        days = json_data.keys()

        for d in days:
            for u in json_data[f'{d}']['UnloadingOrders']:
                for i in range(u['quantity']):
                    orders.append(UnloadingOrder(u['id'], order_id_counter, u['type'], int(d)))
                    order_id_counter += 1
            for p in json_data[f'{d}']['ProductionOrders']:
                for i in range(p['quantity']):
                    orders.append(TransformationOrder(p['id'], order_id_counter, p['initial_type'], p['final_type'], int(d)))
                    order_id_counter += 1
            for l in json_data[f'{d}']['LoadingOrders']:
                for i in range(l['quantity']):
                    orders.append(LoadingOrder(l['id'], order_id_counter, l['name'], l['type'], l['cost'], int(d)))
                    order_id_counter += 1

        return orders