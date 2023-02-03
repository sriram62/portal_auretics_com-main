def get_mrp(batch):
    if batch.mrp == None:
        batch.mrp = 0
    mrp = batch.mrp
    mrp = "{:.2f}".format(mrp)
    mrp = float(mrp)
    return mrp

def get_distributor_price_excluding_tax(mrp, distributor_price, igst):
    if igst == None:
        igst = 0
    if mrp == None:
        mrp = 0
    igst = float(igst)
    mrp = float(mrp)
    distributor_price_amount_ex_tax = mrp/(((100+distributor_price)/100)*((100 + igst)/100))
    distributor_price_amount_ex_tax=round(distributor_price_amount_ex_tax,2)
    distributor_price_amount_ex_tax = float(distributor_price_amount_ex_tax)
    return distributor_price_amount_ex_tax

def calculate_values(product):
    pv_bv_set = []
    all_batches = product.batch_set.all().order_by('-id')
    for batch in all_batches:
        pv_bv_batch = {}
        mrp = get_mrp(batch)
        distributor_price_amount_ex_tax = get_distributor_price_excluding_tax(mrp, product.distributor_price, product.igst)
        # logic for calculate point value
        p_value = product.point_value
        actual_point_value = distributor_price_amount_ex_tax * p_value / 100
        actual_point_value = round(actual_point_value, 2)
        actual_point_value = "{:.2f}".format(actual_point_value)

        # logic for calculate business value
        b_value = product.business_value
        actual_business_value = distributor_price_amount_ex_tax * b_value / 100
        actual_business_value = round(actual_business_value, 2)
        actual_business_value = "{:.2f}".format(actual_business_value)
        
        # Prepare data
        pv_bv_batch['batch'] = batch
        pv_bv_batch['point_value'] = actual_point_value
        pv_bv_batch['business_value'] = actual_business_value
    
        pv_bv_set.append(pv_bv_batch)
    
    return pv_bv_set

def calculated_point_value(product,price,quantity):
    p_value = product.point_value
    if p_value == None:
        p_value = 0
    actual_point_value = float(price) * p_value / 100
    actual_point_value = round(actual_point_value, 2)
    actual_point_value = "{:.2f}".format(actual_point_value)
    if quantity == None:
        quantity = 0
    pv_amount = float(actual_point_value) * int(quantity)
    return pv_amount

def calculated_partial_loyalty_details(product, excess_cri):
    # pv = product.point_value
    # if pv == None:
    #     pv = 0
    # bv = product.business_value
    # if bv == None:
    #     bv = 0
    dp = product.distributor_price
    if dp == None:
        dp = 0
    # tax = product.igst
    # if tax == None:
    #     tax = 0
    dp = round(excess_cri / ((100 + dp) / 100), 2)
    dp_ex_tax = round(dp / ((100 + product.igst)/100))
    pv = round(calculated_point_value(product, dp_ex_tax, 1), 2)
    bv = round(calculated_business_value(product, dp_ex_tax, 1), 2)
    return pv, bv, dp


def calculated_partial_loyalty_point_value(product, price, quantity, total_price):
    p_value = product.point_value
    if p_value == None:
        p_value = 0
    actual_point_value = float(price) * p_value / 100
    actual_point_value = round(actual_point_value, 2)
    actual_point_value = "{:.2f}".format(actual_point_value)
    if quantity == None:
        quantity = 0
    pv_amount = float(actual_point_value) * int(quantity)
    return round(pv_amount * total_price / float(price), 2)


def calculated_business_value(product, price, quantity):
    b_value = product.business_value
    if b_value == None:
        b_value = 0
    actual_business_value = float(price) * b_value / 100
    actual_business_value = round(actual_business_value, 2)
    actual_business_value = "{:.2f}".format(actual_business_value)
    if quantity == None:
        quantity = 0
    bv_amount = float(actual_business_value) * int(quantity)
    return bv_amount


def calculated_partial_loyalty_business_value(product, price, quantity, total_price):
    b_value = product.business_value
    if b_value == None:
        b_value = 0
    actual_business_value = float(price) * b_value / 100
    actual_business_value = round(actual_business_value, 2)
    actual_business_value = "{:.2f}".format(actual_business_value)
    if quantity == None:
        quantity = 0
    bv_amount = float(actual_business_value) * int(quantity)
    return round(bv_amount * total_price / float(price), 2)


def calculate_loyalty_sale_product_total(batch, consumed_cri):
    dp = batch.get_distributor_price()
    mrp = batch.mrp
    pro_rate = dp / mrp
    post_free = mrp - consumed_cri
    return round(post_free * pro_rate, 2)






























#<---------------------------------------------------------------------------------------------------------------------------------------------------------->


# Don't use this function calculation is wrong here, we need to remove this function
def calculated_Pv(product,price,quantity):
    pv = product.point_value
    if pv == None:
        pv = 0
    pv = float(price) * float((pv / 100))
    if quantity == None:
        quantity = 0
    pv_amount = float(pv) * int(quantity)
    return pv_amount

# Don't use this function calculation is wrong here, we need to remove this function
def calculated_Bv(product,price,quantity):
    bv = product.business_value
    if bv == None:
        bv = 0
    bv = float(price) * float((bv / 100))
    if quantity == None:
        quantity = 0
    bv_amount = float(bv) * int(quantity)
    return bv_amount

