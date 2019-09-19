def make_list_purchase(name_list, goods_list, id_customer):
    def cons_list(data_obtain):
        if data_obtain == 'name':
            return name_list
        elif data_obtain == 'goods':
            return goods_list
        elif data_obtain == 'id':
            return id_customer
        else:
            return None

    return cons_list


def get_name_list(list_purchase):
    return list_purchase('name')


def get_goods(list_purchase, type):
    return list_purchase('goods')


def get_id_customer(list_purchase):
    return list_purchase('id')
