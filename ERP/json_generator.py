import json
from operator import attrgetter

from order import *


class JsonGenerator:

    @staticmethod
    def generate(transformation_orders: list[TransformationOrder], delivery_orders: list[DeliveryOrder], loading_orders: list[LoadingOrder]):

        full_list = transformation_orders + delivery_orders + loading_orders
        min_d = min(full_list, key=attrgetter('planning_day')).planning_day
        max_d = max(full_list, key=attrgetter('planning_day')).planning_day

        dictionary = {}

        for d in range(min_d, max_d + 1):

            dictionary[f'{d}'] = {}
            dictionary[f'{d}']['ProductionOrders'] = []
            for order in transformation_orders:
                if order.planning_day == d:
                    dictionary[f'{d}']['ProductionOrders'].append({
                        'id': order.id,
                        'initial_type': order.initial_type,
                        'final_type': order.final_type,
                        'quantity': order.quantity
                    })
            dictionary[f'{d}']['UnloadingOrders'] = []
            for order in delivery_orders:
                if order.planning_day == d:
                    dictionary[f'{d}']['UnloadingOrders'].append({
                        'id': order.id,
                        'type': order.type,
                        'quantity': order.quantity
                    })
            dictionary[f'{d}']['LoadingOrders'] = []
            for order in loading_orders:
                if order.planning_day == d:
                    dictionary[f'{d}']['LoadingOrders'].append({
                        'id': order.id,
                        'name': order.name,
                        'type': order.type,
                        'cost': order.cost,
                        'quantity': order.quantity
                    })

        print(dictionary)

        json_string = json.dumps(dictionary)

        return json_string